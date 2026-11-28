# UAT Plan: Sprint 3 — Spec-Compliant Skills, No Links

- **Stories / criteria:** `STORY-SKL-1` through `STORY-SKL-6` (and Owner Amendment 2026-11-01: final skill directory `.agents/skills/`, real files, no symlinks) in [`docs/sprints/USER_STORIES_SPRINT3.md`](USER_STORIES_SPRINT3.md)
- **Environment and build:** `bobp` 0.3.1 (working tree on `main`, Python 3.15 / `uv` `.venv/`, Linux; clean rebuild verified via `distclean` → `install` → `test` → `lint` → `security-scan` → `build`)
- **Date / tester:** 2026-11-28 / Trin (author & E2E verification), Smith (end-to-end UX acceptance)
- **Entry conditions:** Phases 1–7 complete and gated (Trin UAT, Switch Gate 5a, Morpheus `APPROVE`); `docs/SDLC.md` updated and Tank conformance check passed (`368 passed, 2 skipped, 397 subtests`); live paid Codex+TypeSafe `bobp persona-eval` execution explicitly deferred pending owner approval (Task 3b.3 / SDLC §9).
- **Exit conditions:** All in-scope acceptance scenarios pass (with owner-approved deferral for live paid evals explicitly recorded); zero regressions across `bobp make test`, `lint`, `security-scan`, and `build`; Smith usability sign-off recorded in `agents/CHAT.md`.

## Scenarios

### UAT-SKL-1: Fresh `bobp install` creates real, spec-conformant `.agents/skills/` with zero symlinks

- **Linked criterion:** `STORY-SKL-1` AC1–AC7 (with Owner Amendment `.agents/skills/`), `STORY-SKL-3` AC1, AC4
- **User / task:** Project owner running `bobp install <dir>` on a new project directory.
- **Preconditions and data:** Empty temporary scratch directory (`build/uat_sprint3/fresh`) with isolated `HOME` and `CODEX_HOME`.
- **Steps:**
  1. Run `bobp install <scratch>` and inspect `<scratch>/.agents/skills/`, `<scratch>/agents/`, `<scratch>/AGENTS.md`, and `CODEX_HOME`.
  2. Verify no symlinks exist anywhere under `<scratch>` (including `.agents/skills/`) and no `CODEX_HOME/skills/` directory is created; confirm all 35 skills (10 personas + 25 shared skills) exist as regular `SKILL.md` files, persona memory (`state.md`) stays in `agents/<persona>/`, `agents/.bobp-skills` and `agents/.bobp-version` exist, and `agents/AGENTS.md` does not exist.
  3. Run `bobp make test` (`tests/test_skill_spec.py` and `tests/test_skill_layout.py`).
- **Expected observable outcome:** Exit `0`; 35 real skill directories under `.agents/skills/`; zero symlinks; root `AGENTS.md` created as a regular file; spec test suite passes.
- **Actual outcome:** Exit `0`; 35 real skill directories installed under `.agents/skills/`; zero symlinks under project; zero `CODEX_HOME/skills/` links (only documented Via MCP `config.toml` registered when `codex`+`via` are present); root `AGENTS.md` created as regular file; no `agents/AGENTS.md`; `agents/.bobp-skills` and `agents/.bobp-version` written; full suite green (`368 passed, 397 subtests`).
- **Verdict:** PASS
- **Evidence / issue:** Live scratch run (`build/uat_sprint3/fresh`, cleaned) + `tests/test_skill_layout.py`, `tests/test_skill_spec.py`, `tests/test_bob_manage.py`

### UAT-SKL-2: Legacy migration, selective link removal, ownership preservation, idempotent `bobp update`, and harness-discovery notice

- **Linked criterion:** `STORY-SKL-1` AC5–AC6, `STORY-SKL-2` AC1–AC6, `STORY-SKL-3` AC2–AC5 (with Owner Amendment 2026-11-01 `.agents/skills/`)
- **User / task:** Existing Bob Protocol user upgrading an older project containing legacy symlinks (`.agents -> agents`, `AGENTS.md -> agents/AGENTS.md`), `agents/skills/`, `agents/neo/SKILL.md`, a project-owned skill (`custom-team-skill`), a real `GEMINI.md`, an external symlink (`.cursorrules -> /etc/hosts`), and custom `agents/neo/state.md`.
- **Preconditions and data:** Isolated fixture project (`build/uat_sprint3/legacy`) seeded in the pre-Sprint-3 layout, plus repo `README.md` and `bobp/templates/README.md`.
- **Steps:**
  1. Run `bobp update --dry-run <fixture>` first and confirm zero filesystem writes (`.agents` and `AGENTS.md` symlinks still intact).
  2. Run `bobp update <fixture>` and verify legacy bobp links vanish, external symlink (`.cursorrules -> /etc/hosts`), real `GEMINI.md`, `custom-team-skill`, and `agents/neo/state.md` remain untouched, legacy `AGENTS.md` symlink becomes a real file preserving its text, and skills move to `.agents/skills/`.
  3. Run `bobp update <fixture>` a second time and verify it exits `0` as a no-op with nothing left to migrate.
  4. Verify `STORY-SKL-3 AC5` (with Owner Amendment): confirm `bobp install` / `bobp update` stdout AND both `README.md` and `bobp/templates/README.md` explicitly state that `.agents/skills/` is not discovered by Claude Code and that Gemini CLI requires `context.fileName` to include `"AGENTS.md"`.
- **Expected observable outcome:** `--dry-run` previews without modifying files; real `update` migrates cleanly and prints a concise summary; second `update` reports nothing to migrate; no symlinks created anywhere; `install`/`update` output and both READMEs state the Claude Code `.agents/skills/` limitation and Gemini CLI `context.fileName` requirement.
- **Actual outcome:** `update --dry-run` exited `0` with zero writes (`.agents` and `AGENTS.md` remained symlinks); first `update` exited `0`, replaced `.agents` symlink with real `.agents/skills/`, preserved `custom-team-skill`, real `GEMINI.md`, external `.cursorrules -> /etc/hosts`, `MY ROOT AGENTS` in regular root `AGENTS.md`, and `KEEP ME` in `agents/neo/state.md`; second `update` exited `0` as a no-op; `bobp install` and `bobp update` both printed `Claude Code does not read .agents/skills/; Gemini CLI also needs context.fileName to include "AGENTS.md" in its own settings.`, and `README.md` (`### Harness discovery (skills and AGENTS.md)`) plus `bobp/templates/README.md` (`### Harness discovery (skills and AGENTS.md)`) document both caveats.
- **Verdict:** PASS
- **Evidence / issue:** Live scratch runs (`build/uat_sprint3/{fresh,legacy}`, cleaned), `bobp/tools/setup_agent_links.py:513-516`, `README.md` & `bobp/templates/README.md`, `tests/test_skill_layout.py`, `tests/test_bob_manage.py`, `tests/test_cli_help.py::test_update_dry_run_handles_legacy_agents_symlink_without_crashing`

### UAT-SKL-3: Per-skill `evals/evals.json`, `--list --json`, and evaluating-skills workspace contract

- **Linked criterion:** `STORY-SKL-4` AC1–AC12
- **User / task:** Maintainer inspecting and validating persona evaluation suites.
- **Preconditions and data:** Current workspace with `bobp/templates/agents/**/evals/evals.json` and removed `catalog.json`.
- **Steps:**
  1. Run `uv run bobp persona-eval --list` and `uv run bobp persona-eval --list --json`.
  2. Verify 11 suites are listed, `--list --json` prints a valid 11-element JSON array on stdout only, and `catalog.json` is absent across code and living docs.
  3. Verify malformed `evals.json` (missing field, duplicate ID, path escape) fails naming file and field, and evaluating-skills workspace (`iteration-N`, `--baseline without-skill|previous`, `grading.json`, `benchmark.json`, `feedback.json`) invariants pass in `tests/test_persona_eval.py`.
- **Expected observable outcome:** 11 suites match prior names; JSON output parses cleanly; malformed eval fixtures reject safely; workspace/benchmark tests pass. (Live paid Codex+TypeSafe execution deferred pending owner approval per Task 3b.3.)
- **Actual outcome:** `bobp persona-eval --list --json` exited `0` returning a valid JSON array of 11 suites; zero stale `catalog.json` hits in code or living docs; all `tests/test_persona_eval.py` unit, validation, and offline Promptfoo workspace/benchmark tests pass. Live paid Codex+TypeSafe run remains explicitly deferred pending owner approval.
- **Verdict:** PASS (offline & CLI contract verified; live paid eval deferred per Task 3b.3)
- **Evidence / issue:** Live `bobp persona-eval --list --json` + `tests/test_persona_eval.py`

### UAT-SKL-4: Agent Skills best practices — size budgets, `references/`, descriptions, Gotchas, parity, and cleanup

- **Linked criterion:** `STORY-SKL-5` AC1–AC9, `STORY-SKL-6` AC8–AC10
- **User / task:** Agent loading any of the 35 shipped skills.
- **Preconditions and data:** Canonical `.agents/skills/` and packaged `bobp/templates/agents/`.
- **Steps:**
  1. Run `bobp make test-q ARGS="-k skill_spec"` to enforce ≤500 lines & ≤4,500 tokens per skill, conditional `references/` pointers, trigger phrasing (`use when`/`use for`/`use to`) on all 35 descriptions, `compatibility` on skills invoking `bobp`, `## Gotchas` on `make`, `security`, `bob-protocol`, `sprint`, `build-env`, zero `InvestaCo`/`agents/tools` remnants, zero `__pycache__` under `agents/`, and canonical-vs-packaged parity.
  2. Verify `sprint/references/{sprint-close,loop-rubric}.md` and `build-env/references/{language-conventions,sdlc-guide}.md` exist in both canonical and packaged trees, and mirror docs (`STARTUP.md`, `SHORTHAND_GUIDE.md`, `docs/PERSONA_EVALUATION.md`, `agents/DOCUMENTATION_INDEX.md`) match `bobp/templates/`.
- **Expected observable outcome:** All spec and best-practice subtests pass with zero drift between canonical and packaged skills/docs.
- **Actual outcome:** All 12 `test_skill_spec.py` tests (320 subtests) pass; `diff -u` confirmed zero drift across all 4 mirrored doc pairs and all 35 canonical/packaged skills.
- **Verdict:** PASS
- **Evidence / issue:** `tests/test_skill_spec.py` + `diff -u` mirror verification (`MIRRORS_OK`)

### UAT-SKL-5: Agent-safe CLI (`--help`, `--dry-run`, `clean --yes`, exit codes) and negative paths

- **Linked criterion:** `STORY-SKL-6` AC1–AC6 (AC7 progress-to-stderr intentionally omitted per story opt-out so existing stdout scripts stay unbroken)
- **User / task:** Non-interactive agent discovering and previewing `bobp` subcommands safely.
- **Preconditions and data:** Scratch project directory (`build/uat_sprint3/fresh`) plus isolated `HOME` and `CODEX_HOME`, and `tests/test_cli_help.py`.
- **Steps:**
  1. Run `bobp --help` and `bobp <subcommand> --help` / `-h` across all 17 registered subcommands (including `setup-agent-links`, `tldr`, `make`, `prep-tldr`) and verify zero file changes across project, `HOME`, and `CODEX_HOME`, plus `Exit codes:` (`0`/`1`/`2`) and no version-check stderr notice.
  2. Run `bobp make help` to confirm project Makefile help still works.
  3. Run `bobp clean` (without `--yes`) on a modified `agents/neo/state.md`, then `bobp clean --dry-run`, then `bobp clean --yes`.
  4. Run `bobp update --dry-run` and `bobp pull --dry-run` and confirm zero writes.
- **Expected observable outcome:** Every `--help`/`-h` exits `0` with `Exit codes:` and zero side effects; `bobp make help` runs project Makefile help; `bobp clean` without `--yes` exits `2` leaving files intact; `--dry-run` previews and exits `0` without writes; `bobp clean --yes` resets state and exits `0`.
- **Actual outcome:** All 17 subcommands passed `--help`/`-h` zero-side-effect and exit-code checks (`tests/test_cli_help.py`); live scratch run confirmed `clean` without `--yes` exited `2` preserving `DIRTY STATE`, `clean --dry-run` exited `0` preserving `DIRTY STATE`, and `clean --yes` exited `0` resetting `state.md`.
- **Verdict:** PASS
- **Evidence / issue:** Live scratch run + `tests/test_cli_help.py`, `tests/test_bob_manage.py`

## Results and Handoff

- **Passed / failed / blocked:** 5 passed (`UAT-SKL-1`, `UAT-SKL-2`, `UAT-SKL-3`, `UAT-SKL-4`, `UAT-SKL-5`) / 0 failed / 0 blocked.
- **Open issues and impact:**
  - Live paid Codex+TypeSafe `bobp persona-eval` execution remains deferred pending explicit owner approval (Task 3b.3 / `docs/SDLC.md` §9; Owner: User / Trin).
  - `STORY-SKL-6 AC7` (routing progress lines to stderr) intentionally omitted per story opt-out to preserve existing stdout parsers (Owner: Cypher / Neo).
- **Overall verdict:** PASS — all Sprint 3 acceptance criteria verified via automated suite (`368 passed, 2 skipped, 397 subtests`), clean rebuild (`distclean` → `install` → `test` → `lint` → `security-scan` → `build`), and live scratch CLI UAT.
- **Handoff evidence:** Smith `*user test SPRINT_3` APPROVED (`rubric UAT`: `COVER=PASS STEPS=PASS FAIL=PASS DATA=PASS EVID=PASS`; `rubric LESSON`: all PASS) — recorded in `agents/CHAT.md` and archived in `agents/chat_archive/CHAT_SPRINT_3.md`.
