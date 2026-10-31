"""The audit gate blocks unaccepted advisories and only notes accepted ones."""

import datetime
import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "audit_gate", Path(__file__).resolve().parent.parent / "tools" / "audit_gate.py"
)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def audit(*advisories):
    """Build a minimal `npm audit --json` report from (ghsa, severity, package) tuples."""
    return {"vulnerabilities": {
        pkg: {"via": [{"url": f"https://github.com/advisories/{ghsa}", "severity": sev, "name": pkg}]}
        for ghsa, sev, pkg in advisories
    }}


TODAY = datetime.date(2026, 11, 1)
ACCEPTED = {"GHSA-aaaa": {"accepted_by": "user", "date": "2026-10-31", "reason": "r", "recheck": "c", "expires": "2027-01-29"}}


def accepted_with(**changes):
    return {"GHSA-aaaa": {**ACCEPTED["GHSA-aaaa"], **changes}}


def test_accepted_advisory_does_not_block() -> None:
    blocking, accepted, problems = gate.evaluate(audit(("GHSA-aaaa", "high", "pkg")), ACCEPTED, "high", TODAY)
    assert problems == []
    assert blocking == []
    assert accepted[0][0] == "GHSA-aaaa"


def test_new_high_advisory_blocks() -> None:
    blocking, _, _ = gate.evaluate(audit(("GHSA-aaaa", "high", "a"), ("GHSA-bbbb", "high", "b")), ACCEPTED, "high", TODAY)
    assert [b[0] for b in blocking] == ["GHSA-bbbb"]


def test_advisory_below_level_does_not_block() -> None:
    blocking, _, _ = gate.evaluate(audit(("GHSA-bbbb", "moderate", "b")), ACCEPTED, "high", TODAY)
    assert blocking == []


def test_nested_dependency_via_strings_are_ignored() -> None:
    report = {"vulnerabilities": {"parent": {"via": ["child"]}}}
    assert gate.advisories(report) == {}


def test_expired_acceptance_blocks_again() -> None:
    blocking, accepted, problems = gate.evaluate(
        audit(("GHSA-aaaa", "high", "pkg")), accepted_with(expires="2026-10-31"), "high", TODAY)
    assert [b[0] for b in blocking] == ["GHSA-aaaa"]
    assert accepted == []
    assert problems[0].startswith("EXPIRED GHSA-aaaa")


def test_acceptance_without_expiry_does_not_count() -> None:
    entry = dict(ACCEPTED["GHSA-aaaa"])
    del entry["expires"]
    blocking, accepted, problems = gate.evaluate(audit(("GHSA-aaaa", "high", "pkg")), {"GHSA-aaaa": entry}, "high", TODAY)
    assert [b[0] for b in blocking] == ["GHSA-aaaa"] and accepted == []
    assert problems[0].startswith("INVALID GHSA-aaaa")


def test_acceptance_expiring_soon_still_passes_with_a_warning() -> None:
    blocking, accepted, problems = gate.evaluate(
        audit(("GHSA-aaaa", "high", "pkg")), accepted_with(expires="2026-11-10"), "high", TODAY)
    assert blocking == [] and len(accepted) == 1
    assert problems[0].startswith("EXPIRING GHSA-aaaa")


def test_acceptance_longer_than_90_days_does_not_count() -> None:
    blocking, accepted, problems = gate.evaluate(
        audit(("GHSA-aaaa", "high", "pkg")), accepted_with(expires="2027-03-01"), "high", TODAY)
    assert [b[0] for b in blocking] == ["GHSA-aaaa"] and accepted == []
    assert problems[0].startswith("INVALID GHSA-aaaa")


PIP_REPORT = {"dependencies": [{"name": "pkg", "version": "1.0", "vulns": [
    {"id": "PYSEC-2026-1", "aliases": ["GHSA-aaaa", "CVE-2026-1"], "fix_versions": ["1.1"]}]}]}


def test_python_advisory_blocks_until_accepted_by_alias() -> None:
    found = gate.pip_advisories(PIP_REPORT)
    assert {"PYSEC-2026-1", "GHSA-aaaa", "CVE-2026-1"} <= set(found)
    blocking, _, _ = gate.evaluate({}, {}, "high", TODAY, found=found)
    assert blocking
    blocking, accepted, _ = gate.evaluate({}, ACCEPTED, "high", TODAY, found=found)
    assert not [b for b in blocking if b[0] == "GHSA-aaaa"]
    assert any(a[0] == "GHSA-aaaa" for a in accepted)
