"""Phase 7 tests: agent-safe subcommands (--help side-effect free, --dry-run, clean --yes, exit codes).

Traces: STORY-SKL-6 AC1–6, ADR-S3-7.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bobp import cli
from bobp.tools import _bob_manage


def _snapshot(root: Path) -> dict[str, tuple[int, int]]:
    """Map relative paths under root to (mode, mtime_ns) for side-effect detection."""
    snap: dict[str, tuple[int, int]] = {}
    if not root.exists():
        return snap
    for p in sorted(root.rglob("*")):
        try:
            st = p.lstat()
            snap[str(p.relative_to(root))] = (st.st_mode, st.st_mtime_ns)
        except OSError:
            pass
    return snap


class CliHelpSafetyTests(unittest.TestCase):
    def test_every_subcommand_help_exits_zero_has_exit_codes_and_zero_side_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            proj = base / "project"
            home = base / "home"
            codex_home = base / "codex_home"
            for d in (proj, home, codex_home):
                d.mkdir()
            # Give project a minimal agents/ dir and Makefile so subcommands that check project root run realistically
            (proj / "agents").mkdir()
            (proj / "agents" / "CHAT.md").write_text("# Chat\n")
            (proj / "Makefile").write_text("help:\n\t@echo project-makefile-help\n")

            env = {
                **os.environ,
                "HOME": str(home),
                "CODEX_HOME": str(codex_home),
                "BOBP_NO_VERSION_CHECK": "1",
            }

            proj_before = _snapshot(proj)
            home_before = _snapshot(home)
            codex_before = _snapshot(codex_home)

            for subcmd in sorted(cli.SUBCOMMANDS):
                for flag in ("--help", "-h"):
                    with self.subTest(subcommand=subcmd, flag=flag):
                        res = subprocess.run(
                            [sys.executable, "-m", "bobp.cli", subcmd, flag],
                            cwd=proj,
                            env=env,
                            capture_output=True,
                            text=True,
                        )
                        self.assertEqual(
                            res.returncode,
                            0,
                            f"{subcmd} {flag} failed (rc={res.returncode}): {res.stderr}",
                        )
                        combined = res.stdout + res.stderr
                        self.assertIn("usage:", combined.lower(), f"{subcmd} {flag} missing usage")
                        self.assertIn("Exit codes:", combined, f"{subcmd} {flag} missing exit codes")
                        self.assertEqual(_snapshot(proj), proj_before, f"{subcmd} {flag} mutated project")
                        self.assertEqual(_snapshot(home), home_before, f"{subcmd} {flag} mutated HOME")
                        self.assertEqual(
                            _snapshot(codex_home), codex_before, f"{subcmd} {flag} mutated CODEX_HOME"
                        )

    def test_make_help_target_still_runs_project_makefile(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            (proj / "agents").mkdir()
            (proj / "agents" / "CHAT.md").write_text("# Chat\n")
            (proj / "Makefile").write_text("help:\n\t@echo PROJECT_MAKEFILE_HELP_OK\n")
            env = {**os.environ, "BOBP_NO_VERSION_CHECK": "1"}
            res = subprocess.run(
                [sys.executable, "-m", "bobp.cli", "make", "-vvv", "help"],
                cwd=proj,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("PROJECT_MAKEFILE_HELP_OK", res.stdout)

    def test_help_skips_version_check_notice_without_env_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            (proj / "agents").mkdir()
            (proj / "agents" / ".bobp-version").write_text("0.0.1\n")
            env = {k: v for k, v in os.environ.items() if k != "BOBP_NO_VERSION_CHECK"}
            res = subprocess.run(
                [sys.executable, "-m", "bobp.cli", "merge", "--help"],
                cwd=proj,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertEqual(res.stderr, "")


class DryRunAndCleanConfirmationTests(unittest.TestCase):
    def _install_project(self, target: Path) -> None:
        with patch.object(_bob_manage, "_run_setup_agent_links"):
            _bob_manage.install(target)

    def test_clean_without_yes_exits_2_and_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            self._install_project(proj)
            state_file = proj / "agents" / "neo" / "state.md"
            chat_file = proj / "agents" / "CHAT.md"
            state_file.write_text("KEEP THIS STATE\n")
            chat_file.write_text("KEEP THIS CHAT\n")

            env = {**os.environ, "BOBP_NO_VERSION_CHECK": "1"}
            res = subprocess.run(
                [sys.executable, "-m", "bobp.cli", "clean"],
                cwd=proj,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 2, res.stdout + res.stderr)
            self.assertIn("--yes", res.stdout + res.stderr)
            self.assertEqual(state_file.read_text(), "KEEP THIS STATE\n")
            self.assertEqual(chat_file.read_text(), "KEEP THIS CHAT\n")

    def test_clean_dry_run_exits_0_and_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            self._install_project(proj)
            state_file = proj / "agents" / "neo" / "state.md"
            chat_file = proj / "agents" / "CHAT.md"
            state_file.write_text("KEEP THIS STATE\n")
            chat_file.write_text("KEEP THIS CHAT\n")

            env = {**os.environ, "BOBP_NO_VERSION_CHECK": "1"}
            res = subprocess.run(
                [sys.executable, "-m", "bobp.cli", "clean", "--dry-run"],
                cwd=proj,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("state.md", res.stdout)
            self.assertIn("CHAT.md", res.stdout)
            self.assertEqual(state_file.read_text(), "KEEP THIS STATE\n")
            self.assertEqual(chat_file.read_text(), "KEEP THIS CHAT\n")

    def test_clean_with_yes_resets_state_and_chat(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            self._install_project(proj)
            state_file = proj / "agents" / "neo" / "state.md"
            chat_file = proj / "agents" / "CHAT.md"
            state_file.write_text("OLD STATE\n")
            chat_file.write_text("OLD CHAT\n")

            env = {
                **os.environ,
                "HOME": str(proj / "_home"),
                "CODEX_HOME": str(proj / "_codex"),
                "BOBP_NO_VERSION_CHECK": "1",
            }
            res = subprocess.run(
                [sys.executable, "-m", "bobp.cli", "clean", "--yes"],
                cwd=proj,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("Not started", state_file.read_text())
            self.assertIn("Chat Log Format", chat_file.read_text())

    def test_update_dry_run_previews_and_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            self._install_project(proj)
            neo_skill = proj / ".agents" / "skills" / "neo" / "SKILL.md"
            neo_skill.write_text("stale neo skill\n")
            before = _snapshot(proj)

            env = {
                **os.environ,
                "HOME": str(proj / "_home"),
                "CODEX_HOME": str(proj / "_codex"),
                "BOBP_NO_VERSION_CHECK": "1",
            }
            res = subprocess.run(
                [sys.executable, "-m", "bobp.cli", "update", "--dry-run", str(proj)],
                cwd=proj,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("dry-run", (res.stdout + res.stderr).lower())
            self.assertEqual(neo_skill.read_text(), "stale neo skill\n")
            self.assertEqual(_snapshot(proj), before)

    def test_update_dry_run_handles_legacy_agents_symlink_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            (proj / "agents").mkdir()
            (proj / "agents" / "AGENTS.md").write_text("# Old\n")
            (proj / ".agents").symlink_to("agents")
            before = _snapshot(proj)

            env = {
                **os.environ,
                "HOME": str(proj / "_home"),
                "CODEX_HOME": str(proj / "_codex"),
                "BOBP_NO_VERSION_CHECK": "1",
            }
            res = subprocess.run(
                [sys.executable, "-m", "bobp.cli", "update", "--dry-run", str(proj)],
                cwd=proj,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue((proj / ".agents").is_symlink())
            self.assertEqual(_snapshot(proj), before)

    def test_pull_dry_run_previews_and_changes_nothing(self):
        with tempfile.TemporaryDirectory() as src_tmp, tempfile.TemporaryDirectory() as dst_tmp:
            src, dst = Path(src_tmp), Path(dst_tmp)
            self._install_project(src)
            self._install_project(dst)
            (src / ".agents" / "skills" / "neo" / "SKILL.md").write_text("updated peer text\n")
            before_text = (dst / ".agents" / "skills" / "neo" / "SKILL.md").read_text()
            before = _snapshot(dst)

            env = {**os.environ, "BOBP_NO_VERSION_CHECK": "1"}
            res = subprocess.run(
                [sys.executable, "-m", "bobp.cli", "pull", "--dry-run", str(src)],
                cwd=dst,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("neo/SKILL.md", res.stdout)
            self.assertEqual((dst / ".agents" / "skills" / "neo" / "SKILL.md").read_text(), before_text)
            self.assertEqual(_snapshot(dst), before)


if __name__ == "__main__":
    unittest.main()
