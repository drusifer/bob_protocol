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

---
[<small>2026-08-10 11:47:43</small>] [**make**]->[**all**] *build*:
 Build PASSED | make test | /home/drusifer/Projects/bob_protocol/build/build.out
=== make test @ 2026-08-10 11:47:42 ===
.venv/bin/python -m pytest tests/ -q
............................................                             [100%]
44 passed in 0.59s

---
[<small>2026-08-12 00:06:28</small>] [**Bob**]->[**all**] *prompt fix*:
 Fixed chat_diagram.py: message labels were emitted unquoted, so a literal semicolon in chat text got parsed as a Mermaid statement terminator and broke rendering on GitHub. Added _quote_label() (wraps in double quotes, escapes literal quotes as #quot;), applied only at the line-138 emission point. 2 new regression tests, 46/46 pass. Found via a downstream project (tetris) reporting a GitHub render error.

---
[<small>2026-08-12 12:46:39</small>] [**Bob**]->[**all**] *prompt fix*:
 Correction to the prior fix: quoting alone did NOT protect semicolons (verified against real mermaid 11.16.0 - the quoted-string lexer mode exits early at ';' regardless). Real fix: replace ';' with ',' in _clean_message. Added tools/mermaid_validate/ (Node+jsdom+mermaid, no browser needed) as a real E2E syntax checker, wired into new 'make lint'/'lint-mermaid' targets, plus 5 new pytest E2E tests that shell out to it (skip gracefully if Node unavailable). 51/51 tests pass.

---
[<small>2026-08-12 13:10:55</small>] [**Bob**]->[**all**] *prompt fix*:
 Adjusted the diagram layout per user feedback (too horizontally dense, hard to read): WRAP_WIDTH 40->18 and MAX_MSG_LEN 300->140, so messages stack into narrow vertical columns instead of wide paragraphs, plus a %%{init}%% directive bumping message font to 20px. Confirmed hover tooltips aren't reliably supported by mermaid sequence-diagram arrows on GitHub's static SVG render, so didn't pursue that. 51/51 tests pass, all diagrams re-verified against the real mermaid parser.
