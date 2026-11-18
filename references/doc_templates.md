# Kickoff Document Templates

## 1. Lean `AGENTS.md` Index (<150 Lines)
```markdown
# <Project Name> — Agent Index & Rules

## About Me (Project Context)
- **Builder & Usage Context:** <device, constraints, beginner/mentor preferences>
- **Anti-Sycophancy Rule:** Challenge assumptions politely if an idea adds Effort L / Low Impact or scope creep.

## Persistent Project Docs (Read Before Editing)
- [decisions.md](./decisions.md) — Settled architecture, answered baseline Q&A, Kill Criteria & Graveyard.
- [research.md](./research.md) — Prior-art comparison and Build vs. Configure vs. Wrap verdict.
- [plan.md](./plan.md) — MVP v0.1 slice, Effort/Impact improvement ideas, and 2-3 feature batches.

## Batch Builder Rule
- Build **2–3 small related features per turn** (drop to 1 for auth, payments, or data-loss changes).
- Verify each batch against tests before moving on; log dead ends instead of repeating them.

## Verification Gates
- **Test:** `<command>`
```

## 2. `CLAUDE.md`
```markdown
@AGENTS.md
```

## 3. `research.md` (`FULL` Tier)
Must include a capped 3–5 competitor table (`Tool/Repo | What Works | Where It Fails | Steal | Skip`), a check of local installed tools first, and a `## Build vs. Configure vs. Wrap Verdict` section.

## 4. `decisions.md` (`FULL` Tier)
Must include `## Answered Questions`, `## Settled Decisions`, and `## Kill Criteria & Graveyard` (explicitly listing cut/deferred features so future sessions never re-suggest them).

## 5. `plan.md` (`LIGHT` and `FULL` Tiers)
Must include `## MVP v0.1 (Smallest Useful Slice)`, `## Improvement Ideas (Effort vs. Impact)` with `[Effort: S/M/L | Impact: Low/Med/High | Type: Add/Subtract]` tags, and `## Execution Batches` (`Batch 1`, `Batch 2`, etc. with 2–3 features per batch).
