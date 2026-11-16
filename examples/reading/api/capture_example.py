"""Generate public response examples using a fresh temporary database and token."""
import argparse
import json
from pathlib import Path
import secrets
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient
from main import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="가상 기록만으로 공개 API 결과를 생성합니다.")
    parser.add_argument("--output", type=Path, required=True, help="새 결과 폴더")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("기존 결과를 덮어쓰지 않습니다. 새 출력 폴더를 지정하세요.")
    samples = []
    with TemporaryDirectory(prefix="reading-api-example-") as folder:
        token = secrets.token_urlsafe(32)
        app = create_app(Path(folder) / "books.sqlite3", token)
        with TestClient(app) as client:
            def record(method, path, expected, *, authenticated=True, body=None):
                kwargs = {"headers": {"Authorization": "Bearer " + token}} if authenticated else {}
                if body is not None:
                    kwargs["json"] = body
                response = client.request(method, path, **kwargs)
                assert response.status_code == expected, (method, path, response.status_code)
                item = {"request": {"method": method, "path": path, "authenticated": authenticated},
                        "response": {"status": response.status_code, "body": response.json() if response.content else None}}
                if body is not None:
                    item["request"]["body"] = body
                if "location" in response.headers:
                    item["response"]["location"] = response.headers["location"]
                samples.append(item)
                return response

            record("GET", "/health", 200, authenticated=False)
            record("GET", "/api/books", 401, authenticated=False)
            record("POST", "/api/books", 201, body={"title": "가상의 작은 숲", "author": "가상 작가 도윤", "status": "reading", "note": "공개 예제 기록"})
            record("GET", "/api/books", 200)
            record("PATCH", "/api/books/1", 200, body={"status": "done", "note": "가상 독서 완료"})
            record("GET", "/api/books/1", 200)
            record("POST", "/api/books", 422, body={"title": "", "author": "가상 저자"})
            record("DELETE", "/api/books/1", 204)
            record("GET", "/api/books/1", 404)
            schema = client.get("/openapi.json").json()
    args.output.mkdir(parents=True)
    for name, value in (("requests-and-responses.json", samples), ("openapi.json", schema)):
        (args.output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"공개 가상 요청 {len(samples)}개와 OpenAPI 저장: {args.output}")


if __name__ == "__main__":
    main()
