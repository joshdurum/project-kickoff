#!/usr/bin/env python3
"""Scaffold persistent project planning files scaled to complexity tier (SKIP/LIGHT/FULL)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _render_agents(name: str, tier: str, about_me: str, test_cmd: str) -> str:
    doc_links = ["- [plan.md](./plan.md) — MVP v0.1 slice, improvement ideas, and 2-3 feature batches."]
    if tier == "FULL":
        doc_links.extend([
            "- [decisions.md](./decisions.md) — Settled decisions, answered Q&A, Kill Criteria & Graveyard.",
            "- [research.md](./research.md) — Prior-art matrix and Build vs. Configure vs. Wrap verdict.",
        ])

    return "\n".join([
        f"# {name} — Agent Index & Verification Gates",
        "",
        "## About Me",
        f"- **Context:** {about_me.strip() or 'Builder optimizing for fast MVP shipping and low cognitive friction.'}",
        "- **Anti-Sycophancy:** Challenge assumptions politely if an idea adds Effort L / Low Impact or scope creep.",
        "",
        "## Persistent Project Docs",
        *doc_links,
        "",
        "## Batch Builder Rule",
        "- Execute **2-3 small related features per turn** (drop to 1 when touching auth, migrations, or data-loss code).",
        "- Verify each batch before proceeding; never re-propose items logged in the Graveyard.",
        "",
        "## Verification Gates",
        f"- **Test:** `{test_cmd}`",
        "",
    ])


def _render_research(name: str) -> str:
    return "\n".join([
        f"# Prior-Art Research — {name}",
        "",
        "## Local Environment Check",
        "- Checked installed plugins/scripts before designing custom code.",
        "",
        "## Competitor & Pattern Matrix (Max 5)",
        "| Tool / Repo | What Works | Where It Fails | What We Steal | What We Skip |",
        "| :--- | :--- | :--- | :--- | :--- |",
        "| Example Tool A | Fast capture | Too many required tags | 1-input capture | Complex folder tree |",
        "",
        "## Build vs. Configure vs. Wrap Verdict",
        "- **Decision:** Build lean custom MVP / wrap existing tools (fill in exact rationale).",
        "",
    ])


def _render_decisions(name: str, goal: str, about_me: str) -> str:
    return "\n".join([
        f"# Decisions & Kill Criteria — {name}",
        "",
        "## Answered Questions",
        f"- **Core Goal:** {goal.strip() or 'Ship smallest useful v0.1 quickly.'}",
        f"- **Project Context:** {about_me.strip() or 'Mobile-first / low-friction.'}",
        "",
        "## Settled Decisions",
        "- Keep persistent truth in files (`AGENTS.md`, `decisions.md`, `plan.md`) so fresh sessions never re-debate settled choices.",
        "",
        "## Kill Criteria & Graveyard",
        "- **Rule:** Cut or defer any feature tagged `[Effort: L | Impact: Low]` or requiring `>2` manual daily upkeep steps.",
        "- **Graveyard (Do Not Re-Propose for v0.1):**",
        "  - *(Log deferred integrations and cut ideas here with explicit reasons.)*",
        "",
    ])


def _render_plan(name: str, goal: str, mvp_slice: str) -> str:
    return "\n".join([
        f"# Implementation Plan — {name}",
        "",
        "## MVP v0.1 (Smallest Useful Slice)",
        f"- **Goal:** {goal.strip() or 'Deliver usable v0.1 quickly.'}",
        f"- **v0.1 Scope:** {mvp_slice.strip() or 'Core single-loop flow usable within 72 hours.'}",
        "",
        "## Improvement Ideas (3 per Feature — Effort vs. Impact)",
        "- Feature 1 Ideas:",
        "  1. [Effort: S | Impact: High | Type: Add] Core frictionless helper.",
        "  2. [Effort: S | Impact: Med | Type: Subtract] Remove optional form fields at capture time.",
        "  3. [Effort: M | Impact: Med | Type: Add] Optional v1.1 enhancement (defer if outside v0.1).",
        "",
        "## Execution Batches (2-3 Features per Turn)",
        "- **Batch 1 (Core v0.1):**",
        "  - [ ] Feature 1A",
        "  - [ ] Feature 1B",
        "",
    ])


def scaffold_project(
    project_dir: Path,
    name: str,
    tier: str = "FULL",
    goal: str = "",
    about_me: str = "",
    mvp_slice: str = "",
    test_cmd: str = "python3 -m unittest discover -s tests -v",
    force: bool = False,
) -> dict[str, Any]:
    """Generate variable persistent project files for SKIP, LIGHT, or FULL tiers."""
    tier_norm = tier.strip().upper()
    if tier_norm not in {"SKIP", "LIGHT", "FULL"}:
        raise ValueError(f"Invalid tier {tier!r}; must be SKIP, LIGHT, or FULL.")

    if tier_norm == "SKIP":
        return {"tier": "SKIP", "files_created": [], "skipped_reason": "Tiny task requires no planning docs."}

    project_dir.mkdir(parents=True, exist_ok=True)
    targets: dict[str, str] = {
        "AGENTS.md": _render_agents(name, tier_norm, about_me, test_cmd),
        "CLAUDE.md": "@AGENTS.md\n",
        "plan.md": _render_plan(name, goal, mvp_slice),
    }
    if tier_norm == "FULL":
        targets["research.md"] = _render_research(name)
        targets["decisions.md"] = _render_decisions(name, goal, about_me)

    created: list[str] = []
    preserved: list[str] = []
    for filename, content in targets.items():
        fpath = project_dir / filename
        if fpath.exists() and not force:
            preserved.append(filename)
            continue
        fpath.write_text(content, encoding="utf-8")
        created.append(filename)

    return {
        "tier": tier_norm,
        "project_dir": str(project_dir),
        "files_created": created,
        "files_preserved": preserved,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold persistent kickoff docs scaled by complexity tier.")
    parser.add_argument("--project-dir", type=Path, default=Path("."))
    parser.add_argument("--name", required=True, help="Project or feature name.")
    parser.add_argument("--tier", default="FULL", choices=["SKIP", "LIGHT", "FULL"])
    parser.add_argument("--goal", default="")
    parser.add_argument("--about-me", default="")
    parser.add_argument("--mvp-slice", default="")
    parser.add_argument("--test-cmd", default="python3 -m unittest discover -s tests -v")
    parser.add_argument("--force", action="store_true", help="Overwrite existing planning files.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    res = scaffold_project(
        project_dir=args.project_dir.resolve(),
        name=args.name,
        tier=args.tier,
        goal=args.goal,
        about_me=args.about_me,
        mvp_slice=args.mvp_slice,
        test_cmd=args.test_cmd,
        force=args.force,
    )
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"SCAFFOLD_TIER={res['tier']} created={res['files_created']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
