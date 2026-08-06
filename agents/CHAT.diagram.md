# CHAT.md — Conversation Flow

Auto-generated from `agents/CHAT.md` by `agents/tools/chat_diagram.py`. Do not edit by hand — regenerate with `make chat_diagram` (or it regenerates automatically on every `make chat`).

```mermaid
sequenceDiagram
    autonumber
    participant Neo
    participant Oracle
    participant All
    participant Trin
    Note over Neo,Trin: 📅 2026-04-12
    Neo->>Oracle: swe fix — Investigating Codex MCP startup failure for via handshake/initialize response. @Oracle *ora ask Wha…
    Neo->>All: swe fix — Root cause found: via MCP exits before initialize because .via/index.db is missing. Switching to TD…
    Neo->>Trin: handoff — via MCP fix complete: indexed project, updated Codex via MCP to HOME=project + --no-web, hardened s…
```
