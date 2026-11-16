"""Search a small local reading log without changing its contents."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import unicodedata

FIELDS = {"id", "title", "author", "status", "note"}
STATUSES = ("want", "reading", "done")


class InputError(ValueError):
    """A reading log does not follow the documented input contract."""


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"중복된 JSON 필드가 있습니다: {key}")
        result[key] = value
    return result


def load_books(path: Path) -> list[dict]:
    # shortcut: personal reading logs are read into memory; stream or index large collections.
    try:
        books = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
    except (UnicodeError, ValueError, RecursionError) as error:
        raise InputError(f"UTF-8 JSON을 읽을 수 없습니다: {error}") from error
    if not isinstance(books, list):
        raise InputError("최상위 값은 책 객체의 배열이어야 합니다.")
    identifiers = set()
    for index, book in enumerate(books, 1):
        prefix = f"{index}번째 기록"
        if not isinstance(book, dict) or set(book) != FIELDS:
            raise InputError(f"{prefix}: id, title, author, status, note 필드가 정확히 필요합니다.")
        if type(book["id"]) is not int or book["id"] < 1:
            raise InputError(f"{prefix}: id는 양의 정수여야 합니다.")
        if book["id"] in identifiers:
            raise InputError(f"{prefix}: id가 중복됩니다.")
        identifiers.add(book["id"])
        for field in ("title", "author", "note"):
            value = book[field]
            if not isinstance(value, str) or (field != "note" and not value.strip()):
                raise InputError(f"{prefix}: {field}는 {'비어 있지 않은 ' if field != 'note' else ''}문자열이어야 합니다.")
            if "\0" in value or any(0xD800 <= ord(char) <= 0xDFFF for char in value):
                raise InputError(f"{prefix}: {field}에 NUL 또는 잘못된 Unicode 문자가 있습니다.")
        if book["status"] not in STATUSES:
            raise InputError(f"{prefix}: status는 want, reading, done 중 하나여야 합니다.")
    return books


def folded(text: str) -> str:
    return unicodedata.normalize("NFC", text).casefold()


def search_books(books: list[dict], query: str = "", status: str | None = None) -> list[dict]:
    needle = folded(query.strip())
    return [book for book in books
            if (status is None or book["status"] == status)
            and (needle in folded(book["title"]) or needle in folded(book["author"]))]


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description="독서 JSON을 읽기만 하며 제목·저자와 읽는 상태로 검색합니다.")
    parser.add_argument("--input", type=Path, required=True, help="UTF-8 JSON 배열 파일")
    parser.add_argument("--query", default="", help="제목·저자의 부분 문자열; 생략하면 전체")
    parser.add_argument("--status", choices=STATUSES, help="읽는 상태")
    args = parser.parse_args(argv)
    try:
        result = search_books(load_books(args.input), args.query, args.status)
    except (OSError, InputError) as error:
        print(f"검색 실패: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
