# Agent State

## Context
- Switch (Security Engineer, `*sec`) created 2026-10-31. Authority: runs scans and fixes vulnerable dependencies (upgrade/swap/remove); proposes patches for application source (Neo applies); Tank owns Makefile mechanism/SDLC and gitleaks standards; only the user accepts risk.
- Shared skill: `agents/skills/security/SKILL.md`. Make targets: `security-scan`, `security-scan-secrets`, `security-scan-python`, `security-scan-npm`.

- Gitleaks: `.githooks/pre-commit` + `install-hooks` target added and enabled (core.hooksPath); verified it blocks a staged fake key. Switch re-verifies this on every review.
- Templates: `_template_SECURITY_FINDING.md` (SEC-NNN) and `_template_SECURITY_REVIEW.md`; reviews go in `reviews/`, findings in `findings/`.

## Current Task
**Status:** Findings SEC-001..004 resolved (SEC-002/004 await first CI run).
**Result:** gitleaks clean; pip-audit clean; npm audit: 8 vulns via promptfoo 0.125.1 (latest, no safe fix). Details: `findings/2026-10-31-promptfoo-transitive-vulns.md` (SEC-001).

### Open findings / accepted risks
- FIXED 2026-10-31: SEC-002 (workflows pinned, least privilege, Dependabot), SEC-003 (recap Markdown escaped + test), SEC-004 (CI gitleaks job). SEC-002/004 need confirmation from the first CI run after push.
- Review: `reviews/2026-10-31-v0.2.0-release-review.md` — verdict No blocking findings.
- ACCEPTED (user, 2026-10-31, EXPIRES 2027-01-29 — renew or fix by then; warn from 2027-01-15): SEC-001 promptfoo transitive vulns (3 advisories), recorded in `accepted-risks.json`; gate `tools/audit_gate.py` notes them and blocks new ones. Re-check when promptfoo > 0.125.1.

## Next Steps
1. Confirm the first CI run passes (pinned actions, `secrets` job).
2. Re-run `bobp make security-scan` after any dependency change or promptfoo bump.
3. Mermaid tools lack a lockfile; propose adding one (Tank/SDLC change) so they can be audited.
