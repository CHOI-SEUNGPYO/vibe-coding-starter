import { describe, expect, it, vi } from "vitest";
import {
  filterBooks,
  readBooks,
  STORAGE_KEY,
  validateBook,
  writeBooks,
} from "./books";
import type { Book } from "./books";

const book: Book = {
  id: "one",
  title: "소년이 온다",
  author: "한강",
  status: "reading",
  note: "기억하고 싶은 문장",
  createdAt: "2026-11-16T00:00:00.000Z",
  updatedAt: "2026-11-16T00:00:00.000Z",
};

describe("독서 기록 저장과 검색", () => {
  it("앞뒤 공백 검색, 저자 검색, 상태 필터를 함께 적용한다", () => {
    const books = [
      book,
      {
        ...book,
        id: "two",
        title: "Human Acts",
        author: "Han Kang",
        status: "done" as const,
      },
    ];
    expect(filterBooks(books, "  한강 ", "reading")).toEqual([book]);
    expect(filterBooks(books, "HUMAN", "done")).toHaveLength(1);
    expect(filterBooks(books, "한강", "done")).toEqual([]);
  });
  it("공백 필수 입력과 너무 긴 입력을 거부한다", () => {
    expect(validateBook({ ...book, title: " ", author: "\t" })).toEqual({
      title: "책 제목을 입력해 주세요.",
      author: "저자를 입력해 주세요.",
    });
    expect(
      Object.keys(
        validateBook({
          ...book,
          title: "가".repeat(201),
          author: "나".repeat(121),
          note: "다".repeat(5001),
        }),
      ),
    ).toEqual(["title", "author", "note"]);
  });
  it("정상 기록을 저장하고 다시 읽는다", () => {
    expect(readBooks()).toEqual({ books: [], snapshot: null, error: null });
    const snapshot = writeBooks([book], null);
    expect(readBooks()).toEqual({ books: [book], snapshot, error: null });
  });
  it.each([
    "{broken",
    JSON.stringify([{ ...book, status: "invalid" }]),
    JSON.stringify([book, book]),
  ])("손상된 기록을 읽어도 기존 원본을 덮어쓰지 않는다: %s", (raw) => {
    localStorage.setItem(STORAGE_KEY, raw);
    expect(readBooks().error).toContain("읽지 못했어요");
    expect(localStorage.getItem(STORAGE_KEY)).toBe(raw);
  });
  it("저장공간이 부족하면 성공으로 처리하지 않고 기존 기록을 보존한다", () => {
    const snapshot = writeBooks([book], null);
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new DOMException("full", "QuotaExceededError");
    });
    expect(() => writeBooks([], snapshot)).toThrow("저장하지 못했어요");
    expect(localStorage.getItem(STORAGE_KEY)).toBe(snapshot);
  });
  it("다른 탭이 바꾼 최신 기록을 오래된 화면에서 덮어쓰지 않는다", () => {
    const snapshot = writeBooks([book], null);
    localStorage.setItem(STORAGE_KEY, "[]");
    expect(() => writeBooks([book], snapshot)).toThrow("다른 탭");
    expect(localStorage.getItem(STORAGE_KEY)).toBe("[]");
  });
});
