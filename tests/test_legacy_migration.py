"""Phase 2 of sprint 3: no links, legacy migration, and a real root AGENTS.md."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bobp.tools import _bob_manage, _skill_layout


def _update(target: Path) -> None:
    with patch.object(_bob_manage, "_run_setup_agent_links"):
        _bob_manage.update(target)


def _install(target: Path) -> None:
    with patch.object(_bob_manage, "_run_setup_agent_links"):
        _bob_manage.install(target)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _symlinks(root: Path) -> "list[str]":
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            path = Path(dirpath) / name
            if path.is_symlink():
                found.append(path.relative_to(root).as_posix())
    return sorted(found)


def _legacy_project(root: Path) -> None:
    """A project laid out by an older bobp: links everywhere, skills under agents/."""
    _write(root / "agents" / "AGENTS.md", "# shared instructions\n")
    _write(root / "agents" / "skills" / "make" / "SKILL.md", "old make\n")
    _write(root / "agents" / "skills" / "myown" / "SKILL.md", "project skill\n")
    _write(root / "agents" / "neo" / "SKILL.md", "old neo\n")
    _write(root / "agents" / "neo" / "state.md", "neo memory\n")
    _write(root / "agents" / "foo" / "SKILL.md", "project persona\n")
    _write(root / "agents" / "foo" / "state.md", "foo memory\n")
    _write(root / "agents" / "CHAT.md", "history mentions agents/skills/make/SKILL.md\n")
    os.symlink("AGENTS.md", root / "agents" / "AGENT.md")
    os.symlink("agents/AGENTS.md", root / "AGENTS.md")
    os.symlink("agents/AGENTS.md", root / "AGENT.md")
    os.symlink("agents/AGENTS.md", root / "CHATGPT.md")
    _write(root / "GEMINI.md", "my own gemini notes\n")
    os.symlink("/etc/hosts", root / ".cursorrules")
    os.symlink("agents", root / ".agents")
    (root / ".github").mkdir()
    os.symlink("../agents/AGENTS.md", root / ".github" / "copilot-instructions.md")
    (root / ".claude" / "skills").mkdir(parents=True)
    os.symlink("../../agents/skills/make", root / ".claude" / "skills" / "make")
    os.symlink("../../agents/skills/myown", root / ".claude" / "skills" / "myown")
    os.symlink("../../agents/neo", root / ".claude" / "skills" / "neo")


class LegacyMigrationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "proj"
        self.root.mkdir()
        _legacy_project(self.root)

    def test_only_bobp_links_are_removed(self):
        _update(self.root)
        self.assertEqual(_symlinks(self.root), [".cursorrules"])
        self.assertEqual((self.root / "GEMINI.md").read_text(), "my own gemini notes\n")
        self.assertEqual(os.readlink(self.root / ".cursorrules"), "/etc/hosts")
        self.assertTrue(Path("/etc/hosts").exists())

    def test_empty_github_directory_left_by_bobp_is_removed(self):
        _update(self.root)
        self.assertFalse((self.root / ".github").exists())

    def test_github_directory_with_other_files_is_kept(self):
        _write(self.root / ".github" / "CODEOWNERS", "* @someone\n")
        _update(self.root)
        self.assertTrue((self.root / ".github" / "CODEOWNERS").is_file())
        self.assertFalse((self.root / ".github" / "copilot-instructions.md").exists())

    def test_root_agents_md_becomes_a_real_file_and_agents_copy_is_gone(self):
        _update(self.root)
        agents_md = self.root / "AGENTS.md"
        self.assertTrue(agents_md.is_file() and not agents_md.is_symlink())
        self.assertEqual(agents_md.read_text(), "# shared instructions\n")
        self.assertFalse((self.root / "agents" / "AGENTS.md").exists())
        self.assertFalse(os.path.lexists(self.root / "agents" / "AGENT.md"))

    def test_packaged_skills_are_refreshed_and_old_copies_removed(self):
        _update(self.root)
        make = self.root / ".agents" / "skills" / "make"
        self.assertTrue(make.is_dir() and not make.is_symlink())
        self.assertNotEqual((make / "SKILL.md").read_text(), "old make\n")
        self.assertFalse((self.root / "agents" / "skills").exists())
        self.assertIn("make", _skill_layout.read_manifest(self.root / "agents"))

    def test_project_own_skill_is_moved_not_overwritten_and_not_owned(self):
        _update(self.root)
        own = self.root / ".agents" / "skills" / "myown"
        self.assertTrue(own.is_dir() and not own.is_symlink())
        self.assertEqual((own / "SKILL.md").read_text(), "project skill\n")
        self.assertNotIn("myown", _skill_layout.read_manifest(self.root / "agents"))
        _update(self.root)
        self.assertEqual((own / "SKILL.md").read_text(), "project skill\n")

    def test_persona_skill_moves_out_of_agents_and_memory_stays(self):
        _update(self.root)
        self.assertFalse((self.root / "agents" / "neo" / "SKILL.md").exists())
        self.assertEqual((self.root / "agents" / "neo" / "state.md").read_text(), "neo memory\n")
        neo = self.root / ".agents" / "skills" / "neo"
        self.assertTrue(neo.is_dir() and not neo.is_symlink())
        self.assertNotEqual((neo / "SKILL.md").read_text(), "old neo\n")

    def test_project_own_persona_skill_is_moved_and_memory_stays(self):
        _update(self.root)
        self.assertEqual(
            (self.root / ".agents" / "skills" / "foo" / "SKILL.md").read_text(), "project persona\n"
        )
        self.assertFalse((self.root / "agents" / "foo" / "SKILL.md").exists())
        self.assertEqual((self.root / "agents" / "foo" / "state.md").read_text(), "foo memory\n")
        self.assertNotIn("foo", _skill_layout.read_manifest(self.root / "agents"))

    def test_chat_history_is_left_as_written(self):
        _update(self.root)
        self.assertIn("agents/skills/make/SKILL.md", (self.root / "agents" / "CHAT.md").read_text())

    def test_second_update_changes_nothing(self):
        _update(self.root)
        before = sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*"))
        sizes = {p: p.stat().st_size for p in self.root.rglob("*") if p.is_file()}
        _update(self.root)
        after = sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*"))
        self.assertEqual(before, after)
        self.assertEqual(sizes, {p: p.stat().st_size for p in self.root.rglob("*") if p.is_file()})

    def test_update_prints_what_it_moved_and_removed(self):
        import contextlib
        import io

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            _update(self.root)
        text = out.getvalue()
        self.assertIn("Removed", text)
        self.assertIn("Moved", text)

    def test_dry_run_changes_nothing_and_reports_the_plan(self):
        before = sorted(os.path.relpath(os.path.join(d, n), self.root)
                        for d, ds, fs in os.walk(self.root) for n in ds + fs)
        link_actions = _skill_layout.remove_legacy_links(self.root, dry_run=True)
        move_actions = _skill_layout.migrate_legacy(
            self.root, _bob_manage.templates_dir(), dry_run=True
        )
        after = sorted(os.path.relpath(os.path.join(d, n), self.root)
                       for d, ds, fs in os.walk(self.root) for n in ds + fs)
        self.assertEqual(before, after)
        self.assertTrue(any(a.kind == "remove" for a in link_actions))
        self.assertTrue(any(a.kind == "move" for a in move_actions))


class LinkSafetyTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "proj"
        (self.root / "agents").mkdir(parents=True)

    def test_link_pointing_outside_agents_is_never_removed(self):
        outside = Path(self._tmp.name) / "outside.md"
        outside.write_text("keep\n")
        os.symlink(outside, self.root / "GEMINI.md")
        os.symlink("README.md", self.root / "CHATGPT.md")  # inside project, not agents/
        actions = _skill_layout.remove_legacy_links(self.root)
        self.assertTrue((self.root / "GEMINI.md").is_symlink())
        self.assertTrue((self.root / "CHATGPT.md").is_symlink())
        self.assertEqual(outside.read_text(), "keep\n")
        self.assertEqual([a.kind for a in actions], ["skipped", "skipped"])

    def test_dotdot_escape_through_agents_is_not_treated_as_inside(self):
        os.symlink("agents/../../escape", self.root / "GEMINI.md")
        _skill_layout.remove_legacy_links(self.root)
        self.assertTrue(os.path.lexists(self.root / "GEMINI.md"))

    def test_real_files_and_directories_are_never_touched(self):
        for name in ("AGENT.md", "GEMINI.md", ".cursorrules", "CHATGPT.md"):
            (self.root / name).write_text("mine\n")
        (self.root / ".agents").mkdir()
        (self.root / ".agents" / "keep.txt").write_text("keep\n")
        _skill_layout.remove_legacy_links(self.root)
        for name in ("AGENT.md", "GEMINI.md", ".cursorrules", "CHATGPT.md"):
            self.assertEqual((self.root / name).read_text(), "mine\n")
        self.assertTrue((self.root / ".agents" / "keep.txt").is_file())

    def test_self_referencing_link_does_not_loop_or_get_removed(self):
        os.symlink(".agents", self.root / ".agents")
        _skill_layout.remove_legacy_links(self.root)
        self.assertTrue(os.path.lexists(self.root / ".agents"))

    def test_control_characters_in_project_names_never_reach_the_terminal(self):
        """SEC-007: names come from a possibly hostile repo and are echoed to the terminal."""
        import contextlib
        import io

        bad = "bad\x1b[31mname\x07"
        (self.root / "agents" / "skills" / bad).mkdir(parents=True)
        (self.root / "agents" / "skills" / bad / "SKILL.md").write_text("x\n")
        os.symlink("/etc/hosts", self.root / "GEMINI.md")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            actions = _skill_layout.migrate_legacy(self.root, _bob_manage.templates_dir())
            actions += _skill_layout.remove_legacy_links(self.root)
            for line in _skill_layout.describe(actions):
                print(line)
        self.assertTrue(any("bad" in a.path for a in actions))
        self.assertNotIn("\x1b", out.getvalue())
        self.assertNotIn("\x07", out.getvalue())

    def test_whole_directory_skills_link_into_agents_is_replaced_by_a_real_directory(self):
        (self.root / "agents" / "skills" / "chat").mkdir(parents=True)
        (self.root / "agents" / "skills" / "chat" / "SKILL.md").write_text("old chat\n")
        (self.root / ".claude").mkdir()
        os.symlink("../agents/skills", self.root / ".claude" / "skills")
        _update(self.root)
        skills = self.root / ".agents" / "skills"
        self.assertTrue(skills.is_dir() and not skills.is_symlink())
        self.assertTrue((skills / "chat" / "SKILL.md").is_file())
        self.assertEqual(_symlinks(self.root), [])

    def test_whole_directory_skills_link_elsewhere_is_refused_not_followed(self):
        outside = Path(self._tmp.name) / "shared-skills"
        outside.mkdir()
        (self.root / ".agents").mkdir()
        os.symlink(outside, self.root / ".agents" / "skills")
        with self.assertRaises(_skill_layout.SkillLayoutError):
            _update(self.root)
        self.assertEqual(list(outside.iterdir()), [])

    def test_symlinked_claude_directory_is_not_traversed(self):
        outside = Path(self._tmp.name) / "outside"
        (outside / "skills").mkdir(parents=True)
        os.symlink("../../agents/skills/x", outside / "skills" / "x")
        os.symlink(outside, self.root / ".claude")
        _skill_layout.remove_legacy_links(self.root)
        self.assertTrue(os.path.lexists(outside / "skills" / "x"))

    def test_migration_never_moves_through_a_symlinked_agents_skills(self):
        outside = Path(self._tmp.name) / "outside"
        (outside / "evil").mkdir(parents=True)
        (outside / "evil" / "SKILL.md").write_text("outside\n")
        os.symlink(outside, self.root / "agents" / "skills")
        _skill_layout.migrate_legacy(self.root, _bob_manage.templates_dir())
        self.assertTrue((outside / "evil" / "SKILL.md").is_file())
        self.assertFalse((self.root / ".agents" / "skills" / "evil").exists())


class RootAgentsMdTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "proj"
        self.root.mkdir()

    def test_install_writes_a_real_root_agents_md_and_no_links(self):
        _install(self.root)
        agents_md = self.root / "AGENTS.md"
        bob_agents = self.root / "agents" / "BOB_AGENTS.md"
        self.assertTrue(agents_md.is_file() and not agents_md.is_symlink())
        self.assertIn("agents/BOB_AGENTS.md", agents_md.read_text())
        self.assertTrue(bob_agents.is_file() and not bob_agents.is_symlink())
        self.assertIn("Core Operational Principles", bob_agents.read_text())
        self.assertFalse((self.root / "agents" / "AGENTS.md").exists())
        self.assertFalse(os.path.lexists(self.root / "agents" / "AGENT.md"))
        self.assertEqual(_symlinks(self.root), [])

    def test_install_does_not_overwrite_an_existing_root_agents_md(self):
        (self.root / "AGENTS.md").write_text("project rules\n")
        _install(self.root)
        self.assertEqual((self.root / "AGENTS.md").read_text(), "project rules\n")
        self.assertIn("Core Operational Principles", (self.root / "agents" / "BOB_AGENTS.md").read_text())

    def test_update_never_overwrites_an_edited_root_agents_md(self):
        _install(self.root)
        (self.root / "AGENTS.md").write_text("edited by the project\n")
        (self.root / "agents" / "BOB_AGENTS.md").write_text("stale bob rules\n")
        _update(self.root)
        self.assertEqual((self.root / "AGENTS.md").read_text(), "edited by the project\n")
        self.assertIn(
            "Core Operational Principles", (self.root / "agents" / "BOB_AGENTS.md").read_text()
        )

    def test_update_creates_root_agents_md_when_missing(self):
        _install(self.root)
        (self.root / "AGENTS.md").unlink()
        _update(self.root)
        self.assertIn("agents/BOB_AGENTS.md", (self.root / "AGENTS.md").read_text())
        self.assertIn(
            "Core Operational Principles", (self.root / "agents" / "BOB_AGENTS.md").read_text()
        )

    def test_dangling_legacy_symlink_is_replaced_with_the_packaged_text(self):
        (self.root / "agents").mkdir()
        os.symlink("agents/AGENTS.md", self.root / "AGENTS.md")
        _update(self.root)
        agents_md = self.root / "AGENTS.md"
        self.assertTrue(agents_md.is_file() and not agents_md.is_symlink())
        self.assertIn("agents/BOB_AGENTS.md", agents_md.read_text())
        self.assertIn(
            "Core Operational Principles", (self.root / "agents" / "BOB_AGENTS.md").read_text()
        )

    def test_ensure_root_agents_md_notes_missing_bob_agents_pointer(self):
        (self.root / "AGENTS.md").write_text("custom rules only\n")
        actions = _skill_layout.ensure_root_agents_md(self.root, _bob_manage.templates_dir())
        self.assertTrue(any(a.kind == "note" and a.path == "AGENTS.md" for a in actions))

        (self.root / "AGENTS.md").write_text("Read agents/BOB_AGENTS.md first.\n")
        actions2 = _skill_layout.ensure_root_agents_md(self.root, _bob_manage.templates_dir())
        self.assertFalse(any(a.kind == "note" for a in actions2))

    def test_place_bob_agents_md_refuses_symlinks_and_supports_dry_run(self):
        (self.root / "agents").mkdir()
        outside = Path(self._tmp.name) / "outside.md"
        outside.write_text("DO NOT TOUCH\n")
        os.symlink(outside, self.root / "agents" / "BOB_AGENTS.md")
        with self.assertRaises(_skill_layout.SkillLayoutError):
            _skill_layout.place_bob_agents_md(self.root, _bob_manage.templates_dir())
        self.assertEqual(outside.read_text(), "DO NOT TOUCH\n")

        (self.root / "agents" / "BOB_AGENTS.md").unlink()
        actions = _skill_layout.place_bob_agents_md(
            self.root, _bob_manage.templates_dir(), dry_run=True
        )
        self.assertEqual(len(actions), 1)
        self.assertFalse((self.root / "agents" / "BOB_AGENTS.md").exists())

    def test_agents_copy_that_differs_from_a_real_root_file_is_kept_and_reported(self):
        (self.root / "AGENTS.md").write_text("root version\n")
        (self.root / "agents").mkdir()
        (self.root / "agents" / "AGENTS.md").write_text("agents version, edited\n")
        _update(self.root)
        self.assertEqual((self.root / "AGENTS.md").read_text(), "root version\n")
        self.assertEqual(
            (self.root / "agents" / "AGENTS.md").read_text(), "agents version, edited\n"
        )

    def test_identical_agents_copy_is_removed(self):
        (self.root / "AGENTS.md").write_text("same\n")
        (self.root / "agents").mkdir()
        (self.root / "agents" / "AGENTS.md").write_text("same\n")
        _update(self.root)
        self.assertFalse((self.root / "agents" / "AGENTS.md").exists())


class NoLinkSetupTests(unittest.TestCase):
    def test_setup_script_no_longer_has_link_creating_functions(self):
        from bobp.tools import setup_agent_links

        for name in (
            "create_symlink",
            "setup_claude_skills",
            "setup_codex_skills",
            "setup_root_symlinks",
            "find_shared_skills",
        ):
            self.assertFalse(hasattr(setup_agent_links, name), name)


if __name__ == "__main__":
    unittest.main()
