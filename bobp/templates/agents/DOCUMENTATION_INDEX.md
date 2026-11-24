# BobProtocol Documentation Index

**Last Updated:** 2026-11-23

## Quick Access

Type `*help` for complete command reference with examples.

---

## Primary Documentation

### Getting Started
- **[STARTUP.md](../STARTUP.md)** - LLM startup instructions
- **[docs/WALKTHROUGH.md](../docs/WALKTHROUGH.md)** - Step-by-step user walkthrough: building an app with Bob Protocol
- **[docs/PERSONA_EVALUATION.md](../docs/PERSONA_EVALUATION.md)** - Set up, run, and review persona evaluations
- **[docs/SDLC.md](../docs/SDLC.md)** - Project toolchain, quality gates, and change lifecycle
- **[.agents/skills/init/SKILL.md](../.agents/skills/init/SKILL.md)** - Canonical session initialization & resume skill
- **[.agents/skills/prep-clear/SKILL.md](../.agents/skills/prep-clear/SKILL.md)** - Pre-clear checkpointing & state preservation skill
- **[README.md](../README.md)** - Project overview and team reference
- **[SHORTHAND_GUIDE.md](../SHORTHAND_GUIDE.md)** - Complete trigger/command reference
- **[HELP.md](bob/HELP.md)** - Quick reference for all 10 personas and commands

### Tools
- **`bobp` CLI** - Agent tooling subcommands (`bobp chat`, `bobp make`, `bobp setup-agent-links`, …); run `bobp --help` for the full list. `bobp install`/`update` places real skills in `.agents/skills/` and root `AGENTS.md` (no symlinks); `bobp setup-agent-links` configures Via MCP/index, `agents/PROJECT.md`, and `.gitignore` (and may update user-level Codex MCP config). See the `bob-tools` skill before running it.

---

## Persona Documentation

### Active Personas (10)

| Persona | Role | SKILL.md | Prefix |
|---------|------|----------|--------|
| Bob | Prompt Engineering Expert | [.agents/skills/bob/SKILL.md](../.agents/skills/bob/SKILL.md) | `*new` / `*reprompt` / `*learn` |
| Cypher | Product Manager | [.agents/skills/cypher/SKILL.md](../.agents/skills/cypher/SKILL.md) | `*pm` |
| Morpheus | Tech Lead / Architect | [.agents/skills/morpheus/SKILL.md](../.agents/skills/morpheus/SKILL.md) | `*lead` |
| Neo | Senior Software Engineer | [.agents/skills/neo/SKILL.md](../.agents/skills/neo/SKILL.md) | `*swe` |
| Oracle | Knowledge Officer | [.agents/skills/oracle/SKILL.md](../.agents/skills/oracle/SKILL.md) | `*ora` |
| Trin | QA / Guardian | [.agents/skills/trin/SKILL.md](../.agents/skills/trin/SKILL.md) | `*qa` |
| Mouse | Scrum Master | [.agents/skills/mouse/SKILL.md](../.agents/skills/mouse/SKILL.md) | `*sm` |
| Smith | Expert User & UX Advocate | [.agents/skills/smith/SKILL.md](../.agents/skills/smith/SKILL.md) | `*user` |
| Tank | DevOps Engineer | [.agents/skills/tank/SKILL.md](../.agents/skills/tank/SKILL.md) | `*devops` |
| Switch | Security Engineer | [.agents/skills/switch/SKILL.md](../.agents/skills/switch/SKILL.md) | `*sec` |

---

## Skills & Workflow Loops (`.agents/skills/`)

Bob Protocol organizes autonomous workflows into hierarchical loops and supporting capabilities:

### Planning Loops (Strategic Scoping & Specification)
- **[.agents/skills/epic/SKILL.md](../.agents/skills/epic/SKILL.md)** - Strategic Epic discovery, appetite framing, domain modeling, and de-risking spikes (*Shape Up* / *Inspired*)
- **[.agents/skills/story/SKILL.md](../.agents/skills/story/SKILL.md)** - User story vertical slicing, INVEST acceptance criteria, ADRs, test strategies (*User Story Mapping* / *Agile Estimating*)
- **[.agents/skills/sprint/SKILL.md](../.agents/skills/sprint/SKILL.md)** - Sprint planning, phase execution, review gates, retrospective, and launch (*Scrum Guide*)

### Work Loops (Tactical Execution & Verification)
- **[.agents/skills/bloop/SKILL.md](../.agents/skills/bloop/SKILL.md)** - Conductor for multi-persona autonomous work loops
- **[.agents/skills/impl/SKILL.md](../.agents/skills/impl/SKILL.md)** - TDD implementation loop: test-first, red-green-refactor, acceptance verification (*TDD: By Example*)
- **[.agents/skills/fix/SKILL.md](../.agents/skills/fix/SKILL.md)** - Defect diagnosis & surgical fix: reproduce first, confirm diagnosis, surgical repair, regression sweep (*Debugging*)
- **[.agents/skills/refactor/SKILL.md](../.agents/skills/refactor/SKILL.md)** - Behavior-preserving refactoring: Two-Hats rule, green baseline, zero behavioral drift (*Refactoring*)
- **[.agents/skills/spike/SKILL.md](../.agents/skills/spike/SKILL.md)** - Disposable timeboxed spike: rapid prototyping, zero production code, findings/ADR output (*XP Installed*)
- **[.agents/skills/uat/SKILL.md](../.agents/skills/uat/SKILL.md)** - User acceptance testing: end-to-end scenario verification, UX heuristic evaluation (*Agile Testing*)
- **[.agents/skills/deploy/SKILL.md](../.agents/skills/deploy/SKILL.md)** - Delivery & release loop: pipeline-as-code via Makefile/Taskfile, live smoke test verification (*Continuous Delivery*)

### Session Lifecycle & Protocol Skills
- **[.agents/skills/init/SKILL.md](../.agents/skills/init/SKILL.md)** - Canonical session initialization, setup verification, and cold-start resume
- **[.agents/skills/prep-clear/SKILL.md](../.agents/skills/prep-clear/SKILL.md)** - Pre-clear checkpointing, state preservation, and cold-start resume plan
- **[.agents/skills/judge/SKILL.md](../.agents/skills/judge/SKILL.md)** - Prompt & skill evaluation, bug/anti-pattern cataloging, and instruction optimization
- **[.agents/skills/bob-protocol/SKILL.md](../.agents/skills/bob-protocol/SKILL.md)** - Multi-persona coordination protocol, state management, and routing
- **[.agents/skills/bob-tools/SKILL.md](../.agents/skills/bob-tools/SKILL.md)** - `bobp` CLI operations, output capture, and project setup
- **[.agents/skills/build-env/SKILL.md](../.agents/skills/build-env/SKILL.md)** - Build environment setup (`mise.toml`, `Taskfile.yml`, thin `Makefile` shim, manifests) and `docs/SDLC.md` management
- **[.agents/skills/chat/SKILL.md](../.agents/skills/chat/SKILL.md)** - Structured team communication and handoffs in `CHAT.md`
- **[.agents/skills/linter/SKILL.md](../.agents/skills/linter/SKILL.md)** - Code quality, linting, type checks, and static analysis
- **[.agents/skills/make/SKILL.md](../.agents/skills/make/SKILL.md)** - Project Makefile execution with build output capture
- **[.agents/skills/make-discover/SKILL.md](../.agents/skills/make-discover/SKILL.md)** - Makefile target self-discovery guide
- **[.agents/skills/personas/SKILL.md](../.agents/skills/personas/SKILL.md)** - Persona switching and direct specialist delegation
- **[.agents/skills/security/SKILL.md](../.agents/skills/security/SKILL.md)** - Build-time security scans, gitleaks setup, and safe handling of vulnerable dependencies (used by Switch)
- **[.agents/skills/render/SKILL.md](../.agents/skills/render/SKILL.md)** - Render cloud infrastructure and deployment management
- **[.agents/skills/test-runner/SKILL.md](../.agents/skills/test-runner/SKILL.md)** - Bounded test execution and quiet test runners
- **[.agents/skills/via/SKILL.md](../.agents/skills/via/SKILL.md)** - Strict symbol lookup and relationship queries

---

## Team Communication

- **[CHAT.md](CHAT.md)** - Team communication log (append-only)
- Each persona maintains state in their `<name>/` folder:
  - `state.md` - Working memory: Context, Current Task, and Next Steps sections

---

## Template Files

Located in `agents/templates/`:

- `ARTIFACTS.md` - Artifact inventory, rubric quality standards, and review gates (check: CATALOG)
- `_template_USER_STORIES.md` - Sprint user stories (rubric: STORIES)
- `_template_ARCH.md` - System & sprint architecture (rubric: ARCH)
- `_template_DOMAIN.md` - Domain model & ubiquitous language specification (rubric: DOMAIN)
- `_template_task.md` - Sprint task board (rubric: PLAN)
- `_template_SDLC.md` - Software development lifecycle (rubric: SDLC; language profiles: `_template_SDLC.python.md`, `_template_SDLC.javascript.md`)
- `_template_MAKEFILE.md` - Thin `Makefile` forwarding shim to `Taskfile.yml` (rubric: MAKEFILE)
- `_template_TASKFILE.md` - `Taskfile.yml` (go-task v3) build & ops instructions (rubric: TASKFILE)
- `_template_MISE.md` - `mise.toml` project toolchain pins (rubric: MISE)
- `_template_LESSON.md` - Engineering lessons learned (rubric: LESSON)
- `_template_DECISION.md` - Architecture decision record / MADR (rubric: DECISION)
- `_template_finding.md` - Research spike & technical finding (rubric: FINDING)
- `_template_SECURITY_REVIEW.md` - Security review report with scope, threat model, area checklist, and verdict (rubric: SECURITY REVIEW)
- `_template_SECURITY_FINDING.md` - Security finding with severity, evidence, and who-does-what-next (rubric: SECURITY FINDING)
- `_template_TEST_STRATEGY.md` - Quality & UAT strategy (rubric: STRATEGY)
- `_template_UAT_PLAN.md` - Sprint acceptance test plan (rubric: UAT)
- `_template_PERSONA_SKILL.md` - Persona skill scaffold and review rubric (rubric: PERSONA)
- `_template_state.md` - Agent working memory state (check: STATE)
- `_template_CHAT.md` - CHAT.md message format (check: CHAT)
- `_template_tldr.md` - TLDR block formats (check: TLDR)

---

## Tools

Shipped as `bobp` CLI subcommands, not project-local scripts:

- `bobp chat` - Post messages to CHAT.md
- `bobp make <target>` - Run this project's own `make <target>`, captured to build/build.out and posted to CHAT.md
- `bobp setup-agent-links` - Configure Via MCP/index, create missing `agents/PROJECT.md`, and update `.gitignore` (creates no symlinks; may update user-level Codex Via MCP config). See `.agents/skills/bob-tools/SKILL.md` for details.

---

## Archived Documentation

Historical Oracle notes use the `.archive_*.md` prefix. The current archive is
[`oracle/.archive_COMMANDS.md`](oracle/.archive_COMMANDS.md), consolidated into `bob/HELP.md`.

---

## Documentation Standards

### File Naming
- Persona skills and working memory: `.agents/skills/<persona>/SKILL.md` and `agents/<persona>/state.md`
- Shared skills: `.agents/skills/<skill>/SKILL.md`
- Templates: `agents/templates/_template_*.md`
- Archived notes: `.archive_*.md`

### Structure
- Persona and shared skills as real directories in `.agents/skills/`
- Persona working memory and shared team logs in `agents/<persona>/` and `agents/CHAT.md`
- Shared agent instructions in root `AGENTS.md`
- User-facing walkthroughs in `docs/`; startup and command guides in the repository root
- Project documentation index in `agents/DOCUMENTATION_INDEX.md`

### Maintenance
- Update `*help` when adding commands
- Update tool docs when changing MCPs
- Archive outdated docs with `.archive_` prefix
- Keep `agents/bob/HELP.md`, `STARTUP.md`, and `SHORTHAND_GUIDE.md` in sync with active skills and templates
- Keep this index and its packaged mirror in `bobp/templates/agents/` synchronized

---

## Quick Command Reference

```bash
*help                          # Show complete help (Bob)
*init                          # Initialize session & ready team (Bob)
*prep-clear                    # Checkpoint state before /clear (Active)
*plan epic <name>              # Strategic epic discovery & shaping
*plan story <slice>            # User story slicing & ADRs
*plan sprint                   # Sprint planning container & task board
*impl <task>                   # Feature TDD work-loop (Neo → Trin → Switch → Morpheus)
*fix <defect>                  # Defect diagnosis & surgical fix work-loop
*refactor <target>             # Behavior-preserving refactoring work-loop
*spike <topic>                 # Timeboxed disposable research spike
*uat <scope>                   # End-to-end acceptance & UX audit
*deploy <env>                  # Pipeline deployment & smoke test
*swe impl <task>               # Direct implementation (Neo)
*qa test <scope>               # Direct testing (Trin)
*lead arch <topic>             # Direct architecture guidance (Morpheus)
*ora ask <question>            # Query knowledge base (Oracle)
*sm status                     # Sprint progress & blockers (Mouse)
*pm story <request>            # User story requirements (Cypher)
*user review <scope>           # Usability & HCI review (Smith)
*devops deploy <env>           # Infrastructure & deployment (Tank)
*sec review <target>           # Security review (Switch)
```

---

**For Help:** Type `*help` or read `agents/bob/HELP.md`
