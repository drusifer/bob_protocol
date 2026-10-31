# SEC-003: Chat text is rendered into the diagram file as raw Markdown/HTML

- **Severity:** Low — only people and agents who can write `CHAT.md` can inject, but the output is a file viewers (for example on GitHub) render, and an external image or link would phone home or mislead.
- **Status:** Fixed
- **Verdict:** No blocking findings
- **Date / author:** 2026-10-31 / Switch
- **Affected:** `bobp/tools/chat_diagram.py` — `_recap_details` and the "starts" text in `build_blocks` (new in 0.2.0)
- **Class / reference:** Output encoding / Markdown injection (CWE-79 class, mitigated by GitHub's sanitizer)

## Next Action

| Who | Does what | By / trigger |
|---|---|---|
| Neo | Escape chat-derived text in recap bullets and phase goals (HTML-escape `<`, `>`, `&`; neutralize Markdown links and images, e.g. escape `[`, `]`, `!`, backticks) and add a test | Before the next release |
| Trin | Review the new regression test | After Neo's change |
| Switch | Re-run the reproduction below | After Neo's change |

## Evidence

- **Reproduce / detect:** `build_blocks` on an entry whose body is `UAT passed <img src=https://example.invalid/x.png> [click](https://example.invalid)` produced the line `- **Trin**: UAT passed <img src=https://example.invalid/x.png> [click](https://example.invalid)` unchanged; a phase body with `![t](https://example.invalid/p.png)` also passed through.
- **Observed:** Mermaid labels are quoted and escaped (`_quote_label`); the new Markdown sections are not. Before the split, the same text lived inside quoted Mermaid labels.
- **Confidence:** High that the text is unescaped; Medium on impact, since GitHub strips scripts but still renders remote images and links.

## Impact and Reachability

Content in chat (including text an agent copied from an untrusted page) can embed a remote image, link, or HTML in the rendered `CHAT.diagram.md` and the archived copies. No script execution is expected under GitHub's sanitizer.

## Recommendation

- **Fix:** Escape or strip Markdown/HTML in `_clean_message` output used for Markdown sections (leave the Mermaid path unchanged).
- **Verify:** New test feeds the strings above and asserts the rendered section contains no raw tag, link, or image; `bobp make test` passes.
- **Alternatives rejected:** Wrapping each bullet in a code span (hurts readability).

## Resolution

Fixed 2026-10-31: `_md_escape` in `bobp/tools/chat_diagram.py` HTML-escapes and backslash-escapes chat-derived text in every Markdown section; regression test `test_chat_text_is_escaped_in_markdown_sections` added. Full suite 110 passed; lint passes.

## Risk Acceptance

Not accepted.
