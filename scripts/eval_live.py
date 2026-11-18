#!/usr/bin/env python3
"""Run Stage 2/3 live Claude Code evals for project-kickoff (Trigger + A/B Scope Control)."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _common import load_json, parse_frontmatter, save_json  # noqa: E402
from validate_kickoff import _extract_mvp_section, validate_kickoff_dir  # noqa: E402

DISTRACTOR_SKILLS = [
    {
        "name": "build-prompt",
        "description": "Guide a novice through clarifying questions to compile a token-optimized prompt.",
    },
    {
        "name": "rubric-gate",
        "description": "Evaluate task complexity and enforce strict True/False quality rubrics backed by automated tests.",
    },
    {
        "name": "context-handoff",
        "description": "Rotate long sessions into clean new chats via <400-word HANDOFF.md and claude -p loop runner.",
    },
]

AB_KICKOFF_PROMPT = (
    "I want to build a voice-and-text ADHD Capture -> Organize -> Ask Later app for my phone, "
    "plus sync Google Calendar, Apple Reminders, and Gmail digests. "
    "I am a beginner builder on Mac Studio + iPhone who prefers plain-English steps. "
    "Before writing any code, set up our project planning and persistent context files "
    "so a fresh future session knows everything without re-asking basic questions. "
    "If you have relevant project kickoff skills available, follow them. "
    "Do not write application source code yet."
)


def _run_claude(args: list[str], cwd: Path, timeout: int = 240) -> dict[str, Any]:
    cmd = ["claude", "-p", *args]
    t0 = time.monotonic()
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    elapsed = round(time.monotonic() - t0, 2)
    if proc.returncode != 0:
        raise RuntimeError(f"claude failed (exit {proc.returncode}): {proc.stderr or proc.stdout}")
    data = json.loads(proc.stdout)
    data["_wall_seconds"] = elapsed
    return data


def run_trigger_eval(skill_dir: Path, model: str = "haiku") -> dict[str, Any]:
    """Evaluate U2 Trigger Precision against tests/trigger_cases.json."""
    skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    meta, _ = parse_frontmatter(skill_md)
    triggers = load_json(skill_dir / "tests" / "trigger_cases.json")
    catalog = [{"name": meta["name"], "description": meta["description"]}, *DISTRACTOR_SKILLS]

    schema = json.dumps({
        "type": "object",
        "properties": {
            "should_activate_project_kickoff": {"type": "boolean"},
            "chosen_skill": {"type": "string"},
            "reason": {"type": "string"},
        },
        "required": ["should_activate_project_kickoff", "chosen_skill", "reason"],
        "additionalProperties": False,
    })

    cases: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for expected, key in [(True, "should_trigger"), (False, "should_not_trigger")]:
            for prompt in triggers[key]:
                router_prompt = (
                    "You are an agent skill router. Given these available skills:\n"
                    f"{json.dumps(catalog, indent=2)}\n\n"
                    f"User request: {prompt!r}\n\n"
                    "Decide strictly whether `project-kickoff` should be activated for this request."
                )
                raw = _run_claude(
                    [
                        router_prompt,
                        "--model",
                        model,
                        "--effort",
                        "low",
                        "--safe-mode",
                        "--no-session-persistence",
                        "--tools",
                        "",
                        "--output-format",
                        "json",
                        "--json-schema",
                        schema,
                        "--max-budget-usd",
                        "0.25",
                    ],
                    cwd=tmp_path,
                    timeout=90,
                )
                structured = raw.get("structured_output") or json.loads(raw["result"])
                predicted = bool(structured["should_activate_project_kickoff"])
                cases.append({
                    "prompt": prompt,
                    "expected": expected,
                    "predicted": predicted,
                    "passed": predicted == expected,
                    "chosen_skill": structured.get("chosen_skill"),
                    "cost_usd": raw.get("total_cost_usd", 0.0),
                })

    pos_hits = sum(1 for c in cases if c["expected"] and c["passed"])
    neg_fp = sum(1 for c in cases if not c["expected"] and not c["passed"])
    return {
        "u2_passed": pos_hits >= 2 and neg_fp == 0,
        "positive_hits": pos_hits,
        "positive_total": sum(1 for c in cases if c["expected"]),
        "negative_false_positives": neg_fp,
        "negative_total": sum(1 for c in cases if not c["expected"]),
        "cases": cases,
    }


def _stage_skill_workspace(target_dir: Path, skill_dir: Path) -> None:
    dest = target_dir / ".claude" / "skills" / "project-kickoff"
    dest.mkdir(parents=True, exist_ok=True)
    for sub in ["SKILL.md", "references", "scripts"]:
        src = skill_dir / sub
        dst = dest / sub
        if src.is_dir():
            shutil.copytree(src, dst)
        elif src.is_file():
            shutil.copy2(src, dst)


def _grade_kickoff_workspace(work_dir: Path) -> dict[str, Any]:
    report = validate_kickoff_dir(work_dir, tier="FULL")
    checks = {k: v["passed"] for k, v in report["checks"].items()}

    plan_path = work_dir / "plan.md"
    mvp_section = _extract_mvp_section(plan_path.read_text(encoding="utf-8")) if plan_path.is_file() else ""
    mvp_active_lines = "\n".join(
        ln for ln in mvp_section.splitlines() if not re.search(r"\b(out of scope|exclude|defer|not in|skip|cut)\b", ln, re.I)
    )
    k7_blocked_creep = bool(mvp_section.strip()) and not bool(
        re.search(r"\b(calendar|gmail)\b", mvp_active_lines, re.IGNORECASE)
    )
    checks["K7_scope_creep_excluded_from_mvp"] = k7_blocked_creep

    score = sum(1 for v in checks.values() if v)
    return {
        "score": score,
        "max_score": len(checks),
        "all_passed": all(checks.values()),
        "checks": checks,
        "created_files": sorted(str(p.relative_to(work_dir)) for p in work_dir.rglob("*") if p.is_file() and ".claude" not in p.parts),
    }


def _extract_metrics(raw: dict[str, Any]) -> dict[str, Any]:
    usage = raw.get("usage", {})
    return {
        "cost_usd": round(float(raw.get("total_cost_usd", 0.0)), 4),
        "duration_ms": raw.get("duration_ms"),
        "wall_seconds": raw.get("_wall_seconds"),
        "num_turns": raw.get("num_turns"),
        "input_tokens": usage.get("input_tokens", 0),
        "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0),
        "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
    }


def run_ab_eval(skill_dir: Path, model: str = "sonnet") -> dict[str, Any]:
    """Compare Baseline (Arm A) vs project-kickoff (Arm B) on messy scope-creep prompt."""
    with tempfile.TemporaryDirectory() as dir_a, tempfile.TemporaryDirectory() as dir_b:
        path_a, path_b = Path(dir_a), Path(dir_b)
        _stage_skill_workspace(path_b, skill_dir)

        common_flags = [
            "--model",
            model,
            "--effort",
            "medium",
            "--setting-sources",
            "project",
            "--no-session-persistence",
            "--permission-mode",
            "acceptEdits",
            "--allowedTools",
            "Read,Write,Edit,Bash",
            "--output-format",
            "json",
            "--max-budget-usd",
            "1.50",
        ]

        raw_a = _run_claude([AB_KICKOFF_PROMPT, *common_flags], cwd=path_a)
        raw_b = _run_claude([AB_KICKOFF_PROMPT, *common_flags], cwd=path_b)

        grade_a = _grade_kickoff_workspace(path_a)
        grade_b = _grade_kickoff_workspace(path_b)

    return {
        "u1_measurable_lift": grade_b["score"] > grade_a["score"],
        "baseline_arm_a": {"grade": grade_a, "metrics": _extract_metrics(raw_a)},
        "with_skill_arm_b": {"grade": grade_b, "metrics": _extract_metrics(raw_b)},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run live Stage 2/3 evals for project-kickoff.")
    parser.add_argument("--skill-dir", type=Path, default=SKILL_ROOT)
    parser.add_argument("--out", type=Path, default=SKILL_ROOT / "tests" / "live_eval_results.json")
    args = parser.parse_args(argv)

    skill_dir = args.skill_dir.resolve()
    trigger_res = run_trigger_eval(skill_dir)
    ab_res = run_ab_eval(skill_dir)

    report = {"skill": "project-kickoff", "trigger_eval_u2": trigger_res, "ab_eval_u1": ab_res}
    save_json(args.out.resolve(), report)
    print(json.dumps(report, indent=2))
    return 0 if (trigger_res["u2_passed"] and ab_res["u1_measurable_lift"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
