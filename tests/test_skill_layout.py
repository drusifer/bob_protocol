"""Phase 1 of sprint 3: skills are placed as real directories in .agents/skills/."""

import os
import tempfile
import unittest
from pathlib import Path

from bobp.tools import _bob_manage, _skill_layout
from bobp.tools._skill_layout import SkillLayoutError

from unittest.mock import patch


def _install(target: Path) -> None:
    with patch.object(_bob_manage, "_run_setup_agent_links"):
        _bob_manage.install(target)


def _update(target: Path) -> None:
    with patch.object(_bob_manage, "_run_setup_agent_links"):
        _bob_manage.update(target)


def _tree_symlinks(root: Path) -> "list[Path]":
    return [p for p in root.rglob("*") if p.is_symlink()]


class NameValidationTests(unittest.TestCase):
    def test_valid_and_invalid_names(self):
        for good in ("neo", "bob-protocol", "a1", "x" * 64):
            self.assertTrue(_skill_layout.valid_name(good), good)
        for bad in ("", "-a", "a-", "a--b", "A", "a_b", "a/b", "..", "a.b", "x" * 65, "a b"):
            self.assertFalse(_skill_layout.valid_name(bad), repr(bad))


class InstallPlacesRealSkillsTests(unittest.TestCase):
    def test_every_persona_and_shared_skill_is_a_real_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            _install(target)
            skills = target / ".agents" / "skills"
            names = {p.name for p in skills.iterdir()}
            for persona in ("bob", "cypher", "morpheus", "mouse", "neo", "oracle", "smith", "switch", "tank", "trin"):
                self.assertIn(persona, names)
            for shared in ("sprint", "make", "chat", "security", "via"):
                self.assertIn(shared, names)
            for name in names:
                skill_md = skills / name / "SKILL.md"
                self.assertTrue(skill_md.is_file() and not skill_md.is_symlink(), name)
                self.assertFalse((skills / name).is_symlink(), name)
            self.assertEqual(_tree_symlinks(skills), [])

    def test_no_txt_leftovers_and_no_skill_sources_under_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            _install(target)
            self.assertEqual(list((target / ".claude").rglob("*.txt")), [])
            self.assertFalse((target / "agents" / "skills").exists())
            self.assertFalse(list((target / "agents").glob("*/SKILL.md")))

    def test_persona_memory_stays_out_of_the_skills_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            _install(target)
            self.assertTrue((target / "agents" / "neo" / "state.md").is_file())
            self.assertFalse((target / ".agents" / "skills" / "neo" / "state.md").exists())
            # The skill carries its own test cases (evals/evals.json) but none of the memory.
            self.assertEqual(
                sorted(p.name for p in (target / ".agents" / "skills" / "neo").iterdir()),
                ["SKILL.md", "evals"],
            )
            self.assertTrue((target / ".agents" / "skills" / "neo" / "evals" / "evals.json").is_file())
            self.assertFalse((target / "agents" / "neo" / "evals").exists())

    def test_manifest_lists_installed_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            _install(target)
            owned = _skill_layout.read_manifest(target / "agents")
            self.assertIn("neo", owned)
            self.assertIn("sprint", owned)


class UpdateTests(unittest.TestCase):
    def test_update_refreshes_owned_skills_and_keeps_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            _install(target)
            skill = target / ".agents" / "skills" / "neo" / "SKILL.md"
            skill.write_text("stale\n")
            state = target / "agents" / "neo" / "state.md"
            state.write_text("real work\n")
            _update(target)
            self.assertNotEqual(skill.read_text(), "stale\n")
            self.assertEqual(state.read_text(), "real work\n")

    def test_unowned_existing_skill_is_left_alone_and_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            own = target / ".agents" / "skills" / "make"
            own.mkdir(parents=True)
            (own / "SKILL.md").write_text("my own make skill\n")
            _install(target)
            self.assertEqual((own / "SKILL.md").read_text(), "my own make skill\n")
            self.assertNotIn("make", _skill_layout.read_manifest(target / "agents"))
            _update(target)
            self.assertEqual((own / "SKILL.md").read_text(), "my own make skill\n")

    def test_skip_is_reported_in_the_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "agents").mkdir()
            own = target / ".agents" / "skills" / "make"
            own.mkdir(parents=True)
            actions = _skill_layout.place_skills(target, _bob_manage.templates_dir())
            skipped = [a for a in actions if a.kind == "skipped"]
            self.assertEqual([a.path for a in skipped], [".agents/skills/make"])
            self.assertIn("not installed by bobp", skipped[0].note)

    def test_legacy_bobp_symlink_is_replaced_by_a_real_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "agents" / "skills" / "make").mkdir(parents=True)
            (target / "agents" / "skills" / "make" / "SKILL.md").write_text("old\n")
            skills = target / ".agents" / "skills"
            skills.mkdir(parents=True)
            os.symlink("../../agents/skills/make", skills / "make")
            _skill_layout.place_skills(target, _bob_manage.templates_dir())
            self.assertFalse((skills / "make").is_symlink())
            self.assertTrue((skills / "make" / "SKILL.md").is_file())
            self.assertEqual((target / "agents" / "skills" / "make" / "SKILL.md").read_text(), "old\n")

    def test_symlink_pointing_elsewhere_is_not_touched(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "proj"
            elsewhere = Path(tmp) / "elsewhere"
            elsewhere.mkdir()
            (elsewhere / "SKILL.md").write_text("someone else's\n")
            (target / "agents").mkdir(parents=True)
            skills = target / ".agents" / "skills"
            skills.mkdir(parents=True)
            os.symlink(elsewhere, skills / "make")
            actions = _skill_layout.place_skills(target, _bob_manage.templates_dir())
            self.assertTrue((skills / "make").is_symlink())
            self.assertEqual((elsewhere / "SKILL.md").read_text(), "someone else's\n")
            self.assertTrue(any(a.kind == "skipped" and a.path.endswith("make") for a in actions))

    def test_second_update_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            _install(target)
            before = sorted(str(p.relative_to(target)) for p in target.rglob("*"))
            _update(target)
            after = sorted(str(p.relative_to(target)) for p in target.rglob("*"))
            self.assertEqual(before, after)


class SafetyTests(unittest.TestCase):
    def test_symlinked_claude_dir_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "proj"
            outside = Path(tmp) / "outside"
            (target / "agents").mkdir(parents=True)
            outside.mkdir()
            os.symlink(outside, target / ".agents")
            with self.assertRaises(SkillLayoutError):
                _skill_layout.place_skills(target, _bob_manage.templates_dir())
            self.assertEqual(list(outside.iterdir()), [])

    def test_symlinked_skills_dir_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "proj"
            outside = Path(tmp) / "outside"
            (target / "agents").mkdir(parents=True)
            (target / ".agents").mkdir()
            outside.mkdir()
            os.symlink(outside, target / ".agents" / "skills")
            with self.assertRaises(SkillLayoutError):
                _skill_layout.place_skills(target, _bob_manage.templates_dir())
            self.assertEqual(list(outside.iterdir()), [])

    def test_hostile_manifest_names_cannot_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "proj"
            victim = Path(tmp) / "victim"
            (target / "agents").mkdir(parents=True)
            victim.mkdir()
            (victim / "keep.txt").write_text("keep\n")
            (target / "agents" / ".bobp-skills").write_text("../../victim\n/etc\nneo\n..\n")
            self.assertEqual(_skill_layout.read_manifest(target / "agents"), {"neo"})
            _skill_layout.place_skills(target, _bob_manage.templates_dir())
            self.assertEqual((victim / "keep.txt").read_text(), "keep\n")

    def test_manifest_symlink_or_fifo_is_ignored_without_blocking(self):
        import signal

        with tempfile.TemporaryDirectory() as tmp:
            agents = Path(tmp) / "agents"
            agents.mkdir()
            manifest = agents / ".bobp-skills"
            os.symlink("/dev/stdin", manifest)

            def fail(*_):
                raise AssertionError("manifest read blocked")

            previous = signal.signal(signal.SIGALRM, fail)
            signal.alarm(5)
            try:
                self.assertEqual(_skill_layout.read_manifest(agents), set())
                manifest.unlink()
                os.mkfifo(manifest)
                self.assertEqual(_skill_layout.read_manifest(agents), set())
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, previous)

    def test_planted_symlinks_at_write_targets_are_not_followed(self):
        """SEC-006: a cloned repo must not make install/update overwrite files elsewhere."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "proj"
            victims = Path(tmp) / "victims"
            victims.mkdir()
            target.mkdir()
            _install(target)
            stamp_victim = victims / "stamp"
            tmp_victim = victims / "tmp"
            manifest_victim = victims / "manifest"
            for victim in (stamp_victim, tmp_victim, manifest_victim):
                victim.write_text("original\n")
            agents = target / "agents"
            (agents / ".bobp-version").unlink()
            os.symlink(stamp_victim, agents / ".bobp-version")
            os.symlink(tmp_victim, agents / "..bobp-skills.tmp")
            (agents / ".bobp-skills").unlink()
            os.symlink(manifest_victim, agents / ".bobp-skills")

            _update(target)

            for victim in (stamp_victim, tmp_victim, manifest_victim):
                self.assertEqual(victim.read_text(), "original\n", victim.name)
            self.assertFalse((agents / ".bobp-version").is_symlink())
            self.assertFalse((agents / ".bobp-skills").is_symlink())
            self.assertTrue((agents / ".bobp-skills").is_file())
            # With the manifest unreadable bobp cannot prove it owns the skills already
            # there, so it leaves them (reported as skipped) rather than overwrite them.
            self.assertTrue((target / ".agents" / "skills" / "neo" / "SKILL.md").is_file())

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "agents").mkdir()
            actions = _skill_layout.place_skills(target, _bob_manage.templates_dir(), dry_run=True)
            self.assertTrue(any(a.kind == "create" for a in actions))
            self.assertFalse((target / ".claude").exists())
            self.assertFalse((target / "agents" / ".bobp-skills").exists())


if __name__ == "__main__":
    unittest.main()
