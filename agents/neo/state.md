# Agent State

## Context
- User approved local Promptfoo evaluation using Codex/ChatGPT subscription auth. No GitHub Actions or commit hooks; direct pushes remain.
- Bob owns persona skills; Trin owns evaluation/sign-off; Tank owns tooling and `docs/SDLC.md`.
- Evaluator assets were moved into `bobp/tools/persona_eval_assets/`; `bobp/tools/persona_eval.py` loads the catalog/manifests with `importlib.resources`.
- `bobp persona-eval --setup` explicitly installs locked Node dependencies under the target project's `build/persona-eval/toolchain`; evaluator scratch/reports remain under `build/`.
- Verification: built wheel includes module/catalog/npm manifests; clean Python 3.15 venv installed wheel and successfully ran `bobp persona-eval --list`; full tests passed (95 passed, 2 skipped, 9 subtests). No additional live model evaluation was run.
- Worktree still has uncommitted changes: `.gitignore`, `Makefile`, `docs/SDLC.md`, `pyproject.toml`, `bobp/tools/persona_eval.py`, `tests/test_persona_eval.py`; moved package assets under `bobp/tools/persona_eval_assets/`; removed old `tools/persona-eval/` assets; updated `agents/neo/state.md`, `agents/CHAT.md`, and generated `agents/CHAT.diagram.md`.

## Current Task
**Status:** Packaging implementation complete; Node.js/npm prerequisite handling now prints global setup instructions without installing into target projects. Tank review remains pending.
**Assigned to:** Neo
**Progress:** Packaged evaluator assets and wired the installed Bobp command to setup/use them from arbitrary target projects. `bobp persona-eval --setup` now prints the pinned global npm install command and does not install packages or write into the target project; evaluation checks Node.js >=22.22.0, npm, exact global npm package versions, and PATH, with actionable errors. Updated `docs/SDLC.md` and the `install-evals` help description. Focused tests: 4 passed. Prior package verification: wheel install, installed CLI list, and full suite passed. Tank has not replied to the existing review handoff. Changes are not committed.

## Next Steps
1. Await Tank's review of the SDLC setup/package-path changes and prerequisite documentation.
2. If Tank requests SDLC corrections, update `docs/SDLC.md` with Tank's ownership in mind and rerun only affected verification; otherwise record the review result.
3. Preserve all existing uncommitted changes. Do not commit/push unless the user asks.
4. Do not run another live Promptfoo eval without user guidance; prior live evals were gated by anti-loop guidance.
