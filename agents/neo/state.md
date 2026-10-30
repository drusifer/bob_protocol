# Agent State

## Context
- User approved a local Promptfoo tool using Codex/ChatGPT subscription auth. No GitHub Actions or hooks; direct pushes remain.
- Bob owns persona skills; Trin owns evaluation/sign-off; Tank owns tooling and `docs/SDLC.md`.
- Use the newest Python available through uv (currently 3.15.0; `.python-version` is `3.15`). Do not build Python from source. Prefer current compatible dependencies.
- The eval catalog is stable and versioned. Suites create isolated target projects under `build/persona-eval/runtime/`, run local `bobp install`, then check installed skill use and score the produced artifact with its shared artifact rubric.
- Keep pytest and subprocess temporary files under `build/`; do not write to `/tmp`.
- Trin reviewed the first Bob eval. Skill-use passed; rubric grading was inconclusive because the grader ignored fixture `agents/PROJECT.md` (`via: disabled`) and over-interpreted inherited state requirements. Historical chat records multiple live attempts; do not run another live eval without user guidance.

## Current Task
**Status:** Implementation and live validation complete; handed to Trin for QA sign-off.
**Assigned to:** Neo
**Progress:** `build_config` now includes the fixture capability declaration and scopes Via/state criteria to the installed target. Focused offline tests pass (6 passed, 87 deselected). One user-authorized live eval passed both installed-skill-use and artifact-rubric assertions. Runtime and report are retained under `build/persona-eval/`.

## Next Steps
1. Trin reviews `build/persona-eval/bob-persona-authoring-20261030T131555Z-run1.json` and its retained project at `build/persona-eval/runtime/bob-persona-authoring-20261030T131555Z-run1/project`; verify the rubric against the produced `agents/commit-message-author/SKILL.md`.
2. If Trin signs off, Morpheus reviews the evaluator design, then Tank documents Python/tooling and catalog-based evaluation policy in `docs/SDLC.md`.
3. Keep additional live runs gated by the anti-loop rule and user guidance.
