"""Preview or create a repeatable weekly digest from a local reading CSV."""
from __future__ import annotations

import argparse
import csv
from datetime import date, timedelta
import hashlib
import io
import json
from pathlib import Path
import re
import stat
import sys
import tempfile

VERSION = "reading-weekly-v1"
FIELDS = ("record_id", "title", "author", "status", "pages", "rating", "finished_date")


class InputError(ValueError):
    """An input or output condition that needs the user's correction."""


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def is_link(path: Path) -> bool:
    # Windows junction detection must also work on Python 3.11, before Path.is_junction.
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except (FileNotFoundError, NotADirectoryError):
        attributes = 0
    return path.is_symlink() or bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def read_records(path: Path, encoding: str) -> tuple[list[dict], str]:
    raw = path.read_bytes()
    try:
        content = raw.decode(encoding)
    except UnicodeDecodeError as error:
        raise InputError("인코딩을 확인하세요. 기본은 UTF-8이며 CP949 파일은 --encoding cp949를 지정하세요.") from error
    reader = csv.reader(io.StringIO(content, newline=""), strict=True)
    try:
        headers = next(reader, None)
        if headers is None:
            raise InputError("1행: 헤더가 없습니다.")
        if len(headers) != len(set(headers)) or set(headers) != set(FIELDS):
            raise InputError("1행: 열은 중복 없이 " + ", ".join(FIELDS) + "여야 합니다.")
        records, ids = [], set()
        while True:
            line = reader.line_num + 1
            values = next(reader, None)
            if values is None:
                break
            if len(values) != len(headers):
                raise InputError(f"{line}행: 열 개수가 헤더와 다릅니다.")
            if any(any(ord(char) < 32 or ord(char) == 127 for char in value) for value in values):
                raise InputError(f"{line}행: NUL·제어문자는 사용할 수 없습니다.")
            row = dict(zip(headers, (value.strip() for value in values)))
            for field in ("record_id", "title", "author"):
                if not row[field]:
                    raise InputError(f"{line}행: {field}는 필수입니다.")
            if row["record_id"] in ids:
                raise InputError(f"{line}행: record_id가 중복됩니다.")
            if row["status"] not in ("want", "reading", "done"):
                raise InputError(f"{line}행: status는 want/reading/done 중 하나여야 합니다.")
            if not re.fullmatch(r"[0-9]{1,6}", row["pages"]) or not 1 <= int(row["pages"]) <= 100000:
                raise InputError(f"{line}행: pages는 1~100000의 정수여야 합니다.")
            if row["rating"] and row["rating"] not in ("1", "2", "3", "4", "5"):
                raise InputError(f"{line}행: rating은 빈 값 또는 1~5의 정수여야 합니다.")
            if row["status"] == "done":
                if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", row["finished_date"]):
                    raise InputError(f"{line}행: 완독일은 YYYY-MM-DD여야 합니다.")
                try:
                    date.fromisoformat(row["finished_date"])
                except ValueError as error:
                    raise InputError(f"{line}행: 완독일이 실제 달력 날짜가 아닙니다.") from error
            elif row["finished_date"]:
                raise InputError(f"{line}행: 미완독 기록의 완독일은 비워 두세요.")
            ids.add(row["record_id"])
            row["pages"] = int(row["pages"])
            row["rating"] = int(row["rating"]) if row["rating"] else None
            records.append(row)
    except csv.Error as error:
        raise InputError(f"{reader.line_num}행 부근: CSV 형식이 잘못됐습니다.") from error
    return records, hashlib.sha256(raw).hexdigest()


def parse_week(value: str) -> date:
    try:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            raise ValueError
        start = date.fromisoformat(value)
        start + timedelta(days=6)
    except (ValueError, OverflowError) as error:
        raise InputError("--week는 7일 범위를 표현할 수 있는 YYYY-MM-DD 날짜여야 합니다.") from error
    if start.weekday() != 0:
        raise InputError("--week에는 월요일 날짜를 지정하세요.")
    return start


def plan(input_path: Path, week: str, encoding: str = "utf-8-sig") -> tuple[str, dict, dict[str, bytes]]:
    start = parse_week(week)
    end = start + timedelta(days=6)
    records, source_hash = read_records(input_path, encoding)
    selected = [row for row in records if row["status"] == "done"
                and week <= row["finished_date"] <= end.isoformat()]
    ratings = [row["rating"] for row in selected if row["rating"] is not None]
    intent = {"version": VERSION, "source_sha256": source_hash, "week_start": week, "encoding": encoding}
    key = hashlib.sha256(json_bytes(intent)).hexdigest()
    summary = {
        **intent, "run_key": key, "week_end": end.isoformat(), "input_records": len(records),
        "completed_records": len(selected), "completed_pages": sum(row["pages"] for row in selected),
        "rated_completed_records": len(ratings),
        "average_completed_rating": round(sum(ratings) / len(ratings), 3) if ratings else None,
    }
    average = summary["average_completed_rating"]
    rating = f"{average:g}점 / 5" if average is not None else "평점 없음 (분모 0)"
    digest = (
        f"# 주간 독서 요약\n\n기간: **{week} ~ {end.isoformat()}** (월요일부터 일요일까지, 양끝 포함)\n\n"
        f"- 완독 기록: **{len(selected)}건**\n"
        f"- 완독한 책의 전체 페이지 합: **{summary['completed_pages']:,}쪽**\n"
        f"- 완독 평균 평점: **{rating}**, 평점을 남긴 완독 **{len(ratings)}건** 기준\n\n"
        "완독일이 이 주에 속하는 done 기록만 계산했습니다. 재독은 서로 다른 record_id로 셉니다. "
        "읽는 중인 책의 진도나 실제 독서 시간은 계산하지 않았습니다. "
        "개별 제목·저자·원본 행은 이 결과에 복사하지 않았습니다.\n\n"
        f"원본 SHA-256: `{source_hash}`\n\n실행 키: `{key}`\n"
    )
    files = {"summary.json": json_bytes(summary), "digest.md": digest.encode("utf-8")}
    files["manifest.json"] = json_bytes({"version": VERSION, "run_key": key,
        "files": {name: hashlib.sha256(value).hexdigest() for name, value in files.items()}})
    return key, summary, files


def check_result(destination: Path, expected: dict[str, bytes]) -> bool:
    linked = is_link(destination)
    if not destination.exists() and not linked:
        return False
    if linked or not destination.is_dir():
        raise InputError("완료 경로가 정상 폴더가 아닙니다. 기존 항목을 보존하고 중단합니다.")
    if {item.name for item in destination.iterdir()} != set(expected):
        raise InputError("기존 결과가 불완전하거나 변경됐습니다. 덮어쓰지 않습니다. 다른 출력 경로를 사용하세요.")
    for name, content in expected.items():
        file = destination / name
        if is_link(file) or not file.is_file() or file.read_bytes() != content:
            raise InputError("기존 결과가 불완전하거나 변경됐습니다. 덮어쓰지 않습니다. 다른 출력 경로를 사용하세요.")
    return True


def run(input_path: Path, week: str, output: Path, apply: bool = False, encoding: str = "utf-8-sig") -> dict:
    key, summary, files = plan(input_path, week, encoding)
    destination = output / key
    if output.exists() and not output.is_dir():
        raise InputError("--output은 파일이 아닌 폴더 경로여야 합니다.")
    for parent in (output.absolute(), *output.absolute().parents):
        if is_link(parent):
            raise InputError("출력 경로에는 심볼릭 링크나 junction을 사용할 수 없습니다.")
        if parent.exists() and not parent.is_dir():
            raise InputError("출력 폴더의 상위 경로가 파일입니다. 다른 폴더를 사용하세요.")
    complete = check_result(destination, files)
    action = "already-complete" if complete else "create"
    if apply and not complete:
        output.mkdir(parents=True, exist_ok=True)
        # shortcut: one user's sequential local runs; no distributed scheduler or lock service.
        with tempfile.TemporaryDirectory(prefix=".weekly-tmp-", dir=output) as temporary:
            staging = Path(temporary)
            for name, content in files.items():
                (staging / name).write_bytes(content)
            if destination.exists() or is_link(destination):
                raise InputError("실행 중 같은 결과 경로가 생겼습니다. 다시 실행해 완료 상태를 확인하세요.")
            staging.rename(destination)
        action = "created"
    return {"mode": "apply" if apply else "dry-run", "action": action,
            "run_key": key, "destination": destination.as_posix(), "summary": summary}


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description="독서 CSV의 주간 요약 미리보기. --apply를 지정해야 저장합니다.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--week", required=True, help="월요일 YYYY-MM-DD; 일요일까지 양끝 포함")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--encoding", choices=("utf-8-sig", "cp949"), default="utf-8-sig")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run(args.input, args.week, args.output, args.apply, args.encoding)
    except (InputError, OSError, UnicodeError) as error:
        print(f"자동화 실패: {error}", file=sys.stderr)
        return 2
    print(json_bytes(result).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
