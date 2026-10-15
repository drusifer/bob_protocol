# bobp

`bobp` is the packaged, installable front-end for the **Bob Protocol** — a
multi-persona AI development framework for Claude Code, Codex, and other
agent harnesses. It wraps the loose collection of helper scripts
(`chat.py`, `setup_agent_links.py`, `make.py`, …) that the protocol relies on
into a single `bobp` command, and ships the persona/skill/template content
needed to scaffold the framework into any project.

> Status: pre-release, not yet published to PyPI. Install from source for now.

## Install (from source)

```bash
git clone git@github.com:drusifer/bob_protocol.git
cd bob_protocol
pip install -e .
```

This installs the `bobp` command and the `bobp` Python package (including
`bobp.tools`, the modules backing each subcommand).

## What's in here

- **`bobp/tools/`** — the actual implementation: posting to `CHAT.md`,
  rendering the Mermaid chat diagram, setting up `.claude/skills/` and
  Codex skill links, the `make` output filter, TL;DR tooling, session
  tracing.
- **`bobp/templates/`** — the redistributable Bob Protocol scaffolding
  (persona `SKILL.md` files, shared skills, document templates) that
  `bobp install` copies into a target project. See
  [`bobp/templates/README.md`](bobp/templates/README.md) for what the
  protocol itself provides once installed.
- **`agents/`** (repo root) — this project dogfoods its own framework: Bob
  Protocol is installed into `bob_protocol` itself, so the personas
  (Neo, Trin, Morpheus, Oracle, …) have real state and chat history here,
  same as any other project that installs `bobp`. This is the *live*
  instance, not the template — don't confuse it with
  `bobp/templates/agents/`, which is the generic, reusable source that
  ships in the package.

## Bob Protocol Overview

Bob Protocol coordinates autonomous, multi-agent software engineering through specialized personas and structured SDLC loops:

- **The Team (9 Personas)**: **Neo** (Senior SWE), **Morpheus** (Tech Lead), **Trin** (QA Guardian), **Oracle** (Knowledge Officer), **Mouse** (Scrum Master), **Cypher** (Product Manager), **Bob** (Prompt Engineer), **Smith** (Expert User & UX Advocate), **Tank** (DevOps Engineer).
- **Planning Loops (Strategic Scoping)**: `*plan epic` (*Shape Up* / *Inspired*), `*plan story` (*User Story Mapping* / *Agile Estimating*), `*plan sprint` (*The Scrum Guide*).
- **Work Loops (Tactical Execution)**: `*impl` (TDD — *Beck*), `*fix` (Surgical diagnosis & fix — *Agans*), `*refactor` (Two-Hats behavioral parity — *Fowler*), `*spike` (Disposable exploration — *XP Installed*), `*uat` (User acceptance testing — *Crispin & Gregory*), `*deploy` (Continuous delivery & smoke test — *Humble & Farley*).
- **Loop Conductor (`*bloop`)**: Autonomous multi-persona execution engine with strict anti-loop guards (max 2 failures $\rightarrow$ Oracle $\rightarrow$ user escalate) and context budgeting (`*prep-clear`).
- **Review Rubrics**: 10 Brookhart-compliant quality rubrics measuring deliverable quality and loop effectiveness.

See **[STARTUP.md](STARTUP.md)** for LLM session startup instructions and **[SHORTHAND_GUIDE.md](SHORTHAND_GUIDE.md)** for the complete trigger reference.

## Development

```bash
pip install -e ".[dev]"
make test        # or: python -m unittest discover -s tests
```

## License

GPLv3 — see [LICENSE](LICENSE).
