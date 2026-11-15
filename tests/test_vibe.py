"""Behavioral tests for safe installation and truthful verification."""

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("vibe", Path(__file__).resolve().parents[1] / "scripts" / "vibe.py")
vibe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vibe)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        # macOS's standard /var temp prefix is itself an OS symlink. Resolve
        # that baseline before constructing the deliberate link test cases.
        self.temp_root = Path(self.temporary.name).resolve()
        self.root = self.temp_root / "kit"
        self.target = self.temp_root / "project"
        self.root.mkdir()
        self.write(self.root / "templates/AGENTS.md", "# Project guidance\n")
        self.write(self.root / "config/codex.base.toml", 'sandbox_mode = "workspace-write"\n')
        self.write(self.root / "config/agents/reviewer.toml", 'name = "reviewer"\n')
        self.write(self.root / "mcp/docs.toml", '[mcp_servers.docs]\nurl = "https://example.com/mcp"\n')
        self.write(self.root / "mcp/browser.toml", '[mcp_servers.browser]\ncommand = "node"\n')
        for name in ("shared", "web-only"):
            self.write(self.root / f"skills/{name}/SKILL.md", f"---\nname: {name}\ndescription: A focused test skill.\n---\nDo work.\n")
            self.write(self.root / f"skills/{name}/references/usage.md", "Reference.\n")
        for name in ("minimal", "web", "api", "data", "automation"):
            self.write_json(self.root / f"profiles/{name}.json", {
                "name": name, "description": "Test profile",
                "skills": ["shared", "web-only"] if name == "web" else ["shared"],
                "mcp": [] if name == "minimal" else ["docs"], "checks": [],
            })
        self.root_patch = patch.object(vibe, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.addCleanup(self.temporary.cleanup)

    def write(self, path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_json(self, path, value):
        self.write(path, json.dumps(value))

    def run_cli(self, *arguments):
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            code = vibe.main([*arguments, "--target", str(self.target)])
        return code, output.getvalue()

    def install(self, profile="web", *extra):
        code, output = self.run_cli("init", "--profile", profile, *extra)
        self.assertEqual(code, 0, output)
        return output

    def snapshot(self):
        return {p.relative_to(self.target).as_posix(): p.read_bytes() for p in self.target.rglob("*") if p.is_file()}

    def test_all_profiles_install_and_default_mcp_matches_selection(self):
        for profile in ("minimal", "web", "api", "data", "automation"):
            with self.subTest(profile=profile):
                self.target = self.temp_root / profile
                self.install(profile)
                state = json.loads((self.target / ".vibe/profile.json").read_text())
                self.assertEqual(state["profile"], profile)
                self.assertEqual(state["mcp"], [] if profile == "minimal" else ["docs"])
                self.assertTrue((self.target / ".agents/skills/shared/references/usage.md").is_file())
                self.assertTrue((self.target / ".codex/agents/reviewer.toml").is_file())
                self.assertEqual(self.run_cli("check")[0], 0)

    def test_mcp_opt_out_and_explicit_addition(self):
        self.install("web", "--no-mcp", "--mcp", "browser")
        config = vibe.inspect_config(self.target)
        self.assertEqual(list(config["mcp_servers"]), ["browser"])

    def test_init_and_error_output_are_utf8_with_legacy_stream_encoding(self):
        script = self.root / "scripts/vibe.py"
        script.parent.mkdir()
        shutil.copyfile(SPEC.origin, script)
        for encoding in ("ascii", "cp1252"):
            with self.subTest(encoding=encoding):
                environment = {**os.environ, "PYTHONIOENCODING": encoding}
                result = subprocess.run(
                    [sys.executable, str(script), "init", "--profile", "minimal", "--target", str(self.target)],
                    env=environment, capture_output=True, text=True, encoding="utf-8", check=False)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("설치", result.stdout)
                self.assertTrue((self.target / ".vibe/profile.json").is_file())
                failed = subprocess.run(
                    [sys.executable, str(script), "init", "--profile", "../invalid", "--target", str(self.target)],
                    env=environment, capture_output=True, text=True, encoding="utf-8", check=False)
                self.assertEqual(failed.returncode, 1)
                self.assertIn("오류", failed.stderr)
                self.assertNotIn("Traceback", failed.stderr)

    def test_setup_help_is_utf8_with_legacy_stream_encoding(self):
        script = Path(__file__).resolve().parents[1] / "scripts/setup.py"
        for encoding in ("ascii", "cp1252"):
            with self.subTest(encoding=encoding):
                result = subprocess.run(
                    [sys.executable, str(script), "--help"],
                    env={**os.environ, "PYTHONIOENCODING": encoding},
                    capture_output=True, text=True, encoding="utf-8", check=False)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("환경 선택", result.stdout)

    def test_dry_run_creates_nothing(self):
        self.install("web", "--dry-run")
        self.assertFalse(self.target.exists())

    def test_idempotency_and_preservation_of_project_brief(self):
        self.install()
        self.write_json(self.target / ".vibe/project.json", {"purpose": "User content", "checks": []})
        before = self.snapshot()
        self.install()
        self.assertEqual(before, self.snapshot())

    def test_existing_agents_conflict_makes_zero_changes(self):
        self.write(self.target / "AGENTS.md", "User instructions")
        before = self.snapshot()
        code, output = self.run_cli("init", "--profile", "web")
        self.assertEqual(code, 1)
        self.assertIn("AGENTS.md", output)
        self.assertEqual(before, self.snapshot())

    def test_late_path_conflict_makes_zero_changes(self):
        self.write(self.target / ".vibe", "Existing file instead of directory")
        before = self.snapshot()
        self.assertEqual(self.run_cli("init", "--profile", "web")[0], 1)
        self.assertEqual(before, self.snapshot())

    def test_edited_managed_file_is_never_overwritten(self):
        self.install()
        self.write(self.target / ".codex/config.toml", 'sandbox_mode = "read-only"\n')
        before = self.snapshot()
        code, output = self.run_cli("init", "--profile", "minimal", "--update")
        self.assertEqual(code, 1)
        self.assertIn("수정", output)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(self.run_cli("check")[0], 1)

    def test_update_switches_profile_and_removes_obsolete_skills_and_mcp(self):
        self.install()
        self.assertEqual(self.run_cli("init", "--profile", "minimal")[0], 1)
        self.install("minimal", "--update")
        self.assertFalse((self.target / ".agents/skills/web-only/SKILL.md").exists())
        self.assertFalse((self.target / ".agents/skills/web-only").exists())
        self.assertNotIn("mcp_servers", vibe.inspect_config(self.target))
        self.assertEqual(self.run_cli("check")[0], 0)

    def test_update_preserves_unmanaged_files_in_obsolete_skill_folder(self):
        self.install()
        path = self.target / ".agents/skills/web-only/user-notes.txt"
        self.write(path, "User content")
        self.install("minimal", "--update")
        self.assertEqual(path.read_text(), "User content")

    def test_generated_config_has_one_final_newline(self):
        self.install()
        config = (self.target / ".codex/config.toml").read_bytes()
        self.assertTrue(config.endswith(b"\n"))
        self.assertFalse(config.endswith(b"\n\n"))

    def test_updated_source_requires_update_then_applies(self):
        self.install()
        self.write(self.root / "templates/AGENTS.md", "# New guidance\n")
        before = self.snapshot()
        self.assertEqual(self.run_cli("init", "--profile", "web")[0], 1)
        self.assertEqual(before, self.snapshot())
        self.install("web", "--update")
        self.assertEqual((self.target / "AGENTS.md").read_text(), "# New guidance\n")

    def test_invalid_profile_and_mcp_paths_rejected_before_writes(self):
        for extra in (("--profile", "../escape"), ("--profile", "web", "--mcp", "../escape")):
            self.assertEqual(self.run_cli("init", *extra)[0], 1)
            self.assertFalse(self.target.exists())

    def test_invalid_profile_schema_rejected_before_writes(self):
        self.write_json(self.root / "profiles/web.json", {"name": "web", "description": "Bad", "skills": "shared", "mcp": []})
        self.assertEqual(self.run_cli("init", "--profile", "web")[0], 1)
        self.assertFalse(self.target.exists())

    def test_malformed_toml_rejected_before_writes(self):
        self.write(self.root / "mcp/docs.toml", "[broken\n")
        self.assertEqual(self.run_cli("init", "--profile", "web")[0], 1)
        self.assertFalse(self.target.exists())

    def test_check_rejects_conflicting_default_mcp_combination(self):
        path = self.root / "profiles/web.json"
        profile = json.loads(path.read_text())
        profile["mcp"] = ["docs", "browser"]
        self.write_json(path, profile)
        self.write(self.root / "mcp/browser.toml", '[mcp_servers.docs]\ncommand = "node"\n')
        code, output = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("TOML", output)

    def test_corrupt_state_cannot_delete_project_source(self):
        self.install()
        self.write(self.target / "app.py", "user code")
        path = self.target / ".vibe/profile.json"
        state = json.loads(path.read_text())
        state["files"]["app.py"] = vibe.digest(b"user code")
        self.write_json(path, state)
        before = self.snapshot()
        self.assertEqual(self.run_cli("init", "--profile", "minimal", "--update")[0], 1)
        self.assertEqual(before, self.snapshot())

    def test_symbolic_link_target_refused(self):
        actual = self.temp_root / "actual"
        actual.mkdir()
        try:
            self.target.symlink_to(actual, target_is_directory=True)
        except OSError:
            self.skipTest("OS does not permit test symlinks")
        self.assertEqual(self.run_cli("init", "--profile", "web")[0], 1)
        self.assertEqual(list(actual.iterdir()), [])

    @unittest.skipUnless(os.name == "nt", "Windows junction behavior")
    def test_dangling_junction_refused_before_any_install_writes(self):
        self.target.mkdir()
        actual = self.temp_root / "junction-destination"
        actual.mkdir()
        junction = self.target / ".agents"
        result = subprocess.run(["cmd", "/d", "/c", "mklink", "/J", str(junction), str(actual)],
                                capture_output=True, check=False)
        if result.returncode:
            self.skipTest("OS does not permit test junctions")
        try:
            actual.rmdir()
            self.assertFalse(junction.exists())
            self.assertEqual(self.run_cli("init", "--profile", "web")[0], 1)
            self.assertFalse((self.target / "AGENTS.md").exists())
            self.assertFalse((self.target / ".codex").exists())
        finally:
            junction.rmdir()

    def test_no_checks_is_not_reported_as_verified(self):
        self.install()
        self.assertEqual(self.run_cli("verify")[0], 1)
        self.assertEqual(self.run_cli("verify", "--allow-empty")[0], 0)

    def test_verify_runs_real_command_and_propagates_failure(self):
        self.install()
        self.write_json(self.target / ".vibe/project.json", {"checks": [
            {"name": "pass", "command": ["{python}", "-c", "from pathlib import Path; Path('verified.txt').write_text('ok')"]},
            {"name": "fail", "command": [sys.executable, "-c", "raise SystemExit(7)"]},
        ]})
        code, output = self.run_cli("verify")
        self.assertEqual(code, 1)
        self.assertEqual((self.target / "verified.txt").read_text(), "ok")
        self.assertIn("종료 코드 7", output)

    def test_verify_timeout_and_missing_command_fail(self):
        self.install()
        self.write_json(self.target / ".vibe/project.json", {"checks": [
            {"name": "timeout", "command": ["{python}", "-c", "import time; time.sleep(2)"], "timeout_seconds": 0.05},
            {"name": "missing", "command": ["vibe-command-that-does-not-exist"]},
        ]})
        code, output = self.run_cli("verify")
        self.assertEqual(code, 1)
        self.assertIn("제한 시간", output)

    def test_verify_timeout_stops_descendant_process(self):
        self.install()
        child = "from pathlib import Path; import time; Path('child-started').touch(); time.sleep(2); Path('child-survived').touch()"
        parent = f"import subprocess, sys, time; subprocess.Popen([sys.executable, '-c', {child!r}]); time.sleep(10)"
        self.write_json(self.target / ".vibe/project.json", {"checks": [
            {"name": "worker tree", "command": ["{python}", "-c", parent], "timeout_seconds": 0.8},
        ]})
        code, output = self.run_cli("verify")
        self.assertEqual(code, 1, output)
        self.assertTrue((self.target / "child-started").exists(), "worker did not start in time")
        time.sleep(2.2)
        self.assertFalse((self.target / "child-survived").exists(), "timed-out worker kept running")

    @unittest.skipUnless(shutil.which("npm"), "npm is not installed")
    def test_verify_resolves_and_runs_npm_command(self):
        self.install()
        self.write_json(self.target / ".vibe/project.json", {"checks": [
            {"name": "npm", "command": ["npm", "--version"]},
        ]})
        code, output = self.run_cli("verify")
        self.assertEqual(code, 0, output)

    @unittest.skipUnless(os.name == "nt" and shutil.which("npm"), "Windows npm wrapper behavior")
    def test_batch_shell_syntax_rejected_before_execution(self):
        self.install()
        self.write_json(self.target / ".vibe/project.json", {"checks": [
            {"name": "must not run", "command": ["{python}", "-c", "from pathlib import Path; Path('should-not-exist').touch()"]},
            {"name": "unsafe batch argument", "command": ["npm", "--version", "&echo unexpected"]},
        ]})
        code, output = self.run_cli("verify")
        self.assertEqual(code, 1)
        self.assertIn("특수문자", output)
        self.assertFalse((self.target / "should-not-exist").exists())

    def test_all_check_schemas_validated_before_execution(self):
        self.install()
        self.write_json(self.target / ".vibe/project.json", {"checks": [
            {"name": "must not run", "command": ["{python}", "-c", "from pathlib import Path; Path('should-not-exist').touch()"]},
            {"name": "escape", "command": ["{python}", "-V"], "cwd": "../"},
        ]})
        self.assertEqual(self.run_cli("verify")[0], 1)
        self.assertFalse((self.target / "should-not-exist").exists())

    def test_doctor_checks_env_presence_without_printing_secrets(self):
        self.write(self.root / "mcp/docs.toml", '[mcp_servers.docs]\nurl = "https://example.com/mcp"\nbearer_token_env_var = "VIBE_TEST_TOKEN"\n')
        self.install()
        with patch.dict("os.environ", {"VIBE_TEST_TOKEN": "super-secret-value"}):
            code, output = self.run_cli("doctor")
        self.assertNotIn("super-secret-value", output)
        self.assertEqual(code, 0, output)
        with patch.dict("os.environ", {}, clear=True):
            code, output = self.run_cli("doctor")
        self.assertEqual(code, 1)
        self.assertIn("VIBE_TEST_TOKEN", output)


if __name__ == "__main__":
    unittest.main()
