---
name: build-env
description: Set up a project's build environment with mise (mise.toml), Task (Taskfile.yml), and a thin Makefile forwarding shim alongside the language's manifest (Python pyproject.toml + .venv, JavaScript package.json + lockfile, Go, Rust, ...), and record it in docs/SDLC.md. Use when bootstrapping a build environment, adding a language, updating docs/SDLC.md, or checking for drift at sprint close.
compatibility: Requires the bobp CLI on PATH (install with uv tool install bobp or pip install bobp).
---

One-line summary: Tank bootstraps a build environment using `mise.toml` for pinned tools, `Taskfile.yml` (go-task v3) for build instructions, a thin `Makefile` forwarding shim, and the language's own manifest isolated inside the project.

TLDR:
    Detect what exists first; never replace a package manager, manifest, or traditional Makefile the project already chose unless migration is requested.
    For new projects: pin runtimes and CLI tools in `mise.toml`, put build/test/ops tasks in `Taskfile.yml` (go-task v3), and keep `Makefile` as a thin forwarding shim (`bobp make <target>` -> `task <target>`).
    For new Python projects, use uv by default.
    The language's manifest is the source of truth (pyproject.toml, package.json, go.mod, Cargo.toml); `Taskfile.yml` invokes the native tool.
    Everything installs inside the project (.venv, node_modules) or via `mise install` — never system-wide, never with sudo.
    Done means: from a clean checkout, `mise install` (when present) and `bobp make install && bobp make test` work, and docs/SDLC.md describes it.
    Tank owns docs/SDLC.md. No sprint starts without it; Tank checks the project against it at every sprint close.

# Build Environment Skill

## Triggers

`*devops bootstrap`, `*devops build-env`, `*build-env`, `*devops sdlc`, `*devops sdlc-check`

## When to use

Tank owns this. Run it when:

- a project has no build environment yet (new repo, or code with no manifest);
- a new language or runtime is being added to an existing repo;
- the first third-party dependency is about to be added and there is nowhere declared to put it;
- setup is ad hoc — a bare `requirements.txt`, install steps that live only in a README, "works on
  my machine" reports, or an interpreter that refuses installs (e.g. Python's PEP 668
  "externally-managed-environment" error).

Any persona who hits one of these hands off rather than improvising:
`@Tank *devops bootstrap <language>`.

After the initial setup the manifest belongs to the people changing the code: Neo adds and bumps
dependencies in it. Tank is called back only when the *mechanism* changes — a new language, a
different package manager, a new tool-version pin, or a new standard target.

## Principles

These explain the choices below, so apply them to languages this skill doesn't list.

1. **Detect before you create.** A lockfile or manifest already in the repo is a decision someone
   made. Build on it. Switching package managers is a separate proposal for the user, not part of
   a bootstrap.
2. **Use the ecosystem's convention, not your own.** Each language has one manifest that its tools,
   editors and CI already understand. Put dependencies, tool settings and entry points there.
   Do not invent parallel files or wrapper scripts for things the native tool does.
3. **Isolate inside the project.** Dependencies go in a project-local environment that is
   gitignored. Never install into the system or user interpreter, never use `sudo`, never pass
   override flags such as `--break-system-packages` or `npm install -g`. System installs collide
   with the OS package manager and make the project unreproducible.
4. **`Taskfile.yml` holds the build instructions; `Makefile` is a thin forwarding shim; the native tool does the work.** Every routine task has the same name in every project, so people and agents never need to know which language they are in. For new setups, pin runtimes and CLI tools (`task = "3"`, `gitleaks = "8"`, etc.) in `mise.toml`, declare recipes in `Taskfile.yml` calling the native tool, and forward `make <target>` / `bobp make <target>` through a thin `Makefile` shim. Preserve an existing traditional `Makefile` unless migration is requested.
5. **Reproducible by default.** Commit `mise.toml` and the language lockfile when the ecosystem has one. Pin runtime and CLI versions cleanly. `install` must be safe to run twice.
6. **Prove it from clean.** Setup is not done until it has been deleted and rebuilt once.

## Procedure

1. **Survey.** List manifests, lockfiles, `mise.toml`, `Taskfile.yml`, version pins, existing Makefile targets, CI config and
   any install instructions in docs. Check which tools are actually on the machine
   (`command -v mise task uv npm pnpm go cargo ...`) and whether the system interpreter is managed by the OS.
2. **Decide and say why.** Pick the manifest, package manager and environment location. Prefer, in
   order: what the repo already uses → what a present lockfile implies → the ecosystem default in
   the tables below. For new build automation, default to `mise.toml` + `Taskfile.yml` + thin `Makefile` shim. Post the choice and the reason to CHAT.md before writing files.
3. **Write `mise.toml` and the manifest.** Pin `task = "3"`, `gitleaks = "8"`, and project runtimes/CLIs in `mise.toml`. In the language manifest, declare project metadata, runtime dependencies, a separate dev/test dependency
   group, tool configuration, and entry points for any CLI. Migrate existing dependency lists
   into it without changing versions.
4. **Write `Taskfile.yml` and wire the thin `Makefile` shim.** Define the standard tasks in `Taskfile.yml` (`version: '3'`, `env: PATH` including `{{.HOME}}/.local/share/mise/shims`, `default` / `help` running `task --list`) and front them with a thin `Makefile` forwarding shim (next section). If an existing repo already has a traditional `Makefile`, keep its targets working and add to it unless migrating.
5. **Ignore and pin.** Add the environment directory and `.task/` (Task checksum cache) to `.gitignore`. Add the runtime version pin.
6. **Verify from clean.** Remove the environment directory, then run `mise install` (when applicable) and `bobp make install` followed by
   `bobp make test`. Run `bobp make install` a second time to confirm it is idempotent.
7. **Write `docs/SDLC.md`** (see below) so the choices outlive this session.
8. **Hand off.** Update the README setup section to the two commands above, post the summary to
   CHAT.md (what was chosen, how to add a dependency, anything not verified), and note the
   decision for Oracle.

Ask the user before deleting or replacing a file someone else maintains (an old
`requirements.txt`, a `setup.py`, a hand-written install script). Migrating its contents is in
scope; removing it is their call.

## `docs/SDLC.md` — the project's source of truth for change management, owned by Tank

`docs/SDLC.md` records the project's toolchain, setup, make targets, dependency rules, quality gates, change classes, release process, known deviations, and conformance check. Where generic workflow skills disagree with `docs/SDLC.md`, the SDLC wins. **Tank is the only persona who edits `docs/SDLC.md`**; others propose changes with `@Tank *devops sdlc <what and why>`.

- **Sprint-start gate (blocker):** No sprint is planned without `docs/SDLC.md`. If missing, stop and post `@Tank *devops sdlc`.
- **Authoring, templates, rubric, and sprint-close conformance check:** Read [SDLC guide](references/sdlc-guide.md) when creating, updating, or auditing `docs/SDLC.md` (`*devops sdlc`, `*devops sdlc-check`).

## Standard `Taskfile.yml` & Thin `Makefile` Contract

Use these names in `Taskfile.yml` (forwarded by the thin `Makefile` shim). Omit a task only when it has no meaning for the project; never rename one.

| Task / Target | Does | Notes |
|---|---|---|
| `install` | Create the local environment and install all dependencies, including dev tools | Idempotent. The only task allowed to touch the network (besides `mise install`). |
| `test` | Run the test suite | The gate Trin and CI use — must be the same command in both. |
| `lint` | Static checks (style, types) without changing files | |
| `format` | Rewrite files to the project style | |
| `build` | Produce the distributable artifact | Only if the project ships one. |
| `run` | Start the app / primary entry point | Pass extra arguments via `ARGS="..."` (`{{.CLI_ARGS}}`). |
| `clean` | Remove build outputs and caches (including `.task/`) | Leaves the environment in place. |
| `distclean` | `clean` plus remove the local environment | Used for the from-clean check. |
| `help` | List tasks with descriptions | `default:` task with `aliases: [help]` running `task --list`. |

Rules for `mise.toml`, `Taskfile.yml`, and the thin `Makefile` shim:

- Pin `task = "3"`, `gitleaks = "8"`, and project runtimes/CLIs in `mise.toml`.
- Prepend `{{.HOME}}/.local/share/mise/shims` to `PATH` in `Taskfile.yml` (`env:`) and `Makefile` (`export PATH := ...`) so tools resolve without `mise activate`.
- Run language tools via the local environment (`uv run pytest`, `npm run test`).
- Fail fast with a one-line hint when `task` or the local env is missing (`_check-task` in `Makefile`, `preconditions:` in `Taskfile.yml`).
- Guard build files from `%:` (`Makefile Taskfile.yml mise.toml: ;`) and forward `ARGS` via `$(if $(ARGS),-- $(ARGS))` to `{{.CLI_ARGS}}`.
- Keep pre-Task scripts (`doctor`, `init`) in `Makefile` only when they must run before `task` is installed.
- Use `method: checksum` + `sources:` for expensive steps and gitignore `.task/`.
- Multi-language repos: add suffixed tasks (`install-py`, `test-py`, ...) composed under the unsuffixed task.
- Agents invoke tasks via `bobp make <target>` (see the `make` skill).

Read [language conventions](references/language-conventions.md) when creating or changing a language-specific build environment.

## Done when

- [ ] `mise.toml` pins `task`, `gitleaks`, and runtimes/CLIs; the manifest declares all imports and dev tools.
- [ ] `Taskfile.yml` defines `install`, `test`, `help` (and `lint`/`format`/`build`/`run`/`clean`/`distclean` where meaningful), fronted by a thin `Makefile` shim (or preserved `Makefile`).
- [ ] Local environment dir and `.task/` are gitignored; `mise.toml` and lockfile (if any) are committed.
- [ ] Clean rebuild works (`bobp make install` twice + `bobp make test`) with nothing installed system-wide.
- [ ] `docs/SDLC.md` covers every section above with a Last verified line; README uses `mise install` + `make`/`task`.
- [ ] CHAT.md handoff posted: choices and reasons, how to add a dependency, anything unverified.

## Boundaries

- Tank does not edit application source to make a build pass. Report the failure to Neo.
- Do not change dependency versions while migrating them into a manifest; raise upgrades separately.
- CI, containers and deploy configuration should call the same `make` targets — wiring them is
  Tank's `*devops ci` / `*devops infra` work, not part of this skill.

## Gotchas

- **`bobp make distclean` wrapper caveat (SDLC §9):** `distclean` deletes `build/`, where `bobp make` keeps `build/build.out`, so the wrapper exits with `FileNotFoundError` after `distclean` succeeds. Run `distclean` and `install` as separate commands.
- **Never overwrite an existing toolchain unasked:** Detect existing manifests, lockfiles, and traditional `Makefile`s before generating `mise.toml` / `Taskfile.yml`; switching package managers requires explicit user approval.
- **No system-wide installs:** Never use `sudo`, `--break-system-packages`, or unpinned global installs; isolate dependencies inside `.venv/` / `node_modules/` or `mise.toml`.
