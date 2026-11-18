# Project Kickoff Rules

## 1. Variable Scaffolding Tiers
- **`SKIP`:** `<3` files, single session, no new integrations -> write 0 planning docs.
- **`LIGHT`:** Small 3+ file feature -> write `AGENTS.md`, `CLAUDE.md`, and `plan.md`.
- **`FULL`:** Multi-session app or new integrations -> write `AGENTS.md`, `CLAUDE.md`, `research.md`, `decisions.md`, and `plan.md`.

## 2. Kill Criteria Rules
- **Effort vs. Impact Gate:** Cut or defer any feature tagged `Effort: L` + `Impact: Low` (and any non-essential `v2` integration like Calendar/Email sync during `v0.1`).
- **ADHD Friction Gate:** Reject workflows requiring `>2` manual tagging/filing steps at capture time.
- **Graveyard Persistence:** Every cut or deferred feature MUST be logged in `decisions.md` under `## Kill Criteria & Graveyard` with its reason so fresh chats never re-propose it.

## 3. MVP-First & 3-Idea Rule
- **72-Hour Useful Slice:** `MVP v0.1` must deliver end-to-end user value on the target device (e.g., Capture -> Organize -> Ask Later on phone) before adding external syncs.
- **3 Ideas per Feature:** For each major feature, list 3 improvements tagged `[Effort: S/M/L | Impact: Low/Med/High]`, including at least **1 subtractive/simplification** idea (`Type: Subtract`).

## 4. 2–3 Feature Batching Rule
- Execute **2–3 small features per turn** to minimize stop-and-wait rounds, micro-verifying each before the next, and dropping to **1 feature** when touching auth, migrations, or data-loss code.
