# Agent State

## Context
### Recent Decisions
**2026-08-07 — Eliminate `bobp/tools/_bob_manage.py`** (user-directed, `*arch refactor`)
Move each public function into its own command module; redistribute private
helpers by fan-in. No back-compat shim needed (user confirmed) — delete
`_bob_manage.py` outright, don't leave a re-export stub.

**Function → destination module:**
| Function | From | To |
|---|---|---|
| `install()` | `_bob_manage.py` | `bob_install.py` |
| `update()` | `_bob_manage.py` | `bob_update.py` |
| `pull()` | `_bob_manage.py` | `bob_pull.py` |
| `clean()` | `_bob_manage.py` | `bob_clean.py` |
| `diff()` | `_bob_manage.py` | `bob_diff.py` |

**Private helper → destination, by fan-in:**
- Used by 2+ command modules → `_common.py` (already holds the cross-cutting
  `find_project_root()`, so this is the established home for shared plumbing):
  - `templates_dir()` — used by install, update, diff
  - `_require_dir()` — used by install, update, pull, diff
  - `_run_setup_agent_links()` — used by install, update
  - `_regen_chat_diagram()` — used by update, clean
- Used by exactly one command module → inline into that module as a private helper:
  - `_restore_skill_extensions()` → `bob_install.py`
  - `_write_missing_state_files()`, `_ensure_chat_md()` → `bob_update.py`
  - `_merge_existing()` → `bob_pull.py`
  - `_diff_trees()` → `bob_diff.py`

Each `bob_*.py` keeps its existing thin argparse `main()`, but calls its own
local function instead of `_bob_manage.X(...)`; drop the `from . import
_bob_manage` import.

### Key Findings
- `_bob_manage` is referenced by: the 5 `bob_*.py` wrappers, `cli.py`'s module
  docstring (needs updating, not just deleting the reference), and
  `tests/test_bob_manage.py` (all of it — every test patches or calls into
  `_bob_manage`).
- `agents/neo.docs/state.md` mentions `_bob_manage.py` in a past-work log —
  that's history, not live documentation; leave it alone.

### Important Notes
None yet

## Current Task
**Status:** Handed off to Neo
**Assigned to:** Neo
**Started:** 2026-08-07

### Task Description
Execute the `_bob_manage.py` elimination per the decision above.

### Progress
- [x] Read `_bob_manage.py`, all 5 `bob_*.py` wrappers, `_common.py`, `cli.py`, `tests/test_bob_manage.py`
- [x] Decided function/helper destination mapping (table above)
- [ ] Move functions + helpers into destination modules (Neo)
- [ ] Delete `_bob_manage.py` (Neo)
- [ ] Update `cli.py` module docstring — no longer accurate once `_bob_manage.py` is gone (Neo)
- [ ] Split `tests/test_bob_manage.py` into one file per command module
      (`test_bob_install.py`, `test_bob_update.py`, `test_bob_pull.py`,
      `test_bob_clean.py`, `test_bob_diff.py`), importing from the new
      module and patching helpers on that module (e.g. patch
      `bob_install._run_setup_agent_links`, not `_common._run_setup_agent_links`,
      since `from ._common import ...` binds a local name in bob_install's
      namespace) (Neo)
- [ ] `make test` green (Neo)

### Blockers
None

### Oracle Consultations
None yet

## Next Steps
### Immediate Next Action
Neo: implement per the plan above, run `make test`, report back to Morpheus for architecture review before handoff to Trin.

### Waiting On
Neo's implementation

### Planned Work
- [ ] Morpheus reviews Neo's diff for boundary correctness (no leftover cross-imports, no helper landed in the wrong module)

---
*Last updated: 2026-08-07*
