"""Tests for bobp tldr: file discovery via the system `via` command, TLDR block parsing."""

import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from bobp.tools import tldr

WITH_TLDR = '''"""Module docstring."""

One-line summary of the module.

TLDR:
    First line of the block.
    Second line of the block.

Rest of the file.
'''


def _completed(stdout="", returncode=0, stderr=""):
    return subprocess.CompletedProcess(args=["via"], returncode=returncode, stdout=stdout, stderr=stderr)


class DiscoverFilesTests(unittest.TestCase):
    def _discover(self, *completed):
        with patch.object(tldr.shutil, "which", return_value="/usr/bin/via"), \
                patch.object(tldr.subprocess, "run", side_effect=list(completed)) as run:
            return tldr.discover_files(Path("/p")), run

    def test_indexes_first_then_lists_and_keeps_only_py_and_md(self):
        listing = json.dumps([
            {"symbol_type": "filepath", "file_path": "/p/b.md"},
            {"symbol_type": "filepath", "file_path": "/p/a.py"},
            {"symbol_type": "filepath", "file_path": "/p/data.json"},
            {"symbol_type": "filepath", "file_path": "/p/a.py"},
        ])
        files, run = self._discover(_completed(), _completed(listing))

        self.assertEqual(files, ["/p/a.py", "/p/b.md"])
        index_call, list_call = run.call_args_list
        self.assertEqual(index_call.args[0], ["via", "index", "."])
        argv = list_call.args[0]
        self.assertEqual(argv[0], "via")
        self.assertIn("-tF", argv)
        self.assertEqual(argv[argv.index("-n") + 1], "0")  # no result limit
        for call in (index_call, list_call):
            self.assertEqual(call.kwargs["cwd"], Path("/p"))
            self.assertEqual(call.kwargs["stdin"], subprocess.DEVNULL)

    def test_missing_via_exits_with_a_message_not_a_traceback(self):
        err = io.StringIO()
        with patch.object(tldr.shutil, "which", return_value=None), redirect_stderr(err):
            with self.assertRaises(SystemExit) as ctx:
                tldr.discover_files(Path("/p"))
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("'via' command was not found", err.getvalue())

    def test_failed_index_stops_before_listing(self):
        err = io.StringIO()
        with patch.object(tldr.shutil, "which", return_value="/usr/bin/via"), \
                patch.object(tldr.subprocess, "run",
                             side_effect=[_completed(returncode=1, stderr="disk full")]) as run, \
                redirect_stderr(err):
            with self.assertRaises(SystemExit):
                tldr.discover_files(Path("/p"))
        self.assertEqual(run.call_count, 1)
        self.assertIn("`via index .` failed", err.getvalue())
        self.assertIn("disk full", err.getvalue())

    def test_listing_failure_or_garbage_output_is_reported(self):
        for listing in (_completed(returncode=2, stderr="bad query"), _completed("not json")):
            err = io.StringIO()
            with patch.object(tldr.shutil, "which", return_value="/usr/bin/via"), \
                    patch.object(tldr.subprocess, "run", side_effect=[_completed(), listing]), \
                    redirect_stderr(err):
                with self.assertRaises(SystemExit):
                    tldr.discover_files(Path("/p"))
            self.assertIn("could not list the project's files", err.getvalue())


class MainTests(unittest.TestCase):
    def test_prints_blocks_for_the_project_in_the_current_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "agents").mkdir()
            (root / "has.py").write_text(WITH_TLDR)
            (root / "none.md").write_text("# Nothing here\n")
            out = io.StringIO()
            with patch.object(tldr, "find_project_root", return_value=root), \
                    patch.object(tldr, "discover_files",
                                 return_value=[str(root / "has.py"), str(root / "none.md")]), \
                    redirect_stdout(out):
                tldr.main()

        text = out.getvalue()
        self.assertIn("has.py:\nOne-line summary of the module.\nTLDR:\n    First line of the block.", text)
        self.assertNotIn("none.md", text)

    def test_empty_index_explains_what_to_do(self):
        err = io.StringIO()
        with patch.object(tldr, "find_project_root", return_value=Path("/p")), \
                patch.object(tldr, "discover_files", return_value=[]), redirect_stderr(err):
            with self.assertRaises(SystemExit):
                tldr.main()
        self.assertIn("indexed no .py or .md files", err.getvalue())

    def test_module_does_not_import_via_as_a_library(self):
        source = Path(tldr.__file__).read_text()
        self.assertNotIn("from via", source)
        self.assertNotIn("import via", source)


if __name__ == "__main__":
    unittest.main()
