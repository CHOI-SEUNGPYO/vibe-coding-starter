import { useLayoutEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { statuses, validateBook } from "./books";
import type { Book, BookInput, FieldErrors } from "./books";
import { Icon } from "./Icons";

export default function BookDialog({
  book,
  onClose,
  onSave,
}: {
  book: Book | null;
  onClose: () => void;
  onSave: (input: BookInput, id?: string) => string | null;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const titleInput = useRef<HTMLInputElement>(null);
  const [input, setInput] = useState<BookInput>(() =>
    book
      ? {
          title: book.title,
          author: book.author,
          status: book.status,
          note: book.note,
        }
      : { title: "", author: "", status: "want", note: "" },
  );
  const [errors, setErrors] = useState<FieldErrors>({});
  const [saveError, setSaveError] = useState<string | null>(null);

  useLayoutEffect(() => {
    const element = dialog.current!;
    const opener = document.activeElement;
    element.showModal();
    titleInput.current?.focus();
    return () => {
      element.close();
      if (opener instanceof HTMLElement && opener.isConnected) opener.focus();
    };
  }, []);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextErrors = validateBook(input);
    setErrors(nextErrors);
    setSaveError(null);
    const invalid = Object.keys(nextErrors)[0];
    if (invalid) {
      dialog.current
        ?.querySelector<HTMLElement>(`[name="${invalid}"]`)
        ?.focus();
      return;
    }
    setSaveError(
      onSave(
        {
          ...input,
          title: input.title.trim(),
          author: input.author.trim(),
          note: input.note.trim(),
        },
        book?.id,
      ),
    );
  }

  return (
    <dialog
      ref={dialog}
      className="book-dialog"
      aria-labelledby="dialog-title"
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
    >
      <div className="dialog-heading">
        <div>
          <p className="eyebrow">A PAGE OF YOUR OWN</p>
          <h2 id="dialog-title">
            {book ? "독서 기록 수정" : "새로운 책 기록"}
          </h2>
        </div>
        <button
          className="icon-button"
          type="button"
          onClick={onClose}
          aria-label="대화상자 닫기"
        >
          <Icon name="close" />
        </button>
      </div>
      <p className="dialog-intro">
        마음에 들어온 책 한 권, 나만의 서재에 남겨보세요.
      </p>
      <form noValidate onSubmit={submit}>
        <div className="form-field">
          <label htmlFor="title">
            책 제목 <span>필수</span>
          </label>
          <input
            ref={titleInput}
            id="title"
            name="title"
            value={input.title}
            maxLength={200}
            placeholder="어떤 책을 만났나요?"
            aria-required="true"
            aria-invalid={!!errors.title}
            aria-describedby={errors.title ? "title-error" : undefined}
            onChange={(e) => setInput({ ...input, title: e.target.value })}
          />
          {errors.title && (
            <p className="field-error" id="title-error">
              {errors.title}
            </p>
          )}
        </div>
        <div className="form-field">
          <label htmlFor="author">
            저자 <span>필수</span>
          </label>
          <input
            id="author"
            name="author"
            value={input.author}
            maxLength={120}
            placeholder="책을 쓴 사람"
            aria-required="true"
            aria-invalid={!!errors.author}
            aria-describedby={errors.author ? "author-error" : undefined}
            onChange={(e) => setInput({ ...input, author: e.target.value })}
          />
          {errors.author && (
            <p className="field-error" id="author-error">
              {errors.author}
            </p>
          )}
        </div>
        <div className="form-field">
          <label htmlFor="status">읽는 상태</label>
          <select
            id="status"
            name="status"
            value={input.status}
            onChange={(e) =>
              setInput({
                ...input,
                status: e.target.value as BookInput["status"],
              })
            }
          >
            {Object.entries(statuses).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
        <div className="form-field">
          <label htmlFor="note">
            메모 <span>선택</span>
          </label>
          <textarea
            id="note"
            name="note"
            rows={4}
            maxLength={5000}
            value={input.note}
            placeholder="기억하고 싶은 문장이나 지금의 생각을 적어보세요."
            aria-describedby="note-help"
            onChange={(e) => setInput({ ...input, note: e.target.value })}
          />
          <p className="field-help" id="note-help">
            짧은 한 줄도 충분해요.
            <span>{input.note.length.toLocaleString()} / 5,000</span>
          </p>
        </div>
        {saveError && (
          <p className="error-message" role="alert">
            {saveError}
          </p>
        )}
        <div className="dialog-footer">
          <button className="button secondary" type="button" onClick={onClose}>
            취소
          </button>
          <button className="button primary" type="submit">
            <Icon name="check" size={18} />
            {book ? "수정 내용 저장" : "책 저장하기"}
          </button>
        </div>
      </form>
    </dialog>
  );
}
