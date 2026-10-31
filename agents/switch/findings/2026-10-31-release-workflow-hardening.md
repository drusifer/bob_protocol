# SEC-002: Release workflow uses mutable action refs and default token permissions

- **Severity:** Medium — the publish job holds a PyPI OIDC token, and a compromised or moved action tag would run with it; exploitation needs an upstream compromise, so likelihood is low.
- **Status:** Fixed (verification pending next CI run)
- **Verdict:** No blocking findings (does not block 0.2.0; fix before the next release if possible)
- **Date / author:** 2026-10-31 / Switch
- **Affected:** `.github/workflows/release.yml:18,20,30,42,48`; `.github/workflows/ci.yml` (no `permissions:` block)
- **Class / reference:** Supply-chain / least privilege (CWE-829, CWE-250); GitHub Actions hardening guidance

## Next Action

| Who | Does what | By / trigger |
|---|---|---|
| Tank | Pin every `uses:` to a full commit SHA (keep the tag in a comment) and add top-level `permissions: contents: read` to both workflows, keeping `id-token: write` only on the publish job | Before the next release |
| Switch | Re-review the workflow diff and run `bobp make security-scan` | After Tank's change |

## Evidence

- **Reproduce / detect:** `grep -n "uses:\|permissions" .github/workflows/*.yml` shows `actions/*@v4/v5` and `pypa/gh-action-pypi-publish@release/v1` (a branch ref) in the job that publishes; only the publish job sets `permissions`.
- **Observed:** The `pypi` environment does require reviewers (`gh api .../environments/pypi` → `required_reviewers`), which limits abuse. The build job and `ci.yml` inherit the repository's default token permissions.
- **Confidence:** High on the facts; the default token scope depends on repo settings I did not inspect.

## Impact and Reachability

A malicious update to an unpinned action runs in CI and, in the publish job, can mint a PyPI token for `bobp` and upload a tampered release. Reachable only through an upstream action compromise.

## Recommendation

- **Fix:** SHA-pin actions; minimal `permissions`. Optionally add Dependabot for `github-actions` to keep pins current.
- **Verify:** `grep -n "uses:" .github/workflows/*.yml` shows only 40-character SHAs; a test release still publishes.
- **Alternatives rejected:** Leaving tags (convenient, but the risk lands on the privileged job).

## Resolution

Fixed 2026-10-31: all `uses:` pinned to commit SHAs (verified by grep: none unpinned), `permissions: contents: read` at workflow level in both files, `id-token: write` only on the publish job, `.github/dependabot.yml` added. YAML parses. Real-run verification pending the next CI run and release.

## Risk Acceptance

Not accepted.
