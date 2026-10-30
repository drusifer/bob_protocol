# Bob Protocol — SDLC

This document is the source of truth for building, testing, changing, and releasing this repository. Tank owns it; propose changes with `@Tank *devops sdlc <what and why>`. Update the tooling and this document together.

## 1. Toolchain

| | Python | JavaScript tools |
|---|---|---|
| Runtime | 3.15 development; package supports `>=3.10,<4` | Node `>=22.22.0` for Promptfoo; Node/npm for Mermaid |
| Manifest / lock | `pyproject.toml` / `uv.lock` | `tools/persona-eval/package.json` / `tools/persona-eval/package-lock.json`; Mermaid has no lock |
| Manager / environment | uv / `.venv/` | npm / each tool's `node_modules/` |

`.python-version` selects the latest available Python 3.15 patch. Python requirements use minimum versions; `uv.lock` records the current compatible resolution. Package version is in `bobp/__init__.py`.

## 2. Setup

Install uv and Node/npm. From a clean checkout:

```sh
uv sync --python 3.15 --locked --extra dev
uv run bobp make test
```

uv supplies Python when needed. Mermaid dependencies install on the first lint run. For Promptfoo, run `uv run bobp make install-evals`; Codex must already be logged in locally. The evaluator does not copy credentials into the fixture.

## 3. Make targets and persona evaluation

Run project targets with `bobp make <target>`; prefix with `uv run` when the local CLI is not on `PATH`.

| Target | Purpose |
|---|---|
| `install` | Sync the locked Python environment |
| `install-evals` | Install locked Promptfoo dependencies |
| `test`, `test-q` | Full pytest suite; focused pytest selection (`ARGS="-k name"`) |
| `lint`, `lint-mermaid` | Validate Mermaid fences with the real parser |
| `build` | Build wheel and sdist in `dist/` |
| `system-install` | Optional editable pipx install of `bobp` |
| `clean` | Remove `build/`, `dist/`, and egg metadata; keep `.venv/` |
| `distclean` | Run `clean` and remove `.venv/` |
| `help` | List available targets |
| `deploy-forgejo` | Publish through the external pi-patch script |

There is no `format` or application `run` target. `lint` checks Mermaid only; Python lint/type checks and secret scanning are not configured.

```sh
uv run bobp make install-evals
uv run bobp persona-eval --list
uv run bobp persona-eval <persona-or-suite>
```

Each eval uses a versioned catalog suite, a fresh fixture under `build/persona-eval/runtime/`, and local `bobp install`. It checks installed skill use, then grades the generated artifact with its shared artifact-type rubric. Reports and pytest scratch stay under `build/`, never `/tmp`. Prompts and rubrics are stable; model output and grading are probabilistic. Run one fresh case by default, use `--repeat N` for higher-impact changes, and record failures rather than retrying until green. The catalog currently covers Bob persona authoring and Morpheus design advice. Trin adds/selects a matching suite before signing off when changed behavior lacks coverage. This local subscription-backed eval is a required persona-change gate; CI does not run it.

## 4. Dependencies

- Python: add/remove runtime packages in `[project].dependencies` and dev packages in `[project.optional-dependencies].dev`; run `uv lock` and commit `pyproject.toml` plus `uv.lock`.
- Promptfoo: add/update packages with `npm install --prefix tools/persona-eval --save-dev <package>`; remove with `npm uninstall --prefix tools/persona-eval <package>`. Commit the manifest and lockfile together.
- Mermaid: change `tools/mermaid_validate/package.json` and run `npm install --prefix tools/mermaid_validate`; no lockfile is committed, so its resolved versions are not reproducibly locked.
- Neo maintains application dependencies. New runtimes, managers, Make targets, or quality gates go through Tank.

## 5. Quality gates

| Gate | Command | When |
|---|---|---|
| Python tests | `bobp make test` | Before Trin handoff and at sprint close |
| Focused tests | `bobp make test-q ARGS="-k name"` | During implementation |
| Mermaid validation | `bobp make lint` | When changing diagrams |
| Persona behavior/artifact | `bobp persona-eval <persona-or-suite>` | Trin sign-off for persona-skill changes |
| Package build | `bobp make build` | Release review |

Trin owns gate assertions; Tank owns the runner. Morpheus reviews architecture, and Smith reviews changed user-facing behavior.

## 6. Change management

| Class | Examples | Approval and gates | Record |
|---|---|---|---|
| Routine | Feature, fix, refactor, docs | User-defined scope; relevant Trin QA, persona eval, Morpheus architecture review, or Smith UX review | `task.md` for sprint work, `agents/CHAT.md`, commit |
| Mechanism | Runtime, manifests, Make targets, eval harness, SDLC | Tank review and user agreement; tests and clean-environment check | `docs/SDLC.md`, chat |
| Release | Version bump or publication | Explicit user authorization; build and applicable tests | Version file, tag/release record |
| Emergency | Urgent repository fix | User authorization; relevant tests, then next-sprint review | Chat and follow-up task |

Requests come from the user. Use Bob Protocol planning loops for multi-step work and `task.md` as the single sprint board. The default branch is `main`; direct pushes are permitted and no branch protection is configured. Commit messages follow the recent Conventional Commit pattern (`feat:`, `docs:`, `chore:`). Commit or push only when directed by the user. Never commit credentials, `.venv/`, `node_modules/`, or generated eval output. Revert an integrated bad change with a reviewed `git revert`.

## 7. Versioning and release

Update `bobp.__version__` in `bobp/__init__.py` for a release. `bobp make build` creates `dist/`; `deploy-forgejo` uses a script in the external pi-patch checkout. The existing GitHub release workflow attempts PyPI publication on a published release, but its configuration says trusted-publisher setup is incomplete; verify it before use.

## 8. CI and deployment

`.github/workflows/ci.yml` runs pytest and a CLI help check on pushes to `main` and pull requests using pip and Python 3.10–3.12. `.github/workflows/release.yml` handles published releases. No new Actions workflow or commit hook is part of the local persona-eval gate.

## 9. Known deviations

- Local development uses uv/Python 3.15; CI still uses pip/Python 3.10–3.12 and does not cover the newest runtime.
- Mermaid has no npm lockfile. Local Node 24.13.0 passes lint but emits a transitive dependency engine warning requiring Node 24.15.0 (or 22.22.2+).
- Promptfoo uses local subscription auth and is not run in CI. PyPI trusted publishing is not configured.
- Full tests and lint passed in the existing uv environment; the clean `distclean` rebuild remains for Tank's sprint-close conformance check.

## 10. Conformance check

At sprint close, Tank runs `uv run bobp make distclean`, `uv sync --python 3.15 --locked --extra dev`, `uv run bobp make test`, and all other applicable gates. Confirm Python imports are declared and `uv.lock` matches; eval package changes update its npm lockfile; Make targets match section 3; runtime data stays in `build/`; `.venv/`, `node_modules/`, and generated data remain ignored; workflows still match sections 5 and 8; and the sprint followed section 6.

---
*Last verified: 2026-10-30 against workspace based on `a976401` by Tank.*
