import tempfile
import unittest
from pathlib import Path

from bobp.tools import chat_merge

CLEAN_LOG = """# Chat Message Template:

Agents **must** use this for every message posted to CHAT.md.

---
[<small>2026-04-12 12:00:00</small>] [**Neo**]->[**Trin**] *swe fix*:
 First message.

---
[<small>2026-04-12 12:05:00</small>] [**Trin**]->[**Neo**] *qa handoff*:
 Second message.
"""

CONFLICTED_LOG = """# Chat Message Template:

Agents **must** use this for every message posted to CHAT.md.

---
[<small>2026-04-12 12:00:00</small>] [**Neo**]->[**Trin**] *swe fix*:
 First message.

<<<<<<< HEAD
---
[<small>2026-04-12 12:05:00</small>] [**Trin**]->[**Neo**] *qa handoff*:
 From branch A.
=======
---
[<small>2026-04-12 12:06:00</small>] [**Morpheus**]->[**Neo**] *lead handoff*:
 From branch B.
>>>>>>> feature-branch
"""

DUPLICATED_LOG = """# Chat Message Template:

Agents **must** use this for every message posted to CHAT.md.

---
[<small>2026-04-12 12:00:00</small>] [**Neo**]->[**Trin**] *swe fix*:
 Same message twice.

---
[<small>2026-04-12 12:00:00</small>] [**Neo**]->[**Trin**] *swe fix*:
 Same message twice.
"""


class StripConflictMarkersTests(unittest.TestCase):
    def test_strips_all_marker_variants(self):
        clean, count = chat_merge.strip_conflict_markers(CONFLICTED_LOG)
        self.assertEqual(count, 3)
        self.assertNotIn("<<<<<<<", clean)
        self.assertNotIn("=======", clean)
        self.assertNotIn(">>>>>>>", clean)

    def test_keeps_content_from_both_sides(self):
        clean, _ = chat_merge.strip_conflict_markers(CONFLICTED_LOG)
        self.assertIn("From branch A.", clean)
        self.assertIn("From branch B.", clean)

    def test_clean_text_is_unaffected(self):
        clean, count = chat_merge.strip_conflict_markers(CLEAN_LOG)
        self.assertEqual(count, 0)
        self.assertEqual(clean, CLEAN_LOG)

    def test_diff3_base_marker_is_stripped(self):
        text = "before\n||||||| base\nmerged\n"
        clean, count = chat_merge.strip_conflict_markers(text)
        self.assertEqual(count, 1)
        self.assertNotIn("|||||||", clean)


class DedupBlocksTests(unittest.TestCase):
    def test_drops_exact_duplicate_blocks(self):
        _, blocks = chat_merge.parse_blocks(DUPLICATED_LOG)
        deduped, dupe_count = chat_merge.dedup_blocks(blocks)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(dupe_count, 1)

    def test_keeps_distinct_blocks(self):
        _, blocks = chat_merge.parse_blocks(CLEAN_LOG)
        deduped, dupe_count = chat_merge.dedup_blocks(blocks)
        self.assertEqual(len(deduped), 2)
        self.assertEqual(dupe_count, 0)


class MergeIntegrationTests(unittest.TestCase):
    def test_merge_resolves_a_conflicted_file_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CHAT.md"
            path.write_text(CONFLICTED_LOG)

            chat_merge.merge(path, dry_run=False)

            result = path.read_text()
            self.assertNotIn("<<<<<<<", result)
            self.assertNotIn("=======", result)
            self.assertNotIn(">>>>>>>", result)
            self.assertIn("From branch A.", result)
            self.assertIn("From branch B.", result)

    def test_merge_dedupes_and_sorts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CHAT.md"
            path.write_text(DUPLICATED_LOG)

            chat_merge.merge(path, dry_run=False)

            result = path.read_text()
            self.assertEqual(result.count("Same message twice."), 1)


if __name__ == "__main__":
    unittest.main()
