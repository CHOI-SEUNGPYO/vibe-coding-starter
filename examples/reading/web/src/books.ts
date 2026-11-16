export const STORAGE_KEY = "reading-log:books:v1";
export const statuses = {
  want: "읽고 싶어요",
  reading: "읽고 있어요",
  done: "다 읽었어요",
} as const;
export type BookStatus = keyof typeof statuses;
export type BookInput = {
  title: string;
  author: string;
  status: BookStatus;
  note: string;
};
export type Book = BookInput & {
  id: string;
  createdAt: string;
  updatedAt: string;
};
export type FieldErrors = Partial<Record<keyof BookInput, string>>;

export function validateBook(input: BookInput): FieldErrors {
  const errors: FieldErrors = {};
  if (!input.title.trim()) errors.title = "책 제목을 입력해 주세요.";
  else if (input.title.length > 200)
    errors.title = "책 제목은 200자까지 입력할 수 있어요.";
  if (!input.author.trim()) errors.author = "저자를 입력해 주세요.";
  else if (input.author.length > 120)
    errors.author = "저자는 120자까지 입력할 수 있어요.";
  if (!Object.hasOwn(statuses, input.status))
    errors.status = "읽는 상태를 선택해 주세요.";
  if (input.note.length > 5000)
    errors.note = "메모는 5,000자까지 입력할 수 있어요.";
  return errors;
}

export function filterBooks(
  books: Book[],
  query: string,
  status: BookStatus | "all",
) {
  const term = query.trim().toLocaleLowerCase();
  return books.filter(
    (book) =>
      (status === "all" || book.status === status) &&
      (!term ||
        `${book.title}\n${book.author}`.toLocaleLowerCase().includes(term)),
  );
}

function isBook(value: unknown): value is Book {
  if (!value || typeof value !== "object") return false;
  const book = value as Record<string, unknown>;
  return (
    ["id", "title", "author", "status", "note", "createdAt", "updatedAt"].every(
      (key) => typeof book[key] === "string",
    ) &&
    (book.id as string).length > 0 &&
    Object.keys(validateBook(book as Book)).length === 0 &&
    Number.isFinite(Date.parse(book.createdAt as string)) &&
    Number.isFinite(Date.parse(book.updatedAt as string))
  );
}

export function readBooks(): {
  books: Book[];
  snapshot: string | null;
  error: string | null;
} {
  try {
    const snapshot = window.localStorage.getItem(STORAGE_KEY);
    if (snapshot === null) return { books: [], snapshot, error: null };
    const parsed: unknown = JSON.parse(snapshot);
    if (
      !Array.isArray(parsed) ||
      !parsed.every(isBook) ||
      new Set(parsed.map((book) => book.id)).size !== parsed.length
    )
      throw new Error("Invalid stored books");
    return { books: parsed, snapshot, error: null };
  } catch {
    return {
      books: [],
      snapshot: null,
      error:
        "저장된 기록을 읽지 못했어요. 기존 데이터는 변경하지 않았습니다. 브라우저의 저장 권한을 확인한 뒤 다시 불러와 주세요.",
    };
  }
}

export function writeBooks(
  books: Book[],
  previousSnapshot: string | null,
): string {
  try {
    if (window.localStorage.getItem(STORAGE_KEY) !== previousSnapshot)
      throw new Error("conflict");
    const snapshot = JSON.stringify(books);
    window.localStorage.setItem(STORAGE_KEY, snapshot);
    return snapshot;
  } catch (error) {
    if (error instanceof Error && error.message === "conflict")
      throw new Error(
        "다른 탭에서 기록이 바뀌었어요. 입력한 내용을 복사해 둔 뒤 새로고침해 주세요. 이번 변경은 저장하지 않았습니다.",
      );
    throw new Error(
      "저장하지 못했어요. 입력한 내용은 그대로 있어요. 브라우저 저장 공간과 권한을 확인한 뒤 다시 시도해 주세요.",
    );
  }
}
