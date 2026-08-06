import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from agents.tools import chat_diagram

REPO_ROOT = Path(__file__).resolve().parent.parent

SAMPLE_LOG = """# Chat Message Template:

Agents **must** use this for every message posted to CHAT.md.

---
[<small>2026-04-12 12:34:04</small>] [**make**]->[**all**] *build*:
 Build PASSED | make tldr

---
[<small>2026-04-12 12:49:03</small>] [**Neo**]->[**Oracle**] *swe fix*:
 Investigating a startup failure. This line is deliberately long enough that it exceeds the truncation limit used when rendering short message snippets in the diagram.

---
[<small>2026-06-21 11:33:32</small>] [**Neo**]->[**Trin,Morpheus**] *handoff*:
 Fix complete, please verify.
"""


class ParseEntriesTests(unittest.TestCase):
    def test_parses_all_entries_in_order(self):
        entries = chat_diagram.parse_entries(SAMPLE_LOG)
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0].persona, "make")
        self.assertEqual(entries[1].persona, "Neo")
        self.assertEqual(entries[1].to, "Oracle")
        self.assertEqual(entries[1].cmd, "swe fix")
        self.assertEqual(entries[2].to, "Trin,Morpheus")

    def test_body_is_stripped(self):
        entries = chat_diagram.parse_entries(SAMPLE_LOG)
        self.assertEqual(entries[2].body, "Fix complete, please verify.")


class BuildDiagramTests(unittest.TestCase):
    def test_skips_build_entries_by_default(self):
        entries = chat_diagram.parse_entries(SAMPLE_LOG)
        diagram = chat_diagram.build_diagram(entries)
        self.assertNotIn("make", diagram)
        self.assertIn("Neo->>Oracle:", diagram)

    def test_include_builds_keeps_make_entries(self):
        entries = chat_diagram.parse_entries(SAMPLE_LOG)
        diagram = chat_diagram.build_diagram(entries, include_builds=True)
        self.assertIn("participant make", diagram)
        self.assertIn("make->>All:", diagram)

    def test_multiple_recipients_produce_one_arrow_each(self):
        entries = chat_diagram.parse_entries(SAMPLE_LOG)
        diagram = chat_diagram.build_diagram(entries)
        self.assertIn("Neo->>Trin:", diagram)
        self.assertIn("Neo->>Morpheus:", diagram)

    def test_long_message_is_truncated(self):
        entries = chat_diagram.parse_entries(SAMPLE_LOG)
        label = chat_diagram._label_for(entries[1])
        snippet = label.split(" — ", 1)[-1]
        self.assertLessEqual(len(snippet), chat_diagram.MAX_MSG_LEN)
        self.assertTrue(snippet.endswith("…"))

    def test_date_change_emits_note(self):
        entries = chat_diagram.parse_entries(SAMPLE_LOG)
        diagram = chat_diagram.build_diagram(entries)
        self.assertIn("2026-04-12", diagram)
        self.assertIn("2026-06-21", diagram)

    def test_empty_log_still_renders_a_valid_diagram(self):
        diagram = chat_diagram.build_diagram([])
        self.assertTrue(diagram.startswith("sequenceDiagram"))


class RenderTests(unittest.TestCase):
    def test_render_wraps_diagram_in_mermaid_fence(self):
        output = chat_diagram.render(SAMPLE_LOG)
        self.assertIn("```mermaid", output)
        self.assertIn("sequenceDiagram", output)
        self.assertIn("```\n", output)


class RegenerateTests(unittest.TestCase):
    def test_regenerate_writes_diagram_file_from_chat_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            chat_file = Path(tmp) / "CHAT.md"
            diagram_file = Path(tmp) / "CHAT.diagram.md"
            chat_file.write_text(SAMPLE_LOG)

            chat_diagram.regenerate(chat_file, diagram_file)

            self.assertTrue(diagram_file.exists())
            self.assertIn("Neo->>Oracle:", diagram_file.read_text())


class ChatPyIntegrationTests(unittest.TestCase):
    """Runs the real chat.py CLI in an isolated temp project to verify the
    post-write hook regenerates CHAT.diagram.md, without touching this repo's
    actual agents/CHAT.md."""

    def test_posting_a_message_regenerates_the_diagram(self):
        with tempfile.TemporaryDirectory() as tmp:
            tools_dir = Path(tmp) / "agents" / "tools"
            tools_dir.mkdir(parents=True)
            for name in ("chat.py", "chat_diagram.py"):
                (tools_dir / name).write_text((REPO_ROOT / "agents" / "tools" / name).read_text())
            (Path(tmp) / "agents" / "CHAT.md").write_text("# Chat Log\n")

            result = subprocess.run(
                [sys.executable, str(tools_dir / "chat.py"), "Isolated test message",
                 "--persona", "Trin", "--cmd", "qa test", "--to", "Morpheus"],
                capture_output=True, text=True, cwd=tmp,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            diagram = (Path(tmp) / "agents" / "CHAT.diagram.md").read_text()
            self.assertIn("Trin->>Morpheus:", diagram)


if __name__ == "__main__":
    unittest.main()
