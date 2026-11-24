"""Every packaged skill and persona must satisfy the Agent Skills specification.

Specification: https://agentskills.io/specification
Later sprint 3 phases add the best-practices checks (size, descriptions, pointers)
to this file.
"""

import re
import unittest
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "bobp" / "templates" / "agents"

ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def packaged_skills() -> "list[tuple[str, Path]]":
    """(directory name, SKILL.md.txt path) for every persona and shared skill shipped."""
    found = [(p.parent.name, p) for p in sorted(TEMPLATES.glob("*/SKILL.md.txt"))]
    found += [(p.parent.name, p) for p in sorted((TEMPLATES / "skills").glob("*/SKILL.md.txt"))]
    return found


def frontmatter(path: Path) -> "tuple[dict[str, str], str]":
    """Top-level frontmatter keys (value = text after the colon) and the body."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if match is None:
        raise AssertionError(f"{path}: no YAML frontmatter")
    keys = {}
    for line in match.group(1).splitlines():
        top = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if top:
            keys[top.group(1)] = top.group(2).strip()
    return keys, match.group(2)


class PackagedSkillSpecTests(unittest.TestCase):
    def test_packaged_skills_are_found(self):
        names = [name for name, _ in packaged_skills()]
        self.assertGreaterEqual(len(names), 35)
        self.assertEqual(len(names), len(set(names)), "persona and skill names must be unique")

    def test_name_matches_directory(self):
        for directory, path in packaged_skills():
            with self.subTest(skill=directory):
                keys, _ = frontmatter(path)
                self.assertEqual(keys.get("name", "").strip("'\""), directory)

    def test_name_follows_the_spec_pattern(self):
        for directory, _ in packaged_skills():
            with self.subTest(skill=directory):
                self.assertRegex(directory, NAME_RE)
                self.assertLessEqual(len(directory), 64)

    def test_description_is_present_and_within_limit(self):
        for directory, path in packaged_skills():
            with self.subTest(skill=directory):
                keys, _ = frontmatter(path)
                description = keys.get("description", "")
                self.assertTrue(description, "description is required")
                self.assertLessEqual(len(description), 1024)

    def test_only_specified_frontmatter_keys(self):
        for directory, path in packaged_skills():
            with self.subTest(skill=directory):
                keys, _ = frontmatter(path)
                self.assertFalse(set(keys) - ALLOWED_KEYS, f"unknown keys: {set(keys) - ALLOWED_KEYS}")

    def test_skills_fit_size_budget_and_reference_existing_files_conditionally(self):
        for directory, path in packaged_skills():
            with self.subTest(skill=directory):
                text = path.read_text(encoding="utf-8")
                self.assertLessEqual(len(text.splitlines()), 500)
                self.assertLessEqual((len(text) + 3) // 4, 4500)
                for line in text.splitlines():
                    for target in re.findall(r"references/([\w.-]+\.md)", line):
                        self.assertRegex(line.lower(), r"\bwhen\b|\bif\b")
                        self.assertTrue((path.parent / "references" / target).is_file())


if __name__ == "__main__":
    unittest.main()
