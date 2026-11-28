# Chat Message Template:

Agents **must** use this for every message posted to CHAT.md:


> ## [{msg_num}]: From: @{AgentName}, Subject: {Subject}
> 
> {TLDR(LastStep)};
> 
> ### Request: { An '@' or '*' targeted command  for a specic purpose like 'perform this task Y' or 'help me with X}

---

> **Previous sprint archived:** `agents/chat_archive/CHAT_SPRINT_1.md` (2026-08-09 16:19:09) — Sprint SPRINT_1 (Chat Archive & Report). Built bobp chat-report: archives CHAT.md+CHAT.diagram.md under a sprint moniker to agents/chat_archive/, resets CHAT.md to a pointer header, and --combine stitches all archives into CHAT_FULL.md/.diagram.md. Word-wrapped chat_diagram.py message labels (textwrap+<br/>, 40-char lines, 300-char safety cap) instead of hard-truncating at 100 chars. Taught chat_merge.py to strip leftover git conflict markers and dedupe exact-duplicate blocks. Wired the new *ora report step into the sprint-close workflow and Oracle's SKILL.md (real + bobp/templates copies). 43/43 tests passing.

---

> **Previous sprint archived:** `agents/chat_archive/CHAT_SPRINT_2.md` (2026-11-01 11:14:55) — Sprint 2 made bobp version-aware. bobp --version/-V prints the installed version; install/update record it in agents/.bobp-version; any other command in a project whose recorded version is missing or older prints one stderr line with the bobp update command and carries on (no prompt, owner decision after an initial prompt design). Switch's phase 2 review found SEC-005 (a symlink or FIFO stamp could hang every command); it was fixed test-first and re-verified. Suite grew 130 to 166. Not released or committed.

---

> **Previous sprint archived:** `agents/chat_archive/CHAT_SPRINT_4.md` (2026-11-28 00:41:22) — Sprint 4 replaced bobp chat-merge with bobp merge: conflict-safe merging for timestamped Markdown documents (CHAT.md, LESSONS.md, DECISIONS.md/ADRs), both post-conflict cleanup and optional Git custom merge driver (--git-driver %O %A %B), SEC-005..009 hardened, real git merge/rebase verified, docs/skills synced, 353 tests green.

---

> **Previous sprint archived:** `agents/chat_archive/CHAT_SPRINT_3.md` (2026-11-28 12:12:39) — Sprint 3 (Spec-Compliant Skills, No Links) delivered real .agents/skills/ directories with zero symlinks, root AGENTS.md, legacy migration, per-skill evals/evals.json and evaluating-skills workspaces, Agent Skills best-practices compliance across all 35 skills (size limits, references/, trigger descriptions, Gotchas, compatibility), and agent-safe CLI (--help, --dry-run, clean --yes, exit codes). All 7 phases and Stage 3 closeout passed (368 tests, 397 subtests, clean rebuild, security-scan, Mermaid lint, Smith UX APPROVE).

---

> **Previous sprint archived:** `agents/chat_archive/CHAT_SPRINT_5.md` (2026-11-28 13:18:25) — Sprint 5 (Harness-Native Subagent Definitions & Evaluation) delivered bobp/tools/_subagent_layout.py compiling 30 real project-local persona subagents across Claude Code (.claude/agents/*.md), OpenAI Codex (.codex/agents/*.toml), and Gemini CLI (.gemini/agents/*.md) sharing one agents/<persona>/state.md and agents/CHAT.md, with agents/.bobp-subagents ownership, pre-flight SEC-005/006/007 safety, .claude/* allowlist in .gitignore, dogfooding via bobp update ., and the evidence-backed Better/Worse evaluation report (docs/sprints/EVAL_SPRINT5_SUBAGENTS.md). All gates passed (384 tests, 435 subtests, lint, security-scan, build, Smith UX APPROVE).

---

---
[<small>2026-11-28 13:18:28</small>] [**make**]->[**all**] *build*:
 Build PASSED | make lint | /home/drusifer/Projects/bob_protocol/build/build.out
PASS  agents/chat_archive/CHAT_SPRINT_4.diagram.md [block 7/7]
PASS  agents/chat_archive/CHAT_SPRINT_5.diagram.md
PASS  agents/CHAT.diagram.md
