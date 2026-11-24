"""Phase 4 of sprint 3: rewrite references to the old skill locations."""

import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from bobp.tools import _bob_manage, _path_rewrite, _skill_layout

PERSONAS = _path_rewrite.PERSONAS


def rewrite(
    text: str, personas=PERSONAS, root_agents_md: bool = False, in_skill: bool = False
) -> str:
    return _path_rewrite.rewrite_text(text, personas, root_agents_md, in_skill)


class RewriteRuleTests(unittest.TestCase):
    def test_shared_skill_paths(self):
        self.assertEqual(
            rewrite("See `agents/skills/chat/SKILL.md` and agents/skills."),
            "See `.agents/skills/chat/SKILL.md` and .agents/skills.",
        )

    def test_persona_skill_paths_and_placeholders(self):
        for old, new in (
            ("agents/neo/SKILL.md", ".agents/skills/neo/SKILL.md"),
            ("agents/[persona]/SKILL.md", ".agents/skills/[persona]/SKILL.md"),
            ("agents/<name>/SKILL.md", ".agents/skills/<name>/SKILL.md"),
            ("agents/{persona}/SKILL.md", ".agents/skills/{persona}/SKILL.md"),
            ("agents/*/SKILL.md", ".agents/skills/*/SKILL.md"),
        ):
            with self.subTest(old=old):
                self.assertEqual(rewrite(f"Load {old} now."), f"Load {new} now.")

    def test_markdown_links_and_code_spans(self):
        self.assertEqual(
            rewrite("[`agents/bob/SKILL.md`](agents/bob/SKILL.md)"),
            "[`.agents/skills/bob/SKILL.md`](.agents/skills/bob/SKILL.md)",
        )

    def test_agents_md_moves_to_the_root(self):
        self.assertEqual(rewrite("Read agents/AGENTS.md first."), "Read AGENTS.md first.")

    def test_things_that_must_not_change(self):
        for text in (
            ".agents/skills/bob/SKILL.md",  # the evaluator's own fixture path
            "myagents/skills/x",
            "agents/skills-extra/x",
            "agents/oracle/lessons.md",
            "agents/neo/state.md",
            "docs/agents/skills/x",
            "~/.agents/skills",
            ".agents/skills/neo/SKILL.md",
        ):
            with self.subTest(text=text):
                self.assertEqual(rewrite(text), text)

    def test_a_project_persona_is_rewritten_only_when_named(self):
        self.assertEqual(rewrite("agents/foo/SKILL.md"), "agents/foo/SKILL.md")
        self.assertEqual(
            rewrite("agents/foo/SKILL.md", personas=(*PERSONAS, "foo")),
            ".agents/skills/foo/SKILL.md",
        )

    def test_persona_names_are_matched_literally(self):
        self.assertEqual(
            rewrite("agents/a.b/SKILL.md agents/axb/SKILL.md", personas=("a.b",)),
            ".agents/skills/a.b/SKILL.md agents/axb/SKILL.md",
        )

    def test_relative_docs_links_in_the_root_instructions_lose_their_dotdot(self):
        text = "[`docs/SDLC.md`](../docs/SDLC.md)"
        self.assertEqual(rewrite(text, root_agents_md=True), "[`docs/SDLC.md`](docs/SDLC.md)")
        self.assertEqual(rewrite(text), text)

    def test_links_between_skills_follow_the_new_siblings_layout(self):
        """A persona used to link a shared skill as ../skills/x; both now sit in .agents/skills/."""
        for old, new in (
            ("[Bob Protocol](../skills/bob-protocol/SKILL.md)", "[Bob Protocol](../bob-protocol/SKILL.md)"),
            ("link `../skills/<skill>/SKILL.md` here", "link `../<skill>/SKILL.md` here"),
        ):
            with self.subTest(old=old):
                self.assertEqual(rewrite(old, in_skill=True), new)

    def test_links_from_a_skill_up_to_the_artifact_templates_climb_out_of_claude_skills(self):
        target = "../../../agents/templates/_template_X.md"
        for old in ("../templates/_template_X.md", "../../templates/_template_X.md"):
            with self.subTest(old=old):
                self.assertEqual(rewrite(f"[t]({old})", in_skill=True), f"[t]({target})")

    def test_sibling_skill_links_and_non_skill_files_are_left_alone(self):
        sibling = "[make](../make/SKILL.md)"
        self.assertEqual(rewrite(sibling, in_skill=True), sibling)
        outside = "[x](../skills/x/SKILL.md) [t](../templates/t.md)"
        self.assertEqual(rewrite(outside, in_skill=False), outside)

    def test_skill_link_rules_are_idempotent(self):
        once = rewrite("[a](../skills/x/SKILL.md) [t](../templates/t.md)", in_skill=True)
        self.assertEqual(rewrite(once, in_skill=True), once)

    def test_idempotent(self):
        once = rewrite("agents/skills/x/SKILL.md agents/neo/SKILL.md agents/AGENTS.md")
        self.assertEqual(rewrite(once), once)


class FileWalkTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _write(self, rel: str, text: str = "agents/skills/x\n") -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_rewrites_text_files_and_reports_only_changed_ones(self):
        changed = self._write("a.md")
        same = self._write("b.md", "nothing to do\n")
        result = _path_rewrite.rewrite_files([changed, same], PERSONAS)
        self.assertEqual(result, [changed])
        self.assertEqual(changed.read_text(), ".agents/skills/x\n")
        self.assertEqual(same.read_text(), "nothing to do\n")

    def test_only_documentation_suffixes_are_touched(self):
        for name in ("c.json", "c.py", "c.sh"):
            self._write(name)
        files = [p for p in self.root.iterdir()]
        self.assertEqual(_path_rewrite.rewrite_files(files, PERSONAS), [])
        self.assertEqual((self.root / "c.py").read_text(), "agents/skills/x\n")

    def test_skill_files_get_the_skill_link_rules_and_others_do_not(self):
        skill = self._write("neo/SKILL.md", "[a](../skills/x/SKILL.md)\n")
        packaged = self._write("neo/SKILL.md.txt", "[a](../skills/x/SKILL.md)\n")
        persona_template = self._write(
            "templates/_template_PERSONA_SKILL.md", "[a](../skills/x/SKILL.md)\n"
        )
        other = self._write("neo/HELP.md", "[a](../skills/x/SKILL.md)\n")
        _path_rewrite.rewrite_files([skill, packaged, persona_template, other], PERSONAS)
        for path in (skill, packaged, persona_template):
            self.assertEqual(path.read_text(), "[a](../x/SKILL.md)\n", path.name)
        self.assertEqual(other.read_text(), "[a](../skills/x/SKILL.md)\n")

    def test_md_txt_and_template_suffixes_are_touched(self):
        for name in ("d.md", "SKILL.md.txt", "e.template"):
            self._write(name)
        changed = _path_rewrite.rewrite_files(sorted(self.root.iterdir()), PERSONAS)
        self.assertEqual(len(changed), 3)

    def test_dry_run_writes_nothing(self):
        path = self._write("a.md")
        self.assertEqual(_path_rewrite.rewrite_files([path], PERSONAS, dry_run=True), [path])
        self.assertEqual(path.read_text(), "agents/skills/x\n")

    def test_symlinks_are_neither_followed_nor_written_through(self):
        victim = self._write("victim.json")
        link = self.root / "link.md"
        link.symlink_to(victim)
        self.assertEqual(_path_rewrite.rewrite_files([link], PERSONAS), [])
        self.assertEqual(victim.read_text(), "agents/skills/x\n")
        self.assertTrue(link.is_symlink())

    def test_oversized_and_binary_files_are_skipped(self):
        big = self._write("big.md", "agents/skills/x\n" + "x" * _path_rewrite.MAX_FILE_BYTES)
        binary = self.root / "bin.md"
        binary.write_bytes(b"\xff\xfe\x00agents/skills/x")
        self.assertEqual(_path_rewrite.rewrite_files([big, binary], PERSONAS), [])

    def test_walk_skips_history_and_tooling_directories_and_symlinks(self):
        keep = self._write("agents/templates/t.md")
        for rel in (
            ".git/x.md", "node_modules/x.md", "build/x.md", "agents/chat_archive/x.md",
            ".venv/x.md", "agents/CHAT.md", "agents/CHAT.diagram.md",
        ):
            self._write(rel)
        (self.root / "agents" / "linked").symlink_to(self.root / "agents" / "templates")
        walked = list(_path_rewrite.walk(self.root / "agents"))
        self.assertEqual(walked, [keep])


class ProjectScopeTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _write(self, rel: str, text: str = "agents/skills/x agents/neo/SKILL.md\n") -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_scope_is_the_instruction_files_and_templates_not_history(self):
        targets = {
            self._write("AGENTS.md"),
            self._write("agents/templates/_template_x.md"),
            self._write("agents/PROJECT.md"),
            self._write("agents/DOCUMENTATION_INDEX.md"),
            self._write("agents/bob/HELP.md"),
        }
        untouched = [
            self._write("agents/neo/state.md"),
            self._write("agents/oracle/lessons.md"),
            self._write("agents/switch/findings/f.md"),
            self._write("docs/sprints/USER_STORIES_SPRINT3.md"),
            self._write("docs/LESSONS.md"),
            self._write("README.md"),
        ]
        found = set(_path_rewrite.project_targets(self.root, owned=set()))
        self.assertEqual(found, targets)
        for path in untouched:
            self.assertNotIn(path, found)

    def test_only_skills_the_project_owns_itself_are_in_scope(self):
        mine = self._write(".agents/skills/mine/SKILL.md")
        ours = self._write(".agents/skills/make/SKILL.md")
        found = set(_path_rewrite.project_targets(self.root, owned={"make"}))
        self.assertIn(mine, found)
        self.assertNotIn(ours, found)

    def test_symlinked_root_agents_md_is_not_a_target(self):
        real = self._write("elsewhere.md")
        (self.root / "AGENTS.md").symlink_to(real)
        self.assertNotIn(self.root / "AGENTS.md", _path_rewrite.project_targets(self.root, set()))


class PackagedTemplatesTests(unittest.TestCase):
    def test_no_packaged_file_cites_the_old_layout(self):
        templates = Path(_bob_manage.templates_dir())
        offenders = []
        for path in _path_rewrite.walk(templates):
            if _path_rewrite.rewrite_text(
                path.read_text(encoding="utf-8"),
                PERSONAS,
                root_agents_md=path.name == "AGENTS.md",
                in_skill=path.name in _path_rewrite.SKILL_FILE_NAMES,
            ) != path.read_text(encoding="utf-8"):
                offenders.append(str(path.relative_to(templates)))
        self.assertEqual(offenders, [])


def _update(target: Path) -> str:
    out = StringIO()
    with patch.object(_bob_manage, "_run_setup_agent_links"), redirect_stdout(out):
        _bob_manage.update(target)
    return out.getvalue()


class UpdateIntegrationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def test_update_rewrites_the_root_instructions_and_reports_it(self):
        (self.root / "agents").mkdir()
        (self.root / "agents" / "AGENTS.md").write_text(
            "Read agents/skills/chat/SKILL.md and [SDLC](../docs/SDLC.md)\n"
        )
        os.symlink("agents/AGENTS.md", self.root / "AGENTS.md")
        output = _update(self.root)
        self.assertEqual(
            (self.root / "AGENTS.md").read_text(),
            "Read .agents/skills/chat/SKILL.md and [SDLC](docs/SDLC.md)\n",
        )
        self.assertIn("path reference", output)

    def test_history_is_left_alone_by_update(self):
        (self.root / "agents" / "neo").mkdir(parents=True)
        (self.root / "agents" / "neo" / "state.md").write_text("see agents/skills/chat\n")
        (self.root / "docs" / "sprints").mkdir(parents=True)
        (self.root / "docs" / "sprints" / "s.md").write_text("agents/skills/chat\n")
        _update(self.root)
        self.assertEqual((self.root / "agents" / "neo" / "state.md").read_text(), "see agents/skills/chat\n")
        self.assertEqual((self.root / "docs" / "sprints" / "s.md").read_text(), "agents/skills/chat\n")

    def test_second_update_reports_no_rewrites(self):
        (self.root / "agents").mkdir()
        (self.root / "AGENTS.md").write_text("agents/skills/x\n")
        _update(self.root)
        self.assertNotIn("path reference", _update(self.root))


class GitignoreNoteTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def test_detects_a_gitignore_that_hides_the_whole_agents_directory(self):
        for line in (".agents", ".agents/", "/.agents", "/.agents/", ".agents/*"):
            with self.subTest(line=line):
                (self.root / ".gitignore").write_text(f"build/\n{line}\n")
                self.assertTrue(_skill_layout.gitignore_hides_skills(self.root))

    def test_does_not_flag_narrower_or_absent_rules(self):
        self.assertFalse(_skill_layout.gitignore_hides_skills(self.root))
        (self.root / ".gitignore").write_text(".claude/settings.local.json\n.claude.json\n# .claude\n")
        self.assertFalse(_skill_layout.gitignore_hides_skills(self.root))

    def test_update_prints_the_note(self):
        (self.root / ".gitignore").write_text(".agents\n")
        (self.root / "agents").mkdir()
        self.assertIn(".gitignore", _update(self.root))
        self.assertIn(".agents", _update(self.root))


if __name__ == "__main__":
    unittest.main()
