import { useRef, useState } from "react";
import BookDialog from "./BookDialog";
import { filterBooks, readBooks, statuses, writeBooks } from "./books";
import type { Book, BookInput, BookStatus } from "./books";
import { Icon } from "./Icons";

export default function App() {
  const [store, setStore] = useState(readBooks);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<BookStatus | "all">("all");
  const [editor, setEditor] = useState<{ book: Book | null } | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [writeError, setWriteError] = useState<string | null>(null);
  const [notice, setNotice] = useState("");
  const addButton = useRef<HTMLButtonElement>(null);
  const deleteTrigger = useRef<HTMLButtonElement | null>(null);
  const { books } = store;
  const shown = filterBooks(books, query, filter);
  const counts = { all: books.length, want: 0, reading: 0, done: 0 };
  for (const book of books) counts[book.status]++;

  function commit(nextBooks: Book[]) {
    if (store.error) return store.error;
    try {
      const snapshot = writeBooks(nextBooks, store.snapshot);
      setStore({ books: nextBooks, snapshot, error: null });
      setWriteError(null);
      return null;
    } catch (error) {
      return error instanceof Error
        ? error.message
        : "저장하지 못했어요. 다시 시도해 주세요.";
    }
  }

  function save(input: BookInput, id?: string) {
    const now = new Date().toISOString();
    const nextBooks = id
      ? books.map((book) =>
          book.id === id ? { ...book, ...input, updatedAt: now } : book,
        )
      : [
          { ...input, id: crypto.randomUUID(), createdAt: now, updatedAt: now },
          ...books,
        ];
    const error = commit(nextBooks);
    if (!error) {
      setEditor(null);
      setQuery("");
      setFilter("all");
      setNotice(
        id ? "독서 기록을 수정했어요." : "새로운 책을 서재에 담았어요.",
      );
    }
    return error;
  }

  function remove(book: Book) {
    const error = commit(books.filter((item) => item.id !== book.id));
    if (error) setWriteError(error);
    else {
      setDeleting(null);
      setNotice(`‘${book.title}’ 기록을 삭제했어요.`);
      addButton.current?.focus();
    }
  }

  function resetFilters() {
    setQuery("");
    setFilter("all");
  }

  return (
    <>
      <a className="skip-link" href="#library">
        서재로 바로 가기
      </a>
      <header className="site-header">
        <div className="header-inner">
          <a
            className="brand"
            href="#"
            aria-label="책갈피 홈"
            onClick={resetFilters}
          >
            <span className="brand-mark">
              <Icon name="book" size={24} />
            </span>
            책갈피<span className="brand-subtitle">나의 독서 기록</span>
          </a>
          <span className="local-label">
            <span className="status-dot" />
            나만의 작은 서재
          </span>
        </div>
      </header>
      <main>
        <section className="intro" aria-labelledby="page-title">
          <div className="intro-copy">
            <p className="eyebrow">MY READING JOURNAL</p>
            <h1 id="page-title">
              책장을 넘기고,
              <br />
              <span>기억을 남겨요.</span>
            </h1>
            <p>
              읽고 싶은 책부터 마음에 남은 문장까지.
              <br className="mobile-break" /> 당신의 독서를 차곡차곡 모아보세요.
            </p>
            <button
              ref={addButton}
              className="button primary"
              disabled={!!store.error}
              onClick={() => setEditor({ book: null })}
            >
              <Icon name="plus" />책 기록하기
            </button>
          </div>
          <div className="intro-art" aria-hidden="true">
            <div className="art-label">
              ONE BOOK,
              <br />A NEW WORLD.
            </div>
            <div className="art-book art-back">
              <span>
                THOUGHTS
                <br />
                TO KEEP
              </span>
              <i />
            </div>
            <div className="art-book art-front">
              <span>
                작은 기록이
                <br />
                쌓이는 곳
              </span>
              <div className="cover-window">
                <div />
              </div>
              <small>THE READING JOURNAL</small>
            </div>
            <span className="art-caption">오늘, 어떤 책을 읽고 있나요?</span>
          </div>
        </section>
        <div className="reading-overview" aria-label="내 서재 현황">
          <div className="overview-title">
            <Icon name="book" />
            <span>책과 함께한 시간</span>
          </div>
          <div>
            <span>서재에 담은 책</span>
            <strong>
              {counts.all}
              <small>권</small>
            </strong>
          </div>
          <div>
            <span>읽고 있는 책</span>
            <strong>
              {counts.reading}
              <small>권</small>
            </strong>
          </div>
          <div>
            <span>다 읽은 책</span>
            <strong>
              {counts.done}
              <small>권</small>
            </strong>
          </div>
        </div>
        <section
          id="library"
          className="library"
          aria-labelledby="library-heading"
        >
          <div className="section-heading">
            <h2 id="library-heading">
              내 서재 <span>{counts.all}</span>
            </h2>
            <span className="sort-label">최근 기록한 순</span>
          </div>
          {store.error && (
            <div className="error-message" role="alert">
              <p>{store.error}</p>
              <button
                className="text-button"
                onClick={() => window.location.reload()}
              >
                다시 불러오기
              </button>
            </div>
          )}
          {writeError && (
            <p className="error-message" role="alert">
              {writeError}
            </p>
          )}
          <div className="library-toolbar">
            <div className="filters" aria-label="읽는 상태 필터">
              {Object.entries({ all: "전체", ...statuses }).map(
                ([value, label]) => (
                  <button
                    key={value}
                    aria-pressed={filter === value}
                    onClick={() => setFilter(value as BookStatus | "all")}
                  >
                    {label}
                    <span>{counts[value as keyof typeof counts]}</span>
                  </button>
                ),
              )}
            </div>
            <div className="search-field">
              <Icon name="search" size={18} />
              <input
                aria-label="책 제목 또는 저자 검색"
                type="search"
                value={query}
                placeholder="책 제목 또는 저자 검색"
                onChange={(event) => setQuery(event.target.value)}
              />
            </div>
          </div>
          <p className="sr-only" aria-live="polite">
            {shown.length}권의 책이 표시됩니다.
          </p>
          {shown.length > 0 ? (
            <div className="book-grid">
              {shown.map((book) => (
                <article
                  className="book-card"
                  key={book.id}
                  aria-labelledby={`book-${book.id}`}
                >
                  <div
                    className={`mini-cover cover-${book.status}`}
                    aria-hidden="true"
                  >
                    <small>MY LIBRARY</small>
                    <span>{book.title.slice(0, 14)}</span>
                    <div className="cover-lines" />
                    <i>책갈피</i>
                  </div>
                  <div className="book-content">
                    <span className={`status-badge badge-${book.status}`}>
                      {book.status === "done" ? (
                        <Icon name="check" size={13} />
                      ) : (
                        <span />
                      )}
                      {statuses[book.status]}
                    </span>
                    <h3 id={`book-${book.id}`}>{book.title}</h3>
                    <p className="book-author">{book.author}</p>
                    {book.note ? (
                      <p className="book-note">{book.note}</p>
                    ) : (
                      <p className="book-note no-note">
                        아직 남긴 메모가 없어요.
                      </p>
                    )}
                    <div className="book-meta">
                      <span>
                        {new Date(book.createdAt).toLocaleDateString("ko-KR")}{" "}
                        기록
                      </span>
                      <div>
                        <button
                          className="icon-button"
                          aria-label={`${book.title} 수정`}
                          onClick={() => {
                            setDeleting(null);
                            setEditor({ book });
                          }}
                        >
                          <Icon name="edit" size={17} />
                        </button>
                        <button
                          className="icon-button"
                          aria-label={`${book.title} 삭제`}
                          onClick={(event) => {
                            deleteTrigger.current = event.currentTarget;
                            setWriteError(null);
                            setDeleting(book.id);
                          }}
                        >
                          <Icon name="trash" size={17} />
                        </button>
                      </div>
                    </div>
                    {deleting === book.id && (
                      <div
                        className="delete-confirm"
                        role="group"
                        aria-label={`${book.title} 삭제 확인`}
                      >
                        <p>이 기록을 삭제할까요? 삭제하면 되돌릴 수 없어요.</p>
                        <div>
                          <button
                            className="button secondary small"
                            onClick={() => {
                              setDeleting(null);
                              deleteTrigger.current?.focus();
                            }}
                          >
                            취소
                          </button>
                          <button
                            className="button danger small"
                            onClick={() => remove(book)}
                          >
                            삭제하기
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">
                <Icon name={books.length ? "search" : "book"} size={30} />
              </div>
              <h3>
                {books.length
                  ? "찾는 책이 보이지 않네요"
                  : "첫 번째 책을 기다리고 있어요"}
              </h3>
              <p>
                {books.length
                  ? "다른 제목이나 저자로 찾아보거나, 읽는 상태 필터를 바꿔보세요."
                  : "지금 읽는 책, 언젠가 읽고 싶은 책. 한 권을 기록하며 나만의 서재를 시작해 보세요."}
              </p>
              {books.length ? (
                <button className="text-button" onClick={resetFilters}>
                  검색·필터 초기화 <Icon name="arrow" size={16} />
                </button>
              ) : (
                <button
                  className="text-button"
                  disabled={!!store.error}
                  onClick={() => setEditor({ book: null })}
                >
                  첫 책 기록하기 <Icon name="arrow" size={16} />
                </button>
              )}
            </div>
          )}
        </section>
        <footer className="page-footer">
          <span className="footer-brand">
            책갈피 <small>한 권씩, 나답게.</small>
          </span>
          <p>
            <Icon name="lock" size={14} />
            기록은 이 브라우저에만 저장돼요. 브라우저 데이터를 지우면 사라질 수
            있어요.
          </p>
        </footer>
      </main>
      <div className="toast" role="status" aria-live="polite">
        {notice && (
          <>
            <Icon name="check" size={16} />
            <span>{notice}</span>
            <button aria-label="알림 닫기" onClick={() => setNotice("")}>
              <Icon name="close" size={16} />
            </button>
          </>
        )}
      </div>
      {editor && (
        <BookDialog
          book={editor.book}
          onClose={() => setEditor(null)}
          onSave={save}
        />
      )}
    </>
  );
}
