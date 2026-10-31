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


def _diagram(entries, include_builds=False):
    """All mermaid diagram sources of a log, joined (recap text sections excluded)."""
    blocks = chat_diagram.build_blocks(entries, include_builds=include_builds)
    return "\n\n".join(body for kind, body in blocks if kind == "diagram")


def _rendered(entries):
    return chat_diagram.render("".join(
        f"[<small>{e.ts}</small>] [**{e.persona}**]->[**{e.to}**] *{e.cmd}*:\n {e.body}\n\n---\n"
        for e in entries
    ))


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
        diagram = _diagram(entries)
        self.assertNotIn("make", diagram)
        self.assertIn("Neo->>Oracle:", diagram)

    def test_include_builds_keeps_make_entries(self):
        entries = chat_diagram.parse_entries(SAMPLE_LOG)
        diagram = _diagram(entries, include_builds=True)
        self.assertIn("participant make", diagram)
        self.assertIn("make->>All:", diagram)

    def test_multiple_recipients_produce_one_arrow_each(self):
        entries = chat_diagram.parse_entries(SAMPLE_LOG)
        diagram = _diagram(entries)
        self.assertIn("Neo->>Trin:", diagram)
        self.assertIn("Neo->>Morpheus:", diagram)

    def test_moderately_long_message_is_wrapped_not_truncated(self):
        # Under MAX_MSG_LEN but well over WRAP_WIDTH, so this checks the
        # narrow-column wrapping itself, independent of the truncation cap.
        entry = chat_diagram.Entry(
            ts="2026-04-12 12:00:00", persona="Neo", to="Trin", cmd="swe fix",
            body="Investigating a startup failure in the picker module.",
        )
        note_text = chat_diagram._note_text_for(entry)
        self.assertIn("<br/>", note_text)
        self.assertNotIn("…", note_text)
        for line in note_text.split("<br/>"):
            self.assertLessEqual(len(line), chat_diagram.WRAP_WIDTH)

    def test_message_beyond_safety_cap_is_still_truncated(self):
        huge_body = "word " * 200  # well beyond MAX_MSG_LEN
        entry = chat_diagram.Entry(ts="2026-04-12 12:00:00", persona="Neo", to="Trin", cmd="swe fix", body=huge_body)
        note_text = chat_diagram._note_text_for(entry)
        self.assertIn("…", note_text)

    def test_message_body_renders_as_a_note_not_an_arrow_label(self):
        """The arrow itself should carry only the short cmd — the full
        message snippet belongs in a Note, which gets its own font-size
        config and isn't crammed against the thin arrow line."""
        entry = chat_diagram.Entry(
            ts="2026-04-12 12:00:00", persona="Neo", to="Trin", cmd="swe fix",
            body="Investigating a startup failure.",
        )
        diagram = _diagram([entry])
        arrow_line = next(l for l in diagram.splitlines() if "Neo->>Trin:" in l)
        self.assertEqual(arrow_line.strip(), 'Neo->>Trin: "swe fix"')
        self.assertIn("Note right of Neo:", diagram)
        self.assertIn("Investigating", diagram)

    def test_note_is_anchored_to_sender_not_spanning_the_recipient(self):
        """Regression: `Note over A,B` sizes its box as the literal
        x-distance between A and B (verified in mermaid's own renderer
        source), so with many participants declared between a non-adjacent
        sender/recipient pair, it renders far wider than intended — directly
        undermining the "narrow" redesign. `Note right of <sender>` is
        anchored to the sender alone, independent of how far the recipient
        is, so it must never reference the recipient's id."""
        # Force Cypher and Bob to be non-adjacent by routing other entries
        # between them first, mirroring a real multi-persona log.
        entries = [
            chat_diagram.Entry(ts="2026-04-12 11:00:00", persona="Cypher", to="Smith", cmd="pm handoff", body="a"),
            chat_diagram.Entry(ts="2026-04-12 11:05:00", persona="Smith", to="Morpheus", cmd="user approve", body="b"),
            chat_diagram.Entry(ts="2026-04-12 12:00:00", persona="Cypher", to="Bob", cmd="pm handoff", body="broadcast message"),
        ]
        diagram = _diagram(entries)
        note_line = next(l for l in diagram.splitlines() if "broadcast message" in l)
        self.assertIn("Note right of Cypher:", note_line)
        # The date-divider note legitimately still spans the full width
        # (Note over first,last) — only per-message notes must avoid it.
        message_note_lines = [l for l in diagram.splitlines() if '"a"' in l or '"b"' in l or "broadcast message" in l]
        self.assertTrue(message_note_lines)
        for line in message_note_lines:
            self.assertNotIn("Note over", line)

    def test_date_change_emits_note(self):
        entries = chat_diagram.parse_entries(SAMPLE_LOG)
        diagram = _diagram(entries)
        self.assertIn("2026-04-12", diagram)
        self.assertIn("2026-06-21", diagram)

    def test_next_phase_marker_closes_diagram_and_adds_text_section(self):
        entries = [
            chat_diagram.Entry("2026-04-12 12:00:00", "Mouse", "all", "phase 1", "Parser"),
            chat_diagram.Entry("2026-04-12 12:10:00", "Neo", "Trin", "swe handoff", "Phase 1 implemented."),
            chat_diagram.Entry("2026-04-12 12:20:00", "Trin", "Morpheus", "qa handoff", "UAT phase 1 passed."),
            chat_diagram.Entry("2026-04-12 12:30:00", "Mouse", "all", "phase 2", "CLI"),
            chat_diagram.Entry("2026-04-12 12:40:00", "Neo", "Trin", "swe handoff", "Phase 2 started."),
        ]
        blocks = chat_diagram.build_blocks(entries)
        kinds = [k for k, _ in blocks]
        # start-of-phase-1, diagram, close-out + start-of-phase-2, diagram, phase-2-so-far
        self.assertEqual(kinds, ["text", "diagram", "text", "text", "diagram", "text"])
        self.assertIn("## Phase 2 so far", blocks[5][1])
        self.assertIn("## Phase 1 close-out", blocks[2][1])
        self.assertIn("UAT phase 1 passed", blocks[2][1])
        self.assertIn("## Phase 2 starts", blocks[3][1])
        self.assertNotIn("close-out", blocks[1][1])
        self.assertNotIn("close-out", "\n".join(b for k, b in blocks if k == "diagram"))
        self.assertIn('Mouse->>All: "phase 2"', blocks[4][1])
        self.assertNotIn('"phase 2"', blocks[1][1])

    def test_chat_text_is_escaped_in_markdown_sections(self):
        """SEC-003: chat text must not inject HTML, links, or images into the rendered file."""
        entries = [
            chat_diagram.Entry("2026-04-12 12:00:00", "Mouse", "all", "phase <b>1</b>", "Goal <b>x</b> ![t](https://example.invalid/p.png)"),
            chat_diagram.Entry("2026-04-12 12:10:00", "Tr<in>", "Mouse", "qa handoff",
                               "UAT passed <img src=https://example.invalid/x.png> [click](https://example.invalid) `code` & more"),
            chat_diagram.Entry("2026-04-12 12:30:00", "Mouse", "all", "phase 2", "next"),
        ]
        text = "\n".join(b for k, b in chat_diagram.build_blocks(entries) if k == "text")
        for raw in ("<b>", "<img", "<in>", "![t](", "[click](", "`code`"):
            self.assertNotIn(raw, text)
        self.assertIn("UAT passed", text)
        self.assertIn("&lt;img", text)

    def test_each_diagram_block_is_self_contained(self):
        entries = [
            chat_diagram.Entry("2026-04-12 12:00:00", "Mouse", "all", "phase 1", "Parser"),
            chat_diagram.Entry("2026-04-12 12:10:00", "Neo", "Trin", "swe handoff", "Done."),
            chat_diagram.Entry("2026-04-12 12:30:00", "Mouse", "all", "phase 2", "CLI"),
            chat_diagram.Entry("2026-04-12 12:40:00", "Oracle", "Smith", "ora handoff", "Docs."),
        ]
        diagrams = [b for k, b in chat_diagram.build_blocks(entries) if k == "diagram"]
        self.assertEqual(len(diagrams), 2)
        for d in diagrams:
            self.assertTrue(d.startswith(chat_diagram.INIT_DIRECTIVE))
            self.assertIn("autonumber", d)
        self.assertIn("participant Oracle", diagrams[1])
        self.assertNotIn("participant Oracle", diagrams[0])
        self.assertIn("2026-04-12", diagrams[1])

    def test_render_interleaves_fences_and_text_sections(self):
        entries = [
            chat_diagram.Entry("2026-04-12 12:00:00", "Mouse", "all", "phase 1", "Parser"),
            chat_diagram.Entry("2026-04-12 12:10:00", "Trin", "Morpheus", "qa handoff", "UAT passed."),
            chat_diagram.Entry("2026-04-12 12:30:00", "Mouse", "all", "phase 2", "CLI"),
            chat_diagram.Entry("2026-04-12 12:40:00", "Neo", "Trin", "swe handoff", "Working."),
        ]
        output = _rendered(entries)
        self.assertEqual(output.count("```mermaid"), 2)
        self.assertEqual(output.count("```\n"), 2)
        self.assertLess(output.index("## Phase 1 close-out"), output.index("## Phase 2 starts"))
        between = output[output.index("```\n", output.index("```mermaid")):output.index("```mermaid", 10 + output.index("```mermaid"))]
        self.assertIn("Phase 1 close-out", between)

    def test_sprint_launch_adds_phase_and_sprint_close_out_sections(self):
        entries = [
            chat_diagram.Entry("2026-04-12 12:00:00", "Mouse", "all", "phase 1", "CLI"),
            chat_diagram.Entry("2026-04-12 12:10:00", "Trin", "Morpheus", "qa handoff", "UAT passed."),
            chat_diagram.Entry("2026-04-12 12:20:00", "Cypher", "all", "pm launch", "Sprint complete."),
        ]
        text = "\n".join(b for k, b in chat_diagram.build_blocks(entries) if k == "text")
        self.assertIn("## Phase 1 close-out", text)
        self.assertIn("## Sprint close-out", text)
        self.assertIn("Sprint complete", text)

    def test_explicit_epic_close_adds_close_out_section(self):
        entries = [
            chat_diagram.Entry("2026-04-12 12:00:00", "Cypher", "Smith", "plan epic", "Shape initiative."),
            chat_diagram.Entry("2026-04-12 12:10:00", "Smith", "all", "user approve", "Epic scope approved."),
            chat_diagram.Entry("2026-04-12 12:20:00", "Cypher", "all", "epic close", "Epic shaping complete."),
        ]
        text = "\n".join(b for k, b in chat_diagram.build_blocks(entries) if k == "text")
        self.assertIn("## Epic close-out", text)
        self.assertIn("Epic shaping complete", text)

    def test_epic_to_story_transition_closes_diagram_before_story(self):
        entries = [
            chat_diagram.Entry("2026-04-12 12:00:00", "Cypher", "Smith", "plan epic", "Shape initiative."),
            chat_diagram.Entry("2026-04-12 12:10:00", "Smith", "all", "user approve", "Epic scope approved."),
            chat_diagram.Entry("2026-04-12 12:20:00", "Morpheus", "Cypher", "plan story", "Break down the approved epic."),
        ]
        blocks = chat_diagram.build_blocks(entries)
        self.assertEqual([k for k, _ in blocks], ["diagram", "text", "diagram"])
        self.assertIn("Epic scope approved", blocks[1][1])
        self.assertIn('Morpheus->>Cypher: "plan story"', blocks[2][1])
        self.assertNotIn("plan story", blocks[0][1])

    def test_empty_log_still_renders_a_valid_diagram(self):
        diagram = _diagram([])
        self.assertIn(chat_diagram.INIT_DIRECTIVE, diagram)
        self.assertIn("sequenceDiagram", diagram)

    def test_message_with_semicolon_is_quoted(self):
        # A bare semicolon in an unquoted Mermaid sequence-diagram message is
        # parsed as a statement terminator and breaks the diagram (regression:
        # real chat messages like "...consistency); new US-14..." did this).
        entry = chat_diagram.Entry(
            ts="2026-04-12 12:00:00", persona="Neo", to="Trin", cmd="swe fix",
            body="quit (keybinding consistency); new US-14 requires window-close",
        )
        diagram = _diagram([entry])
        self.assertIn('Neo->>Trin: "swe fix', diagram)
        line = next(l for l in diagram.splitlines() if "Neo->>Trin:" in l)
        self.assertTrue(line.rstrip().endswith('"'))

    def test_message_with_literal_quote_is_escaped_not_broken(self):
        entry = chat_diagram.Entry(
            ts="2026-04-12 12:00:00", persona="Neo", to="Trin", cmd="swe fix",
            body='the flag is called "--mode"',
        )
        diagram = _diagram([entry])
        self.assertNotIn('"--mode"', diagram)  # raw quotes would end the label early
        # narrow wrapping may insert a <br/> inside the escaped run, so check
        # both entity escapes landed rather than the exact unwrapped substring
        self.assertEqual(diagram.count("#quot;"), 2)


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
