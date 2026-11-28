---
name: bob-tools
description: Use when working in a BobProtocol project and you need to understand or run the bobp CLI subcommands, especially chat, chat-diagram, merge, make, setup-agent-links, and teardown-agent-links. This skill explains which commands to run, what each writes, and how to avoid flooding Codex context.
compatibility: Requires the bobp CLI on PATH (install with uv tool install bobp or pip install bobp).
---

One-line summary: Use BobProtocol's tools through the `bobp` CLI's stable subcommands — never reach for the implementation modules under `bobp.tools` directly.

TLDR:
    Use `bobp chat "..." --persona X --cmd Y --to Z` for team log messages — it also regenerates `agents/CHAT.diagram.md` (a Mermaid sequence diagram of the log) automatically.
    Use `bobp chat-diagram` to regenerate the diagram on demand without posting a message.
    Use `bobp merge [PATH]` to resolve Git conflicts and chronologically order timestamped Markdown logs (`CHAT.md`, `LESSONS.md`, `DECISIONS.md`, ADRs), or `--git-driver %O %A %B` as an opt-in Git custom merge driver.
    Use `bobp make <target>` to run this project's own `make <target>` — it captures output to `build/build.out` and posts build status. bobp does not install, own, or modify the project's Makefile.
    Use `bobp setup-agent-links` after installing/updating BobProtocol to configure Via MCP/index, Codex Via MCP, `agents/PROJECT.md`, and `.gitignore` (creates no symlinks).
    Use `bobp teardown-agent-links --dry-run` to inspect legacy symlinks and MCP teardown before removing them.

# BobProtocol Tools

## Triggers

`bobp chat`, `bobp merge`, `bobp make`, `bobp setup-agent-links`, `bobp teardown-agent-links`, `bob tools`, `BobProtocol tools`

## Tool Map

| Subcommand | Use for | Writes |
|------|---------|--------|
| `bobp chat "<msg>" --persona X --cmd Y --to Z` | Append short structured messages to `agents/CHAT.md` | `agents/CHAT.md`, `agents/CHAT.diagram.md` |
| `bobp chat-diagram [--include-builds]` | Render `agents/CHAT.md` as a Mermaid sequence diagram, for humans following the conversation flow | `agents/CHAT.diagram.md` |
| `bobp merge [PATH] [--dry-run] [--order auto\|asc\|desc] [--backup]` | Resolve Git conflict markers and order timestamped Markdown docs (`CHAT.md`, `LESSONS.md`, `DECISIONS.md`, ADRs); also supports opt-in `--git-driver BASE OURS THEIRS` | Target file (or `OURS` in driver mode; optional `<path>.bak` with `--backup`) |
| `bobp make [-v/-vv/-vvv] <target>` | Run this project's own `make <target>`, capturing build/test output and posting build status | `build/build.out`, `agents/CHAT.md` |
| `bobp update [--dry-run] <target>` | Refresh skills, harness subagents, `agents/BOB_AGENTS.md`, and templates in a project, migrating legacy layouts while preserving persona state | `.agents/skills/`, `.claude/agents/`, `.codex/agents/`, `.gemini/agents/`, `agents/BOB_AGENTS.md`, `agents/templates/`, `AGENTS.md` (create-only pointer), `agents/.bobp-skills`, `agents/.bobp-subagents`, `agents/.bobp-version` |
| `bobp pull [--dry-run] <src>` | Pull owned skill, subagent, `agents/BOB_AGENTS.md`, and template updates from a peer project into this one | Existing owned files under `.agents/skills/`, `.claude/agents/`, `.codex/agents/`, `.gemini/agents/`, `agents/BOB_AGENTS.md`, and `agents/templates/` |
| `bobp clean [--dry-run] --yes` | Reset persona state files and `CHAT.md` (requires `--yes`; exits `2` without it; leaves skills and subagents intact) | `agents/*/state.md`, `agents/CHAT.md`, `agents/CHAT.diagram.md` |
| `bobp setup-agent-links` | Configure Via index/MCP, Codex Via MCP, missing `agents/PROJECT.md`, and `.gitignore` (creates no symlinks) | `.mcp.json`, `.via/index.db`, Codex config via `codex mcp add`, `agents/PROJECT.md`, `.gitignore` |
| `bobp teardown-agent-links [--dry-run]` | Remove legacy symlinks from older bobp versions and delegate MCP teardown to via/Codex | Legacy symlinks pointing into `agents/`; via/Codex MCP config |

## General Rules

- Always go through the `bobp` subcommand. Never call `python -m bobp.tools.<module>` or reach into the package internals directly — the subcommand is the stable interface.
- Do not pipe or redirect `bobp make` output into the conversation. It exists to keep full logs in `build/build.out`.
- Inspect `build/build.out` only when the tail or exit code is not enough.
- Keep chat messages under 256 characters. For longer status, write a Markdown summary file and chat the path plus a short summary.
- Consecutive `bobp make` build-status messages replace the previous build entry instead of appending, so routine build/test runs do not fill `agents/CHAT.md`.
- Run `bobp setup-agent-links` after installing BobProtocol or when Via MCP, `.via/index.db`, or `agents/PROJECT.md` needs setup.
- Run `bobp teardown-agent-links --dry-run` first. It removes only legacy symlinks whose target is inside `agents/` and never touches real files or unrelated symlinks.

## bobp chat

```bash
bobp chat "Fixed parser bug" --persona Neo --cmd "swe fix" --to Trin
```

Notes:
- `--cmd` is auto-prefixed with `*` when missing.
- `--to` defaults to `all`; pass it multiple times for multiple recipients.
- When `--persona make` and `--cmd build`, `bobp chat` overwrites the final chat entry if that entry is also a build message (this is what `bobp make` relies on to avoid flooding CHAT.md with routine build noise).
- Every successful post regenerates `agents/CHAT.diagram.md` as a best-effort side effect (a rendering failure prints a warning but never blocks the chat post).

## bobp chat-diagram

`agents/CHAT.diagram.md` is a derived Mermaid `sequenceDiagram` view of `agents/CHAT.md` — one arrow per `Persona->recipient` message, grouped with a date `Note` whenever the day changes, with build-status entries filtered out by default (they're noise for following the persona-to-persona conversation, not part of it). It splits the diagram at phase boundaries (`phase <N>` markers), sprint close (`pm launch`), and epic close (the transition from `plan epic` to `plan story`, or an explicit `epic close`): the diagram closes, a markdown section recaps the close-out (and announces the next phase), and a new self-contained diagram begins. These are deterministic recaps of logged outcome messages, not generated from hidden context. It's regenerated automatically by `bobp chat`; it's a read-only artifact for humans — don't hand-edit it, and agents shouldn't parse it back for context (read `agents/CHAT.md` itself, per the `chat` skill).

Regenerate on demand, e.g. after manually editing `CHAT.md` or archiving old messages:

```bash
bobp chat-diagram                    # skip build-status entries (default)
bobp chat-diagram --include-builds   # include them
```

## bobp merge

Resolve Git merge conflicts and sort timestamped Markdown documents (`CHAT.md`, date-headed logs like `LESSONS.md`, and metadata-dated ADR/decision logs like `DECISIONS.md`):

```bash
bobp merge                           # clean up agents/CHAT.md in place
bobp merge docs/LESSONS.md --dry-run # preview changes without writing
bobp merge docs/DECISIONS.md --order desc
bobp merge --help                    # print opt-in .git/config & .gitattributes snippet
```

Notes:
- Chronological direction (`asc` / `desc`) is auto-detected from non-conflicted entries (override with `--order asc|desc`).
- Preamble conflicts are refused safely (file untouched, exit `1`).
- Optional Git custom merge driver mode (`bobp merge --git-driver %O %A %B`) is strictly opt-in; neither `bobp install`, `bobp update`, nor `bobp merge` modifies `.git/config` or `.gitattributes`. Run `bobp merge --help` for the exact configuration snippet.

## bobp make

See the `make` skill for the full contract. Short version: this project owns its own plain
`Makefile` — `bobp` never installs, generates, or modifies it. `bobp make` just runs
`make <target>` in it, captured:

```bash
bobp make test
bobp make -vv test
bobp make -vvv tldr
```

Verbosity (the flag comes *before* the target):
- *(none)*: quiet, full log in `build/build.out`
- `-v`: stderr
- `-vv`: stderr plus filtered failure lines
- `-vvv`: full stdout and stderr

After a run, use:

```bash
tail -20 build/build.out
```

## bobp setup-agent-links

Run this from the project root after installing BobProtocol or when Via/MCP setup is needed:

```bash
bobp setup-agent-links
```

Skills and root `AGENTS.md` are installed as real files by `bobp install` / `bobp update` — `setup-agent-links` creates **no symlinks**. It:
- converts older `.docs`-suffixed persona folders to `agents/<name>/` and updates internal path references (chat logs stay untouched as history)
- configures via MCP integration with `via install mcp` when `via` is installed, hardening `.mcp.json` with `HOME=<project-root>` and `--no-web`
- creates `.via/index.db` with `via index <project-root>` when missing
- registers Codex MCP integration via `codex mcp add via --env HOME=<project-root> -- <via> mcp serve --no-web <project-root>` when `codex` and `via` are installed
- creates `agents/PROJECT.md` when missing, enabling `via: enabled` only if via MCP setup succeeded
- ensures `.gitignore` has standard ignores without hiding `.agents/skills/`

## bobp teardown-agent-links

Run this from the project root to remove legacy symlinks from older `bobp` versions and uninstall MCP config:

```bash
bobp teardown-agent-links --dry-run
bobp teardown-agent-links
```

It removes only verified legacy symlinks targeting `agents/` (such as older `AGENT.md`, `GEMINI.md`, `.cursorrules`, `CHATGPT.md`, `.github/copilot-instructions.md`, `.agents`, or per-skill symlinks) and delegates MCP cleanup to `via uninstall mcp` and `codex mcp remove via`.

It never removes real files or symlinks pointing outside `agents/`. Use `--keep-mcp` to skip MCP uninstall.
