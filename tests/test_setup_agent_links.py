import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from bobp.tools import setup_agent_links


class SetupAgentLinksTests(unittest.TestCase):
    def test_ensure_via_index_runs_index_when_database_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)

            with (
                patch.object(setup_agent_links.shutil, "which", return_value="/bin/via"),
                patch.object(setup_agent_links.subprocess, "run") as run,
            ):
                run.return_value = Mock(returncode=0, stdout="indexed", stderr="")

                ok = setup_agent_links.ensure_via_index(project_root)

        self.assertTrue(ok)
        run.assert_called_once_with(
            ["/bin/via", "index", str(project_root)],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

    def test_ensure_via_index_skips_when_database_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            index_db = project_root / ".via" / "index.db"
            index_db.parent.mkdir()
            index_db.touch()

            with patch.object(setup_agent_links.subprocess, "run") as run:
                ok = setup_agent_links.ensure_via_index(project_root)

        self.assertTrue(ok)
        run.assert_not_called()

    def test_install_codex_via_mcp_sets_project_home_and_disables_web(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)

            with (
                patch.object(
                    setup_agent_links.shutil,
                    "which",
                    side_effect=lambda name: f"/bin/{name}",
                ),
                patch.object(setup_agent_links.subprocess, "run") as run,
            ):
                run.side_effect = [
                    Mock(returncode=1, stdout="", stderr="not found"),
                    Mock(returncode=0, stdout="added", stderr=""),
                ]

                ok = setup_agent_links.install_codex_via_mcp(project_root)

        self.assertTrue(ok)
        run.assert_any_call(
            [
                "/bin/codex",
                "mcp",
                "add",
                "via",
                "--env",
                f"HOME={project_root}",
                "--",
                "/bin/via",
                "mcp",
                "serve",
                "--no-web",
                str(project_root),
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

    def test_configure_project_via_mcp_sets_project_home_and_disables_web(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            mcp_json = project_root / ".mcp.json"
            mcp_json.write_text(
                json.dumps(
                    {
                        "mcpServers": {
                            "via": {
                                "command": "/bin/python",
                                "args": ["-m", "via", "mcp", "serve", str(project_root)],
                            }
                        }
                    }
                )
            )

            ok = setup_agent_links.configure_project_via_mcp(project_root)

            data = json.loads(mcp_json.read_text())

        self.assertTrue(ok)
        via_entry = data["mcpServers"]["via"]
        self.assertEqual(via_entry["env"], {"HOME": str(project_root)})
        self.assertEqual(
            via_entry["args"],
            ["-m", "via", "mcp", "serve", "--no-web", str(project_root)],
        )

    def test_setup_root_symlinks_creates_agent_md_and_agents_md_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            agents_dir = project_root / "agents"
            agents_dir.mkdir()
            agents_md = agents_dir / "AGENTS.md"
            agents_md.write_text("# Master Agent Instructions\n")

            setup_agent_links.setup_root_symlinks(project_root, agents_dir)

            root_agents_link = project_root / "AGENTS.md"
            root_agent_link = project_root / "AGENT.md"
            agents_agent_link = agents_dir / "AGENT.md"

            self.assertTrue(root_agents_link.is_symlink())
            self.assertTrue(root_agent_link.is_symlink())
            self.assertTrue(agents_agent_link.is_symlink())

            self.assertEqual(root_agents_link.resolve(), agents_md.resolve())
            self.assertEqual(root_agent_link.resolve(), agents_md.resolve())
            self.assertEqual(agents_agent_link.resolve(), agents_md.resolve())

    def test_find_persona_dirs_finds_agent_folders_with_a_skill_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents_dir = Path(tmp) / "agents"
            for folder in ("neo", "trin", "templates", "skills/chat"):
                (agents_dir / folder).mkdir(parents=True)
            for folder in ("neo", "trin", "skills/chat"):
                (agents_dir / folder / "SKILL.md").write_text("---\nname: x\n---\n")

            personas = setup_agent_links.find_persona_dirs(agents_dir)

        self.assertEqual(personas, [("neo", agents_dir / "neo"), ("trin", agents_dir / "trin")])

    def test_setup_claude_skills_replaces_a_skills_dir_link_into_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            agents_dir = project_root / "agents"
            for folder in ("neo", "skills/chat"):
                (agents_dir / folder).mkdir(parents=True)
                (agents_dir / folder / "SKILL.md").write_text("---\nname: x\n---\n")
            (project_root / ".claude").mkdir()
            skills_link = project_root / ".claude" / "skills"
            skills_link.symlink_to("../agents/skills")

            count = setup_agent_links.setup_claude_skills(
                project_root,
                setup_agent_links.find_persona_dirs(agents_dir),
                setup_agent_links.find_shared_skills(agents_dir),
            )

            self.assertEqual(count, 2)
            self.assertFalse(skills_link.is_symlink())
            self.assertEqual((skills_link / "neo").resolve(), (agents_dir / "neo").resolve())
            self.assertEqual(
                (skills_link / "chat").resolve(), (agents_dir / "skills" / "chat").resolve()
            )
            # nothing was written into the agents/ tree itself
            self.assertEqual([p.name for p in (agents_dir / "skills").iterdir()], ["chat"])

    def _make_persona(self, agents_dir: Path, folder: str, skill: str = "---\nname: x\n---\n") -> Path:
        persona = agents_dir / folder
        persona.mkdir(parents=True)
        (persona / "SKILL.md").write_text(skill)
        return persona

    def test_migrate_legacy_layout_renames_folders_and_rewrites_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents_dir = Path(tmp) / "agents"
            neo = self._make_persona(agents_dir, "neo.docs")
            (neo / "state.md").write_text("see agents/neo.docs/notes.md\n")
            doc = agents_dir / "AGENTS.md"
            doc.write_text(
                "Load `agents/[persona].docs/state.md` and `agents/neo.docs/SKILL.md`.\n"
                "See agents/*.docs/ and their `.docs/` folder; export to google.docs too.\n"
            )
            chat = agents_dir / "CHAT.md"
            chat.write_text("wrote agents/neo.docs/summary.md\n")

            migrated = setup_agent_links.migrate_legacy_layout(agents_dir)

            self.assertEqual(migrated, ["neo"])
            self.assertFalse((agents_dir / "neo.docs").exists())
            self.assertEqual(
                (agents_dir / "neo" / "state.md").read_text(), "see agents/neo/notes.md\n"
            )
            self.assertEqual(
                doc.read_text(),
                "Load `agents/[persona]/state.md` and `agents/neo/SKILL.md`.\n"
                "See agents/*/ and their `<name>/` folder; export to google.docs too.\n",
            )
            # chat logs are history and keep the old paths
            self.assertEqual(chat.read_text(), "wrote agents/neo.docs/summary.md\n")
            # already-converted project: nothing to do
            self.assertEqual(setup_agent_links.migrate_legacy_layout(agents_dir), [])

    def _make_tools(self, agents_dir: Path, *names: str) -> Path:
        tools_dir = agents_dir / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        for name in names:
            (tools_dir / name).write_text("# stale copy\n")
        return tools_dir

    def test_remove_legacy_tools_deletes_superseded_scripts_and_empty_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents_dir = Path(tmp) / "agents"
            tools_dir = self._make_tools(agents_dir, *setup_agent_links.LEGACY_TOOL_SCRIPTS)
            (tools_dir / "__pycache__").mkdir()
            (tools_dir / "__pycache__" / "chat.cpython-313.pyc").write_bytes(b"x")

            removed = setup_agent_links.remove_legacy_tools(agents_dir)

            self.assertEqual(removed, sorted(setup_agent_links.LEGACY_TOOL_SCRIPTS))
            self.assertFalse(tools_dir.exists())

    def test_remove_legacy_tools_keeps_project_tools_and_trace_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents_dir = Path(tmp) / "agents"
            tools_dir = self._make_tools(
                agents_dir, "chat.py", "mkf.py", "trace_rules.json", "my_project_tool.py")
            (tools_dir / "__pycache__").mkdir()

            removed = setup_agent_links.remove_legacy_tools(agents_dir)

            self.assertEqual(removed, ["chat.py", "mkf.py"])
            self.assertEqual(
                sorted(p.name for p in tools_dir.iterdir()),
                ["my_project_tool.py", "trace_rules.json"],
            )

    def test_remove_legacy_tools_is_a_no_op_when_nothing_to_remove(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents_dir = Path(tmp) / "agents"
            agents_dir.mkdir()
            self.assertEqual(setup_agent_links.remove_legacy_tools(agents_dir), [])

            tools_dir = self._make_tools(agents_dir, "trace_rules.json", "my_project_tool.py")
            (tools_dir / "__pycache__").mkdir()
            self.assertEqual(setup_agent_links.remove_legacy_tools(agents_dir), [])
            # untouched, including the cache of the project's own tool
            self.assertEqual(
                sorted(p.name for p in tools_dir.iterdir()),
                ["__pycache__", "my_project_tool.py", "trace_rules.json"],
            )

            # second run after a real removal is also quiet
            self._make_tools(agents_dir, "tldr.py")
            self.assertEqual(setup_agent_links.remove_legacy_tools(agents_dir), ["tldr.py"])
            self.assertEqual(setup_agent_links.remove_legacy_tools(agents_dir), [])

    def test_every_legacy_script_has_a_real_bobp_subcommand(self) -> None:
        from bobp.cli import SUBCOMMANDS

        for script, command in setup_agent_links.LEGACY_TOOL_SCRIPTS.items():
            with self.subTest(script=script):
                self.assertTrue(command.startswith("bobp "))
                self.assertIn(command.removeprefix("bobp "), SUBCOMMANDS)

    def test_migrate_persona_folders_merges_without_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agents_dir = Path(tmp) / "agents"
            self._make_persona(agents_dir, "neo", skill="current\n")
            legacy = self._make_persona(agents_dir, "neo.docs", skill="legacy\n")
            (legacy / "notes.md").write_text("only in legacy\n")

            setup_agent_links.migrate_persona_folders(agents_dir)

            self.assertEqual((agents_dir / "neo" / "SKILL.md").read_text(), "current\n")
            self.assertEqual((agents_dir / "neo" / "notes.md").read_text(), "only in legacy\n")
            # the conflicting SKILL.md is kept for a manual merge, not deleted
            self.assertEqual((legacy / "SKILL.md").read_text(), "legacy\n")


if __name__ == "__main__":
    unittest.main()



class ChatExitStatusTests(unittest.TestCase):
    def test_over_length_chat_message_exits_non_zero_and_is_not_recorded(self) -> None:
        import subprocess
        import sys

        with tempfile.TemporaryDirectory() as tmp:
            agents = Path(tmp) / "agents"
            agents.mkdir()
            (agents / "CHAT.md").write_text("# Chat\n\n---\n")
            result = subprocess.run(
                [sys.executable, "-m", "bobp.cli", "chat", "x" * 600, "--persona", "T", "--cmd", "t"],
                cwd=tmp, capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exceeds 512", result.stdout + result.stderr)
            self.assertNotIn("x" * 600, (agents / "CHAT.md").read_text())
