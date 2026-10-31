# SEC-001: promptfoo 0.125.1 pulls in 8 vulnerable transitive npm packages

- **Severity:** Low-to-Medium — dev/eval tooling only; the flaws need attacker-controlled FTP listings or glob patterns the eval flow never supplies (npm rates them 5 high, 3 moderate).
- **Status:** Open
- **Verdict:** No blocking findings (dev-only; blocks `security-scan-npm` until accepted or fixed upstream)
- **Date / author:** 2026-10-31 / Switch
- **Affected:** `bobp/tools/persona_eval_assets/package-lock.json` — `promptfoo@0.125.1` → `basic-ftp`, `get-uri`, `pac-proxy-agent`, `proxy-agent`, `glob`, `minimatch`, `@modelcontextprotocol/server-filesystem`
- **Class / reference:** GHSA-c475-qrg2-pj4r (basic-ftp ≤6.2.0, quadratic-time DoS), GHSA-3g3m-2fjr-6pw4 (glob AbortSignal bypass), GHSA-g3hv-75wg-m249 (minimatch DoS)

## Next Action

| Who | Does what | By / trigger |
|---|---|---|
| User | Decide: accept the risk (recommended) or ask for a different eval runner | Before the next release |
| Switch | Re-run `bobp make security-scan-npm` and upgrade promptfoo if the audit clears | When promptfoo publishes a release newer than 0.125.1 |
| Tank | Record the accepted risk and how `security-scan` treats it in `docs/SDLC.md` | After the user decides |

## Evidence

- **Reproduce / detect:** `bobp make security-scan-npm` → `npm audit --prefix bobp/tools/persona_eval_assets --audit-level=high`: "8 vulnerabilities (3 moderate, 5 high)", all transitive via `promptfoo`.
- **Observed:** `gitleaks` (77 commits) and `pip-audit` (87 pins) are clean. promptfoo 0.125.1 is the latest release; npm's suggested `--force` fix installs `promptfoo@0.5.1`.
- **Confidence:** High on the findings; Medium on the low reachability (based on how the eval flow uses promptfoo).

## Impact and Reachability

Scope is dev/tooling only: users install these packages globally to run `bobp persona-eval`, and none ship in the `bobp` wheel (runtime deps: Jinja2, typesafe-sdk). The realistic worst case is a denial of service or slow run on the user's own machine.

## Recommendation

- **Fix:** None available. Do not apply `npm audit fix --force`. `overrides` in the packaged `package.json` would not help, because users install globally with the command from `bobp persona-eval --setup`.
- **Verify:** `bobp make security-scan-npm` passes after upstream fixes, or the accepted risk is recorded and the gate is adjusted.
- **Alternatives rejected:** Downgrade to promptfoo 0.5.1 (ancient, unrelated major version); replace promptfoo (large change to the eval system for a dev-only risk).

## Risk Acceptance

Not accepted. Awaiting the user's decision.
