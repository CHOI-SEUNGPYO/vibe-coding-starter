"""Setup restores the selected environment and verifies only its enabled servers."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("vibe_setup", Path(__file__).parents[1] / "scripts/setup.py")
setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(setup)


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.root_patch = patch.object(setup, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        (self.root / "profiles").mkdir()
        for name, servers in {
            "minimal": [], "web": ["openai-docs", "context7", "playwright"],
            "api": ["openai-docs", "context7"], "data": ["context7"],
            "automation": ["playwright"],
        }.items():
            (self.root / "profiles" / f"{name}.json").write_text(json.dumps({"mcp": servers}), encoding="utf-8")

    def state(self, profile, servers):
        (self.root / ".vibe").mkdir(exist_ok=True)
        (self.root / ".vibe/profile.json").write_text(json.dumps({"profile": profile, "mcp": servers}), encoding="utf-8")

    def run_setup(self, args, fail_mode=None, node=True):
        commands = []

        def run(command, **kwargs):
            commands.append(command)
            if "--version" in command:
                return subprocess.CompletedProcess(command, 0, stdout="v22.0.0\n")
            code = 7 if fail_mode and command[-1] == fail_mode else 0
            return subprocess.CompletedProcess(command, code)

        output = io.StringIO()
        with patch.object(setup.shutil, "which", side_effect=lambda name: name if node else None), \
                patch.object(setup.subprocess, "run", side_effect=run), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            status = setup.main(args)
        return status, commands, output.getvalue()

    def test_no_argument_restores_active_profile_and_additional_mcp(self):
        self.state("api", ["openai-docs", "github"])
        status, commands, output = self.run_setup([])
        self.assertEqual(status, 0)
        init = next(command for command in commands if "init" in command)
        self.assertIn("api", init)
        self.assertIn("--update", init)
        self.assertIn("github", init)
        self.assertIn("context7", init)
        checks = [command[-1] for command in commands if "scripts/check_mcp.mjs" in command]
        self.assertEqual(checks, ["context7", "docs"])
        self.assertIn("github", output)
        self.assertIn("계정 인증을 검사하지 않습니다", output)

    def test_explicit_profile_switch_uses_new_defaults(self):
        self.state("web", ["openai-docs", "context7", "playwright", "github"])
        status, commands, _ = self.run_setup(["--profile", "data"])
        self.assertEqual(status, 0)
        init = next(command for command in commands if "init" in command)
        self.assertNotIn("github", init)
        self.assertNotIn("playwright", init)
        self.assertEqual([command[-1] for command in commands if "scripts/check_mcp.mjs" in command], ["context7"])

    def test_browser_only_does_not_require_documentation_servers(self):
        status, commands, _ = self.run_setup(["--profile", "automation"])
        self.assertEqual(status, 0)
        self.assertTrue(any("ci" in command for command in commands))
        self.assertEqual([command[-1] for command in commands if "scripts/check_mcp.mjs" in command], ["browser"])

    def test_minimal_needs_no_node_or_network_checks(self):
        status, commands, _ = self.run_setup(["--profile", "minimal"], node=False)
        self.assertEqual(status, 0)
        self.assertFalse(any("scripts/check_mcp.mjs" in command or "ci" in command for command in commands))

    def test_failed_context7_is_not_reported_as_complete(self):
        status, commands, output = self.run_setup(["--profile", "api"], fail_mode="context7")
        self.assertEqual(status, 7)
        self.assertNotIn("환경 준비 완료", output)
        self.assertFalse(any(command[-1] == "docs" for command in commands))

    def test_invalid_stored_profile_is_rejected_before_execution(self):
        self.state("../../outside", [])
        with self.assertRaisesRegex(ValueError, "저장된 프로필"):
            self.run_setup([])


if __name__ == "__main__":
    unittest.main()
