# Agent State

## Context
- Switch (Security Engineer, `*sec`) created 2026-10-31. Authority: runs scans and fixes vulnerable dependencies (upgrade/swap/remove); proposes patches for application source (Neo applies); Tank owns Makefile mechanism/SDLC and gitleaks standards; only the user accepts risk.
- Shared skill: `agents/skills/security/SKILL.md`. Make targets: `security-scan`, `security-scan-secrets`, `security-scan-python`, `security-scan-npm`.

- Gitleaks: `.githooks/pre-commit` + `install-hooks` target added and enabled (core.hooksPath); verified it blocks a staged fake key. Switch re-verifies this on every review.
- Templates: `_template_SECURITY_FINDING.md` (SEC-NNN) and `_template_SECURITY_REVIEW.md`; reviews go in `reviews/`, findings in `findings/`.

## Current Task
**Status:** Sprint 5 Design Gate 2b (`TH-S5-1..5` resolved) & Phase 1–2 security gates cleared (`No blocking findings`) & Sprint 5 LAUNCHED (2026-11-28).
**Result:** Phase 5 & 6 quick passes clear (no external org data, clean text/moves); Phase 7 Gate 5a verified zero-write `--help`/`--dry-run` paths, `clean --yes` scope, SEC-007 `printable()` output hygiene, and version-check help bypass test. Clean-rebuild `bobp make security-scan` passed (`gitleaks` 0 leaks, `pip-audit` clean, `npm audit` clean with 3 accepted SEC-001 advisories expiring `2027-01-29`).

### Open findings / accepted risks
- FIXED 2026-10-31: SEC-002 (workflows pinned, least privilege, Dependabot), SEC-003 (recap Markdown escaped + test), SEC-004 (CI gitleaks job). SEC-002/004 need confirmation from the first CI run after push.
- Review: `reviews/2026-10-31-v0.2.0-release-review.md` — verdict No blocking findings.
- ACCEPTED (user, 2026-10-31, EXPIRES 2027-01-29 — renew or fix by then; warn from 2027-01-15): SEC-001 promptfoo transitive vulns (3 advisories), recorded in `accepted-risks.json`; gate `tools/audit_gate.py` notes them and blocks new ones. Re-check when promptfoo > 0.125.1.

## Next Steps
1. Confirm the first CI run passes (pinned actions, `secrets` job).
2. Re-run `bobp make security-scan` after any dependency change or promptfoo bump.
3. Mermaid tools lack a lockfile; propose adding one (Tank/SDLC change) so they can be audited.
