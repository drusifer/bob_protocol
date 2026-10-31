# SEC-001: promptfoo 0.125.1 pulls in 8 vulnerable transitive npm packages

- **Severity:** Low-to-Medium — dev/eval tooling only; the flaws need attacker-controlled FTP listings or glob patterns the eval flow never supplies (npm rates them 5 high, 3 moderate).
- **Status:** Accepted risk
- **Verdict:** No blocking findings (risk accepted by the user 2026-10-31)
- **Date / author:** 2026-10-31 / Switch
- **Affected:** `bobp/tools/persona_eval_assets/package-lock.json` — `promptfoo@0.125.1` → `basic-ftp`, `get-uri`, `pac-proxy-agent`, `proxy-agent`, `glob`, `minimatch`, `@modelcontextprotocol/server-filesystem`
- **Class / reference:** GHSA-c475-qrg2-pj4r (basic-ftp ≤6.2.0, quadratic-time DoS), GHSA-3g3m-2fjr-6pw4 (glob AbortSignal bypass), GHSA-g3hv-75wg-m249 (minimatch DoS)

## Next Action

| Who | Does what | By / trigger |
|---|---|---|
| User | ~~Decide: accept the risk~~ Accepted 2026-10-31 | Done |
| Switch | Re-run `bobp make security-scan-npm` and upgrade promptfoo (or remove the acceptance) | When promptfoo publishes a release newer than 0.125.1 |
| Tank | Review `tools/audit_gate.py` and the SDLC note on accepted advisories | Next sprint |

## Evidence

- **Reproduce / detect:** `bobp make security-scan-npm` → `npm audit --prefix bobp/tools/persona_eval_assets --audit-level=high`: "8 vulnerabilities (3 moderate, 5 high)", all transitive via `promptfoo`.
- **Observed:** `gitleaks` (77 commits) and `pip-audit` (87 pins) are clean. promptfoo 0.125.1 is the latest release; npm's suggested `--force` fix installs `promptfoo@0.5.1`.
- **Confidence:** High on the findings; Medium on the low reachability (based on how the eval flow uses promptfoo).

## Impact and Reachability

Scope is dev/tooling only: users install these packages globally to run `bobp persona-eval`, and none ship in the `bobp` wheel (runtime deps: Jinja2, typesafe-sdk). The realistic worst case is a denial of service or slow run on the user's own machine.

## Exploitability (added 2026-10-31, from the advisories)

All three root advisories are availability-only (no code execution, no data exposure) and each needs attacker-controlled input that Bobp never supplies:
- **basic-ftp (GHSA-c475-qrg2-pj4r):** a malicious FTP *server* must answer a directory listing the client requests. Reached only through get-uri's ftp: handler (used when a proxy auto-config file is fetched over ftp). Persona evals use no FTP or PAC proxy. Not reachable in normal use (from library structure; promptfoo's code was not traced end to end).
- **glob (GHSA-3g3m-2fjr-6pw4):** an aborted walk keeps reading directories. Only wasted I/O after a timeout; patterns come from our own config.
- **minimatch (GHSA-g3hv-75wg-m249):** needs an attacker-supplied glob pattern; ours come from the repo's own eval config.

Practical worst case: a dev-time eval run on the user's own machine slows or hangs. Rated Low.

## Why it cannot simply be upgraded

promptfoo 0.125.1 is the latest release, but its dependency ranges exclude the patched majors (`glob ^13`, `minimatch ^10`; get-uri needs `basic-ftp ^5`). Patched versions exist: glob 14.0.3, minimatch 11.0.3, basic-ftp 6.2.4. Tested in a scratch install: npm `overrides` for those three give `npm audit` = 0 vulnerabilities and a basic `promptfoo eval` still passes. A full Bobp persona eval on that tree was not completed (test harness error, inconclusive). Overrides only apply to a project install, not to the `npm install --global` command Bobp prints, so shipping them needs a design change (Bobp-owned install prefix).

## Recommendation

- **Fix:** Accept the risk now (not exploitable here). Do not apply `npm audit fix --force` (installs promptfoo 0.5.1). Optional later: install the eval packages into a Bobp-owned prefix with `overrides`, which needs Tank/Morpheus design work and a full eval run on the patched tree.
- **Verify:** `bobp make security-scan-npm` passes after upstream fixes, or the accepted risk is recorded and the gate is adjusted.
- **Alternatives rejected:** Downgrade to promptfoo 0.5.1 (ancient, unrelated major version); replace promptfoo (large change to the eval system for a dev-only risk).

## Risk Acceptance

Accepted by the user on 2026-10-31, **expires 2027-01-29**, for GHSA-c475-qrg2-pj4r (basic-ftp), GHSA-3g3m-2fjr-6pw4 (glob), and GHSA-g3hv-75wg-m249 (minimatch). Scope: dev/eval tooling only. After the expiry date the gate blocks again until the user renews it or the risk is fixed. Re-check: when promptfoo publishes a release newer than 0.125.1, or when Bobp installs eval packages with overrides. Recorded in `agents/switch/accepted-risks.json`; the scan gate notes these and still blocks any new advisory.
