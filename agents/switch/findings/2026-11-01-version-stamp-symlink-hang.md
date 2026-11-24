# SEC-005: Version stamp read follows symlinks and opens FIFOs, so a cloned repo can hang every bobp command (`bobp/tools/_version_check.py`, `_read_stamp`)

- **Severity:** Medium — a repository the user clones can make every `bobp` command in it block forever (availability only; no data is disclosed or changed), and it breaks the sprint's own guarantee that the check never reads stdin or blocks.
- **Status:** Fixed
- **Verdict:** Blocked (until fixed; fails STORY-BOBP-4 AC3 and AC4)
- **Date / author:** 2026-11-01 / Switch
- **Affected:** `bobp/tools/_version_check.py` `_read_stamp()` (Sprint 2, Phase 2)
- **Class / reference:** CWE-400 resource exhaustion / CWE-59 link following; untrusted-file read from a repository

## Next Action

| Who | Does what | By / trigger |
|---|---|---|
| Neo | Add failing tests (symlink and FIFO stamp), then open the stamp with `O_NOFOLLOW \| O_NONBLOCK`, require a regular file via `fstat`, and treat anything else as "no version recorded" | Before Phase 2 review |
| Trin | Re-run the symlink and FIFO reproductions on the real CLI; both must exit promptly | After Neo's fix |
| Switch | Re-review the Phase 2 diff and post the phase 2 verdict | After Trin's UAT |

## Evidence

- **Reproduce / detect:** in a scratch project run `ln -s /dev/stdin agents/.bobp-version` (or `mkfifo agents/.bobp-version`), then `sleep 6 | timeout 4 bobp chat-merge --help`. Safe: it only shows that the command blocks.
- **Observed:** both cases exited 124 (timeout), i.e. the command hung before running the subcommand. Git can store the symlink, so a repository can ship it. The FIFO case needs the file to be created locally.
- **Confidence:** High; reproduced on the real CLI before the fix.

## Impact and Reachability

Reachable by anyone who runs any bobp subcommand inside a repository containing the symlink. Effect is a hang of the tool (and of any agent calling `bobp chat`/`bobp make`), not code execution or disclosure. Scope is runtime, on the user's machine. The stamp is read by every bobp command, so reach is wide.

## Recommendation

- **Fix:** open with `os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))`, then `os.fstat` and require `stat.S_ISREG`; read at most 256 bytes; on any `OSError` or non-regular file return "unrecorded".
- **Verify:** new unit tests for symlink and FIFO stamps (with a hard alarm so a regression fails instead of hanging), plus the two reproductions above on the real CLI; `bobp make test`.
- **Alternatives rejected:** a read timeout in a thread (leaves a stuck thread and still follows the symlink); `Path.is_file()` check before open (racy, and a FIFO or symlink-to-FIFO can slip between check and open).

## Risk Acceptance

Not accepted.
