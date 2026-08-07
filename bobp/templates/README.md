TL;DR: BobProtocol is a reusable Claude Code Skills framework. Invoke personas with `*chat`, Bloop commands (`*fix`, `*impl`, `*plan sprint`), or direct skill triggers. State persists per-persona in `agents/[persona].docs/`.

# BobProtocol: Multi-Persona AI Development Framework

A reusable Claude Code Skills framework that orchestrates a team of specialized AI personas. One LLM dynamically switches between 9 expert roles based on task context, with persistent state and structured handoffs across sessions.

## How It Works

Each persona is a **Claude Code Skill** with:
- YAML frontmatter defining `name`, `description`, and `triggers`
- A command interface invoked by `*prefix command` syntax
- State files in `agents/[persona].docs/` — the only memory that survives context clears and session restarts

All coordination flows through `agents/CHAT.md` — a shared team log that every persona reads on entry.

## The Team

| Persona | Role | Prefix | Responsibility |
|---------|------|--------|----------------|
| **Neo** | Senior SWE | `*swe` | Implementation, debugging, coding |
| **Morpheus** | Tech Lead | `*lead` | Architecture, design decisions, code review |
| **Trin** | QA Guardian | `*qa` | Testing, quality gates, coverage |
| **Oracle** | Knowledge Officer | `*ora` | Documentation, knowledge queries, decisions |
| **Mouse** | Scrum Master | `*sm` | Sprint tracking, coordination, velocity |
| **Cypher** | Product Manager | `*pm` | Requirements, user stories, PRDs |
| **Bob** | Prompt Engineer | `*prompt` | Agent creation, system improvement |
| **Smith** | HCI Expert | `*user` | Usability testing, HCI evaluation, sprint gates |
| **Tank** | DevOps Engineer | `*devops` | IaC, CI/CD, deployment automation, environment management, systems reliability |

## Skills

| Skill | Triggers | Purpose |
|-------|---------|---------|
| `bob-protocol` | `*chat` | Core routing, state management, anti-loop protocol |
| `bloop` | `*fix`, `*impl`, `*qa`, `*review`, `*plan sprint` | Multi-persona workflow chains (Bob Loops) |
| `sprint` | `*plan sprint`, `*sprint retro`, `*sprint launch` | Full sprint cycle |
| `chat` | — | Post structured messages to `agents/CHAT.md` |
| `make` | `*make` | Run project Makefile targets |
| `personas` | `@Persona` | Direct persona reference |

## Invoking Agents

### Bloop commands — full workflow chains (recommended)
```
*fix <bug>               # Neo → Trin → Morpheus fix Bloop
*impl <feature>          # Neo → Trin → Morpheus implementation Bloop
*qa <thing>              # Trin → Morpheus QA Bloop
*review <thing>          # Morpheus → Trin review Bloop
*plan sprint             # Cypher → Smith → Morpheus → Mouse planning Bloop
```

### `*chat` — auto-select a persona for a single task
```
*chat fix the authentication bug in auth.py
*chat what's the current sprint status?
```

### `*chat @Persona` — direct single-persona invocation
Directly invoke a persona using Gemini's `@` syntax or the internal `@Persona` trigger.

```
*chat @neo *fix authentication bug in auth.py
@neo *fix authentication bug in auth.py
*chat @trin *test all
*chat @oracle *ora ask What's our pattern for error handling?
*chat @smith *user review the sprint stories
```

> **Note on Harness Prefixes**: Different AI harnesses use different prefixes for direct invocation (e.g., `@persona` or `/persona` in Gemini CLI, `/persona` in Claude, `$persona` in Codex). If you are invoked directly via such a command, you MUST log the invocation to `agents/CHAT.md` immediately upon entry if it has not already been logged.


### Direct skill triggers — bypass chat routing
```
*swe impl Add input validation to the API
*qa test all
*ora ask Where is the database schema defined?
```

## Project Structure

```
agents/
├── CHAT.md                  # Shared team communication log
├── CHAT.diagram.md          # Auto-generated Mermaid view of CHAT.md (derived, don't edit)
├── PROJECT.md               # Project capabilities (created by setup when missing)
├── PROJECT.md.template      # Reference template for capability declarations
├── [persona].docs/          # Per-persona state and working memory
│   ├── SKILL.md             # Persona definition + command interface
│   └── state.md              # Context, current task, and resume plan (state)
├── skills/
│   ├── bob-protocol/        # Core protocol (*chat routing, state management)
│   ├── bloop/               # Bob Loop commands (*fix, *impl, *qa, *review, *plan sprint)
│   ├── sprint/              # Full sprint cycle
│   ├── chat/                # bobp chat wrapper
│   ├── make/                # bobp make wrapper — captures your project's own Makefile targets
│   └── personas/            # Persona switching reference
├── templates/               # Document and state file templates
└── tools/
    ├── chat.py              # Post to CHAT.md, regenerates CHAT.diagram.md
    ├── chat_diagram.py      # Render CHAT.md as a Mermaid sequence diagram
    ├── make.py              # Build output filter (wraps your project's own `make`)
    └── setup_agent_links.py # Generate .claude/skills/ symlinks
.claude/skills/              # Symlinks → SKILL.md files (auto-generated)
```

`bobp` never installs, generates, or modifies a `Makefile` — that stays entirely
yours. See "Running Your Own Make Targets" below.

## Installing into a Project

`bobp` (`pip install bobp`) is the CLI front-end for all of this — installing,
updating, pulling, diffing, and cleaning a Bob Protocol install are all
`bobp` subcommands, not `make` targets:

```bash
# First install
bobp install /path/to/your/project

# Later, once installed
bobp update /path/to/your/project    # refresh skills/templates, preserving state
bobp pull /path/to/another/project   # pull framework updates from a peer project
bobp diff /path/to/your/project      # compare the template against an install
bobp clean                           # reset state files and remove symlinks (run inside the project)
```

## Project Setup (after install)

1. Run skill link setup:
```bash
bobp setup-agent-links
```

2. Review project capabilities in `agents/PROJECT.md`. Setup creates this file when it is missing:
```markdown
## Capabilities
via: enabled   # personas will use via for code navigation
```

## Team Coordination Commands

These are `bobp` subcommands, not `make` targets — bob never touches your `Makefile`:

```bash
bobp tldr                             # show TL;DR from all project files
bobp chat "..." --persona X --cmd Y   # post a message to CHAT.md
bobp chat-diagram                     # regenerate CHAT.diagram.md on demand
```

## Running Your Own Make Targets

If your project has its own `Makefile` (test, lint, build — whatever you already
use), run it through `bobp make` instead of bare `make` to get output captured to
`build/build.out` and a pass/fail status posted to CHAT.md:

```bash
bobp make test         # silent — exit code + 10-line tail on finish
bobp make -vvv test    # full output live
```

See the `make` skill for the full contract.

## Optional: via Integration

[`via`](https://github.com/drewpifer/via) is a Python codebase symbol index. When enabled in `agents/PROJECT.md`, personas use `via` for code navigation instead of reading files directly — saving significant context.

Running `bobp setup-agent-links` installs the generic via MCP config with `via install mcp`, ensures the project has a `.via/index.db`, and, when Codex is installed, registers the same server with Codex using `codex mcp add via --env HOME=<project-root> -- <via> mcp serve --no-web <project-root>`.

Each persona knows how to use `via` in the way that best fits their role (e.g. Trin uses `--stale` for coverage gap detection, Morpheus uses `-oD` for architecture diagrams).

## State and Cold Start Recovery

State files in `agents/[persona].docs/` are the only memory that survives context clears and session restarts.

Every persona follows the same protocol:
- **ENTRY**: Read `CHAT.md` → load `state.md`
- **EXIT**: Write `state.md` → post handoff to `CHAT.md` → then switch

If resuming after a context clear with no memory:
1. Read the bottom of `agents/CHAT.md` to find the last handoff
2. Load that persona's `state.md`
3. Resume from its `## Next Steps` section

See **[STARTUP.md](STARTUP.md)** for LLM startup instructions.
See **[SHORTHAND_GUIDE.md](SHORTHAND_GUIDE.md)** for the full trigger/command reference.
