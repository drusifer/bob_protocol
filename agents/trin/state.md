# Agent State

## Context
- The Bob persona-authoring suite passed after the grader was grounded in the installed fixture's `agents/PROJECT.md`.
- Morpheus `*advise` was added to the live and packaged persona skills and covered by `morpheus-design-advice`, which installs this checkout into a disposable project and produces an ADR.
- First Morpheus run exposed a rubric ambiguity, not an ADR defect: the template makes Related optional, but DECISION's STATE criterion did not say omission is valid when no earlier ADR exists. Canonical and packaged rubrics now explicitly allow omission or `None` in that case.
- Corrected report: `build/persona-eval/morpheus-design-advice-20261030T132734Z-run1.json`; retained ADR: `build/persona-eval/runtime/morpheus-design-advice-20261030T132734Z-run1/project/docs/decisions/ADR-0001-refund-lifecycle.md`.
- The retained ADR models Payments/Payment/Refund ownership and invariants, gives behavior scenarios, compares three options, and explains KISS/DRY. The report confirms `skill-used: morpheus` and all applicable DECISION rubric criteria pass.
- Full tests: 88 passed, 7 skipped, 9 subtests passed. Mermaid lint passed; Node v24.13 emitted a transitive dependency engine warning, recorded in `docs/SDLC.md`. All pytest/eval scratch and reports are in `build/`.

## Current Task
**Status:** Sprint 5 UAT (`docs/sprints/UAT_PLAN_SPRINT5.md`) & Better/Worse measurements (`docs/sprints/EVAL_SPRINT5_SUBAGENTS.md`) complete and APPROVED (`384 passed, 2 skipped, 435 subtests`); Sprint 5 LAUNCHED (2026-11-28).
**Assigned to:** Trin (`*qa`) — complete
**Progress:** Verified `.agents/skills/` real-directory layout (35 skills, 0 symlinks), legacy migration & idempotent `update`, `STORY-SKL-3 AC5` harness-discovery output & READMEs, per-skill `evals/evals.json` (`--list --json`, 11 suites) + evaluating-skills workspace tests, Phase 5–6 size/references/descriptions/Gotchas/parity tests (`test_skill_spec.py`, 320 subtests), Phase 7 agent-safe CLI (`--help`, `--dry-run`, `clean --yes`), and full clean-rebuild suite (`368 passed, 2 skipped, 397 subtests`). Live paid Codex+TypeSafe eval remains deferred pending owner approval (Task 3b.3).

## Next Steps
1. Await user direction on git commit/release or live paid `bobp persona-eval` approval.
