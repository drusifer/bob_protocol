# bobp

`bobp` is the packaged, installable front-end for the **Bob Protocol** — a
multi-persona AI development framework for Codex, Gemini CLI, Cursor, Copilot,
and other Agent Skills harnesses. It wraps the loose collection of helper scripts
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

### Versions and keeping a project current

`bobp --version` (or `-V`) prints the installed version. `bobp install` and
`bobp update` record that version in the project as `agents/.bobp-version`.
When you run any other `bobp` command inside a project whose recorded version
is missing or older than the installed bobp, it prints one line to stderr
with the command to run and then carries on with what you asked:

```text
bobp: this project was set up with bobp 0.1.0; installed is bobp 0.2.0. Run: bobp update /path/to/project
```

bobp never asks a question or changes the project on its own. The line repeats
on every run until you run `bobp update`. Set `BOBP_NO_VERSION_CHECK=1` to
silence it (for example in CI).

### Harness discovery (skills, subagents, and `AGENTS.md`)

`bobp install` and `bobp update` install all 35 skills (10 personas and 25 shared skills) as real directories under `.agents/skills/`, compile 30 harness-native subagent definitions (10 personas × 3 harnesses), and write shared instructions to a real root `AGENTS.md` with **no symlinks**:

- **Harness-native persona subagents (all 10 personas, shared working memory):**
  - **Claude Code:** `.claude/agents/<persona>.md` (native persona discovery + `--agent <persona>`)
  - **OpenAI Codex:** `.codex/agents/<persona>.toml`
  - **Gemini CLI:** `.gemini/agents/<persona>.md` (`kind: local`)
  - Every generated subagent across all three harnesses reads and updates the **exact same** `agents/<persona>/state.md` and `agents/CHAT.md` (zero harness-private memory, inherited model and tools) so you can switch harnesses mid-task seamlessly. Ownership is tracked in `agents/.bobp-subagents` so custom user agents are never overwritten.
- **Skills (`.agents/skills/`):** discovered automatically by Codex, Gemini CLI, Cursor, and Copilot. Claude Code reads its 10 personas natively from `.claude/agents/` and loads shared workflow skills from `.agents/skills/` on demand.
- **Root instructions (`AGENTS.md`):** read natively by Codex, Cursor, and Copilot. **Gemini CLI** requires adding `"AGENTS.md"` to `context.fileName` in its own settings.

## What's in here

- **`bobp/tools/`** — the actual implementation: posting to `CHAT.md`,
  rendering the Mermaid chat diagram, conflict-safe merging of timestamped
  Markdown logs (`bobp merge`, plus opt-in Git merge driver), installing real
  skills in `.agents/skills/` and configuring Via MCP/capabilities, the `make`
  output filter, TL;DR tooling, session tracing, and persona evaluation.
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
- **Templates & Review Rubrics**: Standardized artifact templates and binary quality checks cataloged in [`agents/templates/ARTIFACTS.md`](agents/templates/ARTIFACTS.md) (stories, architecture, domain model, tasks, ADRs, SDLC, `mise.toml`/`Taskfile.yml`/`Makefile`, security reviews, test strategies, UAT plans, lessons, and persona skills).

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
