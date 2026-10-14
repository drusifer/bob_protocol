import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bobp.tools import chat_report

NODE_AVAILABLE = (
    shutil.which("node") is not None
    and (chat_report.MERMAID_RENDER_DIR / "node_modules").is_dir()
)
SKIP_REASON = (
    "node not on PATH" if shutil.which("node") is None
    else f"{chat_report.MERMAID_RENDER_DIR / 'node_modules'} missing — run `npm install` there"
)

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


PHASED_LOG = """# Chat Message Template:

---
[<small>2026-04-12 12:00:00</small>] [**Cypher**]->[**Smith**] *pm handoff*:
 Stories ready.

---
[<small>2026-04-12 12:05:00</small>] [**Smith**]->[**Mouse**] *user approve*:
 Approved.

---
[<small>2026-04-12 12:10:00</small>] [**Mouse**]->[**all**] *phase 1*:
 Build the parser: tokenizer and its tests.

---
[<small>2026-04-12 12:20:00</small>] [**Neo**]->[**Trin**] *swe handoff*:
 Parser done.

---
[<small>2026-04-12 12:30:00</small>] [**Trin**]->[**Morpheus**] *qa handoff*:
 UAT passed.

---
[<small>2026-04-12 12:40:00</small>] [**Mouse**]->[**all**] *phase 2*:
 Wire the CLI.

---
[<small>2026-04-12 12:50:00</small>] [**Mouse**]->[**all**] *Phase close*:
 Groom, user test, retro and launch.

---
[<small>2026-04-12 13:00:00</small>] [**Oracle**]->[**Smith**] *ora handoff*:
 Docs groomed.
"""


def _write_phased_project(tmp: str, log: str = PHASED_LOG) -> tuple[Path, Path, Path]:
    chat_file, diagram_file, archive_dir = _write_project(tmp)
    chat_file.write_text(log)
    from bobp.tools import chat_diagram
    chat_diagram.regenerate(chat_file, diagram_file)
    return chat_file, diagram_file, archive_dir


class PhaseReportTests(unittest.TestCase):
    def _archive(self, tmp, **kwargs):
        chat_file, diagram_file, archive_dir = _write_phased_project(tmp)
        _, archive_diagram = chat_report.archive(
            chat_file, diagram_file, archive_dir, "SPRINT_9", "Sprint nine summary.", **kwargs)
        return chat_file, archive_dir, archive_diagram.read_text()

    def test_summary_first_then_one_section_per_phase_in_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, text = self._archive(tmp)

        headings = [line for line in text.splitlines() if line.startswith("## ")]
        self.assertEqual(headings, ["## Summary", "## Planning", "## Phase 1", "## Phase 2", "## Close"])
        self.assertLess(text.index("Sprint nine summary."), text.index("## Planning"))

    def test_each_phase_has_its_description_and_its_own_diagram(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, text = self._archive(tmp)

        planning, phase1, phase2, close = text.split("\n## ")[2:]
        self.assertEqual(planning.count("```mermaid"), 1)
        self.assertIn("Cypher", planning)
        self.assertNotIn("Neo", planning)

        self.assertIn("Build the parser: tokenizer and its tests.", phase1)
        self.assertEqual(phase1.count("```mermaid"), 1)
        self.assertIn("Neo", phase1)
        self.assertIn("Trin", phase1)
        self.assertNotIn("Cypher", phase1)
        self.assertNotIn("Oracle", phase1)

        self.assertIn("Groom, user test, retro and launch.", close)
        self.assertIn("Oracle", close)

    def test_marker_message_is_the_heading_not_a_diagram_arrow(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, text = self._archive(tmp)
        phase1 = text.split("\n## ")[3]
        diagram = phase1[phase1.index("```mermaid"):]
        self.assertNotIn("Build the parser", diagram)

    def test_phase_with_no_messages_is_still_listed(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, text = self._archive(tmp)
        phase2 = text.split("\n## ")[4]
        self.assertIn("Wire the CLI.", phase2)
        self.assertIn("_No messages in this phase._", phase2)
        self.assertNotIn("```mermaid", phase2)

    def test_full_text_archive_and_reset_are_unchanged_by_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            chat_file, archive_dir, _ = self._archive(tmp)
            md_text = (archive_dir / "CHAT_SPRINT_9.md").read_text()
            self.assertIn("Parser done.", md_text)
            self.assertIn("*phase 1*", md_text)
            self.assertIn("Previous sprint archived", chat_file.read_text())
            self.assertNotIn("Parser done.", chat_file.read_text())

    def test_log_starting_with_a_marker_has_no_empty_planning_section(self):
        first_marker = "---\n[<small>2026-04-12 12:10:00"
        log = PHASED_LOG[:PHASED_LOG.index("---\n[<small>2026-04-12 12:00:00")] + PHASED_LOG[PHASED_LOG.index(first_marker):]
        with tempfile.TemporaryDirectory() as tmp:
            chat_file, diagram_file, archive_dir = _write_phased_project(tmp, log)
            _, archive_diagram = chat_report.archive(chat_file, diagram_file, archive_dir, "S", "Summary.")
            text = archive_diagram.read_text()
        self.assertNotIn("## Planning", text)
        self.assertIn("## Phase 1", text)

    def test_log_without_markers_archives_exactly_as_before(self):
        with tempfile.TemporaryDirectory() as tmp:
            chat_file, diagram_file, archive_dir = _write_project(tmp)
            live_diagram = diagram_file.read_text()
            _, archive_diagram = chat_report.archive(chat_file, diagram_file, archive_dir, "OLD", "Summary.")
            expected = (chat_report._summary_heading("OLD", "Summary.") + "\n"
                        + live_diagram[live_diagram.find("```mermaid"):])
            self.assertEqual(archive_diagram.read_text(), expected)

    def test_split_phases_returns_none_without_markers(self):
        from bobp.tools.chat_merge import parse_blocks
        _, blocks = parse_blocks(SAMPLE_LOG)
        self.assertIsNone(chat_report.split_phases(blocks))

    def test_phase_titles(self):
        self.assertEqual(chat_report._phase_title("1"), "Phase 1")
        self.assertEqual(chat_report._phase_title("2: CI and publishing"), "Phase 2: CI and publishing")
        self.assertEqual(chat_report._phase_title("close"), "Close")


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


class SvgFallbackTests(unittest.TestCase):
    """These must pass with or without Node installed — svg=True is meant to
    degrade gracefully, never break the archive operation."""

    def test_svg_true_falls_back_to_fence_when_node_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            chat_file, diagram_file, archive_dir = _write_project(tmp)

            with patch("shutil.which", return_value=None):
                archive_md, archive_diagram = chat_report.archive(
                    chat_file, diagram_file, archive_dir, "SPRINT_1", "No Node available.", svg=True)

            diagram_text = archive_diagram.read_text()
            self.assertIn("```mermaid", diagram_text)
            self.assertNotIn(".svg", diagram_text)

    def test_render_svg_returns_false_when_node_missing(self):
        with patch("shutil.which", return_value=None):
            ok = chat_report.render_svg("sequenceDiagram\n    A->>B: hi\n", Path("/tmp/unused.svg"))
        self.assertFalse(ok)


@unittest.skipUnless(NODE_AVAILABLE, SKIP_REASON)
class SvgRenderTests(unittest.TestCase):
    """Exercises the real render path (actual Node + mermaid-cli + a real
    Chrome) — skipped, not failed, where that isn't set up."""

    def test_svg_true_produces_a_real_svg_and_embeds_it_as_an_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            chat_file, diagram_file, archive_dir = _write_project(tmp)

            archive_md, archive_diagram = chat_report.archive(
                chat_file, diagram_file, archive_dir, "SPRINT_1", "Rendered for real.", svg=True)

            archive_svg = archive_dir / "CHAT_SPRINT_1.svg"
            self.assertTrue(archive_svg.exists(), "expected a real .svg file to be written")
            self.assertGreater(archive_svg.stat().st_size, 0)
            svg_content = archive_svg.read_text()
            self.assertIn("<svg", svg_content)

            diagram_text = archive_diagram.read_text()
            self.assertIn("![CHAT_SPRINT_1 diagram](CHAT_SPRINT_1.svg)", diagram_text)
            self.assertNotIn("```mermaid", diagram_text)

    def test_combine_passes_through_svg_image_reference_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            chat_file, diagram_file, archive_dir = _write_project(tmp)
            chat_report.archive(chat_file, diagram_file, archive_dir, "SPRINT_1", "Only sprint.", svg=True)

            out_md, out_diagram = chat_report.combine(
                archive_dir, archive_dir / "CHAT_FULL.md", archive_dir / "CHAT_FULL.diagram.md")

            self.assertIn("![CHAT_SPRINT_1 diagram](CHAT_SPRINT_1.svg)", out_diagram.read_text())


if __name__ == "__main__":
    unittest.main()
