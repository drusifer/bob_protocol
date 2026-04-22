TL;DR: On startup, read CHAT.md for context, load your persona's state files, then wait for user direction. If resuming mid-task, check next_steps.md and continue from there.

# BobProtocol: LLM Startup Instructions

## On Startup (Fresh Session)

1. Read `agents/CHAT.md` — last 10-20 messages for current team context
2. If `agents/PROJECT.md` exists — read it for project capabilities (e.g. `via: enabled`)
3. Display the quick reference below
4. Wait for user input — do not auto-execute tasks

## Cold Start Recovery (After Context Clear or Session Restart)

If you were mid-task when context was lost:

1. Read the bottom of `agents/CHAT.md` — find the last handoff message
2. Identify which persona was active and what command was pending
3. Load that persona's state files:
   - `agents/[persona].docs/context.md`
   - `agents/[persona].docs/current_task.md`
   - `agents/[persona].docs/next_steps.md`
4. Post a resume message:
   ```bash
   make chat MSG="Resuming <task> from last session." PERSONA="<Name>" CMD="resume"
   ```
5. Continue from `next_steps.md` — do not restart from scratch

If `CHAT.md` has no clear handoff, ask the user: *"I'm resuming — what should I pick up?"*

---

## Quick Reference

### Bloop Commands (full workflow chains)
```
*fix <bug>           → Neo fix → Trin UAT → Morpheus review
*impl <feature>      → Neo impl → Trin UAT → Morpheus review
*qa <thing>          → Trin test → Morpheus review
*review <thing>      → Morpheus review → Trin (if needed)
*plan sprint         → Cypher → Smith gate → Morpheus → Smith gate → Mouse
```

### `*chat` Routing
```
*chat <message>                      # auto-select persona
*chat @<Persona> *<command> <args>   # direct invocation
@<Persona> <message>                 # Gemini-style direct invocation
```

**Note on Direct Invocations**: If you are invoked directly via a harness-specific command (e.g., `@persona` or `/persona` in Gemini CLI, `/persona` in Claude, `$persona` in Codex), you MUST log the invocation to `agents/CHAT.md` immediately upon entry if it has not already been logged.

### Direct Skill Triggers
```
*swe impl / *swe fix / *swe test     # Neo
*qa test / *qa verify / *qa review   # Trin
*lead arch / *lead decide            # Morpheus
*ora ask / *ora record / *ora groom  # Oracle
*sm status / *sm plan / *sm blocked  # Mouse
*pm story / *pm doc / *pm assess     # Cypher
*user review / *user test / *user approve  # Smith
*prompt / *reprompt / *learn         # Bob
```

### Make Targets
```bash
make help                          # list all targets
make tldr                          # TL;DR from all project files
make chat MSG="..." PERSONA="..."  # post to CHAT.md
make test V=-vvv                   # run tests (full output)
```

See **[SHORTHAND_GUIDE.md](SHORTHAND_GUIDE.md)** for the full command reference.
