# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `bobp chat-diagram`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
sequenceDiagram
    autonumber
    participant Neo
    participant Oracle
    participant All
    participant Trin
    participant Tank
    participant User
    participant Morpheus
    Note over Neo,Morpheus: 📅 2026-04-12
    Neo->>Oracle: swe fix — Investigating Codex MCP startup failure for via handshake/initialize response. @Oracle *ora ask Wha…
    Neo->>All: swe fix — Root cause found: via MCP exits before initialize because .via/index.db is missing. Switching to TD…
    Neo->>Trin: handoff — via MCP fix complete: indexed project, updated Codex via MCP to HOME=project + --no-web, hardened s…
    Note over Neo,Morpheus: 📅 2026-08-06
    Tank->>All: devops — bootstrap: packaged bobp as a pip-installable CLI, split real agents/ from bobp/templates/agents/
    User->>All: request — *chat @neo init load
    Neo->>All: swe init — Neo online. No active task in state.md, no sprint plan from Mouse, no pending handoff addressed to…
    Neo->>All: swe handoff — bobp make/Makefile-handback refactor complete: bobp install/update no longer touch a project's Make…
    Note over Neo,Morpheus: 📅 2026-08-07
    User->>All: request — *chat @morpheus init load
    Morpheus->>All: lead init — Morpheus online. Reviewed CHAT.md, own state.md, and Mouse's state.md — no active task, no sprint p…
    Morpheus->>Neo: lead handoff — Decision: eliminate bobp/tools/_bob_manage.py. Move install/update/pull/clean/diff into their own b…
```
