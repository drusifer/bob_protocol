TL;DR: BobProtocol is a Claude Code Skills-based multi-persona AI system. Invoke agents with `*chat`, `@Persona *command`, or direct skill triggers. State is maintained per-agent in `agents/[persona].docs/`.

# BobProtocol: Multi-Persona AI Development System

A Claude Code Skills framework that orchestrates a team of specialized AI personas. One LLM dynamically switches between 7 expert roles based on task context, with persistent state and structured handoffs.

## How It Works

Each persona is a **Claude Code Skill** (`.claude/skills/<name>/`) with:
- YAML frontmatter defining `name`, `description`, and `triggers`
- A command interface invoked by `*prefix command` syntax
- State files in `agents/[persona].docs/` for persistent working memory

## The Team

| Persona | Role | Triggers | Responsibility |
|---------|------|----------|----------------|
| **Bob** | Prompt Engineer | `*new`, `*reprompt`, `*learn`, `*help` | Agent creation, system improvement |
| **Cypher** | Product Manager | `*pm story`, `*pm req`, `*pm prioritize` | Requirements, user stories, PRDs |
| **Morpheus** | Tech Lead | `*lead arch`, `*lead plan`, `*lead decide` | Architecture, design decisions |
| **Neo** | Software Engineer | `*swe impl`, `*swe fix`, `*swe test` | Implementation, debugging, coding |
| **Oracle** | Knowledge Officer | `*ora ask`, `*ora record`, `*ora distill`, `*ora tldr` | Documentation, knowledge queries |
| **Trin** | QA Guardian | `*qa test`, `*qa verify`, `*qa review` | Testing, quality gates, code review |
| **Mouse** | Scrum Master | `*sm status`, `*sm plan`, `*sm blocked` | Sprint tracking, coordination |

## Common Skills (available to all personas)

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `bob-protocol` | `*chat` | Multi-persona orchestration workflow |
| `personas` | `*switch`, `@Persona` | Direct persona invocation and handoffs |
| `chat` | — | Post to `agents/CHAT.md` via `make chat` |
| `make` | `*make` | Run project Makefile targets |

## Invoking Agents

### Auto-select (let the system route)
```
*chat fix the authentication bug in auth.py
*chat what's the current sprint status?
```

### Direct invocation
```
*chat @Neo *swe fix authentication bug in auth.py
*chat @Trin *qa test all
*chat @Oracle *ora ask What's our pattern for error handling?
```

### Skill trigger (direct, no chat overhead)
```
*swe impl Add input validation to the API
*qa test all
*ora ask Where is the database schema defined?
```

## Project Structure

```
.claude/skills/          # Symlinks → agent SKILL.md files (auto-generated)
agents/
├── AGENT.md             # Global agent instructions (all personas)
├── CHAT.md              # Shared team communication log
├── [persona].docs/      # Per-agent state and working memory
│   ├── SKILL.md         # Agent definition + command interface
│   ├── context.md       # Accumulated knowledge
│   ├── current_task.md  # Active work
│   └── next_steps.md    # Resume plan
├── skills/              # Shared skills
│   ├── bob-protocol/    # *chat workflow
│   ├── chat/            # make chat wrapper
│   ├── make/            # Makefile targets
│   └── personas/        # Switching reference
├── templates/           # Document templates
└── tools/               # chat.py, setup_agent_links.py
Makefile                 # make help, make tldr, ...
```

## Setup

Run once to create `.claude/skills/` symlinks:
```bash
python agents/tools/setup_agent_links.py
```

## Quick Reference

```bash
make help    # List all make targets
make tldr    # Show TL;DR summaries from all project files
```

See **[STARTUP.md](STARTUP.md)** for LLM startup instructions.
See **[USER_GUIDE.md](USER_GUIDE.md)** for the full workflow guide.
