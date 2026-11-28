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

## [2026-11-28] Avoid unanchored and adjacent quantifiers in regexes on untrusted files

> **Tags:** #Security #Regex #Switch #Neo

### Context
Sprint 4 replaced `bobp chat-merge` with `bobp merge` to parse and resolve conflicts across timestamped Markdown logs (`CHAT.md`, `LESSONS.md`, `DECISIONS.md`) inside potentially untrusted Git repositories. All functional tests and the 10 MiB bounded-read guard passed.

### Observation and Cause
Switch's Phase 1 security review measured two quadratic ReDoS bugs in `bobp/tools/merge.py` well within the 10 MiB cap: (1) `META_DATE_RE` (`:[ \t]*(?:\*\*)?[ \t]*`, SEC-008) collapsed into adjacent `[ \t]*[ \t]*` whenever `**` was absent (4.94s on 20k spaces); (2) `parse_blocks`'s unanchored `re.split(r"\n+(?:---\n+)?(?=...")` (SEC-009) retried `\n+` at every offset inside a blank-line run (9.61s on 20k newlines). Confirmed cause: Python's backtracking `re` engine exhibits $O(N^2)$ behavior whenever an optional group separates two identical character-class quantifiers or an unanchored `re.split` begins with a variable-length quantifier (`\n+`).

### Rule
When writing regexes that scan untrusted repository files (even with a size cap): fold trailing whitespace inside optional wrappers (`(?:\*\*[ \t]*)?` instead of `(?:\*\*)?[ \t]*`), anchor run-starting quantifiers with a negative lookbehind (`(?<!\n)\n+`), use `[ \t]` instead of `\s` on single-line patterns, and add an alarm-guarded regression test on a 50k-character mismatch input (such as `"a" + "\n" * 50_000 + "x"`).

### Evidence and Scope
- **References:** `bobp/tools/merge.py` (`META_DATE_RE`, `parse_blocks`), `tests/test_merge.py` (`test_meta_date_regex_is_linear_time_no_redos`)
- **Applies when:** adding or modifying any regex in `bobp` that runs over repository-supplied text or runs inside a Git hook/merge driver.
