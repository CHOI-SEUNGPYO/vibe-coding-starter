"""Integrity checks must reject incomplete, changed, and escaping skill records."""

import hashlib
import importlib.util
import copy
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
        (self.root / "skills.lock.json").write_text(json.dumps({"schema_version": 2, "skills": [self.entry]}), encoding="utf-8")

    def external(self, origin="vendored", license_name="MIT"):
        revision = "a" * 40
        self.entry.update(origin=origin, repository="community-owner/skill-library", source_path="skills/example",
                          revision=revision, license=license_name, license_file="LICENSE.txt",
                          source_url=f"https://github.com/community-owner/skill-library/tree/{revision}/skills/example",
                          license_url=f"https://github.com/community-owner/skill-library/blob/{revision}/LICENSE")
        if origin == "adapted":
            self.entry.update(adaptations={"SKILL.md": "Use the project's local command instead of a global path."},
                              upstream_sha256={"SKILL.md": "b" * 64})
        self.write_lock()

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

    def test_community_mit_and_apache_sources_accepted(self):
        for license_name in ("MIT", "Apache-2.0"):
            with self.subTest(license=license_name):
                self.external(license_name=license_name)
                self.assertIn("example", integrity.validate_sources(self.root))

    def test_license_can_be_preserved_in_upstream_readme(self):
        self.external()
        (self.skill / "LICENSE.txt").rename(self.skill / "UPSTREAM_README.md")
        self.entry["files"]["UPSTREAM_README.md"] = self.entry["files"].pop("LICENSE.txt")
        self.entry["license_file"] = "UPSTREAM_README.md"
        self.entry["license_url"] = self.entry["license_url"].removesuffix("LICENSE") + "README.md"
        self.write_lock()
        self.assertIn("example", integrity.validate_sources(self.root))

    def test_adapted_source_accepted_and_installed_bytes_checked(self):
        self.external(origin="adapted")
        entries = integrity.validate_sources(self.root)
        self.install()
        self.assertEqual(integrity.validate_installed(self.root, self.root, entries), 1)
        (self.root / ".agents/skills/example/SKILL.md").write_text("unrecorded edit", encoding="utf-8")
        with self.assertRaisesRegex(integrity.IntegrityError, "변경"):
            integrity.validate_installed(self.root, self.root, entries)

    def test_external_repository_rejects_unsafe_names(self):
        self.external()
        for value in ("owner", "owner/repo/extra", "owner@github.com/repo", "owner/repo?x", "owner/..", "../repo", "owner/repo#tag", "-owner/repo", "owner/repo%2fsecret"):
            with self.subTest(repository=value):
                self.entry["repository"] = value
                self.write_lock()
                with self.assertRaises(integrity.IntegrityError):
                    integrity.validate_sources(self.root)

    def test_external_paths_reject_traversal_and_url_markers(self):
        self.external()
        original = copy.deepcopy(self.entry)
        for field in ("source_path", "license_file"):
            for value in ("", ".", "../outside", "/absolute", "a/../b", "a\\b", "a\0b", "https://elsewhere/file"):
                with self.subTest(field=field, value=value):
                    self.entry = copy.deepcopy(original)
                    self.entry[field] = value
                    self.write_lock()
                    with self.assertRaises(integrity.IntegrityError):
                        integrity.validate_sources(self.root)
        for value in ("skills/example?raw=1", "skills/example#fragment", "skills/%2e%2e/secret", "skills/a b"):
            with self.subTest(source_path=value):
                self.entry = copy.deepcopy(original)
                self.entry["source_path"] = value
                self.entry["source_url"] = f"https://github.com/{self.entry['repository']}/tree/{self.entry['revision']}/{value}"
                self.write_lock()
                with self.assertRaises(integrity.IntegrityError):
                    integrity.validate_sources(self.root)

    def test_external_source_url_must_match_every_pinned_component(self):
        self.external()
        original = self.entry["source_url"]
        for value in (original.replace("community-owner/", "different-owner/"),
                      original.replace("a" * 40, "c" * 40), original.replace("/tree/", "/blob/"),
                      original + "?raw=1", original + "#fragment", original + "/extra",
                      original.replace("github.com", "github.com@evil.example")):
            with self.subTest(source_url=value):
                self.entry["source_url"] = value
                self.write_lock()
                with self.assertRaisesRegex(integrity.IntegrityError, "출처 URL"):
                    integrity.validate_sources(self.root)

    def test_license_url_must_match_repository_commit_and_safe_path(self):
        self.external()
        original = self.entry["license_url"]
        for value in (original.replace("community-owner/", "different-owner/"),
                      original.replace("a" * 40, "c" * 40), original.replace("/blob/", "/tree/"),
                      original.replace("github.com", "github.com@evil.example"), original + "?raw=1",
                      original + "#fragment", original.removesuffix("LICENSE") + "../LICENSE",
                      original.removesuffix("LICENSE") + "%2e%2e/LICENSE", original.removesuffix("LICENSE")):
            with self.subTest(license_url=value):
                self.entry["license_url"] = value
                self.write_lock()
                with self.assertRaises(integrity.IntegrityError):
                    integrity.validate_sources(self.root)

    def test_declared_license_must_be_listed_and_present(self):
        self.external()
        self.entry["license_file"] = "UPSTREAM_README.md"
        self.write_lock()
        with self.assertRaisesRegex(integrity.IntegrityError, "라이선스 파일"):
            integrity.validate_sources(self.root)
        self.entry["files"]["UPSTREAM_README.md"] = "a" * 64
        self.write_lock()
        with self.assertRaisesRegex(integrity.IntegrityError, "누락"):
            integrity.validate_sources(self.root)

    def test_external_unsupported_license_rejected(self):
        self.external(license_name="Unspecified")
        with self.assertRaisesRegex(integrity.IntegrityError, "라이선스"):
            integrity.validate_sources(self.root)

    def test_adaptation_requires_nonempty_reasons_and_known_files(self):
        self.external(origin="adapted")
        original = copy.deepcopy(self.entry)
        for value in ({}, None, {"SKILL.md": ""}, {"SKILL.md": "  "}, {"SKILL.md": 123}, {"missing.md": "Changed command"}):
            with self.subTest(adaptations=value):
                self.entry = copy.deepcopy(original)
                self.entry["adaptations"] = value
                if isinstance(value, dict):
                    self.entry["upstream_sha256"] = {key: "b" * 64 for key in value}
                self.write_lock()
                with self.assertRaises(integrity.IntegrityError):
                    integrity.validate_sources(self.root)

    def test_adaptation_requires_original_hashes_for_exactly_changed_files(self):
        self.external(origin="adapted")
        for value in (None, {}, {"SKILL.md": "bad"}, {"SKILL.md": "b" * 64, "LICENSE.txt": "c" * 64},
                      {"LICENSE.txt": "b" * 64}, {"SKILL.md": self.entry["files"]["SKILL.md"]}):
            with self.subTest(upstream_sha256=value):
                self.entry["upstream_sha256"] = value
                self.write_lock()
                with self.assertRaises(integrity.IntegrityError):
                    integrity.validate_sources(self.root)

    def test_raw_vendored_cannot_carry_adaptation_fields(self):
        self.external()
        for field in ("adaptations", "upstream_sha256"):
            self.entry[field] = {}
            self.write_lock()
            with self.assertRaisesRegex(integrity.IntegrityError, "adapted"):
                integrity.validate_sources(self.root)
            del self.entry[field]

    def test_old_schema_requires_explicit_migration(self):
        (self.root / "skills.lock.json").write_text(json.dumps({"schema_version": 1, "skills": [self.entry]}), encoding="utf-8")
        with self.assertRaisesRegex(integrity.IntegrityError, "schema_version 2"):
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
