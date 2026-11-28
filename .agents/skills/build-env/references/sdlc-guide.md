# `docs/SDLC.md` Authoring & Conformance Guide

`docs/SDLC.md` is the project's source of truth for change management, owned by Tank. Other personas read it instead of guessing; where generic workflow skills disagree with `docs/SDLC.md`, the SDLC wins and whoever notices reports it to Tank (`@Tank *devops sdlc <what and why>`).

## Required Sections

Describe what is true in this repo today — runnable commands, not aspirations. Keep it to one or two pages, writing "None" (with a reason) where a section does not apply:

| Section | Answers |
|---|---|
| **Toolchain** | Languages and pinned runtime versions; manifest and lockfile per language; package manager; where the local environment lives. |
| **Setup** | Exact commands from clean checkout to passing tests. |
| **Make targets** | Every standard target the project defines, what it runs, and which standard targets are deliberately absent and why. |
| **Dependencies** | How to add, upgrade and remove one; who may; what must be committed afterwards. |
| **Quality gates** | What must pass before work is handed off and before a sprint closes (tests, lint, type checks, secret scan), as `make` targets. |
| **Change management** | Change classes (routine, mechanism, release, emergency) with proposer, approver, gates and record; request → branch → implement → gate → review → integrate → record flow; commit/push rules; rollback. |
| **Versioning and release** | Where the version lives, when it is bumped, how an artifact is built or published. |
| **CI / deploy** | What runs automatically and where it is configured — or that there is none. |
| **Known deviations** | Anything departing from conventions and why. |
| **Conformance check** | Project-specific list Tank runs at sprint close. |

End the file with a `Last verified` line: date, and the commit or sprint it was checked against.

## Templates & Review Rubric

Start from the templates in `agents/templates/`:

| Template | Use for |
|---|---|
| `agents/templates/_template_SDLC.python.md` | Python: `pyproject.toml` + uv + `.venv` |
| `agents/templates/_template_SDLC.javascript.md` | JavaScript / TypeScript: `package.json` + lockfile |
| `agents/templates/_template_SDLC.md` | Any other language, or multi-language repo |
| `agents/templates/_template_MISE.md` / `_template_TASKFILE.md` / `_template_MAKEFILE.md` | `mise.toml`, `Taskfile.yml`, thin `Makefile` shim (each with its own rubric) |

Copy the matching template to `docs/SDLC.md`, replace every `{placeholder}`, and delete the review rubric (`RUBRIC-START`..`RUBRIC-END`). Correct any pre-filled line that is not true for the repo. Self-check against the **SDLC rubric** (`TRUE`, `WHOLE`, `CLEAN`, `CLASS`, `CHECK`, `GAPS`) before posting; Oracle applies the same rubric at groom when `docs/SDLC.md` changes. See `agents/templates/ARTIFACTS.md`.

## `*devops sdlc` — Create or Update

- **No SDLC yet, environment exists:** survey it, verify from clean, document what you found. Fix small gaps first; list larger ones under Known deviations.
- **No SDLC and no environment:** run the bootstrap Procedure; the SDLC is step 7.
- **Mechanism change requested:** change manifest/Taskfile/Makefile, re-verify from clean, update affected sections and `Last verified` together.

## `*devops sdlc-check` — Sprint-Close Conformance Check

Run after the last phase is reviewed and before Oracle grooms docs:

1. **Rebuild from clean.** `bobp make distclean`, `bobp make install`, `bobp make test` (and each quality-gate target the SDLC lists).
2. **Manifest matches the code.** Every third-party import is declared; nothing installed by hand; no stray dependency file beside the manifest.
3. **Targets match the document.** Listed targets exist and match; new targets are documented or removed.
4. **No side doors.** No doc or script added this sprint bypasses `make` or installs outside the project.
5. **Pins and ignores hold.** Runtime pins, committed lockfiles, and `.gitignore` entries remain intact.
6. **Changes followed the process.** Approvals, gates, and records match the change class.
7. Everything under the SDLC's own Conformance check section.

Outcome posted to `agents/CHAT.md`:
- **Conforms** → update `Last verified` and hand off to Oracle.
- **Legitimate mechanism improvement** → Tank updates `docs/SDLC.md` to match, then hands off.
- **Regression** → `@Neo *swe fix <issue>`; sprint does not close until Tank re-checks.
