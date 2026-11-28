# Persona Evaluation

Bob Protocol includes per-skill evaluations (`evals/evals.json`) for checking whether installed personas use their skills and produce work that meets a rubric. The runner uses Promptfoo to execute each scenario with the local Codex login, then uses TypeSafe Jev to grade the result.

Use these evaluations after changing a persona, its skill, or a shared template that affects persona behavior. They are repeatable local checks, not a guarantee that a persona will behave identically on every task.

## Requirements

- Python environment with `bobp` installed (the `typesafe-sdk` Python dependency is installed with Bobp).
- Node.js `>=22.22.0` and npm on `PATH`.
- Globally installed versions of Promptfoo and the Codex SDK required by Bobp.
- `TYPESAFE_API_KEY` set in the environment.
- A working local Codex login for the Codex SDK provider.

Run setup to check the Node/npm prerequisites and print the pinned global npm install command:

```bash
uv run bobp persona-eval --setup
```

Follow the printed npm command, then make sure npm's global executable directory is on `PATH`. Setup checks Node.js/npm; an evaluation also checks the pinned npm package versions and `TYPESAFE_API_KEY`, with actionable errors when these requirements are missing or outdated. Setup only displays instructions; it does not install npm packages or write into your project. The Codex SDK uses the existing local login, so verify that login separately if the provider cannot start.

## Find and run evaluations

List the 11 suites discovered from packaged per-skill `evals/evals.json` files (also installed into `.agents/skills/<name>/evals/evals.json`):

```bash
uv run bobp persona-eval --list
uv run bobp persona-eval --list --json
```

Run one suite by its ID or run every suite for a persona:

```bash
uv run bobp persona-eval bob-persona-authoring
uv run bobp persona-eval bob
```

Each selected suite runs once in a fresh disposable project by default (`with_skill/`). Pass `--baseline without-skill` (or `--baseline previous` against the saved `skill-snapshot/`) to record a comparison baseline alongside `with_skill/` (opt-in because it doubles external Codex and TypeSafe calls; a baseline result never fails the suite). Repeat with fresh fixtures when checking a change with more than one run:

```bash
uv run bobp persona-eval --repeat 3 bob-persona-authoring
uv run bobp persona-eval --baseline without-skill bob-persona-authoring
```

Run all suites with `uv run bobp persona-eval --all`. This can take longer and makes separate model and grading API calls for every scenario. The suites currently cover Bob authoring, Morpheus design advice, and focused personality behavior suites for the team; `--list` is the current source of truth.

## What a run checks

Every scenario creates a disposable fixture under `build/persona-eval/runtime/`, installs the current Bobp framework into it, and runs the requested task with the installed persona. The evaluator checks that the Codex trace used or read that installed persona skill. Artifact suites also check that the expected file was created. The artifact is then evaluated against its shared rubric; personality behavior suites check required persona sections and role-specific behavior.

For each applicable rubric criterion, Jev returns both:

- A `Choice` classification: `meets`, `partially_meets`, or `does_not_meet`.
- An ordered three-level `Score`: does not meet = 0, partially meets = 1, meets = 2. The report includes the numeric score and probability distribution; its weighted expected score is descriptive and does not determine the pass by itself.

A criterion passes only when the Choice classification is `meets` and the Score's most likely level is also `meets`. If those judgments disagree, the criterion fails and the report flags it for manual review. Deterministic checks also validate countable structure, such as required personality sections and the number of sayings. Criteria that do not apply to a scenario are recorded as N/A.

The CLI reports `PASS` only when all selected Promptfoo assertions pass. One failing assertion or missing expected artifact makes that run fail. Since model output and Jev judgments are probabilistic, review the evidence and repeat a run when the change warrants it; do not keep rerunning until a pass appears.

## Reports and failure review

Each run writes:

- An evaluating-skills workspace under `build/persona-eval/<skill>-workspace/iteration-N/eval-<short-name>/{with_skill,without_skill|old_skill}/{outputs/,timing.json,grading.json}`, plus a per-iteration `benchmark.json` (`run_summary` and `delta`). Earlier iterations are never overwritten, and reviewer notes in `<skill>-workspace/feedback.json` are preserved across runs.
- A JSON report at `build/persona-eval/<suite>-<timestamp>-run<N>.json` (naming the iteration and baseline).
- Its disposable fixture project under `build/persona-eval/runtime/<suite>-<timestamp>-run<N>/project/`.

Start with `grading.json` (`{text, passed, evidence}` entries, `declared_assertions`, and `summary`) and the failed test's `gradingResult.reason` in the JSON report. For Jev rubric rows, inspect the criterion's `classification`, `scoreLevel`, confidence values, probability distributions, and `reviewRequired` flag. Then compare the candidate response or artifact with that row's evidence requirements and the fixture's installed persona skill. A low confidence result or Choice/Score disagreement calls for human review; the evaluator does not provide a separate free-form explanation.

The fixture keeps the generated Promptfoo config and files used for review alongside the scenario. Reports, workspaces, and fixtures are kept under `build/`; remove them when they are no longer useful. Record the suite, pass/fail result, iteration, and report path when using an evaluation as a change gate.

## Data sent for grading

Promptfoo runs the scenario through the Codex SDK using the user's existing local Codex login. The evaluator does not copy Codex credentials or environment variables into the fixture. The TypeSafe Jev request includes the scenario, complete rubric, persona skill instructions, candidate response, candidate artifact when applicable, expected artifact path, and a concise inventory of the fixture's declared capabilities and relevant paths. It omits chat logs, persona state files, and unrelated transcripts, but candidate content can itself contain sensitive information. Scenario content and candidate work are sent to TypeSafe for grading; do not run an evaluation on material that should not be sent to that service.

For evaluation design and troubleshooting workflow, see the [Judge skill](../.agents/skills/judge/SKILL.md). The implementation and project quality gate are documented in `docs/SDLC.md` in the Bob Protocol source checkout.
