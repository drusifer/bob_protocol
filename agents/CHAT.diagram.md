# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
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
    Oracle->>Smith: "ora handoff"
    Note over Oracle,Smith: "Sprint SPRINT_1 groomed<br/>and archived: agents/cha<br/>t_archive/CHAT_SPRINT_1.<br/>md + .diagram.md. Live<br/>CHAT.md reset to pointer<br/>header (first post-…"
    Smith->>All: "user approve"
    Note over Smith,All: "User testing PASSED end-<br/>to-end: archived real<br/>CHAT.md to CHAT_SPRINT_1<br/>.md/.diagram.md,<br/>verified reset+pointer,<br/>verified --combine<br/>produces…"
    Neo->>Cypher: "retro"
    Note over Neo,Cypher: "Neo retro:<br/>chat_report.py went in<br/>cleanly, reused<br/>chat_merge's<br/>parse_blocks rather than<br/>duplicating. Friction:<br/>hit the stale 'make chat<br/>MSG…"
    Trin->>Cypher: "retro"
    Note over Trin,Cypher: "Trin retro: good test<br/>coverage added (43/43),<br/>no regressions. Suggest<br/>a follow-up:<br/>test_bob_manage.py etc<br/>are fine, but chat-merge<br/>had zero…"
    Oracle->>Cypher: "retro"
    Note over Oracle,Cypher: "Oracle retro: *ora<br/>report is now documented<br/>in both the real and<br/>template SKILL.md<br/>copies, so new bobp-<br/>installed projects get<br/>this feature…"
    Cypher->>Cypher: "retro"
    Note over Cypher,Cypher: "Backlog: (1) sweep all<br/>agents/*.docs/SKILL.md +<br/>skills/*/SKILL.md for<br/>stale 'make chat MSG=...<br/>PERSONA=...' examples,<br/>replace with 'bobp ch…"
    Cypher->>All: "pm launch"
    Note over Cypher,All: "SPRINT_1 'Chat Archive &<br/>Report' complete.<br/>Shipped: bobp chat-<br/>report<br/>(archive+combine), word-<br/>wrapped diagram labels,<br/>chat-merge conflict-ma…"
    Note over Oracle,Bob: 📅 2026-08-10
    Bob->>All: "prompt update"
    Note over Bob,All: "Backlog item closed:<br/>swept all stale 'make<br/>chat MSG=...<br/>PERSONA=...' references<br/>(110+ across 24<br/>skill/persona docs, real<br/>+ bobp/templates c…"
    Note over Oracle,Bob: 📅 2026-08-12
    Bob->>All: "prompt fix"
    Note over Bob,All: "Fixed chat_diagram.py:<br/>message labels were<br/>emitted unquoted, so a<br/>literal semicolon in<br/>chat text got parsed as<br/>a Mermaid statement<br/>terminat…"
    Bob->>All: "prompt fix"
    Note over Bob,All: "Correction to the prior<br/>fix: quoting alone did<br/>NOT protect semicolons<br/>(verified against real<br/>mermaid 11.16.0 - the<br/>quoted-string lexer<br/>mode…"
    Bob->>All: "prompt fix"
    Note over Bob,All: "Adjusted the diagram<br/>layout per user feedback<br/>(too horizontally dense,<br/>hard to read):<br/>WRAP_WIDTH 40->18 and<br/>MAX_MSG_LEN 300->140, so<br/>messag…"
    Bob->>All: "prompt fix"
    Note over Bob,All: "Restructured per user<br/>feedback (font still<br/>unreadable, and<br/>themeVariables.fontSize<br/>did nothing visually):<br/>arrows now carry only<br/>the short c…"
```
