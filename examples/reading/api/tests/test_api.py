from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import APP_DIR, create_app


class ReadingApiTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.db = Path(self.temporary.name) / "isolated.sqlite3"
        self.token = "test-token-only-not-a-production-secret"
        self.client = self.enterContext(TestClient(create_app(self.db, self.token)))
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def create(self, **overrides):
        body = {"title": "소년이 온다", "author": "한강", **overrides}
        response = self.client.post("/api/books", headers=self.headers, json=body)
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def assert_error(self, response, status, code):
        self.assertEqual(response.status_code, status, response.text)
        body = response.json()
        self.assertEqual(set(body), {"error"})
        self.assertEqual(set(body["error"]), {"code", "message", "details"})
        self.assertEqual(body["error"]["code"], code)
        self.assertIsInstance(body["error"]["message"], str)
        self.assertIsInstance(body["error"]["details"], list)
        self.assertNotIn(self.token, response.text)

    def test_create_defaults_location_and_unicode_detail(self):
        response = self.client.post("/api/books", headers=self.headers, json={"title": "  어린 왕자 📚  ", "author": "  생텍쥐페리 "})
        self.assertEqual(response.status_code, 201)
        book = response.json()
        self.assertEqual(book, {"id": 1, "title": "어린 왕자 📚", "author": "생텍쥐페리", "status": "want", "note": ""})
        self.assertEqual(response.headers["location"], "/api/books/1")
        self.assertEqual(self.client.get(response.headers["location"], headers=self.headers).json(), book)

    def test_patch_only_supplied_values_and_empty_patch(self):
        original = self.create()
        updated = self.client.patch("/api/books/1", headers=self.headers, json={"status": "done", "note": "별 다섯 개 ⭐\n다시 읽고 싶다."})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["title"], original["title"])
        self.assertEqual(updated.json()["author"], original["author"])
        self.assertEqual(updated.json()["status"], "done")
        self.assertEqual(self.client.patch("/api/books/1", headers=self.headers, json={}).json(), updated.json())
        cleared = self.client.patch("/api/books/1", headers=self.headers, json={"note": ""})
        self.assertEqual(cleared.json()["note"], "")

    def test_delete_is_idempotent_and_does_not_reuse_id(self):
        first = self.create()
        for _ in range(2):
            response = self.client.delete(f"/api/books/{first['id']}", headers=self.headers)
            self.assertEqual(response.status_code, 204)
            self.assertEqual(response.content, b"")
        self.assert_error(self.client.get("/api/books/1", headers=self.headers), 404, "BOOK_NOT_FOUND")
        self.assertGreater(self.create()["id"], first["id"])

    def test_absent_id_get_and_patch_return_404(self):
        self.assert_error(self.client.get("/api/books/99", headers=self.headers), 404, "BOOK_NOT_FOUND")
        for body in ({}, {"title": "없는 책"}):
            self.assert_error(self.client.patch("/api/books/99", headers=self.headers, json=body), 404, "BOOK_NOT_FOUND")
        self.assertEqual(self.client.delete("/api/books/99", headers=self.headers).status_code, 204)

    def test_filter_search_unicode_casefold_and_pagination(self):
        self.create(title="파이썬 입문", author="홍길동", status="reading")
        self.create(title="Straße", author="유럽 작가", status="done")
        third = self.create(title="파이썬 활용", author="다른 작가", status="reading")
        response = self.client.get("/api/books", headers=self.headers, params={"q": "파이썬", "status": "reading", "pageSize": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], [third])
        self.assertEqual(response.json()["pagination"], {"page": 1, "pageSize": 1, "totalItems": 2, "totalPages": 2})
        response = self.client.get("/api/books", headers=self.headers, params={"q": "파이썬", "status": "reading", "pageSize": 1, "page": 2})
        self.assertEqual(response.json()["data"][0]["title"], "파이썬 입문")
        for q in ("STRASSE", "유럽"):
            result = self.client.get("/api/books", headers=self.headers, params={"q": q}).json()
            self.assertEqual(result["pagination"]["totalItems"], 1)
            self.assertEqual(result["data"][0]["title"], "Straße")

    def test_empty_list_and_out_of_range_page(self):
        result = self.client.get("/api/books", headers=self.headers).json()
        self.assertEqual(result, {"data": [], "pagination": {"page": 1, "pageSize": 20, "totalItems": 0, "totalPages": 0}})
        self.create()
        result = self.client.get("/api/books?page=2", headers=self.headers).json()
        self.assertEqual(result["data"], [])
        self.assertEqual(result["pagination"]["totalItems"], 1)

    def test_search_is_literal_and_sql_safe(self):
        expected = self.create(title="100%_완독 ' 기록")
        for q in ("%_", "' 기록"):
            self.assertEqual(self.client.get("/api/books", headers=self.headers, params={"q": q}).json()["data"], [expected])
        self.assertEqual(self.client.get("/api/books", headers=self.headers, params={"q": "' OR 1=1 --"}).json()["data"], [])

    def test_required_title_and_author(self):
        for payload in ({}, {"title": "책"}, {"author": "작가"}):
            with self.subTest(payload=payload):
                self.assert_error(self.client.post("/api/books", headers=self.headers, json=payload), 422, "VALIDATION_ERROR")

    def test_invalid_values_rejected_on_create_and_patch_without_mutation(self):
        original = self.create()
        invalid = [
            {"title": ""}, {"title": "  \t\n"}, {"title": "가" * 201},
            {"author": ""}, {"author": "   "}, {"author": "가" * 201},
            {"title": "\u0000"}, {"author": "\u0000"}, {"title": "책\u0000제목"},
            {"note": "가" * 5001}, {"status": "invalid"},
            {"title": 123}, {"author": True}, {"note": []}, {"status": 1},
            {"extra": "private-value-must-not-be-echoed"}, {"id": 999},
            *[{field: None} for field in ("title", "author", "status", "note")],
        ]
        for invalid_values in invalid:
            with self.subTest(fields=list(invalid_values)):
                for method, url, payload in (
                    (self.client.post, "/api/books", {"title": "책", "author": "작가", **invalid_values}),
                    (self.client.patch, "/api/books/1", invalid_values),
                ):
                    response = method(url, headers=self.headers, json=payload)
                    self.assert_error(response, 422, "VALIDATION_ERROR")
                    self.assertNotIn("private-value-must-not-be-echoed", response.text)
        self.assertEqual(self.client.get("/api/books/1", headers=self.headers).json(), original)
        self.assertEqual(self.client.get("/api/books", headers=self.headers).json()["pagination"]["totalItems"], 1)

    def test_exact_length_boundaries(self):
        book = self.create(title="가" * 200, author="나" * 200, note="다" * 5000)
        self.assertEqual(len(book["note"]), 5000)
        for status in ("want", "reading", "done"):
            response = self.client.patch("/api/books/1", headers=self.headers, json={"status": status})
            self.assertEqual(response.status_code, 200)

    def test_query_and_id_validation(self):
        for params in ({"page": 0}, {"page": "abc"}, {"page": 1000000001}, {"pageSize": 0}, {"pageSize": 101}, {"status": "finished"}, {"q": "가" * 201}):
            self.assert_error(self.client.get("/api/books", headers=self.headers, params=params), 422, "VALIDATION_ERROR")
        for book_id in ("0", "-1", "abc", "9223372036854775808"):
            self.assert_error(self.client.get(f"/api/books/{book_id}", headers=self.headers), 422, "VALIDATION_ERROR")

    def test_malformed_json_and_missing_body(self):
        for body in (b"", b"{broken", b"[]", b"null"):
            response = self.client.post("/api/books", headers={**self.headers, "Content-Type": "application/json"}, content=body)
            self.assert_error(response, 422, "VALIDATION_ERROR")

    def test_missing_and_wrong_tokens_cannot_read_or_write(self):
        self.create()
        for headers in ({}, {"Authorization": "Bearer wrong"}, {"Authorization": "Basic ignored"}, {"Authorization": "Bearer"}):
            for method, url, payload in (("GET", "/api/books", None), ("GET", "/api/books/1", None), ("POST", "/api/books", {"title": "책", "author": "작가"}), ("PATCH", "/api/books/1", {"note": "변조"}), ("DELETE", "/api/books/1", None)):
                response = self.client.request(method, url, headers=headers, json=payload)
                self.assert_error(response, 401, "UNAUTHORIZED")
                self.assertEqual(response.headers["WWW-Authenticate"], "Bearer")
        self.assertEqual(self.client.get("/api/books/1", headers=self.headers).json()["note"], "")
        self.assertEqual(self.client.get("/api/books", headers=self.headers).json()["pagination"]["totalItems"], 1)

    def test_empty_server_token_fails_closed(self):
        for token in ("", "  "):
            with TestClient(create_app(self.db, token)) as client:
                self.assert_error(client.get("/api/books", headers=self.headers), 503, "SERVER_NOT_CONFIGURED")
                self.assertEqual(client.get("/health").status_code, 200)
                self.assertEqual(client.get("/docs").status_code, 200)
        with patch.dict(os.environ, {}, clear=True):
            with TestClient(create_app(self.db)) as client:
                self.assert_error(client.get("/api/books", headers=self.headers), 503, "SERVER_NOT_CONFIGURED")

    def test_public_health_docs_and_openapi_contract(self):
        self.assertEqual(self.client.get("/health").json(), {"status": "ok"})
        self.assertEqual(self.client.get("/docs").status_code, 200)
        spec = self.client.get("/openapi.json").json()
        self.assertEqual(spec["components"]["securitySchemes"]["ReadingLogToken"]["scheme"], "bearer")
        self.assertNotIn("security", spec["paths"]["/health"]["get"])
        for path in ("/api/books", "/api/books/{book_id}"):
            for operation in spec["paths"][path].values():
                self.assertEqual(operation["security"], [{"ReadingLogToken": []}])
                self.assertIn("401", operation["responses"])
                self.assertEqual(operation["responses"]["422"]["content"]["application/json"]["schema"]["$ref"], "#/components/schemas/ErrorResponse")
        self.assertNotIn(self.token, self.client.get("/openapi.json").text)
        patch_schema = spec["components"]["schemas"]["BookPatch"]
        self.assertNotIn("required", patch_schema)
        self.assertEqual(patch_schema["properties"]["title"]["type"], "string")

    def test_unknown_path_and_wrong_method_use_error_envelope(self):
        self.assert_error(self.client.get("/missing"), 404, "NOT_FOUND")
        self.assert_error(self.client.put("/api/books", headers=self.headers, json={}), 405, "METHOD_NOT_ALLOWED")

    def test_post_is_non_idempotent_and_unsupported_key_is_rejected(self):
        first, second = self.create(), self.create()
        self.assertNotEqual(first["id"], second["id"])
        response = self.client.post("/api/books", headers={**self.headers, "Idempotency-Key": "stable-client-intent"}, json={"title": "책", "author": "작가"})
        self.assert_error(response, 400, "UNSUPPORTED_IDEMPOTENCY_KEY")
        self.assertEqual(self.client.get("/api/books", headers=self.headers).json()["pagination"]["totalItems"], 2)

    def test_database_survives_app_recreation(self):
        original = self.create(note="재시작해도 보존")
        with TestClient(create_app(self.db, self.token)) as second:
            self.assertEqual(second.get("/api/books/1", headers=self.headers).json(), original)

    def test_relative_database_path_ignores_current_working_directory(self):
        previous_cwd = Path.cwd()
        try:
            os.chdir(APP_DIR)
            with patch("main.APP_DIR", self.db.parent):
                with TestClient(create_app(self.db.name, self.token)) as client:
                    self.assertEqual(client.post("/api/books", headers=self.headers, json={"title": "경로", "author": "검사"}).status_code, 201)
        finally:
            os.chdir(previous_cwd)
        self.assertEqual(self.client.get("/api/books/1", headers=self.headers).json()["title"], "경로")

    def test_actual_database_write_failure_never_reports_success(self):
        original = self.create()
        for operation in ("INSERT", "UPDATE", "DELETE"):
            with closing(sqlite3.connect(self.db)) as connection:
                with connection:
                    connection.execute(f"CREATE TRIGGER refuse_{operation} BEFORE {operation} ON books BEGIN SELECT RAISE(FAIL, 'private storage detail'); END;")
        requests = (("POST", "/api/books", {"title": "책", "author": "작가"}), ("PATCH", "/api/books/1", {"note": "변경"}), ("DELETE", "/api/books/1", None))
        for method, url, payload in requests:
            response = self.client.request(method, url, headers=self.headers, json=payload)
            self.assert_error(response, 500, "STORAGE_ERROR")
            self.assertNotIn("private storage detail", response.text)
        self.assertEqual(self.client.get("/api/books/1", headers=self.headers).json(), original)

    def test_concurrent_creates_keep_all_records(self):
        def create_one(index):
            return self.client.post("/api/books", headers=self.headers, json={"title": f"책 {index}", "author": "동시 등록"})
        with ThreadPoolExecutor(max_workers=4) as executor:
            responses = list(executor.map(create_one, range(12)))
        self.assertEqual([response.status_code for response in responses], [201] * 12)
        self.assertEqual(len({response.json()["id"] for response in responses}), 12)
        self.assertEqual(self.client.get("/api/books", headers=self.headers).json()["pagination"]["totalItems"], 12)


if __name__ == "__main__":
    unittest.main()
