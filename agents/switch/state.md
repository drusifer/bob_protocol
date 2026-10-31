# Agent State

## Context
- Switch (Security Engineer, `*sec`) created 2026-10-31. Authority: runs scans and fixes vulnerable dependencies (upgrade/swap/remove); proposes patches for application source (Neo applies); Tank owns Makefile mechanism/SDLC and gitleaks standards; only the user accepts risk.
- Shared skill: `agents/skills/security/SKILL.md`. Make targets: `security-scan`, `security-scan-secrets`, `security-scan-python`, `security-scan-npm`.

- Gitleaks: `.githooks/pre-commit` + `install-hooks` target added and enabled (core.hooksPath); verified it blocks a staged fake key. Switch re-verifies this on every review.
- Templates: `_template_SECURITY_FINDING.md` (SEC-NNN) and `_template_SECURITY_REVIEW.md`; reviews go in `reviews/`, findings in `findings/`.

## Current Task
**Status:** First scan complete; awaiting user decision on one finding.
**Result:** gitleaks clean; pip-audit clean; npm audit: 8 vulns via promptfoo 0.125.1 (latest, no safe fix). Details: `findings/2026-10-31-promptfoo-transitive-vulns.md` (SEC-001).

### Open findings / accepted risks
- OPEN: promptfoo transitive vulns (5 high, 3 moderate), dev-only; recommended to accept with re-check when promptfoo > 0.125.1.

## Next Steps
1. Get the user's decision on the promptfoo finding; if accepted, record it here and decide how the gate treats it (Tank/SDLC).
2. Re-run `bobp make security-scan` after any dependency change or promptfoo bump.
3. Mermaid tools lack a lockfile; propose adding one (Tank/SDLC change) so they can be audited.
