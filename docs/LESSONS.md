# Engineering Lessons

## [2026-11-01] Open repo-supplied files without following links or blocking

> **Tags:** #Security #CLI #Switch #Neo

### Context
Sprint 2 added a per-project version stamp, `agents/.bobp-version`, that every `bobp` subcommand reads before it runs. The design promised the check would never read stdin or block. All feature tests and the first UAT passed.

### Observation and Cause
Switch's phase security review found that a repository can ship the stamp as a symlink to `/dev/stdin`, or as a FIFO, and a plain `open().read()` then hangs every bobp command in that repo (reproduced: exit 124). Git stores symlinks, so a clone is enough. The happy-path tests could not see this because they only wrote regular files. Confirmed cause: the read trusted that the path was a regular file.

### Rule
When bobp reads a file whose location is fixed inside a project (stamps, config, markers), treat it as untrusted input: open it with `O_NOFOLLOW | O_NONBLOCK`, require a regular file with `fstat`, cap the bytes read, and treat anything else as "absent". Add a test for a symlink and a FIFO, guarded by an alarm so a regression fails instead of hanging the suite.

### Evidence and Scope
- **References:** `agents/switch/findings/2026-11-01-version-stamp-symlink-hang.md` (SEC-005), `bobp/tools/_version_check.py` `_read_stamp`, `tests/test_version_check.py`
- **Applies when:** any bobp code reads a file from a project directory that may have been cloned from elsewhere before the user has reviewed it.
