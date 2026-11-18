#!/usr/bin/env python3
"""Validate project kickoff docs against strict True/False quality and scope rules."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

EFFORT_IMPACT_RE = re.compile(r"Effort\s*:\s*[SML].*?Impact\s*:\s*(Low|Med|Medium|High)", re.IGNORECASE)
KILL_LEAK_RE = re.compile(r"Effort\s*:\s*L\b.*?Impact\s*:\s*Low\b", re.IGNORECASE)


def _extract_mvp_section(plan_text: str) -> str:
    match = re.search(r"##\s*MVP[^\n]*\n(.*?)(?=\n##\s|\Z)", plan_text, re.DOTALL | re.IGNORECASE)
    return match.group(1) if match else ""


def validate_kickoff_dir(project_dir: Path, tier: str = "FULL") -> dict[str, Any]:
    """Run True/False kickoff checks (K1-K6) on a planned project directory."""
    tier_norm = tier.strip().upper()
    if tier_norm == "SKIP":
        return {"all_passed": True, "tier": "SKIP", "checks": {}}

    agents_path = project_dir / "AGENTS.md"
    claude_path = project_dir / "CLAUDE.md"
    plan_path = project_dir / "plan.md"
    research_path = project_dir / "research.md"
    decisions_path = project_dir / "decisions.md"

    agents_text = agents_path.read_text(encoding="utf-8") if agents_path.is_file() else ""
    claude_text = claude_path.read_text(encoding="utf-8") if claude_path.is_file() else ""
    plan_text = plan_path.read_text(encoding="utf-8") if plan_path.is_file() else ""
    research_text = research_path.read_text(encoding="utf-8") if research_path.is_file() else ""
    decisions_text = decisions_path.read_text(encoding="utf-8") if decisions_path.is_file() else ""

    agents_lines = len(agents_text.splitlines()) if agents_text else 0
    k1 = agents_path.is_file() and 1 <= agents_lines <= 150
    k2 = claude_path.is_file() and "@AGENTS.md" in claude_text
    k3 = (
        bool(re.search(r"##\s*About Me", agents_text, re.IGNORECASE))
        and bool(re.search(r"(2\s*[-–to]+\s*3|batch)", agents_text, re.IGNORECASE))
    )

    mvp_section = _extract_mvp_section(plan_text)
    k4 = (
        plan_path.is_file()
        and bool(mvp_section.strip())
        and bool(re.search(r"batch\s*1|\bBatch\b", plan_text, re.IGNORECASE))
        and bool(EFFORT_IMPACT_RE.search(plan_text))
    )
    k5 = plan_path.is_file() and not bool(KILL_LEAK_RE.search(mvp_section))

    checks: dict[str, dict[str, Any]] = {
        "K1_lean_agents_index": {"passed": k1, "detail": f"exists={agents_path.is_file()}, lines={agents_lines}/150"},
        "K2_claude_imports_agents": {"passed": k2, "detail": f"CLAUDE.md has @AGENTS.md={k2}"},
        "K3_about_me_and_batch_rule": {"passed": k3, "detail": "About Me + batch rule present in AGENTS.md"},
        "K4_plan_mvp_batches_and_tags": {"passed": k4, "detail": "plan.md has MVP, Batches, and Effort/Impact tags"},
        "K5_no_effort_l_low_impact_in_mvp": {"passed": k5, "detail": "MVP v0.1 free of Effort:L/Impact:Low items"},
    }

    if tier_norm == "FULL":
        has_research = (
            research_path.is_file()
            and "|" in research_text
            and bool(re.search(r"(verdict|build vs)", research_text, re.IGNORECASE))
        )
        has_decisions = (
            decisions_path.is_file()
            and bool(re.search(r"##\s*Answered Questions", decisions_text, re.IGNORECASE))
            and bool(re.search(r"Kill Criteria|Graveyard", decisions_text, re.IGNORECASE))
        )
        checks["K6_full_tier_research_and_decisions"] = {
            "passed": has_research and has_decisions,
            "detail": f"research_ok={has_research}, decisions_ok={has_decisions}",
        }

    all_passed = all(c["passed"] for c in checks.values())
    return {"all_passed": all_passed, "tier": tier_norm, "checks": checks}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate kickoff artifacts against True/False rules.")
    parser.add_argument("project_dir", nargs="?", type=Path, default=Path("."))
    parser.add_argument("--tier", default="FULL", choices=["SKIP", "LIGHT", "FULL"])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = validate_kickoff_dir(args.project_dir.resolve(), tier=args.tier)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"KICKOFF_VALID={str(report['all_passed']).upper()} (tier={report['tier']})")
        for cid, info in report["checks"].items():
            tag = "PASS" if info["passed"] else "FAIL"
            print(f"  [{tag}] {cid}: {info['detail']}")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
