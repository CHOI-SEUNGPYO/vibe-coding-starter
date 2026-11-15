"""A vendored design tool must return relevant data without changing its bundle."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CommunityRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.skill = Path(self.temporary.name).resolve() / "ui-ux-pro-max"
        shutil.copytree(ROOT / "skills/ui-ux-pro-max", self.skill)

    def search(self, query):
        environment = dict(os.environ)
        environment.pop("PYTHONDONTWRITEBYTECODE", None)
        environment.pop("PYTHONPYCACHEPREFIX", None)
        environment["PYTHONIOENCODING"] = "cp1252"
        result = subprocess.run(
            [sys.executable, str(self.skill / "scripts/search.py"), query, "--domain", "ux", "--json"],
            env=environment, cwd=self.skill.parent, capture_output=True,
            text=True, encoding="utf-8", timeout=30, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def hashes(self):
        return {p.relative_to(self.skill).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.skill.rglob("*") if p.is_file()}

    def test_focus_search_returns_guidance_without_mutating_bundle(self):
        before = self.hashes()
        result = self.search("keyboard focus modal")
        self.assertGreater(result["count"], 0)
        self.assertTrue(any("focus" in row.get("Issue", "").lower() for row in result["results"]))
        self.assertEqual(self.hashes(), before, "A normal search must not create untracked files inside a skill")

    def test_unmatched_query_does_not_invent_results(self):
        result = self.search("zzzxqvnonexistent74291")
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["results"], [])


if __name__ == "__main__":
    unittest.main()
