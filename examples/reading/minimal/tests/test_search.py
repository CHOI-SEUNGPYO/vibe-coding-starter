from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import unicodedata

APP = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("reading_search", APP / "search.py")
search = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(search)


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "독서.json"
        self.books = [
            {"id": 3, "title": "겨울 책장", "author": "김하늘", "status": "done", "note": "메모\n두 번째 줄"},
            {"id": 1, "title": "Straße", "author": "이봄", "status": "reading", "note": ""},
            {"id": 2, "title": "겨울 산책", "author": "김하늘", "status": "want", "note": ""},
        ]
        self.write(self.books)

    def write(self, value):
        self.path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def test_title_author_filter_and_order(self):
        books = search.load_books(self.path)
        self.assertEqual([3, 2], [book["id"] for book in search.search_books(books, "김하늘")])
        self.assertEqual([2], [book["id"] for book in search.search_books(books, " 겨울 ", "want")])
        self.assertEqual([3, 1, 2], [book["id"] for book in search.search_books(books)])

    def test_unicode_casefold_and_normalization(self):
        books = search.load_books(self.path)
        self.assertEqual([1], [book["id"] for book in search.search_books(books, "STRASSE")])
        decomposed = unicodedata.normalize("NFD", "김하늘")
        self.assertEqual([3, 2], [book["id"] for book in search.search_books(books, decomposed)])

    def test_no_match_empty_list_and_blank_query(self):
        books = search.load_books(self.path)
        self.assertEqual([], search.search_books(books, "없음"))
        self.assertEqual(books, search.search_books(books, "   "))
        self.write([])
        self.assertEqual([], search.load_books(self.path))

    def test_utf8_bom_preserves_content(self):
        self.path.write_text(json.dumps(self.books, ensure_ascii=False), encoding="utf-8-sig")
        self.assertEqual(self.books, search.load_books(self.path))

    def test_invalid_fields_and_values(self):
        cases = [(field, value) for field, values in {
            "id": [True, 0, -1, 1.5, "1", None],
            "title": ["", "   ", None, 123, "NUL\0", "bad\ud800"],
            "author": ["", False], "note": [None, 3],
            "status": ["finished", None, [], {}],
        }.items() for value in values]
        for field, value in cases:
            with self.subTest(field=field, value=repr(value)):
                bad = copy.deepcopy(self.books)
                bad[0][field] = value
                self.path.write_text(json.dumps(bad), encoding="utf-8")
                with self.assertRaises(search.InputError):
                    search.load_books(self.path)

    def test_missing_extra_fields_and_non_array(self):
        for value in ({}, None, 4, [3], [{"id": 1}], [dict(self.books[0], extra=True)]):
            with self.subTest(value=value):
                self.write(value)
                with self.assertRaises(search.InputError):
                    search.load_books(self.path)

    def test_duplicate_ids_and_duplicate_json_keys(self):
        self.write([self.books[0], self.books[0]])
        with self.assertRaisesRegex(search.InputError, "id가 중복"):
            search.load_books(self.path)
        self.path.write_text('[{"id":1,"id":2}]', encoding="utf-8")
        with self.assertRaisesRegex(search.InputError, "중복된 JSON 필드"):
            search.load_books(self.path)

    def test_malformed_json_and_encoding(self):
        for content in (b'', b'[{', b'{"bad":' + b'9' * 5000 + b'}', b'\xff\xfe'):
            with self.subTest(content=content[:20]):
                self.path.write_bytes(content)
                with self.assertRaises(search.InputError):
                    search.load_books(self.path)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(APP / "search.py"), *args],
                              cwd=self.temp.name, capture_output=True, encoding="utf-8", timeout=10)

    def test_cli_utf8_search_does_not_change_input(self):
        original = hashlib.sha256(self.path.read_bytes()).hexdigest()
        result = self.cli("--input", str(self.path), "--query", "김하늘", "--status", "want")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stderr)
        self.assertEqual([2], [book["id"] for book in json.loads(result.stdout)])
        self.assertEqual(original, hashlib.sha256(self.path.read_bytes()).hexdigest())

    def test_cli_no_match_is_success(self):
        result = self.cli("--input", str(self.path), "--query", "없는 책")
        self.assertEqual(0, result.returncode)
        self.assertEqual([], json.loads(result.stdout))

    def test_cli_errors_are_nonzero_without_success_output(self):
        for args in (("--input", str(self.path), "--status", "bad"),
                     ("--input", str(self.path.parent / "missing.json"))):
            with self.subTest(args=args):
                result = self.cli(*args)
                self.assertEqual(2, result.returncode)
                self.assertEqual("", result.stdout)
                self.assertNotIn("Traceback", result.stderr)
        self.path.write_text('{"missing":true}', encoding="utf-8")
        result = self.cli("--input", str(self.path))
        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn("검색 실패", result.stderr)


if __name__ == "__main__":
    unittest.main()
