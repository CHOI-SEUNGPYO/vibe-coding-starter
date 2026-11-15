#!/usr/bin/env python3
"""Restore a complete starter environment without modifying global Codex settings."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ["minimal", "web", "api", "data", "automation"]
MCP_CHECKS = {"openai-docs": "docs", "context7": "context7", "playwright": "browser"}


def select_environment(requested: str | None) -> tuple[str, list[str], bool]:
    state_path = ROOT / ".vibe/profile.json"
    state = json.loads(state_path.read_text(encoding="utf-8-sig")) if state_path.is_file() else None
    if state is not None and not isinstance(state, dict):
        raise ValueError(".vibe/profile.json은 JSON 객체여야 합니다.")
    name = requested or (state or {}).get("profile", "web")
    if name not in PROFILES:
        raise ValueError("저장된 프로필을 확인하세요: " + str(name))
    profile = json.loads((ROOT / "profiles" / f"{name}.json").read_text(encoding="utf-8-sig"))
    enabled = profile["mcp"]
    if not isinstance(enabled, list) or not all(isinstance(item, str) for item in enabled):
        raise ValueError("프로필의 mcp는 이름 배열이어야 합니다.")
    if state is not None and requested is None:
        previous = state.get("mcp")
        if not isinstance(previous, list) or not all(isinstance(item, str) for item in previous):
            raise ValueError("저장된 mcp 목록을 확인하세요.")
        enabled = enabled + previous
    return name, sorted(set(enabled)), state is not None


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description="환경 선택, 의존성 복원, 실제 MCP 연결 검증")
    parser.add_argument("--profile", choices=PROFILES, help="환경 변경; 생략하면 현재 프로필 복원 (최초 실행은 web)")
    args = parser.parse_args(argv)
    profile, enabled_mcp, updating = select_environment(args.profile)
    commands = [[sys.executable, "scripts/vibe.py", "init", "--profile", profile]]
    if updating:
        commands[0].append("--update")
    for server in enabled_mcp:
        commands[0] += ["--mcp", server]
    node = shutil.which("node")
    npm = shutil.which("npm.cmd" if sys.platform == "win32" else "npm")
    if any(server in MCP_CHECKS for server in enabled_mcp) and not node:
        print("Node.js 22 이상이 필요합니다. 설치 후 다시 실행하세요.", file=sys.stderr)
        return 1
    if any(server in MCP_CHECKS for server in enabled_mcp) and node:
        version = subprocess.run([node, "--version"], check=True, capture_output=True, text=True).stdout.strip()
        if int(version.lstrip("v").split(".")[0]) < 22:
            print("Node.js 22 이상이 필요합니다.", file=sys.stderr)
            return 1
    if "playwright" in enabled_mcp:
        if not npm:
            print("npm이 없습니다. Node.js 설치를 확인하세요.", file=sys.stderr)
            return 1
        commands += [[npm, "ci", "--ignore-scripts", "--no-audit", "--no-fund"], [node, "node_modules/playwright/cli.js", "install", "chromium"]]
    commands += [[sys.executable, "scripts/vibe.py", "check"], [sys.executable, "scripts/check_integrity.py"]]
    for server in enabled_mcp:
        if server in MCP_CHECKS:
            commands.append([node, "scripts/check_mcp.mjs", MCP_CHECKS[server]])
    for command in commands:
        print("실행:", " ".join(command), flush=True)
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            print("준비 또는 검증이 실패했습니다. 위 오류를 해결한 뒤 다시 실행하세요.", file=sys.stderr)
            return result.returncode
    unchecked = [server for server in enabled_mcp if server not in MCP_CHECKS]
    if unchecked:
        print("별도 확인이 필요한 연결:", ", ".join(unchecked), "(이 준비 명령은 계정 인증을 검사하지 않습니다.)")
    print(f"{profile} 환경 준비 완료. Codex에서 이 폴더를 신뢰하고 새 채팅을 시작하세요.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"환경 준비 실패: {error}", file=sys.stderr)
        raise SystemExit(1)
