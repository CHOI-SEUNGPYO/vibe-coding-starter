#!/usr/bin/env python3
"""Verify bundled skill bytes and the active project's installed subset, offline."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
IDENTIFIER = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
COMMIT = re.compile(r"[0-9a-f]{40}\Z")


class IntegrityError(ValueError):
    """Source or installed files differ from their declared provenance."""


def reject_link(path: Path) -> None:
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            raise IntegrityError(f"링크 경로는 검사할 수 없습니다: {candidate}")
        if candidate.exists():
            flags = getattr(candidate.lstat(), "st_file_attributes", 0)
            if flags & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
                raise IntegrityError(f"junction 경로는 검사할 수 없습니다: {candidate}")


def read_json(path: Path) -> dict:
    reject_link(path)
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise IntegrityError(f"JSON을 읽을 수 없습니다: {path.name}") from exc
    if not isinstance(value, dict):
        raise IntegrityError(f"JSON 객체가 필요합니다: {path.name}")
    return value


def safe_relative(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise IntegrityError("lock 파일에 잘못된 상대 경로가 있습니다")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value != path.as_posix():
        raise IntegrityError("lock 파일의 경로가 스킬 디렉터리 밖을 가리킵니다")
    return value


def skill_id(value: object) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise IntegrityError("잘못된 스킬 ID가 있습니다")
    return value


def file_hashes(directory: Path) -> dict[str, str]:
    reject_link(directory)
    if not directory.is_dir():
        raise IntegrityError(f"스킬 디렉터리가 없습니다: {directory.name}")
    result = {}
    for path in sorted(directory.rglob("*")):
        reject_link(path)
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif not path.is_dir():
            raise IntegrityError(f"일반 파일이 아닌 경로가 있습니다: {path.name}")
    return result


def compare_files(label: str, expected: dict, actual: dict) -> None:
    missing = sorted(expected.keys() - actual.keys())
    extra = sorted(actual.keys() - expected.keys())
    changed = sorted(key for key in expected.keys() & actual.keys() if expected[key] != actual[key])
    if missing or extra or changed:
        parts = []
        for name, paths in (("누락", missing), ("미등록", extra), ("변경", changed)):
            if paths:
                parts.append(f"{name}: {', '.join(paths)}")
        raise IntegrityError(f"{label} — {'; '.join(parts)}")


def directories(path: Path) -> set[str]:
    reject_link(path)
    if not path.exists():
        return set()
    if not path.is_dir():
        raise IntegrityError(f"디렉터리가 필요합니다: {path}")
    result = set()
    for child in path.iterdir():
        reject_link(child)
        if not child.is_dir():
            raise IntegrityError(f"스킬 디렉터리 밖에 파일이 있습니다: {child.name}")
        result.add(child.name)
    return result


def validate_sources(root: Path) -> dict[str, dict]:
    lock = read_json(root / "skills.lock.json")
    if lock.get("schema_version") != 1 or not isinstance(lock.get("skills"), list) or not lock["skills"]:
        raise IntegrityError("지원하지 않거나 비어 있는 skills.lock.json입니다")
    entries = {}
    for entry in lock["skills"]:
        if not isinstance(entry, dict):
            raise IntegrityError("스킬 lock 항목은 객체여야 합니다")
        name = skill_id(entry.get("id"))
        if name in entries:
            raise IntegrityError(f"중복 스킬 ID: {name}")
        files = entry.get("files")
        if not isinstance(files, dict) or not {"SKILL.md", "LICENSE.txt"} <= files.keys():
            raise IntegrityError(f"{name}: SKILL.md와 LICENSE.txt를 포함한 파일 목록이 필요합니다")
        for relative, checksum in files.items():
            safe_relative(relative)
            if not isinstance(checksum, str) or not SHA256.fullmatch(checksum):
                raise IntegrityError(f"{name}: 올바른 SHA-256이 필요합니다")
        if entry.get("origin") == "vendored":
            revision = entry.get("revision")
            if not isinstance(revision, str) or not COMMIT.fullmatch(revision):
                raise IntegrityError(f"{name}: 외부 스킬은 커밋 SHA로 고정해야 합니다")
            expected_url = f"https://github.com/openai/skills/tree/{revision}/skills/.curated/{name}"
            if entry.get("source_url") != expected_url or entry.get("license") != "Apache-2.0":
                raise IntegrityError(f"{name}: 외부 스킬 출처나 라이선스가 예상과 다릅니다")
        elif entry.get("origin") == "first-party":
            if entry.get("revision") is not None or entry.get("license") != "MIT":
                raise IntegrityError(f"{name}: 직접 작성한 스킬의 버전/라이선스를 확인하세요")
            if not isinstance(entry.get("source_url"), str) or not entry["source_url"].startswith("https://github.com/"):
                raise IntegrityError(f"{name}: 출처 URL이 필요합니다")
        else:
            raise IntegrityError(f"{name}: 지원하지 않는 origin입니다")
        compare_files(f"원본 {name}", files, file_hashes(root / "skills" / name))
        entries[name] = entry
    actual = directories(root / "skills")
    if actual != entries.keys():
        raise IntegrityError(f"skills/와 lock의 스킬 목록이 다릅니다: {', '.join(sorted(actual ^ entries.keys()))}")
    return entries


def validate_installed(root: Path, target: Path, entries: dict[str, dict]) -> int:
    state_path = target / ".vibe/profile.json"
    installed = target / ".agents/skills"
    reject_link(state_path)
    if not state_path.exists():
        if directories(installed):
            raise IntegrityError("설치된 스킬이 있지만 .vibe/profile.json이 없습니다")
        return 0
    state = read_json(state_path)
    profile_name = skill_id(state.get("profile"))
    profile = read_json(root / "profiles" / f"{profile_name}.json")
    names = profile.get("skills")
    if not isinstance(names, list):
        raise IntegrityError("프로필의 skills 배열이 필요합니다")
    expected = {skill_id(name) for name in names}
    if len(expected) != len(names) or not expected <= entries.keys():
        raise IntegrityError("프로필의 스킬 목록에 중복 또는 미등록 스킬이 있습니다")
    actual = directories(installed)
    if actual != expected:
        raise IntegrityError(f"설치된 스킬 목록이 프로필과 다릅니다: {', '.join(sorted(actual ^ expected))}")
    for name in sorted(expected):
        compare_files(f"설치본 {name}", entries[name]["files"], file_hashes(installed / name))
    return len(expected)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=ROOT, help="검사할 설치 프로젝트; 기본값은 이 저장소")
    args = parser.parse_args(argv)
    try:
        entries = validate_sources(ROOT)
        count = validate_installed(ROOT, args.target.absolute(), entries)
    except (IntegrityError, OSError) as exc:
        print(f"무결성 검사 실패: {exc}", file=sys.stderr)
        return 1
    print(f"원본 스킬 {len(entries)}개, 설치 스킬 {count}개: 파일 목록과 SHA-256 일치")
    print("외부 출처 URL·커밋 형식을 확인했습니다. 원격 내용 재조회는 하지 않았습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
