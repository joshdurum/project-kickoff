"""Unit tests for scaffold_project.py and validate_kickoff.py."""

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from eval_live import _grade_kickoff_workspace  # noqa: E402
from scaffold_project import scaffold_project  # noqa: E402
from validate_kickoff import validate_kickoff_dir  # noqa: E402


class TestKickoffScaffoldAndValidation(unittest.TestCase):
    def test_skip_tier_writes_zero_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            res = scaffold_project(Path(tmp), name="tiny-fix", tier="SKIP")
            self.assertEqual(res["files_created"], [])
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_light_tier_scaffolds_minimal_set_and_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            res = scaffold_project(
                tmp_path,
                name="small-feature",
                tier="LIGHT",
                goal="Add export command",
                about_me="CLI user on macOS",
                mvp_slice="Export JSON to stdout",
            )
            self.assertEqual(sorted(res["files_created"]), ["AGENTS.md", "CLAUDE.md", "plan.md"])
            report = validate_kickoff_dir(tmp_path, tier="LIGHT")
            self.assertTrue(report["all_passed"], msg=str(report))

    def test_full_tier_scaffolds_all_docs_and_passes_all_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            res = scaffold_project(
                tmp_path,
                name="adhd-capture",
                tier="FULL",
                goal="Capture -> Organize -> Ask Later on phone",
                about_me="Beginner on Mac Studio + iPhone",
                mvp_slice="1-tap capture + SQLite inbox + ask query",
            )
            self.assertEqual(
                sorted(res["files_created"]),
                ["AGENTS.md", "CLAUDE.md", "decisions.md", "plan.md", "research.md"],
            )
            report = validate_kickoff_dir(tmp_path, tier="FULL")
            self.assertTrue(report["all_passed"], msg=str(report))
            grade = _grade_kickoff_workspace(tmp_path)
            self.assertTrue(grade["all_passed"], msg=str(grade))

    def test_validator_catches_bloated_agents_and_kill_leak_in_mvp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            scaffold_project(tmp_path, name="bad-scope", tier="FULL", mvp_slice="Core capture")
            (tmp_path / "AGENTS.md").write_text("# Bloated\n" * 160, encoding="utf-8")
            (tmp_path / "plan.md").write_text(
                "# Plan\n\n## MVP v0.1\n- Calendar sync [Effort: L | Impact: Low]\n",
                encoding="utf-8",
            )
            report = validate_kickoff_dir(tmp_path, tier="FULL")
            self.assertFalse(report["all_passed"])
            self.assertFalse(report["checks"]["K1_lean_agents_index"]["passed"])
            self.assertFalse(report["checks"]["K5_no_effort_l_low_impact_in_mvp"]["passed"])
            grade = _grade_kickoff_workspace(tmp_path)
            self.assertFalse(grade["checks"]["K7_scope_creep_excluded_from_mvp"])


if __name__ == "__main__":
    unittest.main()
