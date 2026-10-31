#!/usr/bin/env python3
"""
Gate dependency audits (npm audit, pip-audit) on advisories the user has not accepted.

TLDR:
    Runs `npm audit --json` (npm) or `pip-audit -f json` (python), then fails
    (exit 1) only when an advisory at or above --level is NOT covered by a valid
    entry in the accepted-risks file. pip-audit reports no severity, so every
    Python advisory counts as blocking until accepted. Accepted advisories are
    printed with reason, expiry, and re-check trigger so they stay visible.
    Every acceptance needs an `expires` date at most 90 days after its `date`;
    expired, undated, or over-long acceptances do not count, and the gate warns
    14 days ahead. Secrets scanning (gitleaks) is NOT handled here: it is a hard
    block with no acceptance path. Only the user accepts risk; Switch records it
    in agents/switch/accepted-risks.json.
"""

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

LEVELS = ["info", "low", "moderate", "high", "critical"]
WARN_DAYS = 14
MAX_DAYS = 90  # longest allowed acceptance, counted from the `date` it was granted


def advisories(audit):
    """Map GHSA id -> (severity, package) for every advisory in an `npm audit --json` report."""
    found = {}
    for vuln in audit.get("vulnerabilities", {}).values():
        for via in vuln.get("via", []):
            if isinstance(via, dict) and via.get("url"):
                found[via["url"].rsplit("/", 1)[-1]] = (via.get("severity", "info"), via.get("name", "?"))
    return found


def pip_advisories(report):
    """Map advisory id (and each alias) -> (severity, package) from `pip-audit -f json` output.

    pip-audit gives no severity, so every advisory is treated as 'high'.
    """
    found = {}
    for dep in report.get("dependencies", []):
        for vuln in dep.get("vulns", []):
            for ident in [vuln["id"], *vuln.get("aliases", [])]:
                found[ident] = ("high", dep["name"])
    return found


def acceptance_status(entry, today):
    """Return ('active'|'expiring'|'expired'|'undated', expiry date or None) for an accepted entry."""
    try:
        expires = datetime.date.fromisoformat(entry["expires"])
        granted = datetime.date.fromisoformat(entry["date"])
    except (KeyError, ValueError, TypeError):
        return "undated", None
    if (expires - granted).days > MAX_DAYS:
        return "undated", None
    if expires < today:
        return "expired", expires
    if (expires - today).days <= WARN_DAYS:
        return "expiring", expires
    return "active", expires


def evaluate(audit, accepted, level, today=None, found=None):
    """Classify advisories.

    Returns (blocking, accepted_hits, problems): unaccepted advisories >= level
    (including ones whose acceptance expired or is invalid), accepted ones that
    are still valid, and notices about expired, invalid, or soon-to-expire acceptances.
    """
    today = today or datetime.date.today()
    threshold = LEVELS.index(level)
    blocking, accepted_hits, problems = [], [], []
    for ghsa, (severity, package) in sorted((found if found is not None else advisories(audit)).items()):
        entry = accepted.get(ghsa)
        status, expires = acceptance_status(entry, today) if entry else (None, None)
        if status in ("active", "expiring"):
            accepted_hits.append((ghsa, severity, package, entry))
            if status == "expiring":
                problems.append(f"EXPIRING {ghsa} ({package}) on {expires}: re-review and renew or fix")
            continue
        if status == "expired":
            problems.append(f"EXPIRED {ghsa} ({package}) on {expires}: acceptance no longer counts")
        elif status == "undated":
            problems.append(f"INVALID {ghsa} ({package}): acceptance needs a valid `date` and an `expires` date (YYYY-MM-DD) at most {MAX_DAYS} days after it, and does not count")
        if LEVELS.index(severity) >= threshold:
            blocking.append((ghsa, severity, package))
    return blocking, accepted_hits, problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ecosystem", choices=["npm", "python"], default="npm")
    parser.add_argument("--prefix", help="npm project directory to audit (npm)")
    parser.add_argument("--requirements", help="pinned requirements file to audit (python)")
    parser.add_argument("--accepted", required=True, help="JSON file of accepted advisories")
    parser.add_argument("--level", default="high", choices=LEVELS)
    args = parser.parse_args()

    accepted_file = Path(args.accepted)
    accepted = {}
    if accepted_file.is_file():
        accepted = {e["id"]: e for e in json.loads(accepted_file.read_text())["accepted"]}

    if args.ecosystem == "npm":
        command = ["npm", "audit", "--prefix", args.prefix, "--json"]
    else:
        command = ["uvx", "pip-audit", "-r", args.requirements, "--disable-pip", "--no-deps", "-f", "json"]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    try:
        audit = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"{command[0]} produced no JSON (exit {result.returncode}): {result.stderr.strip()[:300]}", file=sys.stderr)
        return 2
    found = pip_advisories(audit) if args.ecosystem == "python" else None

    blocking, accepted_hits, problems = evaluate(audit, accepted, args.level, found=found)
    for ghsa, severity, package, entry in accepted_hits:
        print(f"ACCEPTED {ghsa} ({severity}, {package}) by {entry['accepted_by']} on {entry['date']}: "
              f"{entry['reason']} Expires: {entry['expires']}. Re-check: {entry['recheck']}")
    for problem in problems:
        print(problem)
    for ghsa, severity, package in blocking:
        print(f"BLOCKING {ghsa} ({severity}, {package}): not accepted; fix the dependency or ask the user to accept the risk with an expiry")
    if blocking:
        return 1
    print(f"audit gate passed at level '{args.level}' ({len(accepted_hits)} accepted advisories noted).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
