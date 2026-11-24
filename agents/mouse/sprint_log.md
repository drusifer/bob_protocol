# Sprint Log

## SPRINT_1 — Chat Archive & Report

Stories: `agents/cypher/sprint_SPRINT_1_stories.md`
Architecture: `agents/morpheus/sprint_SPRINT_1_arch.md`

| Phase | Scope | Owner |
|-------|-------|-------|
| 1 | `bobp/tools/chat_report.py` (archive + combine) + `cli.py` registration + tests | Neo |
| 2 | `chat_diagram.py` word-wrap (textwrap + `<br/>`, raised cap) + tests | Neo |
| 3 | `chat_merge.py` conflict-marker stripping + dedup + tests | Neo |
| 4 | Wire archive step into `agents/skills/sprint/SKILL.md` (Stage 3 Step 7) and `agents/oracle/SKILL.md` (`*ora archive`) | Neo |

Each phase: Neo impl → Trin UAT → Morpheus review, per Bloop. Kept small (1 file + tests each) to avoid context overflow.

## SPRINT_2 — Version-Aware bobp (Tier 2)

Stories + architecture (combined): `docs/sprints/USER_STORIES_SPRINT2.md`
Task board: root `task.md`

| Phase | Scope | Owner |
|-------|-------|-------|
| 1 | `bobp --version`/`-V`; `install`/`update` write `agents/.bobp-version` + tests | Neo |
| 2 | `bobp/tools/_version_check.py` + `_common.find_project_root_or_none()` + dispatcher wiring; notify-only stderr notice, no prompt + tests | Neo |

Each phase: Neo impl → Trin UAT → Switch security review → Morpheus review. No Phase 0 (no build-environment change).

## SPRINT_3 — Spec-Compliant Skills, No Links (Tier 1)

Stories + architecture: `docs/sprints/USER_STORIES_SPRINT3.md`
Task board: root `task.md` (Sprint 2's board is saved as `docs/sprints/TASK_SPRINT2.md`)

| Phase | Scope | Owner |
|-------|-------|-------|
| 1 | `_skill_layout.place_skills`, ownership manifest, spec test, install/update place real skills in `.claude/skills/` | Neo |
| 2 | no-links setup, legacy migration and link removal, root `AGENTS.md` | Neo |
| 3 | per-skill `evals/evals.json`, `load_evals`, remove `catalog.json` | Neo |
| 4 | `rewrite_path_refs` on templates and this repo | Neo, Tank |
| 5 | size limits, `references/`, enforcing tests | Bob |
| 6 | descriptions, Gotchas, conditional pointers, cleanup | Bob |
| 7 | agent-safe subcommands (`--help`, `--dry-run`, `--yes`, exit codes) | Neo |

Status (2026-11-01): Phases 1, 2, 3, 3b and 4 done and gated (suite 328 passing). This repo is migrated (`bobp update .` ran; skills live in `.claude/skills/`, `.gitignore` narrowed to `.claude/settings.local.json`) and the old Codex-home links were removed with `bobp teardown-agent-links --keep-mcp`. Next: Phase 5 (size limits), 6 (descriptions, Gotchas), 7 (agent-safe subcommands), then closeout.
Findings this sprint: SEC-005 (symlink/FIFO stamp hang), SEC-006 (stamp/manifest written through symlinks), SEC-007 (escape sequences in echoed names) — all fixed. Open backlog: other install/update writes (state.md, CHAT.md, copy2) still follow planted destination symlinks.
OWNER DECISION 2026-11-01 (in progress, NOT done): move skills from `.claude/skills/` to `.agents/skills/`, no link for Claude Code, and ignore `.claude` in .gitignore again. Done so far: only `_skill_layout.py` groundwork (`CLAUDE_SKILLS_DIR`, `remove_claude_skill_copies`, docstrings); `SKILLS_DIR` was set back to `.claude/skills` so the suite stays green (328 passing). Remaining: (1) flip `SKILLS_DIR`; (2) `update` must remove the old `.agents -> agents` link first (already in LEGACY_LINKS) and call `remove_claude_skill_copies`; (3) `_path_rewrite`: rules to `.agents/skills`, plus an opt-in intermediate rule for `.claude/skills` (not default: user prose may name Claude's own dir); (4) persona_eval: `expose_codex_skills` must stop deleting `.agents` (it rmtree's it), read `.agents/skills`, jev canonical path, 10 evals.json artifact paths; (5) `gitignore_hides_skills` -> `.agents`; (6) text in setup_agent_links, _bob_manage, README; (7) update tests (`.claude`->`.agents` in 4 test files; keep `.claude` for legacy-link tests); (8) rewrite the ~40 template files and re-run `bobp update .` on this repo; (9) restore `.claude` in .gitignore. Claude Code will not see the skills in this project afterwards.
Pending owner decisions: approve a live paid persona-eval run (Codex + TypeSafe) to verify 3b end to end; whether `--baseline` should become the default.
