"""Phase 2 of sprint 2: the notify-only project version check."""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import bobp
from bobp import cli
from bobp.tools import _common, _version_check


def _project(root: Path, stamp: "str | bytes | None") -> Path:
    agents = root / "agents"
    agents.mkdir(parents=True)
    if isinstance(stamp, str):
        (agents / ".bobp-version").write_text(stamp)
    elif isinstance(stamp, bytes):
        (agents / ".bobp-version").write_bytes(stamp)
    return root


def _check(root: Path, sub: str = "chat", env=None, version: str = "1.2.0"):
    err = io.StringIO()
    with patch.object(bobp, "__version__", version):
        _version_check.check(sub, start=root, env=env if env is not None else {}, err=err)
    return err.getvalue()


class ParseVersionTests(unittest.TestCase):
    def test_parses_leading_integers(self):
        self.assertEqual(_version_check.parse_version("0.2.0"), (0, 2, 0))
        self.assertEqual(_version_check.parse_version(" v1.10 \n"), (1, 10))
        self.assertEqual(_version_check.parse_version("0.3.0rc1"), (0, 3, 0))

    def test_unreadable_values_are_none(self):
        for bad in ("", "   ", "abc", "-1.0", ".5", "\x1b[31m"):
            self.assertIsNone(_version_check.parse_version(bad), bad)

    def test_numeric_not_lexical_ordering(self):
        self.assertTrue(_version_check.is_older((0, 9, 0), (0, 10, 0)))
        self.assertFalse(_version_check.is_older((0, 10, 0), (0, 9, 0)))

    def test_missing_components_count_as_zero(self):
        self.assertFalse(_version_check.is_older((1, 2), (1, 2, 0)))
        self.assertFalse(_version_check.is_older((1, 2, 0), (1, 2)))
        self.assertTrue(_version_check.is_older((1, 2), (1, 2, 1)))


class NoticeDecisionTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "proj"
        self.addCleanup(self._tmp.cleanup)

    def test_older_stamp_prints_one_line_with_both_versions_and_command(self):
        _project(self.root, "1.0.0\n")
        out = _check(self.root)
        self.assertEqual(out.count("\n"), 1)
        self.assertIn("bobp 1.0.0", out)
        self.assertIn("installed is bobp 1.2.0", out)
        self.assertIn(f"bobp update {self.root}", out)

    def test_missing_stamp_says_none_recorded(self):
        _project(self.root, None)
        out = _check(self.root)
        self.assertEqual(out.count("\n"), 1)
        self.assertIn("unrecorded", out)
        self.assertIn("bobp update", out)

    def test_empty_garbage_and_non_utf8_count_as_unrecorded(self):
        for stamp in ("", "not a version\n", b"\xff\xfe\x00junk"):
            with self.subTest(stamp=stamp):
                shutil_root = self.root / str(abs(hash(stamp)))
                _project(shutil_root, stamp)
                self.assertIn("unrecorded", _check(shutil_root))

    def test_stamp_that_is_a_directory_counts_as_unrecorded(self):
        _project(self.root, None)
        (self.root / "agents" / ".bobp-version").mkdir()
        self.assertIn("unrecorded", _check(self.root))

    def test_equal_and_newer_stamps_are_silent(self):
        for stamp in ("1.2.0\n", "1.2\n", "1.3.0\n", "2.0.0\n"):
            with self.subTest(stamp=stamp):
                root = self.root / stamp.strip()
                _project(root, stamp)
                self.assertEqual(_check(root), "")

    def test_prerelease_suffix_is_ignored_in_comparison(self):
        _project(self.root, "1.2.0rc1\n")
        self.assertEqual(_check(self.root), "")

    def test_check_works_from_a_subdirectory(self):
        _project(self.root, "1.0.0\n")
        sub = self.root / "src" / "deep"
        sub.mkdir(parents=True)
        self.assertIn(f"bobp update {self.root}", _check(sub))

    def test_outside_a_project_is_silent(self):
        self.root.mkdir()
        # Guard against an agents/ directory in a parent of the temp dir.
        with patch.object(_version_check, "find_project_root_or_none", return_value=None):
            self.assertEqual(_check(self.root), "")


class SwitchesAndSkipTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = _project(Path(self._tmp.name) / "proj", "1.0.0\n")

    def test_install_and_update_never_trigger_the_check(self):
        for sub in ("install", "update"):
            self.assertEqual(_check(self.root, sub=sub), "")

    def test_env_switch_disables_the_check(self):
        for value in ("1", "true", "yes"):
            with self.subTest(value=value):
                self.assertEqual(_check(self.root, env={"BOBP_NO_VERSION_CHECK": value}), "")

    def test_env_switch_zero_or_empty_does_not_disable(self):
        for value in ("0", ""):
            with self.subTest(value=value):
                self.assertNotEqual(_check(self.root, env={"BOBP_NO_VERSION_CHECK": value}), "")


class SafetyTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name)

    def test_control_characters_in_stamp_are_stripped(self):
        root = _project(self.base / "p", "1.0.0\x1b[2J\x1b]0;pwned\x07\n")
        out = _check(root)
        self.assertNotIn("\x1b", out)
        self.assertNotIn("\x07", out)
        self.assertEqual(out.count("\n"), 1)

    def test_long_stamp_is_capped(self):
        root = _project(self.base / "p", "1.0.0" + "x" * 5000 + "\n")
        self.assertLess(len(_check(root)), 500)

    def test_path_with_spaces_and_metacharacters_is_shell_quoted(self):
        root = _project(self.base / "my proj; rm -rf $HOME", "1.0.0\n")
        out = _check(root)
        import shlex

        self.assertIn(shlex.quote(str(root)), out)

    def test_control_characters_in_path_are_stripped(self):
        root = _project(self.base / "ev\x1b[31mil", "1.0.0\n")
        out = _check(root)
        self.assertNotIn("\x1b", out)

    def test_never_reads_stdin(self):
        root = _project(self.base / "p", "1.0.0\n")

        class Boom:
            def read(self, *a):
                raise AssertionError("stdin read")

            readline = read

            def isatty(self):
                raise AssertionError("stdin probed")

        with patch("sys.stdin", Boom()):
            self.assertNotEqual(_check(root), "")

    def _no_hang(self, seconds: int = 5):
        import signal

        def fail(*_):
            raise AssertionError("version check blocked on the stamp (SEC-005)")

        previous = signal.signal(signal.SIGALRM, fail)
        signal.alarm(seconds)
        self.addCleanup(signal.signal, signal.SIGALRM, previous)
        self.addCleanup(signal.alarm, 0)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "needs POSIX FIFOs")
    def test_fifo_stamp_does_not_block_and_counts_as_unrecorded(self):
        root = _project(self.base / "p", None)
        os.mkfifo(root / "agents" / ".bobp-version")
        self._no_hang()
        self.assertIn("unrecorded", _check(root))

    @unittest.skipUnless(hasattr(os, "symlink") and os.path.exists("/dev/stdin"), "needs POSIX")
    def test_symlink_stamp_is_not_followed(self):
        root = _project(self.base / "p", None)
        os.symlink("/dev/stdin", root / "agents" / ".bobp-version")
        self._no_hang()
        self.assertIn("unrecorded", _check(root))

    @unittest.skipUnless(hasattr(os, "symlink"), "needs symlinks")
    def test_symlink_to_a_real_current_stamp_is_still_not_trusted(self):
        root = _project(self.base / "p", None)
        real = self.base / "elsewhere"
        real.write_text("9.9.9\n")
        os.symlink(real, root / "agents" / ".bobp-version")
        self.assertIn("unrecorded", _check(root))

    def test_check_writes_nothing_to_the_project(self):
        root = _project(self.base / "p", "1.0.0\n")
        before = sorted(str(p) for p in root.rglob("*"))
        _check(root)
        self.assertEqual(sorted(str(p) for p in root.rglob("*")), before)
        self.assertEqual((root / "agents" / ".bobp-version").read_text(), "1.0.0\n")

    def test_unexpected_errors_are_swallowed(self):
        root = _project(self.base / "p", "1.0.0\n")
        with patch.object(_version_check, "find_project_root_or_none", side_effect=RuntimeError("boom")):
            self.assertEqual(_check(root), "")

    def test_unwritable_stderr_does_not_raise(self):
        root = _project(self.base / "p", "1.0.0\n")

        class Closed:
            def write(self, *_):
                raise OSError("closed")

            def flush(self):
                raise OSError("closed")

        with patch.object(bobp, "__version__", "1.2.0"):
            _version_check.check("chat", start=root, env={}, err=Closed())


class DispatcherIntegrationTests(unittest.TestCase):
    """The check runs from cli.main() and never changes the subcommand's behavior."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = _project(Path(self._tmp.name) / "proj", "0.0.1\n")
        self._cwd = os.getcwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, self._cwd)
        self.calls = []

        class Stub:
            def __init__(inner, name):
                inner.name = name

            def main(inner):
                import sys

                self.calls.append((inner.name, list(sys.argv)))
                print("subcommand output")

        self.stub = Stub

    def _run(self, argv, env=None):
        out, err = io.StringIO(), io.StringIO()
        env = {"BOBP_NO_VERSION_CHECK": ""} if env is None else env
        with patch.dict(os.environ, env, clear=False), \
                patch("importlib.import_module", side_effect=lambda p: self.stub(p)), \
                redirect_stdout(out), redirect_stderr(err):
            code = cli.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_stale_project_gets_notice_on_stderr_and_subcommand_still_runs(self):
        code, out, err = self._run(["chat", "hello"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "subcommand output\n")
        self.assertIn("bobp update", err)
        self.assertEqual(self.calls, [("bobp.tools.chat", ["chat", "hello"])])

    def test_notice_repeats_on_every_run_while_behind(self):
        for _ in range(3):
            _, _, err = self._run(["chat"])
            self.assertIn("bobp update", err)

    def test_notice_stops_once_the_stamp_is_current(self):
        (self.root / "agents" / ".bobp-version").write_text(f"{bobp.__version__}\n")
        _, _, err = self._run(["chat"])
        self.assertEqual(err, "")

    def test_env_switch_silences_dispatcher(self):
        _, _, err = self._run(["chat"], env={"BOBP_NO_VERSION_CHECK": "1"})
        self.assertEqual(err, "")

    def test_version_help_and_install_update_do_not_check(self):
        for argv in (["--version"], ["-V"], ["--help"]):
            _, _, err = self._run(argv)
            self.assertEqual(err, "", argv)
        for argv in (["install", "x"], ["update", "x"]):
            _, _, err = self._run(argv)
            self.assertNotIn("this project was set up", err, argv)

    def test_check_failure_does_not_block_or_change_exit_code(self):
        with patch.object(_version_check, "find_project_root_or_none", side_effect=RuntimeError("boom")):
            code, out, err = self._run(["chat"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "subcommand output\n")
        self.assertEqual(len(self.calls), 1)

    def test_unknown_subcommand_behavior_is_unchanged(self):
        code, _, err = self._run(["nope"])
        self.assertEqual(code, 1)
        self.assertIn("unknown subcommand", err)
        self.assertNotIn("this project was set up", err)


class CommonHelperTests(unittest.TestCase):
    def test_or_none_returns_none_without_exiting(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("pathlib.Path.is_dir", return_value=False):
                self.assertIsNone(_common.find_project_root_or_none(Path(tmp)))

    def test_or_none_finds_the_project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve() / "p"
            (root / "agents").mkdir(parents=True)
            (root / "a" / "b").mkdir(parents=True)
            self.assertEqual(_common.find_project_root_or_none(root / "a" / "b"), root)

    def test_find_project_root_still_exits_when_missing(self):
        with patch.object(_common, "find_project_root_or_none", return_value=None):
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                _common.find_project_root()


if __name__ == "__main__":
    unittest.main()
