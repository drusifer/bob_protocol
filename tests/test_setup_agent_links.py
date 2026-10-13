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


if __name__ == "__main__":
    unittest.main()
