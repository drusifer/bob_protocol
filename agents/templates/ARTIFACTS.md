# Artifacts and Rubrics

What the agents are expected to produce, which of those have a template and a rubric, and how a
rubric is written and used. Maintained by Bob; reviewed whenever a persona, skill or template is
added.

## Why rubrics

A template tells an author what sections to fill in. It cannot tell a reviewer whether what was
written is any good. A rubric does that: a short set of criteria, each describing what weak,
acceptable and strong work looks like, so that a review is a judgement against something
written down rather than taste. Rubrics here guide a reviewer; nothing computes a score.

## Artifact inventory

| Artifact | Lives in | Author | Template | Rubric | Reviewed by, when |
|---|---|---|---|---|---|
| Sprint stories | `docs/sprints/USER_STORIES_SPRINT<N>.md` | Cypher | `_template_USER_STORIES.md` | **STORIES** | Smith, Gate 1 |
| SDLC | `docs/SDLC.md` | Tank | `_template_SDLC.md`, `.python.md`, `.javascript.md` | **SDLC** | Oracle, at groom when it changed |
| Lessons | `docs/LESSONS.md`, `agents/oracle/lessons.md` | Oracle | `_template_LESSON.md` | **LESSON** | Smith, at the close test |
| Architecture section / `docs/ARCH.md` | sprint stories document; `docs/ARCH.md` | Morpheus | `_template_ARCH.md` | none yet | Smith, Gate 2 |
| Decisions | `docs/DECISIONS.md` | Oracle | none | none | — |
| Task board, sprint log | `task.md`, `agents/mouse/sprint_log.md` | Mouse | none | none | Morpheus, plan review |
| Work summary | `agents/<persona>/<Task>_Summary_<timestamp>.md` | any | none | none | — |
| Gate verdicts, UAT results, code reviews | `agents/CHAT.md` | Smith, Trin, Morpheus | none (chat) | none | — |
| Sprint chat report | `agents/chat_archive/CHAT_<SPRINT>*.md` | Oracle, via `bobp chat-report` | generated | none | — |
| Persona instructions | `agents/<persona>/SKILL.md`, `agents/skills/<name>/SKILL.md` | Bob | inline in Bob's instructions | none yet | — |
| Persona state | `agents/<persona>/state.md` | each persona | `_template_state.md` | none — see below | — |
| Chat messages | `agents/CHAT.md` | all | `_template_CHAT.md` | none — see below | — |
| TLDR blocks | top of `.py` / `.md` files | Oracle | `_template_tldr.md` | none — see below | — |
| Research finding | persona folder | any | `_template_finding.md` | none yet | — |

**Deliberately without a rubric:** persona state, chat messages and TLDR blocks. They go wrong in
mechanical ways — too long, stale, a missing section, the wrong format — and a check that can be
run (a length limit, a required-heading test) catches those better than a reviewer's judgement.

**"None yet"** marks artifacts that have a template and would suit a rubric. Architecture is the
next candidate: it already has an independent reviewer and a gate.

## Rubric format

A rubric is the last thing in a template, between two marker lines so it can be removed cleanly:

```markdown
<!-- RUBRIC-START — for reviewers. Delete everything from here to RUBRIC-END when you turn this
     template into a real document. -->
## Appendix: Review rubric — <NAME>

Reviewed by <who> at <step>. Verdict line: `rubric <NAME>: CODE=L CODE=L ...`

| Code | Criterion | Weak (W) | Acceptable (A) | Strong (S) |
|---|---|---|---|---|
| `CODE` | The question this criterion asks | What you would see | What you would see | What you would see |
<!-- RUBRIC-END -->
```

Rules for writing one:

- **Four to six criteria.** More than that and reviewers stop reading them.
- **Each criterion asks one question** about the document's usefulness to its reader — not
  whether a section exists (the template already ensures that).
- **Describe each level by what a reviewer can observe**, with a concrete tell where possible
  ("an acceptance criterion contains 'should' or 'properly'"), not by adjectives.
- **Codes are short and unique within the rubric**, so a verdict fits on one line.
- **Weak means the document fails its reader on that point**, not that it could be nicer.

## Applying a rubric

1. **The author self-checks** before handing off, and fixes anything they would call Weak.
2. **An independent reviewer** — never the author — applies it at the step named in the rubric.
3. **The reviewer reports a verdict line** in their chat message, one level per criterion:

   ```
   rubric STORIES: OUT=S TEST=A SCOPE=A FAIL=W SIZE=A DESIGN=A
   ```

4. **Verdict rule:** every criterion Acceptable or better → pass. Any Weak → reject, naming the
   criterion and the fix. Strong is recognition, never a requirement.
5. **A rejection says why.** For each Weak, one sentence quoting or pointing at the offending
   text and one saying what would make it Acceptable. If that does not fit in the chat message
   (512 characters), put the detail in a file in the reviewer's folder and cite it.
6. **A criterion that does not apply** is reported as `CODE=n/a` with a reason; it does not count
   as Weak.

Disagreement between author and reviewer about a level goes to the user, not back and forth —
the usual two-attempt limit on fix loops applies.

## Adding a rubric to another template

1. Confirm the artifact has an independent reviewer and an existing step where review happens.
   If it has neither, a rubric will not be used — fix that first or do not add one.
2. Write the appendix in the format above. Draw criteria from how the artifact has actually
   failed its readers in the past, not from general principles.
3. Calibrate: apply it to at least three existing examples of differing quality. If everything
   passes, or two reviewers would plausibly disagree on a level, reword the criterion.
4. Name the rubric in the reviewer's and the author's instructions.
5. Add the row to the inventory above.

## Keeping rubrics out of finished documents

A rubric belongs to the template. Authors delete the block between the markers when they
instantiate a template. Oracle's groom checks that no file outside `agents/templates/` has a line
beginning `<!-- RUBRIC-START` (`grep -rn '^<!-- RUBRIC-START' --include='*.md' .`). Mentioning
the marker in prose is fine; carrying the block is not.
