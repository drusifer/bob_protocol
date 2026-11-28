# Sprint 5 Comparative Evaluation: Harness-Native Subagent Definitions vs. Skills-Only

- **Date:** 2026-11-28
- **Authors:** Trin (measurements & live CLI probes), Smith (UX & cross-harness ergonomics), Morpheus (architecture & maintenance tradeoffs)
- **Stories:** `STORY-AGT-1`, `STORY-AGT-2`, `STORY-AGT-3` in [`USER_STORIES_SPRINT5.md`](USER_STORIES_SPRINT5.md)
- **Environment:** `bobp` 0.3.1 (`main`, Python 3.15 via `uv`), locally installed `claude 2.1.331`, `codex-cli 0.172.0`, `gemini 0.40.1`

---

## Executive Verdict: **MIXED — Net Better for Cross-Harness Switching (especially Claude Code + isolated reviews), with Real Git/Duplication Cost**

If you regularly switch between **Claude Code**, **OpenAI Codex**, and **Gemini CLI** when hitting token limits, harness-native subagent definitions are **net better** than skills-only — primarily because they unlock **native persona discovery in Claude Code** (which previously had zero automatic discovery under `.agents/skills/`) and enable **isolated subagent context windows** for reviewer personas (`Switch`, `Smith`, `Morpheus`, `Trin`) across all three harnesses while preserving a single shared `agents/<persona>/state.md` and `agents/CHAT.md`.

However, they are **not strictly free**: they add **30 generated files (`~413 KiB` / `6,021` lines)** to Git, amplify every persona edit from 2 touched files to **5 touched files**, and introduce **dual registration** in Codex and Gemini CLI (where personas now appear both as Skills in `.agents/skills/` and as Subagents in `.codex/agents/` / `.gemini/agents/`).

---

## 1. Schema & Live-Harness Discovery Check

All probes below were run read-only without spending paid external API tokens.

| Harness | Installed CLI | Subagent Format & Location | Verification Result | Notes / Caveats |
|---|---|---|---|---|
| **Claude Code** | `claude 2.1.331` (`/home/drusifer/.local/bin/claude`) | `.claude/agents/<persona>.md` (YAML `name`, `description` on line 1; no `memory:`, `model`, `tools:`) | **PASS** — all 10 files parse cleanly; `claude --help` confirms native `--agent <agent>` and project `.claude/agents/` discovery; `git check-ignore -v` confirms `.claude/agents/neo.md` is tracked while `.claude/settings.local.json` and `.claude/worktrees/*` stay ignored | Claude Code still does **not** auto-discover the 25 shared workflow skills in `.agents/skills/`; personas must read them on demand via file read tools. |
| **OpenAI Codex** | `codex-cli 0.172.0` (`/usr/bin/codex`) | `.codex/agents/<persona>.toml` (TOML `name`, `description`, `developer_instructions`; no `model`, `sandbox_mode`) | **PASS** — all 10 generated `.toml` files parse cleanly via Python stdlib `tomllib.loads()` (`ALL_10_LIVE_CODEX_TOML_PARSED_OK`); `codex features list` confirms `multi_agent` (`true`) and `multi_agent_v2` (`stable`); `git check-ignore -v` confirms `.codex/agents/neo.toml` is tracked | Required removing an accidental 0-byte `.codex` file committed in `ab6ee5f`. Codex also discovers `.agents/skills/` → dual registration (skill + subagent). |
| **Gemini CLI** | `gemini 0.40.1` (`/usr/bin/gemini`) | `.gemini/agents/<persona>.md` (YAML `name`, `description`, `kind: local` on line 1; no `model`, `tools:`) | **PASS** — all 10 files parse cleanly with `kind: local`; `gemini skills list` confirms Gemini CLI discovers all `.agents/skills/` skills; `git check-ignore -v` confirms `.gemini/agents/neo.md` is tracked | Gemini CLI still requires `"AGENTS.md"` in `context.fileName` in its own settings to auto-load root `AGENTS.md`. Dual registration (skill + subagent) applies here too. |

**Reproducible verification commands:**
- `bobp make test-q ARGS="-k subagent"` (16 tests including `test_repo_committed_subagents_match_packaged_templates` and `tomllib.loads()` round-trip across all 10 personas + adversarial inputs)
- `git check-ignore -v .claude/agents/neo.md .claude/settings.local.json .claude/worktrees/x .codex/agents/neo.toml .gemini/agents/neo.md`
- `claude --help | grep -i -C 2 agent`, `codex features list | grep -i "agent\|subagent\|multi"`, `gemini skills list`

---

## 2. Context, Token, and Repository Footprint Comparison

Measured directly on the dogfooded repository (`uv run python` inventory script over `.agents/skills/`, `.claude/agents/`, `.codex/agents/`, `.gemini/agents/`):

| Surface | Files | Lines | Bytes | Est. Tokens (`chars ÷ 4`) | Delta vs. 10 Persona Skills |
|---|---:|---:|---:|---:|---|
| `.agents/skills/` (all 35 skills) | 35 | 5,209 | 327,976 | ~81,694 | baseline (entire skill library) |
| `.agents/skills/` (10 personas only) | 10 | 1,992 | 138,769 | ~34,540 | baseline (`~3,454` tok/persona avg) |
| `.claude/agents/*.md` | 10 | 2,007 | 140,784 | ~35,034 | `+494` tok total (`~+49` tok/persona) |
| `.codex/agents/*.toml` | 10 | 1,997 | 141,011 | ~35,091 | `+551` tok total (`~+55` tok/persona) |
| `.gemini/agents/*.md` | 10 | 2,017 | 140,904 | ~35,064 | `+524` tok total (`~+52` tok/persona) |
| **Total added generated files** | **+30** | **+6,021** | **+422,699 (~413 KiB)** | **+105,189** | **3× copy of persona text in Git** |

### Runtime Context-Window Impact (What Actually Hits the LLM)
- **Main-session startup overhead (catalog metadata only):** Only **`~404 tokens`** total for all 10 personas' `name` + `description`.
  - **Claude Code:** `+404` tokens (and goes from **0 → 10** natively discoverable personas).
  - **Codex & Gemini CLI:** `+404` tokens *on top of* the existing `~404` tokens already injected from `.agents/skills/` (total `~808` tokens for the 10 personas across both catalogs — negligible on 200k–1M context windows, though semantically redundant).
- **Subagent spawn cost (Option A compiled body vs. Option B thin wrapper):**
  - Compiled body puts the persona's `~3,500` tokens straight into the subagent's system/developer prompt on turn 1 — **saving 1 full tool-call round trip** (`Read .agents/skills/<p>/SKILL.md`) per subagent invocation and eliminating the risk of a subagent forgetting to read its skill file.
  - Because each subagent runs in an **isolated context window**, heavy review/audit tool output (e.g., Switch grepping 30 files or Smith running 11 CLI probes) stays out of the main session's context window — saving far more tokens in the main thread than the `~404` tokens of catalog metadata!

---

## 3. Cross-Harness Switching Ergonomics (`Claude` ↔ `Codex` ↔ `Gemini`)

### Walkthrough: Mid-Sprint Token-Limit Handoff
1. Start implementation in **Claude Code** using `--agent neo` (or delegating to `neo`). Neo reads `agents/CHAT.md` and `agents/neo/state.md`, writes code/tests, updates `agents/neo/state.md` with progress % and Next Steps, and posts a checkpoint to `agents/CHAT.md`.
2. Claude hits its token limit. Switch to **Codex** (or **Gemini CLI**) in the same working tree and invoke `neo` (or hand off to `trin` / `switch` / `morpheus`).
3. Because `.claude/agents/neo.md`, `.codex/agents/neo.toml`, and `.gemini/agents/neo.md` all compile the **exact same** persona instructions, omit harness-private `memory:`, and open with the identical `**Shared Working Memory:**` preamble pointing to `agents/neo/state.md` and `agents/CHAT.md`, the new harness picks up from the exact same `state.md` checkpoint with zero state migration.

### Where It Is Clearly Better
- **Claude Code parity restored:** Sprint 3's Owner Amendment (`.agents/skills/` with zero symlinks) left Claude Code unable to discover any Bob Protocol persona automatically. `.claude/agents/*.md` restores first-class Claude Code persona support (including `claude --agent <persona>`) with **zero symlinks**.
- **True context isolation for reviewers:** Delegating `Switch` (security audit), `Smith` (UX gate), and `Morpheus` (code review) to native subagents keeps large diff/grep traces out of the orchestrator's context and reduces self-review bias.
- **Zero state fragmentation:** All three harnesses read/write the exact same `agents/<persona>/state.md` and `agents/CHAT.md`.

### Where Friction Remains (Honest Trade-Offs)
- **Dual-surface ambiguity in Codex & Gemini CLI:** Because `.agents/skills/<p>/SKILL.md` AND `.codex/agents/<p>.toml` / `.gemini/agents/<p>.md` both exist with identical names (`neo`, `switch`, etc.), users and orchestrators must understand when they want in-thread skill activation vs. isolated subagent spawning.
- **Claude Code still lacks shared workflow skills:** Only the 10 personas live in `.claude/agents/`. Workflow skills (`sprint`, `impl`, `fix`, `bob-tools`) remain in `.agents/skills/` and must be read on demand by Claude Code personas rather than auto-triggered as Claude slash commands.
- **Gemini CLI `AGENTS.md` caveat unchanged:** Users still need `"AGENTS.md"` in Gemini CLI's `context.fileName` setting to load root `AGENTS.md`.
- **Harness schema drift risk:** Unlike the open Agent Skills specification (`agentskills.io`), subagent formats are vendor-owned and still evolving (`codex` has `multi_agent_v2` alongside deprecated `multi_agent`; Claude/Gemini frontmatter keys evolve across minor releases).

---

## 4. Maintenance, Git Churn, and Security Trade-Offs

| Dimension | Skills-Only (`.agents/skills/`) | Skills + Harness Subagents (Sprint 5) |
|---|---|---|
| **Files touched per persona edit** | 2 (`bobp/templates/agents/<p>/SKILL.md.txt` + `.agents/skills/<p>/SKILL.md`) | **5** (the 2 above + `.claude/agents/<p>.md`, `.codex/agents/<p>.toml`, `.gemini/agents/<p>.md`) — automated via `bobp update .` and enforced by `test_repo_committed_subagents_match_packaged_templates` |
| **Repo size overhead** | Baseline (`~328 KiB` for 35 skills) | `+413 KiB` (`+6,021` lines of generated files in Git) |
| **Trust-boundary surface** | 1 skills root (`.agents/skills/`) + `agents/.bobp-skills` | +3 harness roots (`.claude/agents/`, `.codex/agents/`, `.gemini/agents/`) + `agents/.bobp-subagents`; mitigated by pre-flight parent-chain `lstat`, `O_NOFOLLOW | O_NONBLOCK` reads, atomic `write_text_safely`, and `.claude/*` + `!.claude/agents/` allowlist |
| **Custom user agent safety** | Protected by `agents/.bobp-skills` | Protected independently by `agents/.bobp-subagents` (custom files skipped & reported) |
| **Reversibility (`ADR-S5-1`)** | N/A | **High** — isolated in `_subagent_layout.py` + `agents/.bobp-subagents`; removing or making opt-in touches zero skill code |

---

## 5. Explicitly Unmeasured Items (Honest Scope Limits)

The following behavioral questions require **live paid multi-turn API sessions** across Claude, Codex, and Gemini and were **not** executed automatically (consistent with Sprint 3 Task 3b.3 spend rules):
1. **Implicit auto-delegation accuracy:** How often each harness's root orchestrator chooses the right subagent automatically from `description` alone (without explicit `@neo` / `--agent neo` / prompt naming), and whether Codex/Gemini experience any routing confusion between the skill `neo` and the subagent `neo`.
2. **Real-world token savings per sprint:** Measured end-to-end token spend of running a full multi-phase sprint with subagent delegation vs. single-thread persona switching on identical tasks.
3. **Live `claude`/`codex`/`gemini` runtime parsing edge cases:** While all 10 Codex `.toml` files passed stdlib `tomllib.loads()` and all 20 Claude/Gemini `.md` files passed strict YAML frontmatter validation, full runtime invocation inside an authenticated interactive session of each CLI should be spot-checked by the owner during normal daily work.

---

## 6. Recommendation & Decision Options for the Owner

**Recommendation: Keep enabled by default for now, and spot-check one real Claude → Codex → Gemini handoff on your next sprint.**

Why:
- It directly solves your core pain point (**seamless mid-task switching across Claude Code, Codex, and Gemini CLI with one shared `state.md` and zero symlinks**), and the runtime context overhead (`~404` tokens) is tiny.
- The main downside (`+413 KiB` / 5-file Git diff churn on persona edits) is completely automated by `bobp update .` and guarded by `test_repo_committed_subagents_match_packaged_templates`.

If after a week of real cross-harness switching the Git churn or Codex/Gemini dual-registration feels noisy, you have two clean, low-cost pivots thanks to `ADR-S5-1`:
1. **Option 1 (Keep as-is — Recommended):** Keep all 3 harnesses generated by default on `bobp install` / `bobp update`.
2. **Option 2 (Keep Claude-only or opt-in flag):** Generate `.claude/agents/` by default (where the biggest discovery win is) and gate `.codex/agents/` / `.gemini/agents/` behind `--subagents claude,codex,gemini`, or gitignore the generated subagent directories if Git diff noise bothers you.
3. **Option 3 (Drop):** Remove `_subagent_layout.py` cleanly with zero impact on `.agents/skills/`.
