# Agent State

## Context
- User approved a local Promptfoo persona gate using the Codex subscription; no new Actions or commit hooks. Direct pushes remain allowed.
- Ownership: Bob authors personas; Trin owns evaluation/sign-off; Morpheus reviews architecture; Tank owns tools and `docs/SDLC.md`.
- Development uses uv and Python 3.15 (latest patch available through uv); `pyproject.toml` retains `>=3.10,<4`, and Python requirements/lock resolve to current compatible versions.
- `bobp persona-eval` runs versioned catalog suites in isolated projects installed by the current checkout's `bobp install`. Current suites cover Bob persona authoring and Morpheus design advice, judged by their shared artifact rubrics. Reports and pytest/subprocess scratch remain in `build/`.
- Existing CI uses pip/Python 3.10–3.12 and does not run Promptfoo. PyPI trusted publishing is now configured (pending publisher bobp -> drusifer/bob_protocol, release.yml, env `pypi`, reviewer approval required). Mermaid package has no lockfile; Node 24.13 lint passes with an engine warning. These are documented deviations.
- `docs/SDLC.md` is drafted; README development commands now use uv. Full suite: 88 passed, 7 skipped, 9 subtests; Mermaid lint passed. A clean `distclean` rebuild remains for sprint close to avoid deleting retained eval reports from `build/`.

## Current Task
**Release 2026-10-31:** bobp 0.1.0 published to PyPI (tag v0.1.0 at d17cc1a, license -> SPDX GPL-3.0-only, `make release` target added in dcc0aad). Verified fresh-venv install and `bobp --help`. Forgejo registry remains a separate private target. `gh` token initially lacked release permission (403); fixed by user.

**Status:** Completed; SDLC reviewed and approved.
**Assigned to:** Tank
**Progress:** Checked every Make target, CI/release workflow, dependency layout, quality gate, branch/push convention, local eval behavior, and known gap. Oracle's SDLC review passed all six criteria. Full suite and lint pass. `git diff --check` clean.

## Next Steps
0. Next release: bump `__version__`, push to main, run `bobp make release`, approve the `pypi` environment, verify install.
1. Report completion with test/lint results, live suite report paths, and the clean-rebuild caveat.
2. Do not commit or push unless the user asks.
