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

---
[<small>2026-08-09 16:19:17</small>] [**Oracle**]->[**Smith**] *ora handoff*:
 Sprint SPRINT_1 groomed and archived: agents/chat_archive/CHAT_SPRINT_1.md + .diagram.md. Live CHAT.md reset to pointer header (first post-reset entry). Docs updated: sprint/SKILL.md Step 7, oracle.docs/SKILL.md *ora report (+bobp/templates copies). @Smith test SPRINT_1

---
[<small>2026-08-09 16:19:30</small>] [**make**]->[**all**] *build*:
 Build PASSED | make test | /home/drusifer/Projects/bob_protocol/build/build.out
=== make test @ 2026-08-09 16:19:29 ===
.venv/bin/python -m pytest tests/ -q
...........................................                              [100%]
43 passed in 0.71s

---
[<small>2026-08-09 16:19:33</small>] [**Smith**]->[**all**] *user approve*:
 User testing PASSED end-to-end: archived real CHAT.md to CHAT_SPRINT_1.md/.diagram.md, verified reset+pointer, verified --combine produces CHAT_FULL.md/.diagram.md, and confirmed the diagram now shows full wrapped messages (no more mid-sentence <br/>truncation). 43/43 tests. @all sprint retro

---
[<small>2026-08-09 16:19:44</small>] [**Neo**]->[**Cypher**] *retro*:
 Neo retro: chat_report.py went in cleanly, reused chat_merge's parse_blocks rather than duplicating. Friction: hit the stale 'make chat MSG=...' syntax across skill docs immediately on cold start (make chat no longer exists in this repo since the Makefile-handback commit) - backlog item.

---
[<small>2026-08-09 16:19:44</small>] [**Trin**]->[**Cypher**] *retro*:
 Trin retro: good test coverage added (43/43), no regressions. Suggest a follow-up: test_bob_manage.py etc are fine, but chat-merge had zero tests before this sprint despite doing nontrivial timestamp interpolation - worth a coverage sweep of other bobp/tools modules.

---
[<small>2026-08-09 16:19:44</small>] [**Oracle**]->[**Cypher**] *retro*:
 Oracle retro: *ora report is now documented in both the real and template SKILL.md copies, so new bobp-installed projects get this feature too. Docs stayed in sync this sprint.

---
[<small>2026-08-09 16:19:44</small>] [**Cypher**]->[**Cypher**] *retro*:
 Backlog: (1) sweep all agents/*.docs/SKILL.md + skills/*/SKILL.md for stale 'make chat MSG=... PERSONA=...' examples, replace with 'bobp chat ... --persona ... --cmd ... --to ...'. (2) add test coverage for chat.py/make.py beyond the one integration test. Both discovered during SPRINT_1, neither blocking.

---
[<small>2026-08-09 16:19:49</small>] [**Cypher**]->[**all**] *pm launch*:
 SPRINT_1 'Chat Archive & Report' complete. Shipped: bobp chat-report (archive+combine), word-wrapped diagram labels, chat-merge conflict-marker cleanup, sprint-close workflow docs. Live-tested against the real CHAT.md. Backlog opened for next sprint: stale make-chat syntax sweep, bobp/tools test coverage. Sprint complete.

---
[<small>2026-08-10 09:21:45</small>] [**make**]->[**all**] *build*:
 Build PASSED | make test | /home/drusifer/Projects/bob_protocol/build/build.out
=== make test @ 2026-08-10 09:21:44 ===
.venv/bin/python -m pytest tests/ -q
...........................................                              [100%]
43 passed in 0.64s

---
[<small>2026-08-10 09:21:55</small>] [**Bob**]->[**all**] *prompt update*:
 Backlog item closed: swept all stale 'make chat MSG=... PERSONA=...' references (110+ across 24 skill/persona docs, real + bobp/templates copies, plus root STARTUP.md) to 'bobp chat "..." --persona ... --cmd ... --to ...'. Also fixed bare 'make chat'/'make chat_diagram' mentions and the chat skill's usage table. agents/CHAT.md/chat_archive/ log content left untouched (history, not docs). 43/43 tests still pass.
