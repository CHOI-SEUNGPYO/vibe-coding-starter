#!/usr/bin/env python3
"""Install and validate the repository's portable Codex project setup."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
STATE = ".vibe/profile.json"
PROJECT = ".vibe/project.json"


class VibeError(Exception):
    """An actionable configuration or validation error."""


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise VibeError(f"JSON을 읽을 수 없습니다: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise VibeError(f"JSON의 최상위 값은 객체여야 합니다: {path}")
    return value


def identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise VibeError(f"잘못된 {label}: {value!r}")
    return value


def safe_relative(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise VibeError(f"안전하지 않은 상대 경로: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value != path.as_posix():
        raise VibeError(f"안전하지 않은 상대 경로: {value!r}")
    return path


def reject_links(path: Path) -> None:
    """Refuse symlinks and Windows junctions, including existing ancestors."""
    current = path.absolute()
    for item in (current, *current.parents):
        is_junction = getattr(item, "is_junction", lambda: False)
        try:
            attributes = getattr(item.lstat(), "st_file_attributes", 0)
        except (FileNotFoundError, NotADirectoryError):
            attributes = 0
        reparse = bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))
        if item.is_symlink() or is_junction() or reparse:
            raise VibeError(f"심볼릭 링크나 junction 경로는 사용할 수 없습니다: {item}")


def target_path(target: Path, relative: str) -> Path:
    path = target.joinpath(*safe_relative(relative).parts)
    reject_links(path)
    # Existing non-directory ancestors otherwise cause a late, partial install.
    for parent in path.parents:
        if parent == target.parent:
            break
        if parent.exists() and not parent.is_dir():
            raise VibeError(f"폴더가 필요한 위치에 파일이 있습니다: {parent}")
    return path


def source_bytes(path: Path) -> bytes:
    reject_links(path)
    if not path.is_file():
        raise VibeError(f"필수 파일이 없습니다: {path}")
    return path.read_bytes()


def load_profile(name: str) -> dict:
    identifier(name, "프로필 이름")
    path = ROOT / "profiles" / f"{name}.json"
    reject_links(path)
    profile = read_json(path)
    if profile.get("name") != name or not isinstance(profile.get("description"), str):
        raise VibeError(f"프로필 name/description을 확인하세요: {path}")
    for field in ("skills", "mcp"):
        values = profile.get(field)
        if not isinstance(values, list):
            raise VibeError(f"프로필 {field}는 배열이어야 합니다: {path}")
        for value in values:
            identifier(value, field)
        if len(values) != len(set(values)):
            raise VibeError(f"프로필 {field}에 중복 항목이 있습니다: {path}")
    if "checks" in profile and not isinstance(profile["checks"], list):
        raise VibeError(f"프로필 checks는 배열이어야 합니다: {path}")
    return profile


def build_plan(name: str, selected_mcp: list[str]) -> dict[str, bytes]:
    profile = load_profile(name)
    plan = {"AGENTS.md": source_bytes(ROOT / "templates" / "AGENTS.md")}
    config = source_bytes(ROOT / "config" / "codex.base.toml").decode("utf-8-sig")
    for server in sorted(set(selected_mcp)):
        identifier(server, "MCP 이름")
        snippet = source_bytes(ROOT / "mcp" / f"{server}.toml").decode("utf-8-sig")
        config += f"\n# Optional MCP: {server}\n{snippet}\n"
    config = config.rstrip() + "\n"
    try:
        tomllib.loads(config)
    except (ValueError, TypeError) as exc:
        raise VibeError(f"합쳐진 Codex 설정이 올바른 TOML이 아닙니다: {exc}") from exc
    plan[".codex/config.toml"] = config.encode("utf-8")
    agent_dir = ROOT / "config" / "agents"
    reject_links(agent_dir)
    for path in sorted(agent_dir.glob("*.toml")):
        content = source_bytes(path)
        try:
            tomllib.loads(content.decode("utf-8-sig"))
        except ValueError as exc:
            raise VibeError(f"에이전트 설정이 올바른 TOML이 아닙니다: {path}: {exc}") from exc
        plan[f".codex/agents/{path.name}"] = content
    for skill in profile["skills"]:
        directory = ROOT / "skills" / skill
        source_bytes(directory / "SKILL.md")
        for path in sorted(directory.rglob("*")):
            reject_links(path)
            if path.is_file():
                suffix = path.relative_to(directory).as_posix()
                plan[f".agents/skills/{skill}/{suffix}"] = source_bytes(path)
    return plan


def load_state(target: Path) -> dict | None:
    path = target_path(target, STATE)
    if not path.exists():
        return None
    state = read_json(path)
    if state.get("version") != 1 or not isinstance(state.get("files"), dict):
        raise VibeError(f"설치 상태 파일 형식을 확인하세요: {path}")
    identifier(state.get("profile"), "설치 프로필")
    mcp = state.get("mcp")
    if not isinstance(mcp, list):
        raise VibeError("설치 상태의 mcp는 배열이어야 합니다.")
    for server in mcp:
        identifier(server, "설치 MCP")
    for relative, checksum in state["files"].items():
        safe_relative(relative)
        allowed = relative in ("AGENTS.md", ".codex/config.toml") or relative.startswith((".codex/agents/", ".agents/skills/"))
        if not allowed or not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum):
            raise VibeError(f"설치 상태의 관리 파일 항목이 잘못됐습니다: {relative}")
    return state


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=".vibe-tmp-", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def initialize(args: argparse.Namespace) -> int:
    target = args.target.absolute()
    reject_links(target)
    if target.exists() and not target.is_dir():
        raise VibeError(f"대상은 폴더여야 합니다: {target}")
    defaults = [] if args.no_mcp else load_profile(args.profile)["mcp"]
    selected_mcp = sorted(set(defaults + args.mcp))
    plan = build_plan(args.profile, selected_mcp)
    previous = load_state(target)
    previous_files = previous["files"] if previous else {}
    if previous and (previous["profile"] != args.profile or previous["mcp"] != selected_mcp) and not args.update:
        raise VibeError("프로필 또는 MCP를 변경하려면 --update를 사용하세요. 수정된 관리 파일은 덮어쓰지 않습니다.")
    removals = set(previous_files) - set(plan)
    conflicts = []
    writes = {}
    for relative in sorted(set(plan) | removals):
        path = target_path(target, relative)
        if path.exists() and not path.is_file():
            conflicts.append(f"{relative}: 파일 위치에 폴더가 있습니다")
            continue
        actual = path.read_bytes() if path.exists() else None
        desired = plan.get(relative)
        if actual == desired:
            continue
        if actual is not None:
            if relative not in previous_files:
                conflicts.append(f"{relative}: 기존 파일과 내용이 다릅니다")
                continue
            if digest(actual) != previous_files[relative]:
                conflicts.append(f"{relative}: 설치 후 사용자가 수정했습니다")
                continue
            if not args.update:
                conflicts.append(f"{relative}: 업데이트하려면 --update가 필요합니다")
                continue
        if desired is not None:
            writes[relative] = desired
    project_path = target_path(target, PROJECT)
    if project_path.exists() and not project_path.is_file():
        conflicts.append(f"{PROJECT}: 파일 위치에 폴더가 있습니다")
    if conflicts:
        raise VibeError("설치를 적용하지 않았습니다. 충돌을 먼저 해결하세요:\n  " + "\n  ".join(conflicts))
    state = {"version": 1, "profile": args.profile, "mcp": selected_mcp,
             "files": {name: digest(data) for name, data in sorted(plan.items())}}
    state_bytes = json_bytes(state)
    state_path = target_path(target, STATE)
    if not state_path.exists() or state_path.read_bytes() != state_bytes:
        writes[STATE] = state_bytes
    if not project_path.exists():
        writes[PROJECT] = json_bytes({
            "name": target.name,
            "purpose": "프로젝트의 사용자와 해결할 문제를 적으세요.",
            "success_criteria": [],
            "checks": [],
        })
    existing_removals = [relative for relative in sorted(removals) if target_path(target, relative).exists()]
    prefix = "미리보기" if args.dry_run else "설치"
    print(f"{prefix}: {args.profile} → {target}")
    print(f"파일 쓰기 {len(writes)}개, 이전 관리 파일 제거 {len(existing_removals)}개")
    if args.dry_run:
        for relative in sorted(writes):
            print(f"  WRITE {relative}")
        for relative in existing_removals:
            print(f"  REMOVE {relative}")
        return 0
    # All conflicts and unsafe paths were checked before the first mutation.
    # Per-file atomic writes protect readers from half-written TOML/JSON files.
    for relative, content in writes.items():
        if relative != STATE:
            atomic_write(target_path(target, relative), content)
    for relative in existing_removals:
        path = target_path(target, relative)
        path.unlink()
        # Empty obsolete skill folders otherwise look like installed skills to
        # integrity checks. rmdir never removes user-added files or subfolders.
        boundary = target_path(target, ".agents/skills")
        parent = path.parent
        while parent != boundary and boundary in parent.parents:
            reject_links(parent)
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent
    if STATE in writes:
        atomic_write(state_path, writes[STATE])
    print("완료. Codex에서 이 폴더를 열고, 프로젝트 신뢰 여부를 확인한 뒤 새 채팅을 시작하세요.")
    print(f"앱 검증 명령은 {PROJECT}의 checks에 등록하세요.")
    return 0


def inspect_config(target: Path) -> dict:
    path = target_path(target, ".codex/config.toml")
    try:
        return tomllib.loads(source_bytes(path).decode("utf-8-sig"))
    except ValueError as exc:
        raise VibeError(f"Codex TOML 설정 오류: {exc}") from exc


def doctor(args: argparse.Namespace) -> int:
    target = args.target.absolute()
    failures = []
    print(f"Python {sys.version.split()[0]}: OK")
    if shutil.which("git"):
        print("Git: OK")
    else:
        failures.append("Git을 설치하세요.")
    if shutil.which("codex"):
        print("Codex CLI: 발견됨 (로그인/모델 접근 권한은 별도 확인)")
    else:
        print("Codex CLI: 없음. Codex 데스크톱 앱 사용에는 CLI가 필수는 아닙니다.")
    try:
        state = load_state(target)
        if state is None:
            raise VibeError("설치 정보가 없습니다. 먼저 init을 실행하세요.")
        config = inspect_config(target)
        print(f"프로필 {state['profile']}, TOML 구문: OK")
        servers = config.get("mcp_servers", {})
        if not isinstance(servers, dict):
            raise VibeError("mcp_servers는 TOML 테이블이어야 합니다.")
        for name, server in servers.items():
            if not isinstance(server, dict):
                failures.append(f"MCP {name}: 서버 설정은 테이블이어야 합니다.")
                continue
            if server.get("enabled") is False:
                print(f"MCP {name}: 비활성")
                continue
            command = server.get("command")
            if command is not None and (not isinstance(command, str) or not command):
                failures.append(f"MCP {name}: command는 문자열이어야 합니다.")
                continue
            if command and not shutil.which(command):
                failures.append(f"MCP {name}: 실행 명령을 찾을 수 없습니다: {command}")
            required = server.get("env_vars", [])
            token = server.get("bearer_token_env_var")
            if not isinstance(required, list) or any(not isinstance(item, str) for item in required) or (token is not None and not isinstance(token, str)):
                failures.append(f"MCP {name}: 환경 변수 이름 설정이 잘못됐습니다.")
                continue
            if token:
                required = [*required, token]
            for variable in required:
                if not os.environ.get(variable):
                    failures.append(f"MCP {name}: 환경 변수 {variable}이 없습니다.")
            print(f"MCP {name}: 설정 발견 (서버 실행/로그인은 검사하지 않음)")
    except VibeError as exc:
        failures.append(str(exc))
    for failure in failures:
        print(f"확인 필요: {failure}", file=sys.stderr)
    if not failures:
        print("로컬 사전 점검 통과. MCP 연결은 Codex의 도구 목록에서 직접 확인하세요.")
    return 1 if failures else 0


def check(args: argparse.Namespace) -> int:
    """Check shipped inputs and optionally the installed files, without executing MCP."""
    profiles = sorted((ROOT / "profiles").glob("*.json"))
    if not profiles:
        raise VibeError("profiles 폴더에 프로필이 없습니다.")
    skill_count = set()
    for path in profiles:
        profile = load_profile(path.stem)
        build_plan(path.stem, profile["mcp"])
        for server in profile["mcp"]:
            build_plan(path.stem, [server])
        for skill in profile["skills"]:
            content = source_bytes(ROOT / "skills" / skill / "SKILL.md").decode("utf-8-sig")
            if not content.startswith("---\n") and not content.startswith("---\r\n"):
                raise VibeError(f"SKILL.md frontmatter가 없습니다: {skill}")
            parts = content.split("---", 2)
            if len(parts) != 3 or not re.search(r"(?m)^name:\s*\S", parts[1]) or not re.search(r"(?m)^description:\s*\S", parts[1]):
                raise VibeError(f"스킬 name/description이 없습니다: {skill}")
            skill_count.add(skill)
    target = args.target.absolute()
    state = load_state(target)
    if state:
        inspect_config(target)
        altered = []
        for relative, checksum in state["files"].items():
            path = target_path(target, relative)
            if not path.is_file() or digest(path.read_bytes()) != checksum:
                altered.append(relative)
        if altered:
            raise VibeError("설치 원본과 달라진 관리 파일이 있습니다:\n  " + "\n  ".join(altered))
        print(f"설치 관리 파일 {len(state['files'])}개: OK")
    else:
        print("설치 전 상태: 배포 원본만 점검했습니다.")
    print(f"프로필 {len(profiles)}개, 스킬 {len(skill_count)}개, MCP TOML 조합: OK")
    print("이 검사는 설정 무결성 검사입니다. 앱 테스트나 MCP 연결 검사가 아닙니다.")
    return 0


def validate_checks(target: Path) -> list[tuple[str, list[str], Path, float]]:
    project = read_json(target_path(target, PROJECT))
    checks = project.get("checks")
    if not isinstance(checks, list):
        raise VibeError(".vibe/project.json의 checks는 배열이어야 합니다.")
    validated = []
    for index, entry in enumerate(checks):
        if not isinstance(entry, dict):
            raise VibeError(f"checks[{index}]는 객체여야 합니다.")
        name, command = entry.get("name"), entry.get("command")
        if not isinstance(name, str) or not name.strip():
            raise VibeError(f"checks[{index}].name이 필요합니다.")
        if not isinstance(command, list) or not command or any(not isinstance(arg, str) or not arg or "\0" in arg for arg in command):
            raise VibeError(f"검사 {name}: command는 비어 있지 않은 문자열 배열이어야 합니다.")
        relative = entry.get("cwd", ".")
        cwd = target_path(target, relative)
        if not cwd.is_dir():
            raise VibeError(f"검사 {name}: 작업 폴더가 없습니다: {relative}")
        python = sys.executable
        if "venv" in entry:
            if not isinstance(entry["venv"], str) or not entry["venv"]:
                raise VibeError(f"검사 {name}: venv는 작업 폴더 기준의 비어 있지 않은 상대 경로여야 합니다.")
            if command[0] != "{python}":
                raise VibeError(f"검사 {name}: venv를 지정하면 command의 첫 항목은 정확히 {{python}}이어야 합니다.")
            environment = target_path(cwd, entry["venv"])
            config = target_path(environment, "pyvenv.cfg")
            binaries = target_path(environment, "Scripts" if os.name == "nt" else "bin")
            # POSIX venv interpreters normally symlink to the base Python. Keep
            # this path intact so Python discovers the venv's pyvenv.cfg.
            interpreter = binaries / ("python.exe" if os.name == "nt" else "python")
            if not environment.is_dir() or not config.is_file() or not interpreter.is_file():
                raise VibeError(f"검사 {name}: 가상환경이 준비되지 않았습니다: {environment}. "
                                "이 위치에 Python 가상환경을 생성하고 프로젝트 의존성을 설치하세요. "
                                f"필요한 파일: pyvenv.cfg, {interpreter.relative_to(environment)}")
            python = str(interpreter)
        if command[0] == "{python}":
            command = [python, *command[1:]]
        timeout = entry.get("timeout_seconds", 300)
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 86400:
            raise VibeError(f"검사 {name}: timeout_seconds는 0 초과 86400 이하의 수여야 합니다.")
        executable = command[0]
        if "/" in executable or "\\" in executable:
            candidate = Path(executable)
            if not candidate.is_absolute():
                candidate = cwd / candidate
            executable = str(candidate)
        command = [shutil.which(executable) or executable, *command[1:]]
        # Windows dispatches .cmd/.bat via cmd.exe even with shell=False.
        # Resolve npm.CMD explicitly, and reject shell syntax rather than silently
        # interpreting array elements as a second command or variable expansion.
        if os.name == "nt" and Path(command[0]).suffix.lower() in (".cmd", ".bat"):
            if any(re.search(r'[&|<>^%!()"\r\n]', value) for value in command):
                raise VibeError(f"검사 {name}: Windows 배치 명령에 셸 특수문자를 전달할 수 없습니다. 필요하면 node/Python 실행 파일을 직접 사용하세요.")
        validated.append((name, command, cwd, timeout))
    return validated


class WindowsJob:
    """A Windows process job; closing it also stops inherited worker processes."""

    def __init__(self):
        import ctypes
        from ctypes import wintypes

        class BasicLimits(ctypes.Structure):
            _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                        ("flags", wintypes.DWORD), ("min_working_set", ctypes.c_size_t),
                        ("max_working_set", ctypes.c_size_t), ("active_processes", wintypes.DWORD),
                        ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD),
                        ("scheduling", wintypes.DWORD)]

        class ExtendedLimits(ctypes.Structure):
            _fields_ = [("basic", BasicLimits), ("io_counters", ctypes.c_uint64 * 6),
                        ("process_memory", ctypes.c_size_t), ("job_memory", ctypes.c_size_t),
                        ("peak_process_memory", ctypes.c_size_t), ("peak_job_memory", ctypes.c_size_t)]

        self.ctypes = ctypes
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "CreateJobObjectW": ([ctypes.c_void_p, wintypes.LPCWSTR], wintypes.HANDLE),
            "SetInformationJobObject": ([wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD], wintypes.BOOL),
            "OpenProcess": ([wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE),
            "AssignProcessToJobObject": ([wintypes.HANDLE, wintypes.HANDLE], wintypes.BOOL),
            "TerminateJobObject": ([wintypes.HANDLE, wintypes.UINT], wintypes.BOOL),
            "CloseHandle": ([wintypes.HANDLE], wintypes.BOOL),
        }
        for name, (arguments, result) in signatures.items():
            function = getattr(self.kernel, name)
            function.argtypes, function.restype = arguments, result
        self.handle = self.kernel.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = ExtendedLimits()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            error = ctypes.WinError(ctypes.get_last_error())
            self.close()
            raise error

    def assign(self, process: subprocess.Popen) -> None:
        handle = self.kernel.OpenProcess(0x0101, False, process.pid)  # SET_QUOTA | TERMINATE
        if not handle:
            raise self.ctypes.WinError(self.ctypes.get_last_error())
        try:
            if not self.kernel.AssignProcessToJobObject(self.handle, handle):
                raise self.ctypes.WinError(self.ctypes.get_last_error())
        finally:
            self.kernel.CloseHandle(handle)

    def terminate(self) -> None:
        if not self.kernel.TerminateJobObject(self.handle, 1):
            raise self.ctypes.WinError(self.ctypes.get_last_error())

    def close(self) -> None:
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


def run_check(command: list[str], cwd: Path, timeout: float) -> int:
    options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    job = WindowsJob() if os.name == "nt" else None
    try:
        with subprocess.Popen(command, cwd=cwd, shell=False, **options) as process:
            if job:
                try:
                    job.assign(process)
                except OSError:
                    process.kill()
                    process.wait()
                    raise
            try:
                return process.wait(timeout=timeout)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                if job:
                    job.terminate()
                else:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                process.wait()
                raise
    finally:
        if job:
            job.close()


def verify(args: argparse.Namespace) -> int:
    checks = validate_checks(args.target.absolute())
    if not checks:
        print("등록된 앱 검증 명령이 없습니다. .vibe/project.json의 checks를 채우세요.")
        if args.allow_empty:
            print("--allow-empty로 건너뜀: 앱 검증 통과를 뜻하지 않습니다.")
            return 0
        return 1
    failures = 0
    for name, command, cwd, timeout in checks:
        print(f"실행: {name}", flush=True)
        try:
            code = run_check(command, cwd, timeout)
        except subprocess.TimeoutExpired:
            print(f"실패: {name}: 제한 시간 {timeout}초 초과", file=sys.stderr)
            failures += 1
            continue
        except OSError as exc:
            print(f"실패: {name}: {exc}", file=sys.stderr)
            failures += 1
            continue
        print(f"{'통과' if code == 0 else '실패'}: {name} (종료 코드 {code})")
        failures += code != 0
    print(f"등록된 검사 {len(checks)}개 중 {len(checks) - failures}개 통과")
    return 1 if failures else 0


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description="프로젝트별 Codex 하네스 설치와 점검")
    commands = cli.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="프로필을 설치합니다. 기존 수정 파일은 보존합니다.")
    init.add_argument("--profile", required=True, help="minimal, web, api, data, automation")
    init.add_argument("--mcp", action="append", default=[], metavar="NAME", help="프로필 기본 MCP 외에 추가 (반복 가능)")
    init.add_argument("--no-mcp", action="store_true", help="프로필의 기본 MCP를 제외 (--mcp로 지정한 서버는 유지)")
    init.add_argument("--dry-run", action="store_true", help="파일을 바꾸지 않고 계획만 확인")
    init.add_argument("--update", action="store_true", help="수정되지 않은 기존 관리 파일의 갱신 허용")
    init.set_defaults(func=initialize)
    for name, function, help_text in (
        ("doctor", doctor, "현재 설치와 로컬 실행 요건 확인"),
        ("check", check, "배포 프로필/스킬/TOML 및 설치 무결성 확인"),
        ("verify", verify, "프로젝트에 등록한 실제 검증 명령 실행"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.set_defaults(func=function)
        if name == "verify":
            command.add_argument("--allow-empty", action="store_true", help="검사가 없으면 명시적으로 건너뜀")
    for command in commands.choices.values():
        command.add_argument("--target", type=Path, default=ROOT, help="대상 폴더 (기본값: 이 저장소)")
    return cli


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    try:
        args = parser().parse_args(argv)
        return args.func(args)
    except (VibeError, OSError, UnicodeError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
