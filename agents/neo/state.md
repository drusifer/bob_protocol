# Agent State

## Context
### Recent Decisions
- User decided: persona folders are `agents/<name>/`, not `agents/<name>.docs/`. Applies to this
  repo's `agents/` tree and to the packaged templates, so new installs get the new layout.
- User decided: every tool and doc refers only to the new layout, with one exception —
  `bobp setup-agent-links` must convert older `.docs`-style projects to it. I first misread
  "no back compat" as "remove the conversion too" and pushed that in `bd660c3`; the user
  corrected it and the conversion is restored (`setup_agent_links.migrate_legacy_layout()`,
  the only code that knows the old layout). `bobp update` calls it before refreshing files.
- User asked for `setup-agent-links` to handle `.claude/skills` being a whole-directory symlink
  into `agents/`: it now replaces that link with a real directory before linking.

### Key Findings
- A persona is any folder directly under `agents/` holding a `SKILL.md`
  (`_common.find_persona_dirs()`); `skills/`, `templates/`, `chat_archive/` have none at that
  level, so they are not picked up. Template personas are found by `*/SKILL.md.txt`.
- `tests/test_bob_manage.py::test_install_via_the_real_cli` runs the real `setup_agent_links`.
  Before this session it wrote to the developer's real `~/.codex` — one run repointed the
  skill links and the Codex `via` MCP server at a deleted temp dir. It now sets a throwaway
  `CODEX_HOME`. Repaired by re-running `bobp setup-agent-links` here.
- In this repo `.claude/skills` used to be a symlink to `agents/skills`; it is now a real
  directory with 22 links (9 personas, 13 shared skills).

### Important Notes
- An older `.docs`-style project is converted by `bobp setup-agent-links` or `bobp update`:
  folders renamed, path references in agent docs rewritten. `pull`, `clean`, `diff` do not
  convert — run setup first in such a project.
- `CHAT.md`, `CHAT.diagram.md` and `chat_archive/` deliberately keep the old `.docs` paths as
  history.
- Still open from the 2026-08-06 make cleanup: `agents/skills/render/SKILL.md` has generic
  `make X` mentions that may want `bobp make X`; `agents/skills/judge/SKILL.md`'s
  `make judge-trace` / `trace_annotate.py` invocation model is stale. Neither was touched.

## Current Task
**Status:** Chat diagram loop summaries implemented; focused tests passed (20/20). Mermaid parser integration tests skipped because validator dependencies are unavailable.
**Assigned to:** Neo
**Started:** 2026-10-29

### Task Description
Update `bobp chat-diagram` to insert deterministic recap notes at phase, sprint, and epic loop boundaries.

### Progress
- [x] Detect phase boundaries from `phase <N>` markers and summarize the previous phase.
- [x] Summarize a sprint at `pm launch` and an epic at `plan epic` → `plan story` (or explicit `epic close`).
- [x] Keep canonical and packaged `bob-tools` guidance synchronized.
- [x] Run focused tests with `uv run --no-sync pytest tests/test_chat_diagram.py -q` (20 passed).
- [x] Regenerate `agents/CHAT.diagram.md` and record progress in `agents/CHAT.md`.

### Blockers
Mermaid syntax integration tests were skipped because validator dependencies are unavailable in this environment.

### Oracle Consultations
None.

## Next Steps
### Immediate Next Action
No further implementation work for this task. If validating Mermaid syntax is needed, install the validator dependencies and run the focused syntax test.

### Waiting On
- User review of the generated boundary recap behavior.

### Planned Work
- [ ] None queued.

---
*Last updated: 2026-10-29 18:17*
