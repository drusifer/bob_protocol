# UAT Plan: Sprint 5 — Harness-Native Subagent Definitions & Evaluation

- **Stories / criteria:** `STORY-AGT-1`, `STORY-AGT-2`, `STORY-AGT-3` in [`docs/sprints/USER_STORIES_SPRINT5.md`](USER_STORIES_SPRINT5.md)
- **Environment and build:** `bobp` 0.3.1 (working tree on `main`, Python 3.15 / `uv` `.venv/`, Linux; installed CLIs `claude 2.1.331`, `codex-cli 0.172.0`, `gemini 0.40.1`)
- **Date / tester:** 2026-11-28 / Trin (author & verification), Smith (end-to-end UX acceptance)
- **Entry conditions:** Phases 1–2 complete and gated (`384 passed, 2 skipped, 435 subtests`, Switch Gate 5a `No blocking findings`, Morpheus `APPROVE`); `docs/SDLC.md` §7 updated and Tank conformance gates (`test`, `lint`, `security-scan`, `build`) verified.
- **Exit conditions:** All in-scope acceptance scenarios pass with recorded actual outcomes and reproducible evidence; negative/hostile paths verified; Smith UX acceptance (`rubric UAT`) recorded in `agents/CHAT.md`.

## Scenarios

### UAT-AGT-1: Subagent compilation, schema validity, shared-state preamble, and persona-only scope

- **Linked criterion:** `STORY-AGT-1` AC1–AC3, AC8
- **User / task:** Developer installing or updating Bob Protocol in a project to use all 10 personas natively across Claude Code, Codex, and Gemini CLI.
- **Preconditions and data:** Packaged templates under `bobp/templates/agents/` and scratch project directory (`build/pytest/subagent_cli/e2e_flow`).
- **Steps:**
  1. Run `bobp install <scratch>` and inspect `.claude/agents/`, `.codex/agents/`, `.gemini/agents/`.
  2. Verify exactly 10 real regular files per harness (30 total, zero symlinks, zero shared workflow skills like `make`/`sprint`/`chat`).
  3. Validate YAML frontmatter (`name`, `description` for Claude; `name`, `description`, `kind: local` for Gemini; `---` on line 1; no `memory:`/`model:`/`tools:`) and parse all 10 Codex `.toml` files with stdlib `tomllib.loads()` (`name`, `description`, `developer_instructions`; no `model`/`sandbox_mode`).
  4. Verify every file carries the generated-file notice and prominent top `**Shared Working Memory:**` preamble pointing to `agents/<persona>/state.md` and `agents/CHAT.md`.
- **Expected observable outcome:** Exit `0`; 30 valid regular files; all 10 TOML files round-trip cleanly via `tomllib.loads()`; adversarial YAML/TOML escaping passes; shared-state preamble present in all 30 files.
- **Actual outcome:** Passed (`tests/test_subagent_layout.py::TestSubagentCompilation`, live `uv run bobp update .`, and `ALL_10_LIVE_CODEX_TOML_PARSED_OK`); zero symlinks; 10 personas only; zero hardcoded models or harness-private memory.
- **Verdict:** PASS
- **Evidence / issue:** `tests/test_subagent_layout.py` (`test_compile_generates_30_valid_subagents_for_10_personas_only`, `test_adversarial_yaml_and_toml_escaping_round_trips`), `bobp make test` (`384 passed, 435 subtests`)

### UAT-AGT-2: Ownership preservation, hostile-tree refusal, `--dry-run`, idempotency, and `clean` boundary

- **Linked criterion:** `STORY-AGT-1` AC4–AC7, `STORY-AGT-2` AC7
- **User / task:** Maintainer upgrading a project containing custom user subagents or cloned untrusted symlinks/FIFOs.
- **Preconditions and data:** Isolated scratch projects containing custom `.claude/agents/neo.md` + `my-helper.toml`, hostile symlinks/regular files/FIFOs at `agents/`, harness dirs, `agents/.bobp-subagents`, target files, and `.gitignore`.
- **Steps:**
  1. Run `place_subagents` / `bobp update` on a project with custom `.claude/agents/neo.md`; verify it is skipped with a sanitized message and untouched across two consecutive updates.
  2. Run `bobp install` / `bobp update` against symlinked `agents/`, `.claude`, `.codex`, `.gemini`, `*/agents`, `agents/.bobp-subagents`, and a regular file at `.codex`; verify exit `1` without raw traceback and zero partial writes across sibling harness dirs.
  3. Run `bobp update --dry-run <scratch>` on a drifted subagent file and confirm exact planned paths printed with zero writes.
  4. Run `bobp clean --yes` and verify `state.md`/`CHAT.md` reset while generated + custom subagent files stay intact.
  5. Test FIFO at manifest/target/`.gitignore` and symlinked `.gitignore` under `signal.alarm(5)`.
- **Expected observable outcome:** Custom agents survive; hostile parents/manifest abort cleanly (exit `1`, no traceback, zero partial writes); FIFOs/symlinks never block or get followed; `--dry-run` writes nothing; `clean --yes` leaves subagents intact.
- **Actual outcome:** All ownership, pre-flight symlink/regular-file/FIFO, `--dry-run`, idempotency, control-char sanitization, and `clean --yes` checks passed cleanly.
- **Verdict:** PASS
- **Evidence / issue:** `tests/test_subagent_layout.py` (`test_place_subagents_preserves_custom_files_and_tracks_manifest`, `test_preflight_refuses_symlinked_parents_and_manifest_with_zero_partial_writes`, `test_fifo_at_manifest_target_or_gitignore_never_blocks`, `test_cli_catches_hostile_symlink_and_exits_1_cleanly`, `test_preflight_refuses_regular_file_at_codex_and_symlinked_gitignore_is_safe`, `test_control_chars_sanitized_in_error_and_summary`)

### UAT-AGT-3: Git tracking (`.gitignore` allowlist), repo dogfooding, `diff`, `pull`, and documentation parity

- **Linked criterion:** `STORY-AGT-2` AC1–AC6
- **User / task:** Contributor cloning this repository or syncing updates via `bobp diff` / `bobp pull`.
- **Preconditions and data:** Live repository after updating `.gitignore` (`.claude/*` + `!.claude/agents/`), removing accidental 0-byte `.codex` file, and running `uv run bobp update .`; plus peer scratch projects for `diff`/`pull`.
- **Steps:**
  1. Run `git check-ignore -v .claude/agents/neo.md .claude/settings.local.json .claude/worktrees/x .codex/agents/neo.toml .gemini/agents/neo.md`.
  2. Verify `bobp install`, `bobp update`, and `bobp update --dry-run` warn when `.gitignore` hides harness subagent dirs wholesale (`.claude`, `.codex/`, `.gemini/**`) and stay silent for allowlist `.claude/*` + `!.claude/agents/`.
  3. Run `bobp diff` on a pre-Sprint-5 project (missing `.bobp-subagents` note) and on a drifted post-install project (reports drifted owned file, ignores custom agent).
  4. Run `bobp pull --dry-run <peer>` and `bobp pull <peer>` (updates owned subagent, ignores custom agent, skips symlinked `src` parent).
  5. Verify repo-parity test (`test_repo_committed_subagents_match_packaged_templates`) and living docs (`README.md`, `bobp/templates/README.md`, `.agents/skills/bob-tools/SKILL.md` + mirror, `docs/SDLC.md`).
- **Expected observable outcome:** `.claude/agents/`, `.codex/agents/`, `.gemini/agents/` tracked while `.claude/settings.local.json` and `.claude/worktrees/x` ignored; all 30 live repo subagents match compiled templates; `diff`/`pull`/`--dry-run` behave cleanly; docs & mirrors in sync.
- **Actual outcome:** `git check-ignore -v` ignored only `.claude/settings.local.json` and `.claude/worktrees/x` (exit `0`); `uv run bobp update .` created 10+10+10=30 real files; `test_repo_committed_subagents_match_packaged_templates` (30 subtests) and `test_install_update_dry_run_diff_pull_and_clean_end_to_end` passed; docs and packaged mirrors synced.
- **Verdict:** PASS
- **Evidence / issue:** `git check-ignore -v`, `uv run bobp update .`, `tests/test_subagent_layout.py`, `README.md`, `bobp/templates/README.md`, `bob-tools/SKILL.md`, `docs/SDLC.md`

### UAT-AGT-4: Evidence-backed Better/Worse evaluation report (`EVAL_SPRINT5_SUBAGENTS.md`)

- **Linked criterion:** `STORY-AGT-3` AC1–AC3
- **User / task:** Project owner deciding whether to keep, refine, or drop harness-native subagent definitions.
- **Preconditions and data:** Completed dogfooded repository, live installed `claude 2.1.331`, `codex-cli 0.172.0`, `gemini 0.40.1`, and `docs/sprints/EVAL_SPRINT5_SUBAGENTS.md`.
- **Steps:**
  1. Inspect `docs/sprints/EVAL_SPRINT5_SUBAGENTS.md` for all required sections: schema & live-harness discovery probes, byte/line/token & Git-churn measurements, Claude ↔ Codex ↔ Gemini switching walkthrough, maintenance/security/failure-mode comparison, explicit unmeasured items, and clear verdict + decision options.
  2. Verify every quantitative measurement cites its reproducible command and that unmeasured live-API behaviors are explicitly flagged.
- **Expected observable outcome:** Complete, honest, data-backed evaluation report with concrete Keep / Opt-in / Drop options and reproducible commands.
- **Actual outcome:** `docs/sprints/EVAL_SPRINT5_SUBAGENTS.md` records exact live CLI versions (`claude 2.1.331`, `codex-cli 0.172.0`, `gemini 0.40.1`), measured footprints (`+30` files, `+6,021` lines, `+413 KiB`, `~404` catalog tokens), dual-registration and Claude workflow-skill caveats, 3 explicit unmeasured paid-API items, and a clear Mixed / Net-Better recommendation with 3 actionable options.
- **Verdict:** PASS
- **Evidence / issue:** `docs/sprints/EVAL_SPRINT5_SUBAGENTS.md`

## Results and Handoff

- **Passed / failed / blocked:** 4 passed (`UAT-AGT-1`, `UAT-AGT-2`, `UAT-AGT-3`, `UAT-AGT-4`) / 0 failed / 0 blocked.
- **Open issues and impact:** Live paid multi-turn auto-delegation benchmarks across Claude/Codex/Gemini APIs remain unmeasured without explicit owner spend approval (documented transparently in `docs/sprints/EVAL_SPRINT5_SUBAGENTS.md` §5; Owner: User).
- **Overall verdict:** PASS — all Sprint 5 acceptance criteria verified via automated suite (`384 passed, 2 skipped, 435 subtests`), `git check-ignore`, live CLI probes, and SDLC gates.
- **Handoff evidence:** Smith `*user test SPRINT_5` APPROVED (`rubric UAT`: PASS across all 4 criteria; 30/30 live subagents & 9 read-only CLI probes verified; zero blocking UX defects) — recorded in `agents/CHAT.md` and archived in `agents/chat_archive/CHAT_SPRINT_5.md`.
