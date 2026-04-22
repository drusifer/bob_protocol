TL;DR: BobProtocol is a reusable Claude Code Skills framework. Invoke personas with `*chat`, Bloop commands (`*fix`, `*impl`, `*plan sprint`), or direct skill triggers. State persists per-persona in `agents/[persona].docs/`.

# BobProtocol: Multi-Persona AI Development Framework

A reusable Claude Code Skills framework that orchestrates a team of specialized AI personas. One LLM dynamically switches between 8 expert roles based on task context, with persistent state and structured handoffs across sessions.

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
├── PROJECT.md               # Project capabilities (created by setup when missing)
├── PROJECT.md.template      # Reference template for capability declarations
├── [persona].docs/          # Per-persona state and working memory
│   ├── SKILL.md             # Persona definition + command interface
│   ├── context.md           # Accumulated knowledge (state)
│   ├── current_task.md      # Active work (state)
│   └── next_steps.md        # Resume plan (state)
├── skills/
│   ├── bob-protocol/        # Core protocol (*chat routing, state management)
│   ├── bloop/               # Bob Loop commands (*fix, *impl, *qa, *review, *plan sprint)
│   ├── sprint/              # Full sprint cycle
│   ├── chat/                # make chat wrapper
│   ├── make/                # Makefile targets
│   └── personas/            # Persona switching reference
├── templates/               # Document and state file templates
└── tools/
    ├── chat.py              # Post to CHAT.md
    ├── mkf.py               # Build output filter (wraps make)
    └── setup_agent_links.py # Generate .claude/skills/ symlinks
.claude/skills/              # Symlinks → SKILL.md files (auto-generated)
Makefile                     # Bob-managed; project targets in Makefile.prj
```

## Installing into a Project

```bash
# First install
make install_bob TARGET=/path/to/your/project
```

### Makefile Integration
`install_bob` and `update_bob` handle your existing `Makefile` surgically:
1.  If a `Makefile` already exists, the bob-managed targets are installed as **`Makefile.bob`**.
2.  `include Makefile.bob` is added to the top of your existing `Makefile`.
3.  Bob-managed targets (`chat`, `update_bob`, etc.) are directly available via `make`.
4.  Project targets (e.g. `make test`) are automatically routed through `mkf.py` for logging and output filtering if they are wrapped in `ifdef MKF_ACTIVE`.

If no `Makefile` exists, one is created as the primary `Makefile`.

## Project Setup (after install)

1. Run skill link setup:
```bash
python agents/tools/setup_agent_links.py
```

2. Review project capabilities in `agents/PROJECT.md`. Setup creates this file when it is missing:
```markdown
## Capabilities
via: enabled   # personas will use via for code navigation
```

## Make Targets

```bash
make help                        # list all targets
make tldr                        # show TL;DR from all project files
make chat MSG="..." PERSONA="..."  # post a message to CHAT.md
make diff_bob TARGET=<path>      # diff framework files with a project
make update_bob TARGET=<path>    # push framework updates to a project
make pull_bob SRC=<path>         # pull framework updates from a project
make clean_bob                   # reset state files and remove symlinks
```

Build output is filtered through `mkf` — use `V=-vvv` for full output:
```bash
make test V=-vvv
```

## Optional: via Integration

[`via`](https://github.com/drewpifer/via) is a Python codebase symbol index. When enabled in `agents/PROJECT.md`, personas use `via` for code navigation instead of reading files directly — saving significant context.

Running `python agents/tools/setup_agent_links.py` installs the generic via MCP config with `via install mcp`, ensures the project has a `.via/index.db`, and, when Codex is installed, registers the same server with Codex using `codex mcp add via --env HOME=<project-root> -- <via> mcp serve --no-web <project-root>`.

Each persona knows how to use `via` in the way that best fits their role (e.g. Trin uses `--stale` for coverage gap detection, Morpheus uses `-oD` for architecture diagrams).

## State and Cold Start Recovery

State files in `agents/[persona].docs/` are the only memory that survives context clears and session restarts.

Every persona follows the same protocol:
- **ENTRY**: Read `CHAT.md` → load `context.md`, `current_task.md`, `next_steps.md`
- **EXIT**: Write state files → post handoff to `CHAT.md` → then switch

If resuming after a context clear with no memory:
1. Read the bottom of `agents/CHAT.md` to find the last handoff
2. Load that persona's state files
3. Resume from `next_steps.md`

See **[STARTUP.md](STARTUP.md)** for LLM startup instructions.
See **[SHORTHAND_GUIDE.md](SHORTHAND_GUIDE.md)** for the full trigger/command reference.
