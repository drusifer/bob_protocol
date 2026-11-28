# Sprint 5 Task Board: Harness-Native Subagent Definitions & Evaluation

*   **Goal**: Compile 30 real project-local subagent definitions (10 personas × 3 harnesses: `.claude/agents/*.md`, `.codex/agents/*.toml`, `.gemini/agents/*.md`) from the canonical persona `SKILL.md` files sharing one `agents/<persona>/state.md` and `agents/CHAT.md`, track them in Git, dogfood in this repo, and produce an evidence-backed Better/Worse evaluation report (`docs/sprints/EVAL_SPRINT5_SUBAGENTS.md`).
*   **Tier**: Tier 1 (Major) — stories and architecture in `docs/sprints/USER_STORIES_SPRINT5.md` (Sprint 3's completed board is archived at `docs/sprints/TASK_SPRINT3.md`).
*   **Branch**: none (`docs/SDLC.md` §6 has no sprint branch; commit only when directed by the owner)
*   **Status**: Complete — Sprint 5 Launched (2026-11-28; commits/version bump/release remain owner's decision per `docs/SDLC.md` §6/§7)

---

## Stage 0: SDLC Gate (Blocker)

- [x] **Task 0.1:** Verify `docs/SDLC.md` exists and is current. (*Owner: Mouse | Trace: N/A — sprint gate | Verification: `test -f docs/SDLC.md`*) — verified 2026-11-28. Pure Python stdlib (`>=3.10,<4`), no new dependency, runtime, or Make target; no Tank Phase 0 required.

---

## Sprint Execution Phases

### Phase 1: Subagent compiler, layout safety, and CLI integration
*Phase goal: `bobp/tools/_subagent_layout.py` safely compiles and manages all 30 subagent files across Claude Code, Codex, and Gemini CLI with `agents/.bobp-subagents` ownership manifest, pre-flight hostile-tree checks, safe `pull`/`diff`/`--dry-run`, updated CLI `--help`, and comprehensive schema + security tests.*
- [x] **Task 1.1:** Tests first (`tests/test_subagent_layout.py` covering YAML/TOML round-trips, adversarial escaping, single shared `state.md` preamble, no `memory:`/`model`/`tools:`, custom agent preservation, alarm-guarded symlink/FIFO pre-flight & `pull`/`diff` parent checks, SEC-007 control-char sanitization, 50k-char linear-time bounds, `--dry-run` immutability, `.gitignore` negation checks), then implement `bobp/tools/_subagent_layout.py`, wire into `bobp/tools/_bob_manage.py` (`install`, `update`, `pull`, `diff`, caught `SubagentLayoutError` → stderr exit `1`), and update `--help` in `bobp/tools/bob_{install,update,pull,diff,clean}.py`. (*Owner: Neo | Level: L3 — new filesystem trust-boundary module, custom stdlib YAML/TOML emitters, touches 4 CLI subcommands | Trace: STORY-AGT-1 AC1–8, STORY-AGT-2 AC2/4/5/7, ADR-S5-1..4 | Verification: `bobp make test-q ARGS="-k subagent"` then `bobp make test`*)
- [x] **Task 1.2:** UAT: install, update (`--dry-run` + real + idempotent 2nd run), pull (`--dry-run` + real), diff (pre-Sprint-5 & post-install), custom agent survival, and hostile symlink rejection in scratch projects. (*Owner: Trin | Level: L2 | Trace: STORY-AGT-1 AC1–8, STORY-AGT-2 AC2/4/5/7 | Verification: UAT verdict and evidence in `agents/CHAT.md`*)
- [x] **Task 1.3:** Security review (Gate 5a): verify all 5 Design Gate 2b hardening items (`TH-S5-1`..`5`), parent-dir checks, YAML/TOML escaping, regex-free manifest/frontmatter parsing, fail-closed `max_bytes + 1` reads, and security regression tests. (*Owner: Switch | Level: L2 | Trace: Design Gate 2b | Verification: `security gate (phase 1): ...` verdict line in `agents/CHAT.md`*)
- [x] **Task 1.4:** Code review and `ADR-S5-1..4` compliance. (*Owner: Morpheus | Level: L2 | Trace: STORY-AGT-1/2, ADR-S5-1..4 | Verification: review result recorded in `agents/CHAT.md`*)

### Phase 2: Repo dogfooding, documentation updates, and Better/Worse evaluation
*Phase goal: `.gitignore` uses `.claude/*` + `!.claude/agents/`, stray 0-byte `.codex` file is removed so `bobp update .` generates all 30 real subagent files on this repo, living docs & mirrors are synced, and `docs/sprints/EVAL_SPRINT5_SUBAGENTS.md` delivers an evidence-backed Better/Worse evaluation.*
- [x] **Task 2.1:** Update `.gitignore` (`.claude/*` + `!.claude/agents/`), remove stray 0-byte `.codex` regular file, run `bobp update .` to generate all 30 real subagent files in this repo, add a repo-parity test ensuring committed subagents match packaged templates, and update `README.md`, `bobp/templates/README.md`, `.agents/skills/bob-tools/SKILL.md` (+ packaged mirror). (*Owner: Neo & Oracle | Level: L2 — dogfood repo migration & doc sync | Trace: STORY-AGT-2 AC1/3/6 | Verification: `bobp make test` and `diff` checks on mirrors*)
- [x] **Task 2.2:** Run live read-only discovery/schema measurements against installed `claude`, `codex`, and `gemini` CLIs + byte/token/Git-churn measurements, and author `docs/sprints/EVAL_SPRINT5_SUBAGENTS.md` (with Trin measurements, Smith UX ergonomics, and Morpheus architecture tradeoffs + clear Better/Mixed/Worse verdict). (*Owner: Trin, Smith, Morpheus | Level: L2 — empirical evaluation & recommendation | Trace: STORY-AGT-3 AC1–3 | Verification: `docs/sprints/EVAL_SPRINT5_SUBAGENTS.md` reviewed and cited commands reproducible*)
- [x] **Task 2.3:** Security review quick pass (Phase 2: `.gitignore` allowlist verification, generated files clean, `bobp make security-scan`). (*Owner: Switch | Level: L1 | Trace: TH-S5-2 | Verification: `security gate (phase 2): ...` verdict line in `agents/CHAT.md`*)
- [x] **Task 2.4:** Review repo dogfood diff, doc parity, and evaluation report completeness. (*Owner: Morpheus | Level: L2 | Trace: STORY-AGT-2/3 | Verification: review result recorded in `agents/CHAT.md`*)

---

## Stage 3: Sprint Closeout

- [x] **Task C.1:** Update `docs/SDLC.md` §7 for harness-native subagents and run Tank conformance check (`bobp make test`, `lint`, `security-scan`, `build`). (*Owner: Tank | Level: L2 | Trace: STORY-AGT-2 AC6 | Verification: all SDLC gates green in `agents/CHAT.md`*)
- [x] **Task C.2:** Oracle SDLC rubric review (`SDLC` rubric) + doc grooming check, followed post-launch by `bobp chat-report --moniker SPRINT_5`. (*Owner: Oracle | Level: L1 | Trace: N/A — closeout | Verification: `SDLC` rubric PASS & archived `CHAT_SPRINT_5.md`*)
- [x] **Task C.3:** Author `docs/sprints/UAT_PLAN_SPRINT5.md` (Trin) and run Smith end-to-end UX & UAT acceptance (`rubric UAT` + live CLI probes + review of `EVAL_SPRINT5_SUBAGENTS.md`). (*Owner: Smith | Level: L2 | Trace: STORY-AGT-1..3 | Verification: Smith `APPROVE` in `agents/CHAT.md`*)
- [x] **Task C.4:** Sprint 5 retrospective and backlog grooming (`agents/mouse/sprint_log.md`). (*Owner: Mouse | Level: L1 | Trace: N/A — closeout | Verification: retros posted in `agents/CHAT.md`*)
- [x] **Task C.5:** Cypher `*pm launch SPRINT_5` (commits/version bump/release remain owner's decision per `docs/SDLC.md` §6/§7). (*Owner: Cypher | Level: L1 | Trace: N/A — release decision | Verification: launch posted in `agents/CHAT.md`*)
