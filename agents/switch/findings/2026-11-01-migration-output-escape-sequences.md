# SEC-007: Migration and skip messages echo project file names unfiltered (`bobp/tools/_skill_layout.py` `describe`, `summarize`)

- **Severity:** Low — a cloned repository can name a directory with terminal escape sequences; `bobp update` would print it raw, which can rewrite what the user sees (for example hide or fake a line). No file is changed and nothing runs.
- **Status:** Fixed
- **Verdict:** No blocking findings (Low; fixed anyway because it repeats Sprint 2's lesson and costs one function)
- **Date / author:** 2026-11-01 / Switch
- **Affected:** `describe()` and `summarize()` in `bobp/tools/_skill_layout.py` (Sprint 3, Phase 2)
- **Class / reference:** CWE-150 improper neutralization of escape sequences; same class as the Sprint 2 version-notice sanitizing

## Next Action

| Who | Does what | By / trigger |
|---|---|---|
| Neo | Pass every echoed path and note through `printable()` (drops control and format characters, caps length) | Done with this finding |
| Switch | Include "names echoed to the terminal are filtered" in the checklist for later phases | Phases 3 to 7 |

## Evidence

- **Reproduce / detect:** create `agents/skills/<name containing ESC and BEL>/SKILL.md` in a scratch project and run `migrate_legacy` then `describe`.
- **Observed:** before the fix the output line contained `\x1b[31m` and `\x07`; after the fix it contained neither (`tests/test_legacy_migration.py::test_control_characters_in_project_names_never_reach_the_terminal`).
- **Confidence:** High.

## Impact and Reachability

Reachable by running `bobp update` in a hostile repository. Terminal display only. Scope is runtime.

## Recommendation

- **Fix:** `printable()` in `_skill_layout.py`, applied in `describe` and `summarize`.
- **Verify:** the test above and `bobp make test`.
- **Alternatives rejected:** rejecting such names outright (they are still skipped by the name rule; the message just has to be safe).

## Risk Acceptance

Not accepted.
