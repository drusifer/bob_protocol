---
name: make
description: Invoke project Makefile targets. All targets route through mkf (build output filter) automatically — output is captured to build/build.out and status is posted to CHAT.md.
triggers: ["*make"]
---

# Make Skill

## Overview

All project automation runs through `make`. Every target (except `help` and `chat`) is
automatically routed through **mkf** (`agents/tools/mkf.py`) — the build output filter. You do not
need to call mkf directly; just run `make <target>`.

## CRITICAL — Do not capture make output into context

**Never** run make with output redirected into the conversation context:

```bash
# WRONG — floods context window, defeats mkf entirely
Bash(make update_bob 2>&1)
Bash(make update_bob V=-vvv 2>&1)

# CORRECT — mkf handles output; only the tail + exit code appear
Bash(make update_bob)
Bash(make update_bob V=-vv)
```

mkf exists specifically to keep build output out of the context window. Piping or capturing the full output (via `2>&1` or shell redirection into a variable) defeats this and bloats the context. Always let mkf manage the output — check `build/build.out` directly if you need details after a run.

---

## What mkf does

- Captures all build output to `build/build.out`
- Prints the last 10 lines of output on exit
- Posts build status + tail to `agents/CHAT.md` as persona `make`
- Returns the make exit code — callers can rely on it for pass/fail

## Verbosity

Control how much output appears in your terminal during the run using `V=`:

| Flag | Terminal output |
|------|----------------|
| *(none — default)* | Silent. Exit code only. Full log in `build/build.out`. |
| `V=-v`   | stderr only |
| `V=-vv`  | stderr + filtered stdout (failures, errors) |
| `V=-vvv` | stderr + full stdout (everything) |

```bash
make pull_bob                  # silent — exit code + tail on finish
make pull_bob V=-v             # show stderr live
make pull_bob V=-vvv           # show everything live
```

## Targets

### General
| Command | Description |
|---------|-------------|
| `make help` | Show available make targets (bypasses mkf) |
| `make chat` | Post a message to CHAT.md (bypasses mkf) |
| `make tldr` | Show TL;DR summaries from all project files |

### Installation & Maintenance
| Command | Description |
|---------|-------------|
| `make install_bob` | Copy agents into a project and set up skill links (`make install_bob TARGET=/path`) |
| `make update_bob` | Update agents and skills in a project, preserving state (`make update_bob TARGET=/path`) |
| `make pull_bob` | Pull updates from another project using BobProtocol (`make pull_bob SRC=/path`) |
| `make clean_bob` | Remove generated symlinks and reset agent memory/state files |

## Output file

Full build log is always at `build/build.out`. Inspect it after any run:

```bash
cat build/build.out        # full log
tail -20 build/build.out   # last 20 lines
```

## Fallback

If a target does not exist, add it to the Makefile — do not invoke tools directly.
Place real recipes inside the `ifdef MKF_ACTIVE` block so they are captured by mkf.
Targets that must run interactively or bypass mkf (like `help` or `chat`) should be defined
in the `else` block alongside `help` and `chat`.
