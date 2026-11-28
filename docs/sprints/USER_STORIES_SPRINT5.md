# Sprint 5 User Stories: Harness-Native Subagent Definitions & Evaluation

*   **Branch**: none — the SDLC (§6) has no sprint branch; work lands on `main` and is committed only when the user directs
*   **Source**: the owner, 2026-11-28 ("I want harness-native subagent defs"; "I need to work across Claude, Codex, and Gemini and switch between them when i run out of tokens"; Option A compiled body with a single shared `state.md`; `.claude` gitignore was only for the old symlink issue; "yes lets do it and evaluate if it is better or wores")
*   **Status**: Approved — Gate 1 (Smith), Gate 2 (Smith), Gate 2b (Switch) passed (2026-11-28)

## Goal

When switching mid-task between **Claude Code**, **OpenAI Codex**, and **Gemini CLI** (for example when hitting token limits on one harness), every one of the 10 Bob Protocol personas is natively discoverable as a real project-local subagent in all three harnesses while sharing the exact same `agents/<persona>/state.md` and `agents/CHAT.md`. All subagent files are compiled deterministically from the 10 canonical persona `SKILL.md` sources on `bobp install` and `bobp update` (single source of truth, zero symlinks), tracked in Git, and evaluated objectively in a written report answering whether harness-native subagent definitions are better or worse than skills-only.

## Assumptions made for the owner

Owner decisions (2026-11-28):
1. Target the 3 harnesses the owner switches across: **Claude Code** (`.claude/agents/<persona>.md`), **OpenAI Codex** (`.codex/agents/<persona>.toml`), and **Gemini CLI** (`.gemini/agents/<persona>.md`).
2. Compile each persona's full instructions from the canonical persona `SKILL.md` (Option A) rather than thin wrapper stubs.
3. All 3 harnesses must share the **exact same** `agents/<persona>/state.md` and `agents/CHAT.md` (no harness-private memory).
4. Commit the generated subagent directories in Git and replace `.claude` in `.gitignore` with the least-privilege allowlist `.claude/*` + `!.claude/agents/` so `.claude/agents/` is tracked while local Claude settings, caches, and worktrees stay ignored.
5. Generate subagent definitions for the **10 personas only** (the 25 workflow/tool skills remain in `.agents/skills/`), inheriting the active session's model and tools so every persona can update `state.md` and run `bobp chat`.
6. Evaluate whether harness-native subagents are better or worse than skills-only.

Decided on the owner's behalf (confirmed by owner's go-ahead):
7. Never overwrite or delete a user-created custom subagent file in `.claude/agents/`, `.codex/agents/`, or `.gemini/agents/` that `bobp` did not place itself.
8. Do not add third-party Python dependencies (keep pure stdlib compatible with Python `>=3.10,<4` per `docs/SDLC.md` §1).

---

## STORY-AGT-1: Generate harness-native subagent definitions for Claude, Codex, and Gemini
**Owner:** Neo

**As a** developer switching between Claude Code, OpenAI Codex, and Gemini CLI mid-project,
**I want** `bobp install` and `bobp update` to generate real, spec-valid subagent definitions for all 10 personas in `.claude/agents/`, `.codex/agents/`, and `.gemini/agents/` directly from the packaged persona skills,
**so that** every persona works natively on turn 1 in all three harnesses while sharing one `agents/<persona>/state.md` and `agents/CHAT.md`.

### Acceptance Criteria
1. After `bobp install <dir>` or `bobp update <dir>`, all 10 Bob Protocol personas (`bob`, `cypher`, `morpheus`, `mouse`, `neo`, `oracle`, `smith`, `switch`, `tank`, `trin`) exist as real regular files (zero symlinks) in:
   - `<dir>/.claude/agents/<persona>.md` (valid YAML frontmatter with `name` and `description`, no `memory:` field, Markdown body compiled from the persona's `SKILL.md`)
   - `<dir>/.codex/agents/<persona>.toml` (valid TOML with `name`, `description`, and `developer_instructions` compiled from the persona's `SKILL.md`)
   - `<dir>/.gemini/agents/<persona>.md` (valid YAML frontmatter with `name`, `description`, `kind: local`, Markdown body compiled from the persona's `SKILL.md`)
2. None of the 25 shared workflow/tool skills (`make`, `sprint`, `chat`, etc.) are placed in `.claude/agents/`, `.codex/agents/`, or `.gemini/agents/`; they remain in `.agents/skills/`.
3. Every generated subagent omits hardcoded `model` pins, tool-blocking restrictions, and harness-private memory settings, and explicitly states that working memory is the shared `agents/<persona>/state.md` and `agents/CHAT.md` at the project root.
4. Ownership safety: `bobp` tracks which subagent files it placed; if a project already has its own custom file in `.claude/agents/`, `.codex/agents/`, or `.gemini/agents/` (even with a colliding persona name), `bobp` leaves it untouched and prints a clear skip message naming the path and reason.
5. Failure & hostile-tree safety: if any parent directory (`.claude`, `.claude/agents`, `.codex`, `.codex/agents`, `.gemini`, `.gemini/agents`) is a symlink or a non-directory file, `bobp` refuses to write through it and exits non-zero with an actionable error naming the path (SEC-005/006/007).
6. `bobp update --dry-run <dir>` previews the exact subagent files that would be added, refreshed, or skipped, writes zero files, and exits `0`.
7. Running `bobp update <dir>` a second time refreshes bobp-owned subagent files idempotently, leaves custom subagents and persona `state.md` / `CHAT.md` untouched, and creates zero symlinks.
8. Automated tests validate every generated file's syntax and schema (YAML frontmatter parsing for Claude/Gemini, TOML parsing for Codex, no control-character leaks, shared-state instruction present, zero hardcoded models, zero symlinks, hostile-symlink refusal, custom-agent preservation, and `--dry-run` immutability).

---

## STORY-AGT-2: Track in Git, dogfood in this repo, and update docs
**Owner:** Neo (repo & gitignore), Oracle (docs)
**Depends on:** STORY-AGT-1

**As a** maintainer or contributor cloning a Bob Protocol project,
**I want** the generated `.claude/agents/`, `.codex/agents/`, and `.gemini/agents/` directories committed in Git (not hidden by `.gitignore`) and accurately documented across the project's guides,
**so that** switching between Claude, Codex, and Gemini works immediately on any clone without extra setup or misleading docs.

### Acceptance Criteria
1. This repository's `.gitignore` replaces `.claude` with the least-privilege allowlist `.claude/*` and `!.claude/agents/` so `.claude/agents/` is trackable in Git while `.claude/settings.local.json`, worktrees, caches, and local agent memory stay ignored.
2. `bobp install` and `bobp update` warn the user (without silently editing their `.gitignore`) if a target project's `.gitignore` ignores `.claude`, `.codex`, or `.gemini` wholesale so the generated subagent directories would be hidden from Git.
3. Running `bobp update .` on this repository generates all 30 real subagent files (10 personas × 3 harnesses) under `.claude/agents/`, `.codex/agents/`, and `.gemini/agents/` and passes `bobp make test`.
4. `bobp diff <dir>` compares each bobp-owned subagent file (`.claude/agents/<p>.md`, `.codex/agents/<p>.toml`, `.gemini/agents/<p>.md`) against freshly compiled output from the packaged persona templates, reporting missing or differing files while ignoring user-created custom subagents.
5. `bobp pull <src>` updates existing bobp-owned subagent files from `<src>` alongside owned skills and templates (leaving custom user subagents untouched), and `bobp pull --dry-run <src>` lists any bobp-owned subagent files that would be updated while writing nothing.
6. Living documentation and packaged mirrors (`README.md`, `bobp/templates/README.md`, `.agents/skills/bob-tools/SKILL.md` + packaged mirror, and `docs/SDLC.md` §7) accurately document the three subagent directories, the shared `agents/<persona>/state.md` guarantee, and the updated Claude Code support (personas via `.claude/agents/`, shared workflow skills referenced in `.agents/skills/`).
7. Failure path: if a target project's `.gitignore` is a symlink or unreadable, the gitignore check treats it safely without crashing or following links (SEC-005).

---

## STORY-AGT-3: Evaluate whether harness-native subagents are better or worse
**Owner:** Trin (measurements & probes), Smith (UX/ergonomics), Morpheus (architecture tradeoffs)
**Depends on:** STORY-AGT-1, STORY-AGT-2

**As the** project owner deciding whether to keep, refine, or drop harness-native subagent definitions,
**I want** a concrete, evidence-backed evaluation report comparing skills-only vs. skills + harness-native subagent definitions across Claude Code, Codex, and Gemini CLI,
**so that** I can make an informed decision grounded in real measurements rather than speculation.

### Acceptance Criteria
1. A written report exists at `docs/sprints/EVAL_SPRINT5_SUBAGENTS.md` containing:
   - **Schema & live-harness discovery check:** Results of validating generated files against the locally installed `claude`, `codex`, and `gemini` CLIs (recording exact versions, commands run, and any schema/discovery gaps or caveats found without spending external paid API tokens unless explicitly approved).
   - **Context & token footprint comparison:** Measured file counts, byte/token sizes (chars ÷ 4), main-session metadata overhead vs. per-subagent startup cost, and Git diff churn across skills-only vs. skills + 30 generated subagent files.
   - **Cross-harness switching evaluation:** Concrete walkthrough of switching mid-task across Claude ↔ Codex ↔ Gemini using the shared `agents/<persona>/state.md` and `agents/CHAT.md`, noting what works seamlessly and where friction remains (e.g., Claude Code still not auto-discovering `.agents/skills/` workflow skills, Gemini CLI `context.fileName`, subagent isolation vs. single-thread persona switching).
   - **Maintenance, security & failure-mode comparison:** Sync/drift risk, ownership manifest complexity, blast radius on `bobp update`, and what happens if a harness changes its subagent schema.
   - **Clear verdict & recommendation:** Explicit "Better / Mixed / Worse" verdict with concrete reasons and actionable options (keep as default, make opt-in via flag, or drop).
2. Every quantitative claim in the report cites the exact measurement command or test artifact used to produce it.
3. Failure / limitation honesty: anything that could not be verified end-to-end without paid live API turns (e.g., probabilistic LLM delegation rates) is explicitly flagged as unmeasured rather than assumed.

---

## Out of Scope
- Generating subagent definitions for Cursor (`.cursor/agents/`) or GitHub Copilot (`.github/agents/`) — not requested by the owner for this sprint; can be added cleanly later if the evaluation recommends keeping the feature.
- Generating subagent definitions for the 25 shared workflow/tool skills (`make`, `sprint`, `chat`, etc.).
- Hardcoding model names or read-only tool sandboxes per persona (owner confirmed inherited defaults so every persona can update `state.md` and post to `CHAT.md`).
- Configuring harness-global user directories (`~/.claude/agents/`, `~/.codex/agents/`, `~/.gemini/agents/`) or modifying `~/.gemini/settings.json`.
- Running paid live LLM benchmark suites across Claude/Codex/Gemini APIs without explicit owner spend approval.
- Committing, bumping `bobp.__version__`, or releasing to PyPI (owner decision per `docs/SDLC.md` §6/§7).

## Open Questions
None — all material product choices were confirmed by the owner on 2026-11-28.

---

# Architecture Document: Sprint 5 — Harness-Native Subagent Definitions

*   **Status**: Approved — Gate 2 (Smith) & Gate 2b (Switch) passed (2026-11-28)
*   **Author**: Morpheus
*   **Last Updated**: 2026-11-28
*   **Scope**: Sprint 5 Architecture (`STORY-AGT-1`..`STORY-AGT-3`)

---

## 1. Executive Summary & System Overview

Bob Protocol keeps the 10 packaged persona `SKILL.md.txt` files as the **single source of truth** and adds a cohesive pure-stdlib module, `bobp/tools/_subagent_layout.py`, that compiles and manages 30 real project-local subagent definitions (10 personas × 3 harnesses: Claude Code `.claude/agents/<p>.md`, OpenAI Codex `.codex/agents/<p>.toml`, Gemini CLI `.gemini/agents/<p>.md`) during `bobp install` and `bobp update`. All three harnesses explicitly point every persona at the exact same root working memory (`agents/<persona>/state.md` and `agents/CHAT.md`) with zero harness-private memory, zero symlinks, and an ownership manifest (`agents/.bobp-subagents`) protecting custom user subagents. No new Python dependencies, runtimes, or Make targets are introduced.

## 2. System Context & Boundaries

- **Inputs:** Packaged persona `SKILL.md.txt` templates (`bobp/templates/agents/<persona>/SKILL.md.txt`), existing project directories, `agents/.bobp-subagents` ownership manifest, and `.gitignore`.
- **Outputs (strictly inside `<project>/`):**
  - `.claude/agents/<persona>.md` (10 files)
  - `.codex/agents/<persona>.toml` (10 files)
  - `.gemini/agents/<persona>.md` (10 files)
  - `agents/.bobp-subagents` (ownership manifest)
- **Trust Boundaries:** Target `<project>/` and `pull <src>` trees are untrusted (possibly cloned Git repos). Every harness parent directory, target file, `.gitignore`, and manifest is checked via `lstat` / `O_NOFOLLOW | O_NONBLOCK` + `S_ISREG` + size cap (SEC-005/006/007). Nothing is written outside `<project>/`, and no network calls are made.
- **Explicit Non-Interactions:** `bobp clean` leaves generated subagent files untouched (resets only `state.md` and `CHAT.md`). Shared workflow/tool skills (25 skills) remain solely in `.agents/skills/`.

## 3. Component & Container Architecture

### Component Inventory

| Component | Responsibility | Inputs | Outputs |
|---|---|---|---|
| `bobp/tools/_subagent_layout.py` (new) | Parse persona `SKILL.md` frontmatter/body; render Claude `.md`, Codex `.toml`, Gemini `.md`; pre-flight hostile-tree check; ownership manifest (`agents/.bobp-subagents`); `place_subagents(project, tmpl, dry_run)`; `gitignore_hides_subagents(project)`; `diff_subagents(project, tmpl)`; `summarize()`/`describe()` | `project: Path`, `tmpl: Path`, `dry_run: bool` | `list[Action]`, generated files, manifest, formatted summaries |
| `bobp/tools/_bob_manage.py` (edit) | Wire `place_subagents` + gitignore warning into `install()` and `update(dry_run=...)`; wire safe owned-subagent sync into `pull(src, dry_run=...)` and compiled comparison into `diff(target)` | CLI invocations (`install`, `update`, `pull`, `diff`) | Console summaries, updated project files, exit codes `0`/`1` |
| `bobp/tools/bob_{install,update,pull,diff,clean}.py` (edit) | Update `--help` descriptions to reflect generated subagent behavior (and note `clean` leaves subagent defs untouched) | CLI `-h/--help` | Accurate help output (exit `0`, zero side effects) |
| `.gitignore` (edit) | Replace `.claude` with least-privilege allowlist `.claude/*` + `!.claude/agents/` in this repo so `.claude/agents/` is tracked while local Claude files stay ignored | Repo `.gitignore` | Updated `.gitignore` |
| `tests/test_subagent_layout.py` (new) | Unit, schema (`tomllib` / YAML frontmatter), hostile-tree/symlink, manifest, `--dry-run`, `pull`/`diff`, and repo-parity tests | Packaged templates, tmp fixtures | Pytest pass/fail verdicts |
| `docs/sprints/EVAL_SPRINT5_SUBAGENTS.md` (new) | Evidence-backed comparative evaluation (schema probes vs live `claude`/`codex`/`gemini` CLIs, byte/token counts, cross-harness switching walkthrough, maintenance/security tradeoffs, verdict) | Measurements, CLI probes, review findings | Owner decision report |

## 4. Runtime Interaction & Critical Flows

### `bobp install` / `bobp update` Subagent Placement Flow
1. **Compile in memory:** Read the 10 packaged persona `SKILL.md.txt` files via `_skill_layout.template_skills(tmpl)` (`is_persona=True`), extract YAML `name`, `description`, and Markdown body, and render all 30 target texts in memory (failing fast if any packaged persona lacks valid `name`/`description`).
2. **Pre-flight hostile-tree check (before ANY write):** Verify non-symlink directory chains (`os.lstat` / `O_DIRECTORY | O_NOFOLLOW`) for `agents`, `.claude`, `.claude/agents`, `.codex`, `.codex/agents`, `.gemini`, `.gemini/agents`, and verify `agents/.bobp-subagents` is either absent (`ENOENT`) or a regular non-symlink file (not a symlink, dir, or FIFO). If any check fails, abort immediately with `SubagentLayoutError` (sanitized path via `_skill_layout.printable()`, caught in `_bob_manage.py` → stderr, exit `1`, zero partial writes across harnesses).
3. **Read ownership manifest:** Open `agents/.bobp-subagents` via `_read_regular_safe()` (non-symlink parent `agents/` + `O_RDONLY | O_NONBLOCK | O_NOFOLLOW` + `S_ISREG` + looped read up to `64 KiB + 1`, failing closed on oversize or decode error). Validate lines without regex (`len(line) <= 128`, exact harness prefix/suffix match, `_skill_layout.valid_name(stem)`).
4. **Plan & execute per target (30 files):**
   - Inspect target path via single `os.lstat(dest)`.
   - Symlink at target path → `Action("skipped", rel, "symlink; refusing to overwrite")`.
   - Non-regular existing file (dir/FIFO) → `Action("skipped", rel, "not a regular file")`.
   - Existing regular file not in `owned` → `Action("skipped", rel, "exists and was not installed by bobp")`.
   - Missing → `Action("create", rel)` (write atomically via `write_text_safely` unless `dry_run=True`).
   - Owned regular file → `Action("replace", rel)` (write atomically via `write_text_safely` unless `dry_run=True`).
5. **Write manifest & report:** When `not dry_run`, atomically write `agents/.bobp-subagents` via `write_text_safely`.
   - Normal run: print concise per-harness counts (`Subagents in .claude/agents/: X added, Y refreshed, Z skipped.`) plus every skipped file with `_skill_layout.printable()`.
   - `--dry-run`: print per-harness counts plus every exact planned path (`would create`/`would refresh`/`skipped`) and write zero files.
6. **`.gitignore` check (both `install` and `update`, including `--dry-run`):** Read `<project>/.gitignore` via `_read_regular_safe(project, ".gitignore", 256 * 1024)` (fail-closed on symlink/FIFO/oversize). Check exact non-comment line membership for `.claude`, `.claude/`, `/.claude`, `/.claude/`, `.claude/*`, `/.claude/*`, `.claude/**`, `/.claude/**` (and equivalents for `.codex`/`.gemini`), respecting Git negation semantics: wholesale `<dir>` / `<dir>/` always hides `<dir>/agents/`; `<dir>/*` / `<dir>/**` hides it unless negated by `!<dir>/agents` or `!<dir>/agents/` (or `/`-prefixed equivalent). Print an actionable note naming the hidden directory(ies) without modifying `.gitignore`.

### `bobp pull` & `bobp diff` Flows
- **`bobp diff <dir>`:** Verifies non-symlink parent directory chains (`agents`, `.claude`, `.claude/agents`, `.codex`, `.codex/agents`, `.gemini`, `.gemini/agents`). If `agents/.bobp-subagents` is absent, prints `Note: agents/.bobp-subagents missing (pre-Sprint 5 install); run bobp update <printable(dir)> to generate harness subagents.` Otherwise compiles the 30 expected files and compares each bobp-owned path (read via `_read_regular_safe()` with parent-dir verification) against the target, reporting `Only in template: <rel>` or `Files differ: <rel>` while ignoring custom user subagents.
- **`bobp pull <src>` (and `--dry-run`):** Reads `agents/.bobp-subagents` from the destination project via `_read_regular_safe()`. Before every read/write, verifies non-symlink parent directory chains in **both** `src` and `root` (`.claude`, `.claude/agents`, `.codex`, `.codex/agents`, `.gemini`, `.gemini/agents`) and reads both `src/<rel>` and checks `root/<rel>` with `_read_regular_safe(..., max_bytes=1 MiB)` (fail closed on oversize/symlink/FIFO); updates `root/<rel>` atomically via `write_text_safely` (or prints `would update <printable(rel)>` under `--dry-run`), never touching custom user subagents.

## 5. Interface & Contract Specifications

### Generated File Formats

All persona `SKILL.md.txt` sources are parsed with a **line-by-line frontmatter scan** (no multiline regex: line 0 must be `---`, scan until closing `---`, split `key: value` on first `:`, require `_skill_layout.valid_name(name)` and `name == dir_name`, reject empty `description`).

1. **Claude Code — `.claude/agents/<persona>.md`**
   - Line 1 starts with `---` (YAML frontmatter): `name` and single-line double-quoted YAML `description` (`_yaml_double_quote`: escapes `\`, `"`, `\n`, `\r`, `<0x20`, `\x7f`, `\x80-\x9f`, `\u2028`, `\u2029`) only — no `memory:`, no `model:`, no `tools:`/`disallowedTools:`.
   - Immediately after closing `---`: HTML generated-file comment + prominent `**Shared Working Memory:**` preamble naming `agents/<persona>/state.md` and `agents/CHAT.md` + persona `SKILL.md` body.
2. **Gemini CLI — `.gemini/agents/<persona>.md`**
   - Line 1 starts with `---` (YAML frontmatter): `name`, single-line double-quoted YAML `description`, and `kind: local` (no `model:`, no `tools:`).
   - Same generated-file comment, `**Shared Working Memory:**` preamble, and persona body.
3. **OpenAI Codex — `.codex/agents/<persona>.toml`**
   - Line 1 `# Generated by bobp from .agents/skills/<persona>/SKILL.md — overwritten by bobp update.`
   - Keys: `name`, `description` (TOML basic strings escaping `\`, `"`, `\b`, `\t`, `\n`, `\f`, `\r`, and all remaining `<0x20` plus `\x7f` as `\u00XX`), and `developer_instructions` (TOML multiline basic string `"""\n...\n"""` normalizing `\r\n`/`\r` → `\n`, escaping `\` → `\\`, escaping runs of 3+ quotes `"{3,}` → `\"` × len, and escaping `<0x20` except `\n`/`\t` plus `\x7f` as `\u00XX`; no `model` or `sandbox_mode`).
   - Serialized using pure Python stdlib (zero runtime dependency, Python 3.10+ compatible) and verified by `tomllib.loads()` round-trip in pytest on Python 3.11+.

### Ownership Manifest (`agents/.bobp-subagents`)
- UTF-8 regular file, sorted project-relative POSIX paths (one per line), e.g. `.claude/agents/neo.md`, max 64 KiB (fail closed if `> 64 KiB`).
- Validated **without regex**: `len(line) <= 128`, exact prefix/suffix match against the 3 harness specs (`(".claude/agents/", ".md")`, `(".codex/agents/", ".toml")`, `(".gemini/agents/", ".md")`), and `_skill_layout.valid_name(stem)`.

## 6. Cross-Cutting Concepts & Resilience

### Failure Modes & Error Handling
| Failure Mode | Trigger / Condition | System Behavior | User Impact | Blast Radius |
|---|---|---|---|---|
| Hostile symlinked harness dir | `.claude`, `.codex`, `.gemini` or `*/agents` is a symlink or file | Pre-flight check raises `SubagentLayoutError` before any write; CLI prints sanitized error to stderr, exits `1` | Clear path & reason; zero partial writes | None (zero files modified) |
| Hostile manifest | `agents/.bobp-subagents` is a symlink, dir, or FIFO | Pre-flight check refuses to read/overwrite; exits `1` | Clear error naming manifest | None |
| Custom colliding subagent | User created `.claude/agents/neo.md` not in manifest | Skipped and reported with sanitized path + reason; other files proceed | User file preserved intact | Isolated to skipped file |
| Symlinked `.gitignore` | Target `.gitignore` is a symlink or FIFO | `_read_regular_safe()` returns `None`; warning skipped without blocking/following | Command completes cleanly | None |
| Symlink in `bobp pull <src>` | Source or dest subagent file is a symlink | Skipped safely without reading/writing through symlink | Safe refusal; no secret exfiltration or overwrite | Isolated to skipped file |

### Security & Privacy
- **Trust / access boundaries:** All filesystem reads on untrusted project files (`agents/.bobp-subagents`, `.gitignore`, `pull` source/dest, `diff` targets) use `os.open(..., O_RDONLY | O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))` + `stat.S_ISREG` + size cap (SEC-005). All writes use `_common.write_text_safely()` (atomic temp-file + `os.replace`, SEC-006). All echoed paths pass through `_skill_layout.printable()` (SEC-007).
- **Sensitive data:** No credentials, tokens, or user-global paths (`~/.claude`, `~/.codex`, `~/.gemini`) are read or modified.

## 7. Technical Stack & SDLC / Build Impact

* **Languages & Runtime:** Python `>=3.10,<4` (dev 3.15 via `uv`). Pure standard library only (custom minimal YAML/TOML emitter for Python 3.10 compatibility; `tomllib` used in tests on Python 3.11+ with a clean fallback/guard).
* **Core Libraries & Tools:** `pytest` (existing dev dependency).
* **Build-Environment Check (CRITICAL):**
  * Does this design add a new language, package manager, runtime version, or external tool? **No** — no Tank Phase 0 required.
  * Routine change under `docs/SDLC.md` §6; Tank updates `docs/SDLC.md` §7 at Stage 3 closeout.

## 8. Architectural Decisions (ADRs) & Technical Debt

### Decision Records
* **ADR-S5-1 (Dedicated `_subagent_layout.py` module + separate `agents/.bobp-subagents` manifest):** Keep subagent compilation and ownership isolated from `_skill_layout.py` (`agents/.bobp-skills`) so skills (directory-level, 35 entries) and subagents (file-level, 30 entries across 3 harnesses) remain cleanly decoupled and independently testable (and trivially removable if the evaluation recommends dropping them).
* **ADR-S5-2 (Pure stdlib TOML/YAML emitter for Python 3.10+):** Avoid adding `tomli-w` or `PyYAML` to `pyproject.toml`; emitting 2–3 fixed flat keys (`name`, `description`, `kind`/`developer_instructions`) is ~35 lines of auditable stdlib code, validated by `tomllib.loads()` in tests on Python 3.11+.
* **ADR-S5-3 (Compiled full body + top shared-state preamble, no harness-private memory/model/tools):** Compiles each persona's full `SKILL.md` body with a top `**Shared Working Memory:**` preamble pointing to `agents/<persona>/state.md` and `agents/CHAT.md`, omitting `memory:`, `model`, and tool blocks so switching Claude ↔ Codex ↔ Gemini never splits state or breaks `bobp chat` / `state.md` exit gates.
* **ADR-S5-4 (Pre-flight validation across all 3 harness dirs before first write):** Prevents partial cross-harness updates when one harness directory contains a hostile symlink.

### Acknowledged Technical Debt & Trade-offs
* **30 generated files in Git:** Committing `.claude/agents/`, `.codex/agents/`, and `.gemini/agents/` duplicates persona prompt prose across 3 directories in Git diffs whenever a persona skill changes. Sprint 5's `STORY-AGT-3` evaluation explicitly measures this diff/token cost so the owner can decide whether to keep default generation, make it opt-in, or drop it.
* **Claude Code shared workflow skills:** `.claude/agents/*.md` gives Claude Code native access to all 10 personas, but Claude Code still does not auto-discover the 25 shared workflow skills in `.agents/skills/` (personas read them on demand via file reads). Recorded openly in docs and the evaluation report.

