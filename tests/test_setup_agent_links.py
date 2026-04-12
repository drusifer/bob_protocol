import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from agents.tools import setup_agent_links


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


if __name__ == "__main__":
    unittest.main()
