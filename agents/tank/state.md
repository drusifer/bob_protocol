# Agent State

## Context
- User approved a local Promptfoo persona gate using the Codex subscription; no new Actions or commit hooks. Direct pushes remain allowed.
- Ownership: Bob authors personas; Trin owns evaluation/sign-off; Morpheus reviews architecture; Tank owns tools and `docs/SDLC.md`.
- Development uses uv and Python 3.15 (latest patch available through uv); `pyproject.toml` retains `>=3.10,<4`, and Python requirements/lock resolve to current compatible versions.
- `bobp persona-eval` runs versioned catalog suites in isolated projects installed by the current checkout's `bobp install`. Current suites cover Bob persona authoring and Morpheus design advice, judged by their shared artifact rubrics. Reports and pytest/subprocess scratch remain in `build/`.
- Existing CI uses pip/Python 3.10–3.12 and does not run Promptfoo. PyPI trusted publishing is now configured (pending publisher bobp -> drusifer/bob_protocol, release.yml, env `pypi`, reviewer approval required). Mermaid package has no lockfile; Node 24.13 lint passes with an engine warning. These are documented deviations.
- `docs/SDLC.md` is drafted; README development commands now use uv. Full suite: 88 passed, 7 skipped, 9 subtests; Mermaid lint passed. A clean `distclean` rebuild remains for sprint close to avoid deleting retained eval reports from `build/`.

## Current Task
**Status:** Sprint 5 Task C.1 SDLC conformance check PASSED (2026-11-28); Sprint 5 LAUNCHED (`384 passed, 2 skipped, 435 subtests`, lint, security-scan, build `bobp-0.3.1` green; `docs/SDLC.md` §7 updated).
**Assigned to:** Oracle (`*ora groom`)
**Progress:** Updated `docs/SDLC.md` §3 (per-skill `evals/evals.json`, `--list --json`, evaluating-skills workspace/baseline layout), §7 (real `.agents/skills/`, no links, root `AGENTS.md`, `bobp merge`, agent-safe `--help`/`--dry-run`/`clean --yes`), §9 (clean rebuild record & live-eval owner-approval deferral), and `Last verified: 2026-11-28`. Ran full clean rebuild: `bobp make distclean` (documented SDLC §9 `build/build.out` exception after clean completed), `bobp make install` (`uv sync --locked`), `bobp make test` (`368 passed, 2 skipped, 397 subtests`), `bobp make lint` (all Mermaid blocks PASS), `bobp make security-scan` (`gitleaks` 0 leaks, `pip-audit` clean, `npm audit` clean with 3 accepted SEC-001 advisories), and `bobp make build` (`bobp-0.3.1` wheel/sdist).

## Next Steps
1. Oracle reviews `docs/SDLC.md` (`SDLC` rubric) and completes Task C.2 grooming; Smith executes Task C.3 E2E UAT; team retro & Cypher Sprint 3 launch.
2. Do not commit, bump version, or release until directed by the owner (SDLC §6/§7).
