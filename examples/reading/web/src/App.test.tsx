import { fireEvent, render, screen, within } from "@testing-library/react";
import { StrictMode } from "react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import App from "./App";
import { STORAGE_KEY } from "./books";

async function fillBook(title = "소년이 온다") {
  const user = userEvent.setup();
  await user.click(screen.getByRole("button", { name: "책 기록하기" }));
  await user.type(screen.getByLabelText(/책 제목 필수/), title);
  await user.type(screen.getByLabelText(/저자 필수/), "한강");
  await user.selectOptions(screen.getByLabelText("읽는 상태"), "reading");
  await user.type(screen.getByLabelText(/메모 선택/), "오래 기억할 문장");
  return user;
}

it("등록 → 검색 → 수정 → 재진입 → 삭제 흐름에서 저장된 값이 화면과 일치한다", async () => {
  const view = render(<App />);
  expect(screen.getByText("첫 번째 책을 기다리고 있어요")).toBeTruthy();
  const user = await fillBook();
  await user.click(screen.getByRole("button", { name: "책 저장하기" }));
  expect(screen.getByRole("heading", { name: "소년이 온다" })).toBeTruthy();
  await user.type(screen.getByRole("searchbox"), "없는 책");
  expect(screen.getByText("찾는 책이 보이지 않네요")).toBeTruthy();
  await user.click(screen.getByRole("button", { name: /검색·필터 초기화/ }));
  await user.type(screen.getByRole("searchbox"), "한강");
  await user.click(screen.getByRole("button", { name: "소년이 온다 수정" }));
  const title = screen.getByLabelText(/책 제목 필수/);
  await user.clear(title);
  await user.type(title, "소년이 온다 — 다시 읽기");
  await user.selectOptions(screen.getByLabelText("읽는 상태"), "done");
  await user.click(screen.getByRole("button", { name: "수정 내용 저장" }));
  view.unmount();
  render(<App />);
  expect(
    screen.getByRole("heading", { name: "소년이 온다 — 다시 읽기" }),
  ).toBeTruthy();
  expect(screen.getByText("오래 기억할 문장")).toBeTruthy();
  await user.click(
    screen.getByRole("button", { name: "소년이 온다 — 다시 읽기 삭제" }),
  );
  await user.click(screen.getByRole("button", { name: "삭제하기" }));
  expect(screen.getByText("첫 번째 책을 기다리고 있어요")).toBeTruthy();
  expect(JSON.parse(localStorage.getItem(STORAGE_KEY)!)).toEqual([]);
});

it("빈 제목 저장 시 필드 오류를 보여주고 입력으로 포커스를 돌린다", async () => {
  const user = userEvent.setup();
  render(<App />);
  await user.click(screen.getByRole("button", { name: "책 기록하기" }));
  await user.click(screen.getByRole("button", { name: "책 저장하기" }));
  expect(screen.getByText("책 제목을 입력해 주세요.")).toBeTruthy();
  expect(document.activeElement).toBe(screen.getByLabelText(/책 제목 필수/));
  expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
});

it("저장 실패 시 대화상자와 입력을 보존하고 복구 후 다시 저장한다", async () => {
  render(<App />);
  const user = await fillBook();
  const fail = vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
    throw new DOMException("full", "QuotaExceededError");
  });
  await user.click(screen.getByRole("button", { name: "책 저장하기" }));
  expect(screen.getByRole("alert").textContent).toContain("저장하지 못했어요");
  expect(
    (screen.getByLabelText(/책 제목 필수/) as HTMLInputElement).value,
  ).toBe("소년이 온다");
  expect(localStorage.getItem(STORAGE_KEY)).toBeNull();
  fail.mockRestore();
  await user.click(screen.getByRole("button", { name: "책 저장하기" }));
  expect(screen.getByRole("heading", { name: "소년이 온다" })).toBeTruthy();
  expect(screen.queryByRole("dialog")).toBeNull();
});

it("삭제 저장이 실패하면 목록과 저장된 기록이 그대로 남는다", async () => {
  render(<App />);
  const user = await fillBook();
  await user.click(screen.getByRole("button", { name: "책 저장하기" }));
  const before = localStorage.getItem(STORAGE_KEY);
  vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
    throw new DOMException("full", "QuotaExceededError");
  });
  await user.click(screen.getByRole("button", { name: "소년이 온다 삭제" }));
  await user.click(screen.getByRole("button", { name: "삭제하기" }));
  expect(screen.getByRole("heading", { name: "소년이 온다" })).toBeTruthy();
  expect(screen.getByRole("alert").textContent).toContain("저장하지 못했어요");
  expect(localStorage.getItem(STORAGE_KEY)).toBe(before);
});

it("읽기 실패 시 새 기록으로 덮어쓰지 않고 등록을 막는다", () => {
  localStorage.setItem(STORAGE_KEY, "broken original");
  render(<App />);
  expect(screen.getByRole("alert").textContent).toContain(
    "기존 데이터는 변경하지 않았습니다",
  );
  expect(
    (screen.getByRole("button", { name: "책 기록하기" }) as HTMLButtonElement)
      .disabled,
  ).toBe(true);
  expect(localStorage.getItem(STORAGE_KEY)).toBe("broken original");
});

it("대화상자는 제목에 포커스를 두고 취소 시 원래 등록 버튼으로 돌려준다", async () => {
  render(<StrictMode><App /></StrictMode>);
  const user = userEvent.setup();
  const opener = screen.getByRole("button", { name: "책 기록하기" });
  await user.click(opener);
  expect(document.activeElement).toBe(screen.getByLabelText(/책 제목 필수/));
  const dialog = screen.getByRole("dialog");
  expect(
    within(dialog).getByRole("heading", { name: "새로운 책 기록" }),
  ).toBeTruthy();
  fireEvent(dialog, new Event("cancel"));
  expect(screen.queryByRole("dialog")).toBeNull();
  expect(document.activeElement).toBe(opener);
});

it("수정 창을 닫으면 해당 책의 수정 버튼으로 포커스가 돌아온다", async () => {
  render(<App />);
  const user = await fillBook();
  await user.click(screen.getByRole("button", { name: "책 저장하기" }));
  const opener = screen.getByRole("button", { name: "소년이 온다 수정" });
  await user.click(opener);
  expect(document.activeElement).toBe(screen.getByLabelText(/책 제목 필수/));
  await user.click(screen.getByRole("button", { name: "대화상자 닫기" }));
  expect(document.activeElement).toBe(opener);
});

it("키보드로 삭제를 취소하면 해당 삭제 버튼으로 포커스가 돌아온다", async () => {
  render(<App />);
  const user = await fillBook();
  await user.click(screen.getByRole("button", { name: "책 저장하기" }));
  const opener = screen.getByRole("button", { name: "소년이 온다 삭제" });
  await user.click(opener);
  screen.getByRole("button", { name: "취소" }).focus();
  await user.keyboard("{Enter}");
  expect(screen.queryByRole("group", { name: "소년이 온다 삭제 확인" })).toBeNull();
  expect(document.activeElement).toBe(opener);
  expect(screen.getByRole("heading", { name: "소년이 온다" })).toBeTruthy();
});
