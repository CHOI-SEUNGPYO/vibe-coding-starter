"""Integrity checks must reject incomplete, changed, and escaping skill records."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("check_integrity", Path(__file__).parents[1] / "scripts/check_integrity.py")
integrity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(integrity)


class SkillIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.skill = self.root / "skills/example"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("---\nname: example\ndescription: Example\n---\n", encoding="utf-8")
        (self.skill / "LICENSE.txt").write_text("MIT", encoding="utf-8")
        files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.skill.iterdir()}
        self.entry = {"id": "example", "origin": "first-party", "revision": None,
                      "source_url": "https://github.com/example/starter/tree/main/skills/example",
                      "license": "MIT", "files": files}
        self.write_lock()

    def write_lock(self):
        (self.root / "skills.lock.json").write_text(json.dumps({"schema_version": 1, "skills": [self.entry]}), encoding="utf-8")

    def install(self):
        (self.root / "profiles").mkdir()
        (self.root / "profiles/minimal.json").write_text(json.dumps({"skills": ["example"]}), encoding="utf-8")
        (self.root / ".vibe").mkdir()
        (self.root / ".vibe/profile.json").write_text(json.dumps({"profile": "minimal"}), encoding="utf-8")
        shutil.copytree(self.skill, self.root / ".agents/skills/example")

    def test_clean_source_only_and_installed(self):
        entries = integrity.validate_sources(self.root)
        self.assertEqual(integrity.validate_installed(self.root, self.root, entries), 0)
        self.install()
        self.assertEqual(integrity.validate_installed(self.root, self.root, entries), 1)

    def test_cli_output_is_utf8_with_legacy_stream_encoding(self):
        script = self.root / "scripts/check_integrity.py"
        script.parent.mkdir()
        shutil.copyfile(SPEC.origin, script)
        for encoding in ("ascii", "cp1252"):
            with self.subTest(encoding=encoding):
                result = subprocess.run(
                    [sys.executable, str(script)],
                    env={**os.environ, "PYTHONIOENCODING": encoding},
                    capture_output=True, text=True, encoding="utf-8", check=False)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("원본 스킬 1개", result.stdout)

    def test_modified_source(self):
        (self.skill / "SKILL.md").write_text("modified", encoding="utf-8")
        with self.assertRaisesRegex(integrity.IntegrityError, "변경"):
            integrity.validate_sources(self.root)

    def test_missing_source(self):
        (self.skill / "LICENSE.txt").unlink()
        with self.assertRaisesRegex(integrity.IntegrityError, "누락"):
            integrity.validate_sources(self.root)

    def test_unregistered_source_file(self):
        (self.skill / "unexpected.py").write_text("print('unexpected')", encoding="utf-8")
        with self.assertRaisesRegex(integrity.IntegrityError, "미등록"):
            integrity.validate_sources(self.root)

    def test_unregistered_skill(self):
        (self.root / "skills/unregistered").mkdir()
        with self.assertRaisesRegex(integrity.IntegrityError, "스킬 목록"):
            integrity.validate_sources(self.root)

    def test_lock_path_escape(self):
        self.entry["files"]["../outside.txt"] = "a" * 64
        self.write_lock()
        with self.assertRaises(integrity.IntegrityError):
            integrity.validate_sources(self.root)

    def test_floating_external_revision(self):
        self.entry.update(origin="vendored", revision="main", license="Apache-2.0")
        self.write_lock()
        with self.assertRaisesRegex(integrity.IntegrityError, "커밋 SHA"):
            integrity.validate_sources(self.root)

    def test_unexpected_external_source(self):
        self.entry.update(origin="vendored", revision="a" * 40, license="Apache-2.0")
        self.write_lock()
        with self.assertRaisesRegex(integrity.IntegrityError, "출처"):
            integrity.validate_sources(self.root)

    def test_tampered_installed_copy(self):
        entries = integrity.validate_sources(self.root)
        self.install()
        (self.root / ".agents/skills/example/SKILL.md").write_text("tampered", encoding="utf-8")
        with self.assertRaisesRegex(integrity.IntegrityError, "설치본"):
            integrity.validate_installed(self.root, self.root, entries)

    def test_missing_and_extra_installed_skill(self):
        entries = integrity.validate_sources(self.root)
        self.install()
        (self.root / ".agents/skills/unexpected").mkdir()
        with self.assertRaisesRegex(integrity.IntegrityError, "스킬 목록"):
            integrity.validate_installed(self.root, self.root, entries)
        shutil.rmtree(self.root / ".agents/skills")
        with self.assertRaisesRegex(integrity.IntegrityError, "스킬 목록"):
            integrity.validate_installed(self.root, self.root, entries)

    def test_installation_without_state(self):
        entries = integrity.validate_sources(self.root)
        self.install()
        (self.root / ".vibe/profile.json").unlink()
        with self.assertRaisesRegex(integrity.IntegrityError, "profile.json"):
            integrity.validate_installed(self.root, self.root, entries)

    def test_skill_symlink_is_rejected(self):
        other = self.root / "outside.txt"
        other.write_text("outside", encoding="utf-8")
        link = self.skill / "linked.txt"
        try:
            link.symlink_to(other)
        except (OSError, NotImplementedError):
            self.skipTest("This environment does not allow creating symlinks")
        with self.assertRaisesRegex(integrity.IntegrityError, "링크"):
            integrity.validate_sources(self.root)


if __name__ == "__main__":
    unittest.main()
