import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

APP = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("weekly_digest", APP / "weekly_digest.py")
digest = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(digest)


class WeeklyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.source = self.root / "reading.csv"
        self.source.write_bytes((APP / "samples/reading-log.csv").read_bytes())
        self.output = self.root / "new/output"

    def tearDown(self):
        self.temporary.cleanup()

    def snapshot(self, path):
        return {p.relative_to(path).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in path.rglob("*") if p.is_file()}

    def cli(self, *extra, output=None, source=None, week="2026-11-09"):
        return subprocess.run([sys.executable, str(APP / "weekly_digest.py"),
            "--input", str(source or self.source), "--week", week,
            "--output", str(output or self.output), *extra],
            capture_output=True, encoding="utf-8", cwd=self.root, timeout=20)

    def records(self):
        with self.source.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.reader(stream))

    def rewrite(self, rows, encoding="utf-8-sig"):
        stream = io.StringIO(newline="")
        csv.writer(stream, lineterminator="\n").writerows(rows)
        self.source.write_bytes(stream.getvalue().encode(encoding))

    def test_dry_run_has_correct_week_boundary_and_no_writes(self):
        before = self.source.read_bytes()
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.output.parent.exists())
        plan = json.loads(result.stdout)
        self.assertEqual((plan["mode"], plan["action"]), ("dry-run", "create"))
        summary = plan["summary"]
        self.assertEqual(summary["completed_records"], 3)
        self.assertEqual(summary["completed_pages"], 540)
        self.assertEqual(summary["average_completed_rating"], 4)
        self.assertEqual(summary["rated_completed_records"], 2)
        self.assertEqual(summary["source_sha256"], hashlib.sha256(before).hexdigest())
        self.assertEqual(self.source.read_bytes(), before)

    def test_apply_and_retry_are_identical_without_rewriting(self):
        first = self.cli("--apply")
        self.assertEqual(first.returncode, 0, first.stderr)
        result = json.loads(first.stdout)
        self.assertEqual(result["action"], "created")
        folder = Path(result["destination"])
        self.assertEqual({p.name for p in folder.iterdir()}, {"summary.json", "digest.md", "manifest.json"})
        before = self.snapshot(self.output)
        retry = self.cli("--apply")
        self.assertEqual(retry.returncode, 0, retry.stderr)
        self.assertEqual(json.loads(retry.stdout)["action"], "already-complete")
        self.assertEqual(self.snapshot(self.output), before)
        preview = self.cli()
        self.assertEqual(json.loads(preview.stdout)["action"], "already-complete")
        self.assertEqual(self.snapshot(self.output), before)

    def test_changed_input_creates_new_key_and_preserves_previous(self):
        original = digest.run(self.source, "2026-11-09", self.output, True)
        old = self.snapshot(Path(original["destination"]))
        rows = self.records(); rows[1][4] = "121"; self.rewrite(rows)
        changed = digest.run(self.source, "2026-11-09", self.output, True)
        self.assertNotEqual(original["run_key"], changed["run_key"])
        self.assertEqual(changed["summary"]["completed_pages"], 541)
        self.assertEqual(self.snapshot(Path(original["destination"])), old)

    def test_empty_week_and_header_only_input(self):
        result = digest.run(self.source, "2026-01-05", self.output, True)
        self.assertEqual(result["summary"]["completed_records"], 0)
        self.assertIsNone(result["summary"]["average_completed_rating"])
        self.rewrite([list(digest.FIELDS)])
        result = digest.run(self.source, "2026-11-09", self.output, True)
        self.assertEqual(result["summary"]["input_records"], 0)

    def test_year_boundary_week(self):
        self.rewrite([list(digest.FIELDS), ["x", "가상", "저자", "done", "100", "5", "2027-01-03"],
                      ["y", "가상2", "저자", "done", "100", "1", "2027-01-04"]])
        result = digest.run(self.source, "2026-12-28", self.output)
        self.assertEqual(result["summary"]["week_end"], "2027-01-03")
        self.assertEqual(result["summary"]["completed_records"], 1)
        self.assertEqual(result["summary"]["average_completed_rating"], 5)

    def test_bad_week_is_rejected_without_output(self):
        for value in ("2026-11-10", "2026-11-9", "2026-02-30", "9999-12-31", "nope"):
            with self.subTest(value=value):
                result = self.cli("--apply", week=value)
                self.assertEqual(result.returncode, 2)
                self.assertIn("--week", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse(self.output.exists())

    def test_utf8_bom_and_cp949_are_explicit(self):
        rows = self.records()
        self.rewrite(rows)
        expected = digest.run(self.source, "2026-11-09", self.output)["summary"]["completed_pages"]
        self.rewrite(rows, "cp949")
        failed = self.cli("--apply")
        self.assertEqual(failed.returncode, 2)
        self.assertIn("인코딩", failed.stderr)
        self.assertFalse(self.output.exists())
        success = self.cli("--apply", "--encoding", "cp949")
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertEqual(json.loads(success.stdout)["summary"]["completed_pages"], expected)

    def test_invalid_values_have_row_context_and_no_output(self):
        rows = self.records()
        for index, value in ((0, ""), (1, " "), (2, "\0"), (3, "finished"),
                             (4, "-1"), (4, "NaN"), (4, "9" * 5000), (4, "100001"),
                             (5, "4.5"), (5, "inf"), (6, "2026-02-29"), (6, "")):
            with self.subTest(index=index, value=value[:12]):
                row = rows[1].copy(); row[index] = value
                self.rewrite([rows[0], row])
                result = self.cli("--apply")
                self.assertEqual(result.returncode, 2)
                self.assertIn("2행", result.stderr)
                self.assertFalse(self.output.exists())

    def test_duplicate_id_bad_headers_and_rows(self):
        rows = self.records()
        cases = [rows + [rows[1]], [rows[0][:-1], rows[1][:-1]],
                 [["title", *rows[0][1:]], rows[1]], [rows[0], rows[1][:-1]],
                 [rows[0], rows[1] + ["extra"]], [rows[0], []]]
        for bad in cases:
            with self.subTest(bad=bad[:1]):
                self.rewrite(bad)
                with self.assertRaises(digest.InputError):
                    digest.run(self.source, "2026-11-09", self.output, True)
                self.assertFalse(self.output.exists())

    def test_empty_file_and_bad_csv_fail(self):
        for value in (b"", b'record_id,title,author,status,pages,rating,finished_date\na,"unclosed'):
            self.source.write_bytes(value)
            result = self.cli("--apply")
            self.assertEqual(result.returncode, 2)
            self.assertFalse(self.output.exists())

    def test_missing_input_and_output_file_fail(self):
        result = self.cli("--apply", source=self.root / "missing.csv")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.output.exists())
        blocker = self.root / "file"; blocker.write_text("keep")
        for output in (blocker, blocker / "child", self.source):
            result = self.cli("--apply", output=output)
            self.assertEqual(result.returncode, 2)
        self.assertEqual(blocker.read_text(), "keep")

    def test_tampered_and_incomplete_results_are_not_reused(self):
        result = digest.run(self.source, "2026-11-09", self.output, True)
        folder = Path(result["destination"])
        for name in ("summary.json", "digest.md", "manifest.json"):
            original = (folder / name).read_bytes()
            (folder / name).write_bytes(b"tampered")
            for apply in (False, True):
                with self.assertRaisesRegex(digest.InputError, "불완전하거나 변경"):
                    digest.run(self.source, "2026-11-09", self.output, apply)
            self.assertEqual((folder / name).read_bytes(), b"tampered")
            (folder / name).write_bytes(original)
        (folder / "digest.md").unlink()
        with self.assertRaises(digest.InputError):
            digest.run(self.source, "2026-11-09", self.output, True)

    def test_extra_result_file_is_not_silently_accepted(self):
        result = digest.run(self.source, "2026-11-09", self.output, True)
        folder = Path(result["destination"])
        (folder / "unexpected").write_text("keep")
        with self.assertRaises(digest.InputError):
            digest.run(self.source, "2026-11-09", self.output, True)
        self.assertEqual((folder / "unexpected").read_text(), "keep")

    def test_mid_write_failure_cleans_staging_and_keeps_old_results(self):
        prior = digest.run(self.source, "2026-11-02", self.output, True)
        snapshot = self.snapshot(self.output)
        original = self.source.read_bytes()
        real_write = Path.write_bytes
        def fail_digest(path, value):
            if path.name == "digest.md":
                raise OSError("simulated disk full")
            return real_write(path, value)
        with patch.object(Path, "write_bytes", fail_digest):
            with self.assertRaises(OSError):
                digest.run(self.source, "2026-11-09", self.output, True)
        self.assertEqual(self.snapshot(self.output), snapshot)
        self.assertEqual(self.source.read_bytes(), original)
        self.assertFalse(list(self.output.glob(".weekly-tmp-*")))
        retry = digest.run(self.source, "2026-11-09", self.output, True)
        self.assertEqual(retry["action"], "created")
        self.assertTrue(Path(prior["destination"]).is_dir())

    @unittest.skipUnless(os.name == "nt", "Windows junction regression")
    def test_windows_junctions_are_rejected_without_new_pathlib_api(self):
        actual = self.root / "actual"
        actual.mkdir()
        linked = self.root / "linked"
        key, _, files = digest.plan(self.source, "2026-11-09")
        for name, content in files.items():
            (actual / name).write_bytes(content)
        before = self.snapshot(actual)
        source_before = self.source.read_bytes()
        for output, junction in ((linked / "child", linked), (self.output, self.output / key)):
            junction.parent.mkdir(parents=True, exist_ok=True)
            if any(char in str(junction) + str(actual) for char in '&|<>^%"\r\n'):
                self.skipTest("test paths contain command interpreter metacharacters")
            created = subprocess.run(["cmd", "/d", "/v:off", "/c", "mklink", "/J", str(junction), str(actual)],
                                     capture_output=True, text=True)
            self.assertEqual(created.returncode, 0, created.stderr)
            self.assertTrue(junction.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
            # Simulate the unavailable API while exercising a real Windows junction.
            with patch.object(Path, "is_junction", lambda self: False, create=True):
                for apply in (False, True):
                    with self.assertRaises(digest.InputError):
                        digest.run(self.source, "2026-11-09", output, apply)
            self.assertEqual(self.snapshot(actual), before)
            self.assertEqual(self.source.read_bytes(), source_before)

    def test_reparse_result_file_is_rejected_before_reuse(self):
        result = digest.run(self.source, "2026-11-09", self.output, True)
        folder = Path(result["destination"])
        before = self.snapshot(folder)
        original_lstat = Path.lstat
        def reparse_stat(path, *args, **kwargs):
            observed = original_lstat(path, *args, **kwargs)
            if path == folder / "summary.json":
                return SimpleNamespace(st_mode=observed.st_mode, st_file_attributes=1024)
            return observed
        with patch.object(Path, "lstat", reparse_stat), patch.object(digest.stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024, create=True):
            with self.assertRaises(digest.InputError):
                digest.run(self.source, "2026-11-09", self.output, True)
        self.assertEqual(self.snapshot(folder), before)


if __name__ == "__main__":
    unittest.main()
