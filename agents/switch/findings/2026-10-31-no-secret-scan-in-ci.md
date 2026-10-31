# SEC-004: Secret scanning runs only in a local, bypassable hook

- **Severity:** Low — gitleaks protects only clones that ran `install-hooks`, and `git commit --no-verify` skips it; history is currently clean (84 commits).
- **Status:** Fixed (verification pending next CI run)
- **Verdict:** No blocking findings
- **Date / author:** 2026-10-31 / Switch
- **Affected:** `.github/workflows/ci.yml`; `.githooks/pre-commit`
- **Class / reference:** Defense in depth for secret leakage (CWE-798 class)

## Next Action

| Who | Does what | By / trigger |
|---|---|---|
| Tank | Add a CI job that runs `gitleaks` (git-aware, full history) on push and pull request, and record it in `docs/SDLC.md`; user to confirm CI changes are wanted, since the SDLC currently says no new workflows for the persona-eval gate | Next sprint |
| User | Decide whether CI secret scanning is in scope | Before Tank starts |

## Evidence

- **Reproduce / detect:** `.github/workflows/ci.yml` runs pytest and `bobp --help` only. `bobp make security-scan-secrets` is clean locally (84 commits, no leaks).
- **Observed:** The hook works (blocked a staged fake key, exit 1) and handles a missing `gitleaks`, but a contributor without hooks enabled is unprotected.
- **Confidence:** High.

## Impact and Reachability

A secret committed from a clone without the hook, or with `--no-verify`, would reach `main` unnoticed until someone ran the scan.

## Recommendation

- **Fix:** CI gitleaks job with `fetch-depth: 0`, and SHA-pinned action (see SEC-002) or a pinned binary download.
- **Verify:** A pull request containing a test secret fails the job.
- **Alternatives rejected:** Server-side hooks (not available on GitHub-hosted repos).

## Resolution

Fixed 2026-10-31: new `secrets` job in `ci.yml` (full history, gitleaks 8.26.0 download verified against a pinned SHA-256). Real-run verification pending the first push.

## Risk Acceptance

Not accepted.
