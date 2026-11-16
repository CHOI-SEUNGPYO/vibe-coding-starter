"""One-person reading log API backed by a local SQLite file."""

from contextlib import asynccontextmanager, closing, contextmanager
import hmac
import os
from pathlib import Path
import sqlite3
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Path as PathParam, Query, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from starlette.exceptions import HTTPException as StarletteHTTPException


APP_DIR = Path(__file__).resolve().parent
BookStatus = Literal["want", "reading", "done"]
Title = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=200, pattern=r"^[^\x00]*$")]
Note = Annotated[str, StringConstraints(strict=True, max_length=5000)]
BookId = Annotated[int, PathParam(ge=1, le=9223372036854775807)]


class BookCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: Title
    author: Title
    status: BookStatus = "want"
    note: Note = ""


class BookPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Unset defaults are ignored by exclude_unset; explicit null still fails validation.
    title: Title = Field(default_factory=lambda: None)
    author: Title = Field(default_factory=lambda: None)
    status: BookStatus = Field(default_factory=lambda: None)
    note: Note = Field(default_factory=lambda: None)


class Book(BookCreate):
    id: int


class Pagination(BaseModel):
    page: int
    pageSize: int
    totalItems: int
    totalPages: int


class BookList(BaseModel):
    data: list[Book]
    pagination: Pagination


class ErrorDetail(BaseModel):
    location: list[str | int]
    message: str
    type: str


class Error(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: Error


class Health(BaseModel):
    status: Literal["ok"]


def error(status: int, code: str, message: str, details: list | None = None, headers=None):
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message, "details": details or []}},
        headers=headers,
    )


def create_app(database_path: str | Path | None = None, api_token: str | None = None) -> FastAPI:
    configured_path = database_path if database_path is not None else os.getenv("BOOKS_DB_PATH", "data/books.sqlite3")
    db_path = Path(configured_path).expanduser()
    if not db_path.is_absolute():
        db_path = APP_DIR / db_path
    db_path = db_path.resolve()
    token = api_token if api_token is not None else os.getenv("BOOKS_API_TOKEN", "")

    @contextmanager
    def database():
        with closing(sqlite3.connect(db_path, timeout=5)) as connection:
            connection.row_factory = sqlite3.Row
            connection.create_function("casefold", 1, str.casefold, deterministic=True)
            with connection:
                yield connection

    @asynccontextmanager
    async def lifespan(_app):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with database() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL CHECK(length(title) BETWEEN 1 AND 200),
                    author TEXT NOT NULL CHECK(length(author) BETWEEN 1 AND 200),
                    status TEXT NOT NULL CHECK(status IN ('want', 'reading', 'done')),
                    note TEXT NOT NULL CHECK(length(note) <= 5000)
                )
            """)
        yield

    app = FastAPI(
        title="개인 독서 기록 API",
        version="1.0.0",
        description="개인용 단일 토큰 API. 책 API에는 Bearer 토큰이 필요합니다. POST는 비멱등이며 자동 재시도하면 중복 등록될 수 있습니다.",
        lifespan=lifespan,
        responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    )
    bearer = HTTPBearer(auto_error=False, scheme_name="ReadingLogToken")

    def authorize(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
        if not token or not token.strip():
            raise HTTPException(503, {"code": "SERVER_NOT_CONFIGURED", "message": "API 인증 설정이 필요합니다."})
        if credentials is None or not hmac.compare_digest(credentials.credentials.encode(), token.encode()):
            raise HTTPException(
                401,
                {"code": "UNAUTHORIZED", "message": "올바른 Bearer 토큰이 필요합니다."},
                headers={"WWW-Authenticate": "Bearer"},
            )

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request, exc):
        # Do not echo request values, which can contain private notes or credentials.
        details = [{"location": list(item["loc"]), "message": item["msg"], "type": item["type"]} for item in exc.errors()]
        return error(422, "VALIDATION_ERROR", "입력값을 확인해 주세요.", details)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_request, exc):
        if isinstance(exc.detail, dict):
            return error(exc.status_code, exc.detail["code"], exc.detail["message"], headers=exc.headers)
        return error(exc.status_code, {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}.get(exc.status_code, "HTTP_ERROR"), str(exc.detail), headers=exc.headers)

    @app.exception_handler(sqlite3.Error)
    async def storage_error(_request, _exc):
        return error(500, "STORAGE_ERROR", "저장소 작업을 완료하지 못했습니다.")

    @app.exception_handler(Exception)
    async def unexpected_error(_request, _exc):
        return error(500, "INTERNAL_ERROR", "요청을 처리하지 못했습니다.")

    @app.get("/health", response_model=Health, tags=["system"])
    def health():
        with database() as connection:
            connection.execute("SELECT 1").fetchone()
        return {"status": "ok"}

    books = APIRouter(
        prefix="/api/books",
        tags=["books"],
        dependencies=[Depends(authorize)],
        responses={401: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
    )

    def get_book(connection, book_id):
        row = connection.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
        if row is None:
            raise HTTPException(404, {"code": "BOOK_NOT_FOUND", "message": "독서 기록을 찾을 수 없습니다."})
        return dict(row)

    @books.post("", status_code=201, response_model=Book, responses={400: {"model": ErrorResponse}}, description="같은 본문으로 반복 호출하면 매번 새 기록이 생깁니다. Idempotency-Key는 지원하지 않으며 전달하면 400을 반환합니다.")
    def create_book(book: BookCreate, response: Response, idempotency_key: Annotated[str | None, Header()] = None):
        if idempotency_key is not None:
            raise HTTPException(400, {"code": "UNSUPPORTED_IDEMPOTENCY_KEY", "message": "Idempotency-Key를 지원하지 않습니다. 등록 요청은 자동 재시도하지 마세요."})
        with database() as connection:
            cursor = connection.execute(
                "INSERT INTO books (title, author, status, note) VALUES (?, ?, ?, ?)",
                (book.title, book.author, book.status, book.note),
            )
            result = get_book(connection, cursor.lastrowid)
        response.headers["Location"] = f"/api/books/{result['id']}"
        return result

    @books.get("", response_model=BookList, description="ID 내림차순. q는 제목·저자의 Unicode 대소문자를 구분하지 않는 부분 문자열 검색입니다. 빈 q는 전체 조회입니다.")
    def list_books(
        q: Annotated[str, Query(max_length=200)] = "",
        status: Annotated[BookStatus | None, Query()] = None,
        page: Annotated[int, Query(ge=1, le=1000000000)] = 1,
        pageSize: Annotated[int, Query(ge=1, le=100)] = 20,
    ):
        conditions, values = [], []
        if q.strip():
            conditions.append("(instr(casefold(title), ?) > 0 OR instr(casefold(author), ?) > 0)")
            values.extend([q.strip().casefold()] * 2)
        if status is not None:
            conditions.append("status = ?")
            values.append(status)
        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        with database() as connection:
            connection.execute("BEGIN")
            total = connection.execute("SELECT count(*) FROM books" + where, values).fetchone()[0]
            rows = connection.execute("SELECT * FROM books" + where + " ORDER BY id DESC LIMIT ? OFFSET ?", [*values, pageSize, (page - 1) * pageSize]).fetchall()
        return {"data": [dict(row) for row in rows], "pagination": {"page": page, "pageSize": pageSize, "totalItems": total, "totalPages": (total + pageSize - 1) // pageSize}}

    @books.get("/{book_id}", response_model=Book, responses={404: {"model": ErrorResponse}})
    def read_book(book_id: BookId):
        with database() as connection:
            return get_book(connection, book_id)

    @books.patch("/{book_id}", response_model=Book, responses={404: {"model": ErrorResponse}}, description="전달한 필드만 변경합니다. null은 허용하지 않습니다. {}는 기존 기록을 그대로 반환하며, 없는 ID는 404입니다.")
    def update_book(book_id: BookId, book: BookPatch):
        changes = book.model_dump(exclude_unset=True)
        with database() as connection:
            if changes:
                assignments = ", ".join(f"{field} = ?" for field in changes)
                connection.execute(f"UPDATE books SET {assignments} WHERE id = ?", [*changes.values(), book_id])
            return get_book(connection, book_id)

    @books.delete("/{book_id}", status_code=204, description="기록이 없어도 204를 반환하므로 삭제 요청을 반복할 수 있습니다.")
    def delete_book(book_id: BookId):
        with database() as connection:
            connection.execute("DELETE FROM books WHERE id = ?", (book_id,))
        return Response(status_code=204)

    app.include_router(books)
    return app


app = create_app()
