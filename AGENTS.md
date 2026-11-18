# project-kickoff — Project Instructions & Verification Gates

## Stack Overview
- **Primary Stack:** Python 3 (standard library only, zero external dependencies), Markdown (`SKILL.md`, templates).
- **Target Ecosystem:** Hybrid Antigravity (`agy` orchestrator) + Claude Code (`claude` executor), standalone GitHub-ready skill repo.

## Key Files (Read Before Editing)
- [SKILL.md](./SKILL.md) — Core skill instructions loaded on trigger.
- [references/doc_templates.md](./references/doc_templates.md) — Templates for `AGENTS.md`, `research.md`, `decisions.md`, `plan.md`.
- [references/kickoff_rules.md](./references/kickoff_rules.md) — Adaptive tier, Kill Criteria, MVP-first, and batching rules.

## Working Rules
- Keep `SKILL.md` under 180 lines and generated `AGENTS.md` files under 150 lines.
- Keep all scripts pure Python stdlib so verification requires zero `pip install` steps.

## Verification Gates
Run these exact commands before marking any change complete:
- **Test:** `python3 -m unittest discover -s tests -v`
- **Syntax Check:** `python3 -m compileall -q scripts tests`
