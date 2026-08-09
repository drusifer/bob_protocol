import tempfile
import unittest
from pathlib import Path

from bobp.tools import chat_report

SAMPLE_LOG = """# Chat Message Template:

Agents **must** use this for every message posted to CHAT.md.

---
[<small>2026-04-12 12:34:04</small>] [**make**]->[**all**] *build*:
 Build PASSED

---
[<small>2026-04-12 12:49:03</small>] [**Neo**]->[**Oracle**] *swe fix*:
 Investigating a startup failure.
"""


def _write_project(tmp: str) -> tuple[Path, Path, Path]:
    agents_dir = Path(tmp) / "agents"
    agents_dir.mkdir(parents=True)
    chat_file = agents_dir / "CHAT.md"
    diagram_file = agents_dir / "CHAT.diagram.md"
    chat_file.write_text(SAMPLE_LOG)
    from bobp.tools import chat_diagram
    chat_diagram.regenerate(chat_file, diagram_file)
    return chat_file, diagram_file, agents_dir / "chat_archive"


class ArchiveTests(unittest.TestCase):
    def test_writes_md_and_diagram_archives_with_summary_heading(self):
        with tempfile.TemporaryDirectory() as tmp:
            chat_file, diagram_file, archive_dir = _write_project(tmp)

            archive_md, archive_diagram = chat_report.archive(
                chat_file, diagram_file, archive_dir, "SPRINT_1", "Shipped the archive tool.")

            self.assertTrue(archive_md.exists())
            self.assertTrue(archive_diagram.exists())
            md_text = archive_md.read_text()
            self.assertIn("# CHAT_SPRINT_1 — Sprint Archive", md_text)
            self.assertIn("Shipped the archive tool.", md_text)
            self.assertIn("Neo", md_text)
            diagram_text = archive_diagram.read_text()
            self.assertIn("Shipped the archive tool.", diagram_text)
            self.assertIn("```mermaid", diagram_text)

    def test_resets_live_chat_file_to_pointer_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            chat_file, diagram_file, archive_dir = _write_project(tmp)

            chat_report.archive(chat_file, diagram_file, archive_dir, "SPRINT_1", "Summary text.")

            reset_text = chat_file.read_text()
            self.assertIn("Chat Message Template", reset_text)
            self.assertIn("Previous sprint archived", reset_text)
            self.assertIn("CHAT_SPRINT_1.md", reset_text)
            self.assertNotIn("Investigating a startup failure", reset_text)

    def test_regenerates_diagram_file_to_match_reset_chat(self):
        with tempfile.TemporaryDirectory() as tmp:
            chat_file, diagram_file, archive_dir = _write_project(tmp)

            chat_report.archive(chat_file, diagram_file, archive_dir, "SPRINT_1", "Summary text.")

            self.assertNotIn("Neo->>Oracle", diagram_file.read_text())

    def test_refuses_to_overwrite_existing_archive_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            chat_file, diagram_file, archive_dir = _write_project(tmp)
            chat_report.archive(chat_file, diagram_file, archive_dir, "SPRINT_1", "First close.")
            # Re-seed CHAT.md so there's something to archive again.
            chat_file.write_text(SAMPLE_LOG)

            with self.assertRaises(SystemExit):
                chat_report.archive(chat_file, diagram_file, archive_dir, "SPRINT_1", "Second close.")

    def test_force_overwrites_existing_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            chat_file, diagram_file, archive_dir = _write_project(tmp)
            chat_report.archive(chat_file, diagram_file, archive_dir, "SPRINT_1", "First close.")
            chat_file.write_text(SAMPLE_LOG)

            archive_md, _ = chat_report.archive(
                chat_file, diagram_file, archive_dir, "SPRINT_1", "Second close.", force=True)

            self.assertIn("Second close.", archive_md.read_text())


class CombineTests(unittest.TestCase):
    def test_combines_archives_in_natural_moniker_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            chat_file, diagram_file, archive_dir = _write_project(tmp)
            chat_report.archive(chat_file, diagram_file, archive_dir, "SPRINT_2", "Second sprint.")
            chat_file.write_text(SAMPLE_LOG)
            chat_report.archive(chat_file, diagram_file, archive_dir, "SPRINT_10", "Tenth sprint.")
            chat_file.write_text(SAMPLE_LOG)
            chat_report.archive(chat_file, diagram_file, archive_dir, "SPRINT_1", "First sprint.")

            out_md, out_diagram = chat_report.combine(
                archive_dir, archive_dir / "CHAT_FULL.md", archive_dir / "CHAT_FULL.diagram.md")

            text = out_md.read_text()
            self.assertLess(text.index("First sprint."), text.index("Second sprint."))
            self.assertLess(text.index("Second sprint."), text.index("Tenth sprint."))
            self.assertIn("Tenth sprint.", out_diagram.read_text())

    def test_errors_when_no_archives_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive_dir = Path(tmp) / "chat_archive"
            archive_dir.mkdir()
            with self.assertRaises(SystemExit):
                chat_report.combine(archive_dir, archive_dir / "CHAT_FULL.md", archive_dir / "CHAT_FULL.diagram.md")

    def test_combine_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            chat_file, diagram_file, archive_dir = _write_project(tmp)
            chat_report.archive(chat_file, diagram_file, archive_dir, "SPRINT_1", "Only sprint.")

            out_md = archive_dir / "CHAT_FULL.md"
            out_diagram = archive_dir / "CHAT_FULL.diagram.md"
            chat_report.combine(archive_dir, out_md, out_diagram)
            first = out_md.read_text()
            chat_report.combine(archive_dir, out_md, out_diagram)
            second = out_md.read_text()

            self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
