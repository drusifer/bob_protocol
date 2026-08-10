# SPRINT_1 UAT — Chat Archive & Report

Verified against `agents/cypher.docs/sprint_SPRINT_1_stories.md`.

- **S1** (archive): unit tests + a live CLI smoke test (isolated temp dir, not the
  real `agents/CHAT.md`) confirm archive + reset + pointer header work end to end.
  Overwrite guard names both `--force` and the exact conflicting path.
- **S2** (combine): idempotent (re-run produces identical output), natural moniker
  ordering (`SPRINT_2` sorts before `SPRINT_10`), each section's summary comes from
  the archive's own heading — not re-supplied.
- **S3** (word-wrap): long messages wrap with `<br/>` at 40 chars/line; the 300-char
  safety cap still truncates pathological messages; short messages unaffected.
- **S4** (chat-merge): all 4 conflict-marker variants (`<<<<<<<`, `|||||||`, `=======`,
  `>>>>>>>`) stripped, both sides' content preserved, exact-duplicate blocks dropped,
  clean-input behavior unchanged.
- CLI error paths checked live: missing `--moniker`, `--combine`+`--moniker` conflict,
  empty-string moniker — all clear messages, exit code 1.
- `bobp make test`: 43/43 passing.

**Result: PASS.**
