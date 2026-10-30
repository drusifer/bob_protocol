# Agent State

## Context
- Reviewed Trin's QA handoff and current `bobp/tools/persona_eval.py`, catalog, Makefile, Python/uv manifests, and live Promptfoo report.
- Architecture is fit for the approved local gate: explicit versioned suite selection, fresh target project per run under `build/persona-eval/runtime/`, current-checkout `bobp install`, isolated install paths, actual Codex project-skill discovery, offline Codex provider and read-only rubric grader, JSON report retained in `build/`.
- Promptfoo uses the host Codex login only for the evaluator process. Install/setup subprocesses isolate `HOME`, `CODEX_HOME`, `PATH`, and temp paths within the retained build directory.
- No Makefile assumption in target projects. The root repo's Makefile provides `install-evals` and `test-q`; the evaluator itself is a `bobp persona-eval` CLI command.
- Current CI already exists in `.github/workflows/ci.yml` and release workflow exists separately. CI tests Python 3.10–3.12 with pip and does not run subscription-backed Promptfoo; do not alter CI/actions or add hooks under the user's direction. Tank should document this deviation and the local Trin eval gate.
- Reviewed the new Morpheus `*advise` method after Trin's pass. It clearly separates open-ended `*guide`, option recommendation `*advise`, and binding `*decide`; domain modeling, BDD examples, KISS/DRY tradeoffs, and the consequential-question threshold fit Morpheus's role.

## Current Task
**Status:** Completed; evaluator and `*advise` design reviews passed.
**Assigned to:** Morpheus
**Progress:** Evaluator architecture and Morpheus advice-method review passed. Catalog and local credentials boundary are clear; build outputs and scratch remain in `build/`. SDLC must state that the Promptfoo gate is a local Trin sign-off, not CI automation, and expose current CI/Python and Node engine warnings as known deviations.

## Next Steps
1. Tank and Oracle completed the SDLC review; all six SDLC rubric checks passed.
2. Clean-rebuild conformance remains scheduled for sprint close; retained eval reports are under `build/`.
3. Await the next architecture request.
