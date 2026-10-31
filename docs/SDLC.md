# Bob Protocol — SDLC

This document is the source of truth for building, testing, changing, and releasing this repository. Tank owns it; propose changes with `@Tank *devops sdlc <what and why>`. Update the tooling and this document together.

## 1. Toolchain

| | Python | JavaScript tools |
|---|---|---|
| Runtime | 3.15 development; package supports `>=3.10,<4` | Node.js `>=22.22.0` and npm for persona evaluation; Node/npm for Mermaid |
| Manifest / lock | `pyproject.toml` / `uv.lock` | Packaged `bobp/tools/persona_eval_assets/package.json` and lockfile; Mermaid has no lock |
| Manager / environment | uv / `.venv/` | npm / each tool's `node_modules/` |

`.python-version` selects the latest available Python 3.15 patch. Python requirements use minimum versions; `uv.lock` records the current compatible resolution. Package version is in `bobp/__init__.py`.

## 2. Setup

Install uv and Node/npm. From a clean checkout:

```sh
uv sync --python 3.15 --locked --extra dev
uv run bobp make test
```

Persona evaluation has external system prerequisites: Node.js `>=22.22.0`, npm on `PATH`, and a TypeSafe API key in `TYPESAFE_API_KEY`. `pip install bobp` installs the official `typesafe-sdk` Python dependency, but does not install system executables or npm packages. The `bobp persona-eval --setup` command checks Node.js/npm and prints the global install command; evaluation checks Node.js/npm and the API key with actionable errors when prerequisites are missing or outdated. Setup does not install packages or write files into the user's project. Promptfoo and the Codex SDK are pinned in Bobp's packaged npm manifest. The Codex SDK runs each target persona using the user's existing local Codex login; Jev grades each rubric criterion through TypeSafe's API. The evaluator does not copy Codex credentials into the fixture. Eval content and artifacts are sent to TypeSafe for rubric grading. uv supplies Python when needed, and Mermaid dependencies install on the first lint run. For Promptfoo, run `uv run bobp persona-eval --setup` and follow its instructions.

## 3. Make targets and persona evaluation

Run project targets with `bobp make <target>`; prefix with `uv run` when the local CLI is not on `PATH`.

| Target | Purpose |
|---|---|
| `install` | Sync the locked Python environment |
| `install-evals` | Print instructions for globally installing pinned Promptfoo dependencies |
| `test`, `test-q` | Full pytest suite; focused pytest selection (`ARGS="-k name"`) |
| `lint`, `lint-mermaid` | Validate Mermaid fences with the real parser |
| `build` | Build wheel and sdist in `dist/` |
| `system-install` | Optional editable `uv tool` install of `bobp` into uv's tool environment |
| `clean` | Remove `build/`, `dist/`, and egg metadata; keep `.venv/` |
| `distclean` | Run `clean` and remove `.venv/` |
| `help` | List available targets |
| `deploy-forgejo` | Publish through the external pi-patch script |
| `release` | Run tests, tag `v<version>` (version from `bobp/__init__.py`), push the tag, and create the GitHub Release; the release workflow publishes to PyPI by trusted publishing. Needs `gh` authorized to create releases; runs only from `main` matching `origin/main`; refuses if the release exists |

There is no `format` or application `run` target. `lint` checks Mermaid only; Python lint/type checks and secret scanning are not configured.

```sh
uv run bobp persona-eval --setup
uv run bobp persona-eval --list
uv run bobp persona-eval <persona-or-suite>
```

Each eval uses a versioned catalog suite, a fresh fixture under `build/persona-eval/runtime/`, and local `bobp install`. It checks installed skill use, then grades either a generated artifact with its shared artifact-type rubric or a focused persona behavior against its installed skill and role-specific criteria. Promptfoo runs the scenarios with the local Codex login. The custom Python assertion sends Jev structured state containing the scenario, full rubric, persona instructions, candidate response or artifact, expected artifact path, declared capabilities, and a concise fixture path inventory. For each atomic rubric criterion, Jev returns a `Choice` classification (`meets`, `partially_meets`, or `does_not_meet`) and an ordered three-level `Score` (expected value 0–2); both include confidence/probability data. A criterion passes only when the classifier says `meets` and the score distribution's most likely level also says `meets`; the probability-weighted expected score is reported separately, and differing most-likely levels are flagged for review. Persona-section headings, shared-baseline text, values count, and sayings count are checked deterministically; Jev classifies the role relevance of each saying and scenario behavior. Reports and pytest scratch stay under `build/`, never `/tmp`. Prompts and rubric criteria are stable during a target-fix loop; target output and Jev judgments are probabilistic. Run one fresh case by default, use `--repeat N` for higher-impact changes, and record failures rather than retrying until green. The catalog covers Bob authoring, Morpheus design advice, and focused personality-behavior suites for the other eight personas. Trin adds/selects a matching suite before signing off when changed behavior lacks coverage. This local persona-change gate does not run in CI.

## 4. Dependencies

- Python: add/remove runtime packages in `[project].dependencies` and dev packages in `[project.optional-dependencies].dev`; run `uv lock` and commit `pyproject.toml` plus `uv.lock`. `typesafe-sdk` is a runtime dependency used by the Jev rubric grader.
- Persona evaluation system prerequisites: Node.js `>=22.22.0`, npm, and `TYPESAFE_API_KEY` are external prerequisites; declare them in this document and preserve the evaluator's startup checks and actionable errors.
- Promptfoo and Codex SDK: update `bobp/tools/persona_eval_assets/package.json` and lockfile with npm (`npm install --prefix bobp/tools/persona_eval_assets --save-dev <package>`); remove with `npm uninstall --prefix bobp/tools/persona_eval_assets <package>`. Commit both packaged assets. Users install the pinned dependencies globally with the command printed by `bobp persona-eval --setup`; Bobp does not install packages into their projects.
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
- Promptfoo's Codex target provider uses local subscription auth; Jev grading uses the external TypeSafe API and is not run in CI. PyPI trusted publishing is not configured.
- Full tests and lint passed in the existing uv environment; the clean `distclean` rebuild remains for Tank's sprint-close conformance check.

## 10. Conformance check

At sprint close, Tank runs `uv run bobp make distclean`, `uv sync --python 3.15 --locked --extra dev`, `uv run bobp make test`, and all other applicable gates. Confirm Python imports are declared and `uv.lock` matches; eval package changes update its npm lockfile; Make targets match section 3; runtime data stays in `build/`; `.venv/`, `node_modules/`, and generated data remain ignored; workflows still match sections 5 and 8; and the sprint followed section 6.

---
*Last verified: 2026-10-30 against workspace based on `a976401` by Tank.*
