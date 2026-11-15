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


def main() -> int:
    parser = argparse.ArgumentParser(description="환경 선택, 의존성 복원, 실제 MCP 연결 검증")
    parser.add_argument("--profile", choices=["minimal", "web", "api", "data", "automation"], default="web")
    args = parser.parse_args()
    commands = [[sys.executable, "scripts/vibe.py", "init", "--profile", args.profile]]
    if (ROOT / ".vibe/profile.json").is_file():
        commands[0].append("--update")
    profile = json.loads((ROOT / "profiles" / f"{args.profile}.json").read_text(encoding="utf-8"))
    node = shutil.which("node")
    npm = shutil.which("npm.cmd" if sys.platform == "win32" else "npm")
    if profile["mcp"] and not node:
        print("Node.js 22 이상이 필요합니다. 설치 후 다시 실행하세요.", file=sys.stderr)
        return 1
    if profile["mcp"] and node:
        version = subprocess.run([node, "--version"], check=True, capture_output=True, text=True).stdout.strip()
        if int(version.lstrip("v").split(".")[0]) < 22:
            print("Node.js 22 이상이 필요합니다.", file=sys.stderr)
            return 1
    if "playwright" in profile["mcp"]:
        if not npm:
            print("npm이 없습니다. Node.js 설치를 확인하세요.", file=sys.stderr)
            return 1
        commands += [[npm, "ci", "--ignore-scripts", "--no-audit", "--no-fund"], [node, "node_modules/playwright/cli.js", "install", "chromium"]]
    commands += [[sys.executable, "scripts/vibe.py", "check"], [sys.executable, "scripts/check_integrity.py"]]
    if profile["mcp"]:
        commands.append([node, "scripts/check_mcp.mjs", "all" if "playwright" in profile["mcp"] else "docs"])
    for command in commands:
        print("실행:", " ".join(command), flush=True)
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            print("준비 또는 검증이 실패했습니다. 위 오류를 해결한 뒤 다시 실행하세요.", file=sys.stderr)
            return result.returncode
    print(f"{args.profile} 환경 준비 완료. Codex에서 이 폴더를 신뢰하고 새 채팅을 시작하세요.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"환경 준비 실패: {error}", file=sys.stderr)
        raise SystemExit(1)
