"""Phase 1 of sprint 2: `bobp --version` and the agents/.bobp-version stamp."""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import bobp
from bobp import cli
from bobp.tools import _bob_manage


def _install(target: Path) -> None:
    with patch.object(_bob_manage, "_run_setup_agent_links"):
        _bob_manage.install(target)


def _update(target: Path) -> None:
    with patch.object(_bob_manage, "_run_setup_agent_links"):
        _bob_manage.update(target)


def _run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = cli.main(argv)
    return code, out.getvalue(), err.getvalue()


class VersionFlagTests(unittest.TestCase):
    def test_long_flag_prints_one_line_and_exits_zero(self):
        code, out, _ = _run_cli(["--version"])
        self.assertEqual(code, 0)
        self.assertEqual(out, f"bobp {bobp.__version__}\n")

    def test_short_flag_matches_long_flag(self):
        self.assertEqual(_run_cli(["-V"]), _run_cli(["--version"]))

    def test_version_is_the_package_version(self):
        with patch.object(bobp, "__version__", "9.8.7"):
            _, out, _ = _run_cli(["--version"])
        self.assertEqual(out, "bobp 9.8.7\n")

    def test_help_lists_the_flag(self):
        _, out, _ = _run_cli(["--help"])
        self.assertIn("--version", out)

    def test_version_works_outside_a_project_and_touches_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("pathlib.Path.cwd", return_value=Path(tmp)):
                code, out, err = _run_cli(["--version"])
            self.assertEqual(code, 0)
            self.assertEqual(err, "")
            self.assertEqual(list(Path(tmp).iterdir()), [])


class StampTests(unittest.TestCase):
    def test_install_writes_one_line_stamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            _install(target)
            stamp = target / "agents" / ".bobp-version"
            self.assertEqual(stamp.read_text(), f"{bobp.__version__}\n")

    def test_update_creates_missing_stamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            _install(target)
            stamp = target / "agents" / ".bobp-version"
            stamp.unlink()
            _update(target)
            self.assertEqual(stamp.read_text(), f"{bobp.__version__}\n")

    def test_update_overwrites_an_older_stamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            _install(target)
            stamp = target / "agents" / ".bobp-version"
            stamp.write_text("0.0.1\n")
            _update(target)
            self.assertEqual(stamp.read_text(), f"{bobp.__version__}\n")

    def test_update_still_preserves_state_and_chat(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            _install(target)
            state = target / "agents" / "neo" / "state.md"
            state.write_text("real work\n")
            chat = target / "agents" / "CHAT.md"
            chat.write_text("real chat\n")
            _update(target)
            self.assertEqual(state.read_text(), "real work\n")
            self.assertEqual(chat.read_text(), "real chat\n")

    def test_refused_install_leaves_stamp_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "agents").mkdir()
            stamp = target / "agents" / ".bobp-version"
            stamp.write_text("0.0.1\n")
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                _install(target)
            self.assertEqual(stamp.read_text(), "0.0.1\n")

    def test_failed_update_leaves_stamp_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            _install(target)
            stamp = target / "agents" / ".bobp-version"
            stamp.write_text("0.0.1\n")
            with patch.object(_bob_manage, "_regen_chat_diagram", side_effect=RuntimeError("boom")):
                with self.assertRaises(RuntimeError):
                    _update(target)
            self.assertEqual(stamp.read_text(), "0.0.1\n")


if __name__ == "__main__":
    unittest.main()
