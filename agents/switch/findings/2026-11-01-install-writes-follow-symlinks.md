# SEC-006: Version stamp and skill manifest are written through symlinks, so a cloned repo can make `bobp install`/`update` overwrite any file the user can write (`bobp/tools/_bob_manage.py` `write_stamp`, `bobp/tools/_skill_layout.py` `write_manifest`)

- **Severity:** Medium — a repository the user clones can plant `agents/.bobp-version` (or the manifest's temp file) as a symlink to a victim file, and the next `bobp update` overwrites that file with bobp-chosen text. The text is short and fixed in form (a version string, or skill names), so it cannot plant a working script, but it can destroy a user file such as a shell profile.
- **Status:** Fixed
- **Verdict:** Blocked (until fixed)
- **Date / author:** 2026-11-01 / Switch
- **Affected:** `write_stamp()` in `bobp/tools/_bob_manage.py` (introduced in Sprint 2); `write_manifest()` in `bobp/tools/_skill_layout.py` (Sprint 3, Phase 1)
- **Class / reference:** CWE-59 link following / CWE-73 external control of file name; untrusted project file written by a trusted tool

## Next Action

| Who | Does what | By / trigger |
|---|---|---|
| Neo | Add failing tests for a symlinked stamp and a symlinked manifest temp file, then write both through one helper that writes a random temp file in the same directory (`O_EXCL`) and `os.replace`s it over the target (rename replaces a symlink itself, never its target) | Before Phase 1 review |
| Trin | Re-run both reproductions on the real CLI; the victim files must be unchanged | After the fix |
| Switch | Re-review; carry the remaining write paths (below) into the Phase 2 checklist | After Trin's re-run |

## Evidence

- **Reproduce / detect:** in a scratch project, `ln -s <victim> agents/.bobp-version` (and, separately, `ln -s <victim> agents/..bobp-skills.tmp`), then run `bobp update <project>` with scratch `HOME` and `CODEX_HOME`. Safe: the victims are scratch files.
- **Observed:** the stamp victim changed from `original` to `0.2.0`; the manifest victim changed from `original` to the list of skill names (`bloop bob bob-protocol …`). No error was shown.
- **Confidence:** High; reproduced on the real CLI before the fix.

## Impact and Reachability

Reachable by anyone who runs `bobp install --force` or `bobp update` inside a repository that ships such a symlink. Effect is destruction of one user-writable file per symlink, not code execution or disclosure. Scope is runtime, on the user's machine. The stamp write exists since Sprint 2, so released-in-working-tree code (0.2.0, not yet published) is affected; no published version contains it.

## Recommendation

- **Fix:** one helper `write_text_safely(path, text)` in `bobp/tools/_common.py`: `tempfile.mkstemp(dir=path.parent)` then write, close, `os.replace(tmp, path)`; use it for the stamp and the manifest.
- **Verify:** new unit tests for both symlink cases (victim unchanged, target is now a regular file), the two reproductions above, `bobp make test`.
- **Alternatives rejected:** checking `is_symlink()` before `write_text` (racy and easy to forget); opening with `O_NOFOLLOW` only (the temp-file-and-rename form also gives atomic updates).
- **Remaining, same class:** other install/update writes into project files (`state.md`, `CHAT.md`, copied templates via `shutil.copy2`) also follow a planted destination symlink. They are existing behavior and wider than this phase; they go on the Phase 2 review checklist and the backlog.

## Risk Acceptance

Not accepted.
