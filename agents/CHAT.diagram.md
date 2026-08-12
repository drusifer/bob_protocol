# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
%%{init: {"themeVariables": {"fontSize": "20px"}}}%%
sequenceDiagram
    autonumber
    participant Oracle
    participant Smith
    participant All
    participant Neo
    participant Cypher
    participant Trin
    participant Bob
    Note over Oracle,Bob: 📅 2026-08-09
    Oracle->>Smith: "ora handoff — Sprint SPRINT_1<br/>groomed and<br/>archived: agents/c<br/>hat_archive/CHAT_S<br/>PRINT_1.md +<br/>.diagram.md. Live<br/>CHAT.md reset to<br/>pointer header<br/>(first post-…"
    Smith->>All: "user approve — User testing<br/>PASSED end-to-end:<br/>archived real<br/>CHAT.md to CHAT_SP<br/>RINT_1.md/.diagram<br/>.md, verified<br/>reset+pointer,<br/>verified --combine<br/>produces…"
    Neo->>Cypher: "retro — Neo retro:<br/>chat_report.py<br/>went in cleanly,<br/>reused<br/>chat_merge's<br/>parse_blocks<br/>rather than<br/>duplicating.<br/>Friction: hit the<br/>stale 'make chat<br/>MSG…"
    Trin->>Cypher: "retro — Trin retro: good<br/>test coverage<br/>added (43/43), no<br/>regressions.<br/>Suggest a follow-<br/>up:<br/>test_bob_manage.py<br/>etc are fine, but<br/>chat-merge had<br/>zero…"
    Oracle->>Cypher: "retro — Oracle retro: *ora<br/>report is now<br/>documented in both<br/>the real and<br/>template SKILL.md<br/>copies, so new<br/>bobp-installed<br/>projects get this<br/>feature…"
    Cypher->>Cypher: "retro — Backlog: (1) sweep<br/>all agents/*.docs/<br/>SKILL.md +<br/>skills/*/SKILL.md<br/>for stale 'make<br/>chat MSG=...<br/>PERSONA=...'<br/>examples, replace<br/>with 'bobp ch…"
    Cypher->>All: "pm launch — SPRINT_1 'Chat<br/>Archive & Report'<br/>complete. Shipped:<br/>bobp chat-report<br/>(archive+combine),<br/>word-wrapped<br/>diagram labels,<br/>chat-merge<br/>conflict-ma…"
    Note over Oracle,Bob: 📅 2026-08-10
    Bob->>All: "prompt update — Backlog item<br/>closed: swept all<br/>stale 'make chat<br/>MSG=...<br/>PERSONA=...'<br/>references (110+<br/>across 24<br/>skill/persona<br/>docs, real +<br/>bobp/templates c…"
    Note over Oracle,Bob: 📅 2026-08-12
    Bob->>All: "prompt fix — Fixed<br/>chat_diagram.py:<br/>message labels<br/>were emitted<br/>unquoted, so a<br/>literal semicolon<br/>in chat text got<br/>parsed as a<br/>Mermaid statement<br/>terminat…"
    Bob->>All: "prompt fix — Correction to the<br/>prior fix: quoting<br/>alone did NOT<br/>protect semicolons<br/>(verified against<br/>real mermaid<br/>11.16.0 - the<br/>quoted-string<br/>lexer mode…"
    Bob->>All: "prompt fix — Adjusted the<br/>diagram layout per<br/>user feedback (too<br/>horizontally<br/>dense, hard to<br/>read): WRAP_WIDTH<br/>40->18 and<br/>MAX_MSG_LEN<br/>300->140, so<br/>messag…"
```
