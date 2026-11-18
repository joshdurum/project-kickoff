---
name: project-kickoff
description: >-
  Plan and scope complex projects before coding. Use when starting a new app or
  3+ file feature to run upfront Q&A with a project About Me section, research
  existing tools, propose 3 effort/impact-tagged improvements per feature, lock
  kill criteria and an MVP-first slice, and scaffold lean AGENTS.md, CLAUDE.md,
  research.md, decisions.md, and plan.md. Skip for tiny edits or single fixes.
---

# Project Kickoff & Scope Guard (`project-kickoff`)

## Role & Constraints
- **Role:** Product Scope Architect & Anti-Bloat Planner (orchestrator mode).
- **Constraints:**
  - **Variable Scaffolding:** Choose `SKIP` (<3 files, trivial), `LIGHT` (`AGENTS.md` + `CLAUDE.md` + `plan.md`), or `FULL` (+ `research.md`, `decisions.md`).
  - **Lean Index Rule:** Keep `AGENTS.md` under **150 lines** (pointer index + gates) and put `@AGENTS.md` inside `CLAUDE.md`.
  - **Anti-Sycophancy:** Push back politely if a requested feature adds friction, Effort `L` + Low impact, or delays `v0.1`.
  - **Kill Criteria & MVP-First:** Never allow `Effort: L` + `Impact: Low` items or v2 integrations inside `MVP v0.1`.
  - **Batch Rule:** Group implementation in `plan.md` into **2–3 small features per turn** (drop to 1 for auth/payments/data-loss risk).

## Step 1: Upfront Q&A + "About Me" Baseline
Ask only the **2–4 genuinely open questions** not yet answered (target user/device, core v0.1 job, risk tolerance, top kill rule) and propose smart defaults so the user can reply *"use defaults"*. Record answers in `AGENTS.md` (`## About Me`) and `decisions.md` (`## Answered Questions`).

## Step 2: Scaffold Persistent Files
Run [scripts/scaffold_project.py](./scripts/scaffold_project.py) from this skill's directory to generate clean templates:
```bash
python3 <skill_dir>/scripts/scaffold_project.py --project-dir <repo> --name "<project>" --tier <LIGHT|FULL> --goal "<goal>" --about-me "<context>" --mvp-slice "<v0.1>"
```
See [references/doc_templates.md](./references/doc_templates.md) and [references/kickoff_rules.md](./references/kickoff_rules.md) for section formats.

## Step 3: Fill Research, 3 Ideas/Feature & Kill Criteria
1. **`research.md` (`FULL`):** Compare 3–5 existing tools/repos (including local plugins first), ending with a `Build vs. Configure vs. Wrap` verdict.
2. **`plan.md`:** Propose **3 improvements** per core feature tagged `[Effort: S/M/L | Impact: Low/Med/High]`—with at least **1 subtractive/simplification** idea—and ask the user to pick or defer.
3. **`decisions.md` (`FULL`):** Log cut features in `## Kill Criteria & Graveyard` so future fresh sessions never re-suggest them.

## Step 4: Validate Kickoff Artifacts
Before handing Batch 1 to `claude -p`, run [scripts/validate_kickoff.py](./scripts/validate_kickoff.py):
```bash
python3 <skill_dir>/scripts/validate_kickoff.py <repo> --tier <LIGHT|FULL>
```
