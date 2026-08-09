import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bobp.tools import chat, chat_diagram

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

    def test_long_message_is_wrapped_not_truncated(self):
        entries = chat_diagram.parse_entries(SAMPLE_LOG)
        label = chat_diagram._label_for(entries[1])
        snippet = label.split(" — ", 1)[-1]
        self.assertIn("<br/>", snippet)
        self.assertNotIn("…", snippet)
        for line in snippet.split("<br/>"):
            self.assertLessEqual(len(line), chat_diagram.WRAP_WIDTH)

    def test_message_beyond_safety_cap_is_still_truncated(self):
        huge_body = "word " * 200  # well beyond MAX_MSG_LEN
        entry = chat_diagram.Entry(ts="2026-04-12 12:00:00", persona="Neo", to="Trin", cmd="swe fix", body=huge_body)
        label = chat_diagram._label_for(entry)
        snippet = label.split(" — ", 1)[-1]
        self.assertIn("…", snippet)

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
    """Runs the real `bobp.tools.chat` CLI in-process against an isolated temp
    project (cwd = tmp, containing agents/CHAT.md) to verify the post-write
    hook regenerates CHAT.diagram.md, without touching this repo's actual
    agents/CHAT.md. chat.py finds the project root by walking up from cwd, so
    no script files need to be copied into the temp project. Calls chat.main()
    directly (patching sys.argv and cwd) instead of shelling out to
    `sys.executable -m bobp.tools.chat` — that indirection bought nothing here
    and broke on any interpreter that isn't the one bobp is installed into
    (e.g. plain `pytest` on a system Python), since chat.py is an ordinary
    importable module, not something that needs process isolation to test."""

    def test_posting_a_message_regenerates_the_diagram(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "agents").mkdir(parents=True)
            (Path(tmp) / "agents" / "CHAT.md").write_text("# Chat Log\n")

            argv = ["chat", "Isolated test message",
                    "--persona", "Trin", "--cmd", "qa test", "--to", "Morpheus"]
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                with patch("sys.argv", argv):
                    chat.main()
            finally:
                os.chdir(cwd)

            diagram = (Path(tmp) / "agents" / "CHAT.diagram.md").read_text()
            self.assertIn("Trin->>Morpheus:", diagram)


if __name__ == "__main__":
    unittest.main()
