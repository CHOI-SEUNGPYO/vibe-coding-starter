"""Validate a local reading CSV and write a reproducible report to a new folder."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import date
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile

APP_DIR = Path(__file__).resolve().parent
FIELDS = ("record_id", "title", "author", "status", "pages", "rating", "finished_date")
STATUSES = {"want": "읽고 싶음", "reading": "읽는 중", "done": "완독"}
FONT = APP_DIR / "fonts" / "NotoSansKR-Regular.ttf"
BOLD_FONT = APP_DIR / "fonts" / "NotoSansKR-Bold.ttf"


class InputError(ValueError):
    """An input or output choice the user can correct."""


def read_records(path: Path, encoding: str = "utf-8-sig") -> tuple[list[dict], str]:
    raw = path.read_bytes()
    try:
        content = raw.decode(encoding)
    except UnicodeDecodeError as error:
        raise InputError(f"{encoding}로 읽을 수 없습니다. 원본 인코딩을 확인하세요. "
                         "CP949 파일이면 --encoding cp949를 지정하세요.") from error
    reader = csv.reader(io.StringIO(content, newline=""), strict=True)
    try:
        headers = next(reader, None)
        if headers is None:
            raise InputError("1행: 헤더가 없습니다. 샘플 CSV의 열 이름을 확인하세요.")
        if len(headers) != len(set(headers)):
            raise InputError("1행: 중복된 열 이름이 있습니다.")
        if set(headers) != set(FIELDS):
            raise InputError("1행: 열 이름은 정확히 " + ", ".join(FIELDS) + "여야 합니다.")
        records, identifiers = [], set()
        while True:
            line = reader.line_num + 1
            values = next(reader, None)
            if values is None:
                break
            if len(values) != len(headers):
                raise InputError(f"{line}행: 열 개수가 헤더와 다릅니다.")
            row = dict(zip(headers, (value.strip() for value in values)))
            if any(any(ord(char) < 32 or ord(char) == 127 for char in value) for value in values):
                raise InputError(f"{line}행: NUL이나 제어문자는 사용할 수 없습니다.")
            for field in ("record_id", "title", "author"):
                if not row[field]:
                    raise InputError(f"{line}행: {field}는 비어 있을 수 없습니다.")
            if row["record_id"] in identifiers:
                raise InputError(f"{line}행: 중복 record_id입니다. 재독 기록도 다른 ID를 사용하세요.")
            if row["status"] not in STATUSES:
                raise InputError(f"{line}행: status는 want, reading, done 중 하나여야 합니다.")
            if not re.fullmatch(r"[0-9]{1,6}", row["pages"]) or not 1 <= int(row["pages"]) <= 100000:
                raise InputError(f"{line}행: pages는 1~100000 사이의 정수여야 합니다.")
            if row["rating"] and row["rating"] not in ("1", "2", "3", "4", "5"):
                raise InputError(f"{line}행: rating은 빈 값 또는 1~5 사이의 정수여야 합니다.")
            if row["status"] == "done":
                if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", row["finished_date"]):
                    raise InputError(f"{line}행: 완독 기록의 finished_date는 YYYY-MM-DD여야 합니다.")
                try:
                    date.fromisoformat(row["finished_date"])
                except ValueError as error:
                    raise InputError(f"{line}행: finished_date가 실제 달력 날짜가 아닙니다.") from error
            elif row["finished_date"]:
                raise InputError(f"{line}행: 미완독 기록의 finished_date는 비워 두세요.")
            identifiers.add(row["record_id"])
            row["pages"] = int(row["pages"])
            row["rating"] = int(row["rating"]) if row["rating"] else None
            records.append(row)
    except csv.Error as error:
        raise InputError(f"{reader.line_num}행 부근: CSV 형식이 잘못됐습니다 ({error}).") from error
    return records, hashlib.sha256(raw).hexdigest()


def summarize(records: list[dict], source_hash: str) -> tuple[dict, list[dict], list[dict]]:
    completed = [row for row in records if row["status"] == "done"]
    ratings = [row["rating"] for row in completed if row["rating"] is not None]
    counts = Counter(row["status"] for row in records)
    status = [{"status": key, "label": label, "records": counts[key]} for key, label in STATUSES.items()]
    by_month = Counter(row["finished_date"][:7] for row in completed)
    pages = Counter()
    for row in completed:
        pages[row["finished_date"][:7]] += row["pages"]
    monthly = []
    if by_month:
        first_year, first_month = map(int, min(by_month).split("-"))
        last_year, last_month = map(int, max(by_month).split("-"))
        for offset in range(first_year * 12 + first_month - 1, last_year * 12 + last_month):
            year, month = divmod(offset, 12)
            key = f"{year:04d}-{month + 1:02d}"
            monthly.append({"month": key, "completed_records": by_month[key], "completed_pages": pages[key]})
    summary = {
        "source_sha256": source_hash,
        "total_records": len(records),
        "completed_records": len(completed),
        "completed_pages": sum(row["pages"] for row in completed),
        "rated_completed_records": len(ratings),
        "average_completed_rating": round(sum(ratings) / len(ratings), 3) if ratings else None,
        "status_counts": {key: counts[key] for key in STATUSES},
        "completion_month_start": monthly[0]["month"] if monthly else None,
        "completion_month_end": monthly[-1]["month"] if monthly else None,
    }
    return summary, monthly, status


def draw_chart(summary: dict, monthly: list[dict], status: list[dict], destination: Path) -> None:
    # Keep the font cache inside the project, including on machines without a GUI.
    os.environ.setdefault("MPLCONFIGDIR", str(APP_DIR / ".cache" / "matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import font_manager, pyplot as plt
    from matplotlib.ticker import MaxNLocator

    if not FONT.is_file() or not BOLD_FONT.is_file():
        raise InputError("번들 한글 폰트가 없습니다. fonts/의 파일을 복원하세요.")
    font_manager.fontManager.addfont(str(FONT))
    font_manager.fontManager.addfont(str(BOLD_FONT))
    family = font_manager.FontProperties(fname=FONT).get_name()
    with plt.rc_context({"font.family": family, "axes.unicode_minus": False,
                         "font.size": 11, "axes.labelcolor": "#53615c", "text.color": "#203a35"}):
        fig = plt.figure(figsize=(14, 8), facecolor="#f6f5ef")
        try:
            fig.text(.07, .92, "나의 독서 기록", fontsize=27, weight="bold")
            fig.text(.07, .865, "완독일로 살펴본 독서 흐름 · 원본 CSV의 전체 기록", fontsize=12, color="#53615c")
            for x, title, value in ((.07, "전체 기록", f"{summary['total_records']:,}건"),
                                    (.36, "완독 기록", f"{summary['completed_records']:,}건"),
                                    (.65, "완독 페이지 합계", f"{summary['completed_pages']:,}쪽")):
                fig.text(x, .775, title, color="#53615c", fontsize=11)
                fig.text(x, .71, value, fontsize=26, weight="bold")
            axes = fig.subplots(1, 2, gridspec_kw={"left": .07, "right": .96, "bottom": .19,
                                                 "top": .59, "wspace": .28, "width_ratios": [1.6, 1]})
            month_ax, status_ax = axes
            for axis in axes:
                axis.set_facecolor("#f6f5ef")
                axis.spines[["top", "right", "left"]].set_visible(False)
                axis.spines["bottom"].set_color("#c9d3cd")
                axis.tick_params(length=0, colors="#53615c", pad=8)
                axis.set_axisbelow(True)
            month_ax.set_title("월별 완독 기록", loc="left", pad=20, weight="bold")
            month_ax.set_ylabel("완독 기록 수 (건)")
            month_ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            month_ax.grid(axis="y", color="#dfe4de", linewidth=.7)
            if monthly:
                positions = list(range(len(monthly)))
                values = [row["completed_records"] for row in monthly]
                # shortcut: long histories use a line so thousands of bars do not overwhelm a static chart.
                if len(monthly) <= 36:
                    bars = month_ax.bar(positions, values, color="#216b59", width=.6)
                    month_ax.bar_label(bars, padding=5, color="#216b59")
                else:
                    month_ax.plot(positions, values, color="#216b59", linewidth=2)
                step = max(1, (len(monthly) + 7) // 8)
                ticks = positions[::step]
                month_ax.set_xticks(ticks, [monthly[i]["month"] for i in ticks], rotation=30, ha="right")
                month_ax.set_ylim(0, max(values) * 1.3 + .5)
            else:
                month_ax.set_ylim(0, 1)
                month_ax.set_xticks([])
                month_ax.text(.5, .5, "아직 완독 기록이 없어요", transform=month_ax.transAxes,
                              ha="center", color="#53615c")
            status_ax.set_title("현재 읽는 상태", loc="left", pad=20, weight="bold")
            bars = status_ax.barh([row["label"] for row in status], [row["records"] for row in status],
                                  color=["#d4b785", "#7699ad", "#216b59"], height=.55)
            status_ax.bar_label(bars, padding=7)
            status_ax.set_xlim(0, max(row["records"] for row in status) * 1.3 + 1)
            status_ax.set_xlabel("기록 수 (건)")
            status_ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            status_ax.grid(axis="x", color="#dfe4de", linewidth=.7)
            rating = summary["average_completed_rating"]
            rating_text = f"{rating:g} / 5" if rating is not None else "평점 없음"
            fig.text(.07, .08, f"완독 평균 평점 {rating_text}  ·  평점을 남긴 완독 {summary['rated_completed_records']}건 기준",
                     fontsize=11)
            fig.text(.07, .04, "페이지는 완독한 책의 전체 분량 합계입니다. 같은 책의 재독은 각각 한 기록으로 셉니다.",
                     fontsize=9, color="#53615c")
            fig.savefig(destination, dpi=150, facecolor=fig.get_facecolor(), metadata={"Software": "reading-data"})
        finally:
            plt.close(fig)


def write_report(input_path: Path, output: Path, encoding: str = "utf-8-sig") -> dict:
    if output.exists() or output.is_symlink():
        raise InputError("결과 폴더가 이미 있습니다. 덮어쓰지 않습니다. --output에 새 폴더를 지정하세요.")
    records, source_hash = read_records(input_path, encoding)
    summary, monthly, status = summarize(records, source_hash)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".reading-tmp-", dir=output.parent) as temporary:
        staging = Path(temporary)
        (staging / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        for name, fields, rows in (("monthly.csv", ("month", "completed_records", "completed_pages"), monthly),
                                   ("status.csv", ("status", "label", "records"), status)):
            with (staging / name).open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
        rating = summary["average_completed_rating"]
        average = f"{rating:g} / 5" if rating is not None else "계산하지 않음 (분모 0)"
        report = (
            "# 독서 기록 분석\n\n"
            f"전체 {summary['total_records']}건 중 완독은 {summary['completed_records']}건입니다. "
            f"완독한 책의 전체 분량 합계는 {summary['completed_pages']:,}쪽입니다.\n\n"
            f"완독 평균 평점: **{average}**. 완독 중 평점을 남긴 {summary['rated_completed_records']}건만 분모로 사용했습니다. "
            "미평점을 0점으로 계산하지 않았습니다.\n\n"
            "![월별 완독과 현재 상태](reading-summary.png)\n\n"
            "## 지표와 한계\n\n"
            "- 월별 집계는 finished_date의 달을 사용합니다. 첫 완독 달과 마지막 완독 달 사이의 기록 없는 달은 0입니다.\n"
            "- pages는 책 전체 분량입니다. 미완독 책의 페이지나 하루 독서량을 합친 지표가 아닙니다.\n"
            "- 같은 책의 재독은 다른 record_id를 가진 별도 기록으로 셉니다. 고유 도서 수와 다릅니다.\n"
            "- 입력 오류가 있으면 일부 행을 버리고 계산하지 않고 전체 실행을 실패시킵니다.\n"
            "- 개인 기록의 기술 통계입니다. 표본 밖의 독서 성향이나 인과관계를 추론하지 않습니다.\n\n"
            f"원본 SHA-256: `{source_hash}`\n\n"
            "집계표는 monthly.csv와 status.csv, 구조화된 요약은 summary.json에 있습니다. "
            "원본 제목·저자·개별 행은 결과에 복사하지 않았습니다.\n"
        )
        (staging / "report.md").write_text(report, encoding="utf-8", newline="\n")
        draw_chart(summary, monthly, status, staging / "reading-summary.png")
        if output.exists() or output.is_symlink():
            raise InputError("결과 폴더가 생겨 작업을 중단했습니다. 새 --output 경로를 사용하세요.")
        staging.rename(output)
    return summary


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description="독서 기록 CSV를 검증하고 새 폴더에 집계표와 한국어 차트를 만듭니다.")
    parser.add_argument("--input", type=Path, required=True, help="원본 CSV 경로; 수정하지 않습니다")
    parser.add_argument("--output", type=Path, required=True, help="아직 존재하지 않는 결과 폴더")
    parser.add_argument("--encoding", choices=("utf-8-sig", "cp949"), default="utf-8-sig")
    args = parser.parse_args(argv)
    try:
        summary = write_report(args.input, args.output, args.encoding)
    except (InputError, OSError, UnicodeError) as error:
        print(f"분석 실패: {error}", file=sys.stderr)
        return 2
    print(f"분석 완료: 전체 {summary['total_records']}건, 완독 {summary['completed_records']}건. "
          f"결과: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
