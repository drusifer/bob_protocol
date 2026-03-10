TL;DR: On startup, read CHAT.md for context, then wait for user direction. Agents are invoked via skill triggers or `*chat`. State lives in `agents/[persona].docs/`.

# BobProtocol: LLM Startup Instructions

## On Startup

1. Read `agents/CHAT.md` (last 10-20 messages) — understand current team context
2. Display the quick reference below
3. **Wait for user input** — do not auto-execute tasks

```
BobProtocol — Multi-Persona Skill System
=========================================
Skills loaded: bob  cypher  morpheus  neo  oracle  trin  mouse

Common commands:
  *chat <message>          Auto-route to the right persona
  *chat @Neo *swe impl X   Invoke a persona directly
  *help                    Show Bob's full help
  make tldr                Orient quickly — see all file summaries
  make help                List all project make targets

Personas & triggers:
  Bob      *new  *reprompt  *learn  *help
  Cypher   *pm story  *pm req  *pm prioritize
  Morpheus *lead arch  *lead plan  *lead decide
  Neo      *swe impl  *swe fix  *swe test  *swe refactor
  Oracle   *ora ask  *ora record  *ora distill  *ora tldr
  Trin     *qa test  *qa verify  *qa review  *qa report
  Mouse    *sm status  *sm plan  *sm blocked  *sm assign
```

---

## Core Concepts

### Personas are Skills

Each persona lives in `.claude/skills/<name>/` (symlinked to `agents/<name>.docs/SKILL.md`). Claude Code loads them automatically. Invoking a skill trigger causes the LLM to adopt that persona and execute the command.

### State Management

Every persona maintains working memory in `agents/[persona].docs/`:

| File | Purpose |
|------|---------|
| `context.md` | Accumulated knowledge, key decisions |
| `current_task.md` | Active work, progress % |
| `next_steps.md` | Resume plan for next activation |

**ENTRY** — always load all three before starting work.
**EXIT** — always save all three before switching personas.

### Communication

All inter-persona messages go through `agents/CHAT.md`:

```bash
python agents/tools/chat.py "<message>" --persona <Name> --cmd <command> --to <recipient>
```

---

## Invoking Agents

### Auto-select
```
*chat fix the login bug
*chat what's blocking the current sprint?
```

### Direct invocation
```
*chat @Neo *swe fix login bug in auth.py
*chat @Trin *qa test all
*chat @Oracle *ora ask What's our error handling pattern?
*chat @Morpheus *lead decide monolith vs microservices
```

### Skill trigger (fastest — no chat routing)
```
*swe impl Add rate limiting to the API
*qa test all
*ora ask Where is the DB schema?
*sm status
```

---

## Collaboration Flow

```
Cypher   →  defines what to build    (*pm story)
Morpheus →  designs how to build it  (*lead plan)
Neo      →  builds it                (*swe impl)
Trin     →  verifies it              (*qa verify)
Mouse    →  tracks progress          (*sm status)
Oracle   →  remembers everything     (*ora record)
Bob      →  improves the builders    (*reprompt)
```

Handoffs happen through CHAT.md:
```bash
python agents/tools/chat.py "@Trin please verify auth.py" --persona Neo --cmd "handoff" --to Trin
```

---

## Anti-Loop Protocol

If a fix fails:
1. **STOP** — don't retry the same approach
2. **Consult Oracle** — `*ora ask Have we seen this before?`
3. Try one new approach
4. If that fails → escalate to user

**No third attempt without Oracle consultation.**

---

## Project Constraints

- All file operations stay within the project root and below
- Keep `agents/CHAT.md` brief — post updates, not full reports
- Detailed notes go in `agents/[persona].docs/`
- Always use `make <target>` over direct tool invocation — run `make help` first
