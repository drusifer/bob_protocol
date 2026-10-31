# bobp

`bobp` is the packaged, installable front-end for the **Bob Protocol** — a
multi-persona AI development framework for Claude Code, Codex, and other
agent harnesses. It wraps the loose collection of helper scripts
(`chat.py`, `setup_agent_links.py`, `make.py`, …) that the protocol relies on
into a single `bobp` command, and ships the persona/skill/template content
needed to scaffold the framework into any project.

> Status: `bobp` 0.1.0 is published on PyPI (`pip install bobp` or `uv tool install bobp`). The `main` branch is ahead of that release (for example, it adds the Switch security persona); install from source to use it before the next release.

## Contents

- [Install](#install)
- [What's in here](#whats-in-here)
- [Bob Protocol overview](#bob-protocol-overview)
- [Development](#development)
- [Documentation and guides](#documentation-and-guides)
- [License](#license)

## Install

From PyPI (latest release):

```bash
uv tool install bobp   # or: pip install bobp
bobp --help
```

From source (latest `main`):

```bash
git clone git@github.com:drusifer/bob_protocol.git
cd bob_protocol
uv sync --python 3.15 --locked --extra dev
uv run bobp --help
```

This creates the locked development environment in `.venv/` and runs the
packaged CLI from that environment. To install `bobp` as a uv-managed user
tool, run `uv run bobp make system-install` from the checkout.

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

- **The Team (10 Personas)**: **Neo** (Senior SWE), **Morpheus** (Tech Lead), **Trin** (QA Guardian), **Oracle** (Knowledge Officer), **Mouse** (Scrum Master), **Cypher** (Product Manager), **Bob** (Prompt Engineer), **Smith** (Expert User & UX Advocate), **Tank** (DevOps Engineer), **Switch** (Security Engineer).
- **Planning Loops (Strategic Scoping)**: `*plan epic` (*Shape Up* / *Inspired*), `*plan story` (*User Story Mapping* / *Agile Estimating*), `*plan sprint` (*The Scrum Guide*).
- **Work Loops (Tactical Execution)**: `*impl` (TDD — *Beck*), `*fix` (Surgical diagnosis & fix — *Agans*), `*refactor` (Two-Hats behavioral parity — *Fowler*), `*spike` (Disposable exploration — *XP Installed*), `*uat` (User acceptance testing — *Crispin & Gregory*), `*deploy` (Continuous delivery & smoke test — *Humble & Farley*).
- **Loop Conductor (`*bloop`)**: Autonomous multi-persona execution engine with strict anti-loop guards (max 2 failures $\rightarrow$ Oracle $\rightarrow$ user escalate) and context budgeting (`*prep-clear`).
- **Review Rubrics**: 10 Brookhart-compliant quality rubrics measuring deliverable quality and loop effectiveness.

See **[STARTUP.md](STARTUP.md)** for LLM session startup instructions, **[docs/WALKTHROUGH.md](docs/WALKTHROUGH.md)** for a complete step-by-step tutorial, and **[SHORTHAND_GUIDE.md](SHORTHAND_GUIDE.md)** for the complete trigger reference.

## Development

```bash
uv sync --python 3.15 --locked --extra dev
uv run bobp make test   # captured project test run
uv run bobp make install-hooks    # enable the gitleaks pre-commit hook (once per clone)
uv run bobp make security-scan     # secrets + dependency audits
uv run bobp make release           # tag v<version> and publish via GitHub Release to PyPI
```

See [docs/SDLC.md](docs/SDLC.md) for the full toolchain, gates, and release process.

## Documentation and guides

- [Documentation index](agents/DOCUMENTATION_INDEX.md) — personas, skills, and templates
- [Startup guide](STARTUP.md) — initialize or resume a Bob Protocol session
- [Shorthand guide](SHORTHAND_GUIDE.md) — command and skill trigger reference
- [Walkthrough](docs/WALKTHROUGH.md) — build an example application with the workflow
- [Persona evaluation](docs/PERSONA_EVALUATION.md) — setup, run, and review persona eval suites
- [SDLC](docs/SDLC.md) — toolchain, quality gates, and change lifecycle
- [Packaged template README](bobp/templates/README.md) — framework scaffolding shipped by `bobp`

## License

GPLv3 — see [LICENSE](LICENSE).
