from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
import analyze


class ReadingAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="reading-test-")
        self.folder = Path(self.temporary.name)
        self.input = self.folder / "독서 기록.csv"
        self.output = self.folder / "결과"
        self.row = {"record_id": "R001", "title": "가상의 책", "author": "가상 저자", "status": "done",
                    "pages": "123", "rating": "4", "finished_date": "2024-02-29"}

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, rows=None, headers=analyze.FIELDS, encoding="utf-8-sig"):
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows([self.row] if rows is None else rows)
        self.input.write_bytes(stream.getvalue().encode(encoding))

    def test_fixed_sample_aggregates_and_zero_months(self):
        rows, digest = analyze.read_records(APP / "samples/reading-log.csv")
        summary, monthly, status = analyze.summarize(rows, digest)
        self.assertEqual(summary["total_records"], 12)
        self.assertEqual(summary["completed_records"], 7)
        self.assertEqual(summary["completed_pages"], 2000)
        self.assertEqual(summary["rated_completed_records"], 6)
        self.assertEqual(summary["average_completed_rating"], 4.333)
        self.assertEqual(summary["status_counts"], {"want": 2, "reading": 3, "done": 7})
        self.assertEqual([row["month"] for row in monthly], [f"2026-{i:02d}" for i in range(1, 7)])
        self.assertEqual([row["completed_records"] for row in monthly], [2, 0, 2, 0, 2, 1])
        self.assertEqual([row["completed_pages"] for row in monthly], [420, 0, 580, 0, 640, 360])
        self.assertEqual(sum(row["records"] for row in status), 12)

    def test_full_output_preserves_source_and_repeats(self):
        self.write()
        before = self.input.read_bytes()
        with warnings.catch_warnings():
            warnings.simplefilter("error", UserWarning)
            summary = analyze.write_report(self.input, self.output)
            analyze.write_report(self.input, self.folder / "다시 실행")
        self.assertEqual(self.input.read_bytes(), before)
        self.assertEqual(summary["source_sha256"], hashlib.sha256(before).hexdigest())
        expected = {"summary.json", "monthly.csv", "status.csv", "report.md", "reading-summary.png"}
        self.assertEqual({p.name for p in self.output.iterdir()}, expected)
        for name in expected:
            with self.subTest(file=name):
                self.assertEqual((self.output / name).read_bytes(), (self.folder / "다시 실행" / name).read_bytes())
                if name.endswith((".json", ".csv", ".md")):
                    self.assertNotIn(b"\r\n", (self.output / name).read_bytes())
        from PIL import Image
        with Image.open(self.output / "reading-summary.png") as image:
            self.assertEqual(image.format, "PNG")
            self.assertEqual(image.size, (2100, 1200))
        self.assertNotIn(self.row["title"], (self.output / "report.md").read_text(encoding="utf-8"))

    def test_header_only_is_valid_empty_analysis(self):
        self.write([])
        with warnings.catch_warnings():
            warnings.simplefilter("error", UserWarning)
            summary = analyze.write_report(self.input, self.output)
        self.assertEqual(summary["total_records"], 0)
        self.assertEqual(summary["completed_pages"], 0)
        self.assertIsNone(summary["average_completed_rating"])
        self.assertIsNone(summary["completion_month_start"])
        self.assertEqual(summary["rated_completed_records"], 0)
        with (self.output / "monthly.csv").open(encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(list(csv.DictReader(stream)), [])

    def test_cp949_is_explicit_and_utf8_bom_supported(self):
        for encoding in ("utf-8", "utf-8-sig", "cp949"):
            with self.subTest(encoding=encoding):
                self.write(encoding=encoding)
                rows, _ = analyze.read_records(self.input, "cp949" if encoding == "cp949" else "utf-8-sig")
                self.assertEqual(rows[0]["title"], "가상의 책")
        with self.assertRaisesRegex(analyze.InputError, "--encoding cp949"):
            analyze.read_records(self.input)

    def test_headers_empty_missing_extra_duplicate(self):
        header = ",".join(analyze.FIELDS)
        for content in ("", "\n", "title,author\n", header + ",extra\n", header + ",title\n"):
            with self.subTest(content=content):
                self.input.write_text(content, encoding="utf-8")
                with self.assertRaisesRegex(analyze.InputError, "1행"):
                    analyze.read_records(self.input)

    def test_ordered_headers_need_not_match_sample_order(self):
        self.write(headers=tuple(reversed(analyze.FIELDS)))
        rows, _ = analyze.read_records(self.input)
        self.assertEqual(rows[0]["pages"], 123)

    def test_bad_row_width_and_csv_syntax(self):
        for ending in ("R1,title\n", "R1,title,author,done,123,4,2024-02-29,extra\n", "\n", '"unclosed\n'):
            with self.subTest(ending=ending):
                self.input.write_text(",".join(analyze.FIELDS) + "\n" + ending, encoding="utf-8")
                with self.assertRaises(analyze.InputError):
                    analyze.read_records(self.input)

    def test_required_text_and_control_characters(self):
        for field in ("record_id", "title", "author"):
            for value in ("", "   ", "before\x00after", "before\nafter", "before\x7fafter"):
                with self.subTest(field=field, value=value):
                    self.write([{**self.row, field: value}])
                    with self.assertRaisesRegex(analyze.InputError, "2행"):
                        analyze.read_records(self.input)

    def test_invalid_numeric_values_and_unknown_status(self):
        cases = {
            "pages": ("", "0", "-2", "1.0", "NaN", "null", "100001", "１２３", "1e3", "9" * 5000),
            "rating": ("0", "6", "4.5", "NaN", "null", "inf", "false"),
            "status": ("", "finished", "DONE"),
        }
        for field, values in cases.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    self.write([{**self.row, field: value}])
                    with self.assertRaisesRegex(analyze.InputError, "2행"):
                        analyze.read_records(self.input)

    def test_date_contract(self):
        for value in ("", "2023-02-29", "2024-13-01", "2024-2-29", "20240229", "0000-01-01", "NaN"):
            with self.subTest(value=value):
                self.write([{**self.row, "finished_date": value}])
                with self.assertRaisesRegex(analyze.InputError, "finished_date"):
                    analyze.read_records(self.input)
        self.write([{**self.row, "status": "reading"}])
        with self.assertRaisesRegex(analyze.InputError, "미완독"):
            analyze.read_records(self.input)

    def test_duplicate_id_rejected_but_reread_allowed(self):
        self.write([self.row, self.row])
        with self.assertRaisesRegex(analyze.InputError, "3행: 중복 record_id"):
            analyze.read_records(self.input)
        self.write([self.row, {**self.row, "record_id": "R002"}])
        rows, digest = analyze.read_records(self.input)
        self.assertEqual(analyze.summarize(rows, digest)[0]["completed_records"], 2)

    def test_missing_rating_not_zero_and_unfinished_rating_excluded(self):
        self.write([{**self.row, "rating": ""}, {**self.row, "record_id": "R2", "status": "reading", "finished_date": ""}])
        rows, digest = analyze.read_records(self.input)
        summary, _, _ = analyze.summarize(rows, digest)
        self.assertEqual(summary["rated_completed_records"], 0)
        self.assertIsNone(summary["average_completed_rating"])
        self.assertEqual(summary["completed_pages"], 123)

    def test_existing_output_untouched(self):
        self.write()
        self.output.mkdir()
        marker = self.output / "keep.txt"
        marker.write_bytes(b"existing report")
        with self.assertRaisesRegex(analyze.InputError, "이미 있습니다"):
            analyze.write_report(self.input, self.output)
        self.assertEqual(marker.read_bytes(), b"existing report")
        self.assertEqual(list(self.output.iterdir()), [marker])

    def test_invalid_input_produces_no_partial_output(self):
        self.write([{**self.row, "pages": "bad"}])
        before = self.input.read_bytes()
        with self.assertRaises(analyze.InputError):
            analyze.write_report(self.input, self.output)
        self.assertFalse(self.output.exists())
        self.assertEqual(self.input.read_bytes(), before)

    def test_render_failure_cleans_staging_and_preserves_input(self):
        self.write()
        before = self.input.read_bytes()
        with patch.object(analyze, "draw_chart", side_effect=OSError("simulated image write failure")):
            with self.assertRaisesRegex(OSError, "simulated"):
                analyze.write_report(self.input, self.output)
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.folder.glob(".reading-tmp-*")), [])
        self.assertEqual(self.input.read_bytes(), before)

    def test_missing_font_fails_without_partial_output(self):
        self.write()
        with patch.object(analyze, "FONT", self.folder / "missing.ttf"):
            with self.assertRaisesRegex(analyze.InputError, "폰트"):
                analyze.write_report(self.input, self.output)
        self.assertFalse(self.output.exists())

    def test_cli_headless_with_korean_paths_and_error_exit(self):
        self.write()
        command = [sys.executable, str(APP / "analyze.py"), "--input", str(self.input), "--output", str(self.output)]
        result = subprocess.run(command, cwd=self.folder, env={**os.environ, "MPLBACKEND": "TkAgg"},
                                capture_output=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("분석 완료", result.stdout)
        self.assertEqual(json.loads((self.output / "summary.json").read_text())["completed_records"], 1)
        retry = subprocess.run(command, capture_output=True, encoding="utf-8", timeout=30)
        self.assertEqual(retry.returncode, 2)
        self.assertIn("덮어쓰지 않습니다", retry.stderr)

    def test_cli_oversized_number_has_row_error_without_traceback(self):
        self.write([{**self.row, "pages": "9" * 5000}])
        result = subprocess.run([sys.executable, str(APP / "analyze.py"), "--input", str(self.input),
                                 "--output", str(self.output)], capture_output=True, encoding="utf-8", timeout=15)
        self.assertEqual(result.returncode, 2)
        self.assertIn("2행: pages", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
