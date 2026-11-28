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

Status (2026-11-28): **COMPLETE & LAUNCHED (`*pm launch SPRINT_3`)**. All Phases 1–7, the Owner Amendment (`.agents/skills/` real dirs, zero symlinks), and Stage 3 Closeout (Tank clean rebuild + SDLC §3/§7/§9 updates, Oracle grooming + `CHAT_SPRINT_3` report, Smith E2E UX `APPROVE`, Team Retro, Cypher Launch) finished. Full suite: `368 passed, 2 skipped, 397 subtests`, Mermaid lint, security-scan, and package build (`bobp-0.3.1`) green.
Findings this sprint: SEC-005 (symlink/FIFO stamp hang), SEC-006 (stamp/manifest written through symlinks), SEC-007 (escape sequences in echoed names) — all fixed.
Sprint 3 Retro Backlog:
- Smith HCI polish (#1–#6): `trace-annotate --help` stale script path; 1-line subcommand descriptions in `bobp --help`; `setup-agent-links` runtime banner wording; `persona-eval --all` help `"catalog"` wording; `bob-tools/SKILL.md` 256-vs-512 chat limit note; `clean --dry-run`/`--help` mentioning `teardown_agent_links --keep-mcp`.
- Open security backlog: remaining install/update writes (`state.md`, `CHAT.md`, `copy2`) following planted destination symlinks.
- Pending owner decisions: commit/version bump/release (`docs/SDLC.md` §6/§7); approve a live paid Codex+TypeSafe `bobp persona-eval` run (Task 3b.3); whether `--baseline` should become default.

## SPRINT_4 — `bobp merge` for Timestamped Documents (Tier 1, KISS)

Stories + architecture: `docs/sprints/USER_STORIES_SPRINT4.md`
Task board: root `task.md`

| Phase | Scope | Owner |
|-------|-------|-------|
| 1 | Replace `chat_merge.py` with `bobp/tools/merge.py` (`bobp merge`), multi-format parser (`chat`/`heading`/`metadata`), post-conflict cleanup + preamble guard, asc/desc order, SEC-005/006/007 I/O, update `chat_report.py` & `setup_agent_links.py`, tests | Neo |
| 2 | Add `--git-driver BASE OURS THEIRS` 3-way merge driver + real-`git` E2E tests | Neo |
| 3 | Update `--help` opt-in Git snippet & active skills/templates/docs (remove stale `chat-merge` refs) | Bob, Oracle |

Each coding phase: Neo impl → Trin UAT → Switch security review → Morpheus review. No Phase 0 (pure Python stdlib, no build-env change).

## SPRINT_5 — Harness-Native Subagent Definitions & Evaluation (Tier 1)

Stories + architecture: `docs/sprints/USER_STORIES_SPRINT5.md`
Evaluation report: `docs/sprints/EVAL_SPRINT5_SUBAGENTS.md`
UAT plan: `docs/sprints/UAT_PLAN_SPRINT5.md`
Task board: root `task.md` (`docs/sprints/TASK_SPRINT5.md`)

| Phase | Scope | Owner |
|---|---|---|
| 1 | `bobp/tools/_subagent_layout.py` (30 compiled subagents across `.claude/agents/*.md`, `.codex/agents/*.toml`, `.gemini/agents/*.md`, `agents/.bobp-subagents` manifest, pre-flight parent-chain & SEC-005/006/007 checks, stdlib YAML/TOML emitters, `.gitignore` negation checks), CLI wiring (`install`/`update`/`pull`/`diff` + `--help`), `tests/test_subagent_layout.py` | Neo |
| 2 | `.gitignore` allowlist (`.claude/*` + `!.claude/agents/`), remove stray 0-byte `.codex` file, dogfood `bobp update .` + repo-parity test, sync README/`bob-tools`/`SDLC.md`, author `docs/sprints/EVAL_SPRINT5_SUBAGENTS.md` | Neo, Oracle, Trin, Smith, Morpheus |

Status (2026-11-28): **COMPLETE & LAUNCHED (`*pm launch SPRINT_5`)**. Full suite `384 passed, 2 skipped, 435 subtests`, Mermaid lint, security-scan, package build (`bobp-0.3.1`), Switch Gate 5a, Morpheus review, and Smith E2E UX `APPROVE` all green.
Sprint 5 Retro Backlog:
- Smith polish (#1–#3): mention Claude Code in `README.md` line 4 opening sentence & subagents in `bobp/templates/README.md` `update` inline comment; align `install --help` vs `update --help` harness path phrasing; print `No differences found.` on clean `bobp diff`.
- Morpheus polish: remove unused `must_exist` param in `_check_dir_chain`, hoist `import json`, add `getattr(os, "O_NONBLOCK", 0)`, add `Skipped subagent diff:` message on oversized manifest/symlinked harness dir, optional early pre-flight in `install()`.
- Owner decision: after spot-checking real Claude ↔ Codex ↔ Gemini switching, choose Option 1 (keep all 3 default), Option 2 (Claude-only or `--subagents` opt-in), or Option 3 (drop cleanly via `ADR-S5-1`); also decide commit/version bump/PyPI release (`docs/SDLC.md` §6/§7).
