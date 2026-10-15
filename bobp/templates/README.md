TL;DR: BobProtocol is a reusable Claude Code Skills framework. Invoke personas with `*chat`, Bloop commands (`*fix`, `*impl`, `*plan sprint`), or direct skill triggers. State persists per-persona in `agents/[persona]/`.

# BobProtocol: Multi-Persona AI Development Framework

A reusable Claude Code Skills framework that orchestrates a team of specialized AI personas. One LLM dynamically switches between 9 expert roles based on task context, with persistent state and structured handoffs across sessions.

## How It Works

Each persona is a **Claude Code Skill** with:
- YAML frontmatter defining `name`, `description`, and `triggers`
- A command interface invoked by `*prefix command` syntax
- State files in `agents/[persona]/` — the only memory that survives context clears and session restarts

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

## Skills & Workflow Loops

Bob Protocol organizes autonomous workflows into hierarchical loops and supporting capabilities:

### Planning Loops (Strategic Scoping & Specification)
| Skill / Trigger | Focus / Deliverable | Literature |
|-----------------|---------------------|------------|
| `epic` / `*plan epic` | Problem framing, appetite budget, domain model (`DOMAIN.md`) | *Shape Up* (Singer) / *Inspired* (Cagan) |
| `story` / `*plan story` | Vertical user story slicing, INVEST criteria, ADRs (`ARCH.md`), test strategy | *User Story Mapping* (Patton) / *Agile Estimating* (Cohn) |
| `sprint` / `*plan sprint` | Sprint planning, SDLC verification, task board (`task.md`) with Work Loops | *The Scrum Guide* (Schwaber & Sutherland) |

### Work Loops (Tactical Execution Chains)
| Skill / Trigger | Execution Chain | Invariant / Literature |
|-----------------|-----------------|------------------------|
| `impl` / `*impl` | Neo TDD → Trin verify → Morpheus review | **Test-First**: failing test required before production code (*TDD* — Beck) |
| `fix` / `*fix` | Neo diagnose → User confirm → Neo fix → Trin test → Morpheus review | **Reproduce First**: diagnose & confirm before edits (*Debugging* — Agans) |
| `refactor` / `*refactor` | Morpheus plan → Trin baseline → Neo restructure → Trin parity → Morpheus | **Two Hats**: zero behavioral change, green before/after (*Refactoring* — Fowler) |
| `spike` / `*spike` | Oracle survey → Neo prototype → Morpheus decision/ADR | **Disposable**: timeboxed, zero prod commits (*XP Installed* / *Shape Up*) |
| `uat` / `*uat` | Trin acceptance matrix → Smith UX audit → Cypher sign-off | **Real-World Experience**: end-to-end evaluation (*Agile Testing* — Crispin) |
| `deploy` / `*deploy` | Tank Makefile deploy → Trin live smoke test | **Pipeline as Code**: automated release via SDLC Makefile (*Continuous Delivery*) |
| `bloop` / `*bloop` | Multi-persona work-loop conductor and catalog | Autonomous orchestration, state preservation, anti-loop guards |

### Supporting Protocol & Tool Skills
- **Session Lifecycle**: `init` (session startup & discovery), `prep-clear` (checkpointing state before `/clear`), `judge` (prompt & tool evaluation)
- **Protocol & Operations**: `bob-protocol` (routing & state protocol), `bob-tools` (`bobp` CLI operations), `build-env` (`docs/SDLC.md` management), `chat` (team logging), `linter` (code analysis), `make` (captured target runner), `make-discover` (target self-discovery), `personas` (specialist switching), `render` (cloud deployment), `test-runner` (bounded tests), `via` (symbol lookup)

## Invoking Agents

### Autonomous Workflow Loops (Recommended)
```bash
# Strategic Planning Loops
*plan epic <name>        # Cypher framing → Smith gate → Morpheus domain → (Spikes)
*plan story <slice>      # Cypher story → Smith gate 1 → Morpheus arch → Trin test → Smith gate 2
*plan sprint             # Cypher → Smith gate → Morpheus → Smith gate → Mouse task board

# Tactical Work Loops
*impl <task>             # Neo TDD (red-green-refactor) → Trin verify → Morpheus review
*fix <bug>               # Neo repro/diagnose → confirm → surgical fix → Trin regression sweep
*refactor <target>       # Morpheus plan → Trin baseline → Neo restructure → Trin parity
*spike <topic>           # Oracle survey → Neo prototype → Morpheus decision / ADR
*uat <scope>             # Trin scenario matrix → Smith UX evaluation → Cypher sign-off
*deploy <env>            # Tank Makefile deploy → Trin live smoke test
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
├── [persona]/               # Per-persona state and working memory (e.g. neo/, trin/)
│   ├── SKILL.md             # Persona definition + command interface
│   └── state.md             # Context, current task, and resume plan (state)
├── skills/                  # 24 shared skills discovered by harnesses
│   ├── epic/                # Strategic epic planning (*plan epic)
│   ├── story/               # User story slicing & ADRs (*plan story)
│   ├── sprint/              # Sprint planning & cadence container (*plan sprint)
│   ├── impl/                # Feature TDD work-loop (*impl)
│   ├── fix/                 # Defect diagnosis & surgical fix work-loop (*fix)
│   ├── refactor/            # Behavior-preserving refactoring work-loop (*refactor)
│   ├── spike/               # Disposable research spike work-loop (*spike)
│   ├── uat/                 # End-to-end acceptance & UX audit work-loop (*uat)
│   ├── deploy/              # Automated delivery & live smoke work-loop (*deploy)
│   ├── bloop/               # Work-loop conductor & catalog (*bloop)
│   ├── init/                # Session initialization & resume (*init, *resume)
│   ├── prep-clear/          # Context checkpointing before /clear (*prep-clear)
│   ├── judge/               # Agent & prompt optimization loop (*judge)
│   └── ...                  # Supporting tool skills (make, chat, via, build-env, etc.)
└── templates/               # Document and state file templates (ARTIFACTS.md, rubrics)
.claude/skills/              # Symlinks → persona and skill folders (generated by `bobp setup-agent-links`)
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

## State Management and Cold Start Recovery

State files in `agents/[persona]/state.md` are your working memory — the only state that survives context clears and session restarts.

Every persona follows the strict State Management Protocol:
- **ENTRY**: Read `agents/CHAT.md` (last 10–20 messages) → load `agents/[persona]/state.md`
- **WORK**: Update working memory with progress, blockers, and findings
- **EXIT (Mandatory Hard Gate)**:
  1. Follow `agents/skills/prep-clear/SKILL.md` before `/clear` or persona switch — flush Context, Current Task progress %, and Next Steps cold-start resume plan to `state.md`.
  2. Post handoff message: `bobp chat "<summary> @NextPersona *command" --persona <Name> --cmd handoff --to <next>`.
  3. Never switch personas or clear context without completing both steps.

If resuming after a context clear with no memory:
1. Run `*init` or read the bottom of `agents/CHAT.md` to find the last handoff
2. Load that persona's `state.md`
3. Resume immediately from its `## Next Steps` section

See **[STARTUP.md](STARTUP.md)** for LLM startup instructions.
See **[SHORTHAND_GUIDE.md](SHORTHAND_GUIDE.md)** for the full trigger/command reference.
