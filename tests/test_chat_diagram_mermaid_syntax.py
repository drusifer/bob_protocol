"""End-to-end regression test: diagrams chat_diagram.py generates must parse
as valid Mermaid, verified against mermaid's real parser (not a hand-rolled
character check). A prior "wrap every label in quotes" fix looked plausible
and passed a naive check, but mermaid's lexer turned out to still choke on
a semicolon even inside quotes — this test would have caught that, because
it asks the real parser, not a proxy.

Requires Node + the validator's npm dependencies (tools/mermaid_validate/).
Skips (does not fail) if either is unavailable, so this suite doesn't block
environments without Node — but runs for real, no mocking, wherever it can.
"""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from bobp.tools import chat_diagram

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = REPO_ROOT / "tools" / "mermaid_validate" / "validate.mjs"
NODE_MODULES = REPO_ROOT / "tools" / "mermaid_validate" / "node_modules"

NODE_AVAILABLE = shutil.which("node") is not None and NODE_MODULES.is_dir()
SKIP_REASON = (
    "node not on PATH" if shutil.which("node") is None
    else f"{NODE_MODULES} missing — run `npm install` in tools/mermaid_validate/"
)


def _validate(md_text):
    """Write md_text to a temp file, run it through the real Mermaid parser,
    return (ok: bool, output: str)."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(md_text)
        path = f.name
    try:
        result = subprocess.run(
            ["node", str(VALIDATOR), path],
            capture_output=True, text=True, timeout=30,
        )
        return result.returncode == 0, result.stdout + result.stderr
    finally:
        Path(path).unlink(missing_ok=True)


@unittest.skipUnless(NODE_AVAILABLE, SKIP_REASON)
class MermaidSyntaxE2ETests(unittest.TestCase):
    def test_harness_actually_detects_broken_mermaid(self):
        """Sanity check on the test harness itself: a genuinely broken
        diagram (unquoted semicolon, the original bug) must be REJECTED.
        If this test doesn't fail on bad input, the other PASS assertions
        in this file are meaningless."""
        broken = (
            "```mermaid\nsequenceDiagram\n"
            "    participant A\n    participant B\n"
            "    A->>B: quit (consistency); new US-14 requires window-close\n"
            "```\n"
        )
        ok, output = _validate(broken)
        self.assertFalse(ok, f"harness failed to detect a known-broken diagram:\n{output}")

    def test_semicolon_in_message_body_produces_valid_mermaid(self):
        entry = chat_diagram.Entry(
            ts="2026-04-12 12:00:00", persona="Smith", to="Morpheus", cmd="user approve",
            body="quit (keybinding consistency); new US-14 requires OS window-close",
        )
        rendered = chat_diagram.render(
            "[<small>2026-04-12 12:00:00</small>] [**Smith**]->[**Morpheus**] *user approve*:\n"
            " quit (keybinding consistency); new US-14 requires OS window-close\n"
        )
        ok, output = _validate(rendered)
        self.assertTrue(ok, f"generator produced unparseable Mermaid:\n{output}")

    def test_long_wrapped_message_with_semicolon_produces_valid_mermaid(self):
        """Regression case for the actual bug: a long message that gets
        <br/>-wrapped AND contains a semicolon before the wrap point — this
        combination is what broke the "just quote it" fix (quoting alone got
        past the semicolon but then choked on <br/>'s '<' a few tokens
        later, because mermaid's lexer's quoted-string mode doesn't survive
        a semicolon)."""
        long_body = (
            "user approve — *user approve. Sprint 2 stories approved "
            "with 2 additions: US-9 picker now requires Up/Down/Enter nav "
            "+ Esc/Q clean quit (keybinding consistency); new US-14 "
            "requires OS window-close (X) in 3D mode to quit as cleanly "
            "as Q/Esc (platform convention). @Morpheus *lead arch sprint"
        )
        chat_text = (
            "[<small>2026-04-12 12:00:00</small>] [**Smith**]->[**Morpheus**] *user approve*:\n"
            f" {long_body}\n"
        )
        rendered = chat_diagram.render(chat_text)
        self.assertIn("<br/>", rendered, "test fixture should exercise the wrap path")
        ok, output = _validate(rendered)
        self.assertTrue(ok, f"generator produced unparseable Mermaid:\n{output}")

    def test_literal_double_quote_in_message_produces_valid_mermaid(self):
        chat_text = (
            "[<small>2026-04-12 12:00:00</small>] [**Neo**]->[**Trin**] *swe fix*:\n"
            ' the flag is called "--mode", not --renderer\n'
        )
        rendered = chat_diagram.render(chat_text)
        ok, output = _validate(rendered)
        self.assertTrue(ok, f"generator produced unparseable Mermaid:\n{output}")

    def test_full_multi_persona_log_produces_valid_mermaid(self):
        """Closest thing to the real failure: many entries, multiple
        recipients, dates, semicolons, long bodies — the actual shape of a
        real CHAT.md archive, not a single crafted line."""
        chat_text = "\n".join([
            "[<small>2026-04-12 09:00:00</small>] [**Cypher**]->[**Smith**] *pm handoff*:",
            " Stories ready; please review before Morpheus starts architecture.",
            "",
            "---",
            "[<small>2026-04-12 09:15:00</small>] [**Smith**]->[**Morpheus,Mouse**] *user approve*:",
            " Approved with 2 additions: nav must support Esc; quit must be clean.",
            "",
            "---",
            "[<small>2026-04-13 10:00:00</small>] [**Neo**]->[**Trin**] *swe handoff*:",
            ' Fixed the "--mode" flag; all tests green; ready for UAT.',
            "",
        ])
        rendered = chat_diagram.render(chat_text)
        ok, output = _validate(rendered)
        self.assertTrue(ok, f"generator produced unparseable Mermaid:\n{output}")


if __name__ == "__main__":
    unittest.main()
