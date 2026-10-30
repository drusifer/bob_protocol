<!--
Persona skill template. Owned by Bob — see `agents/bob/SKILL.md`.
Copy this scaffold into `agents/<name>/SKILL.md`, replace placeholders, and remove this note
and the rubric block before saving the generated persona skill.
-->
---
name: agent-name
description: When to use this agent...
---

# Agent Name - Role Title

> **Protocol**: This agent uses the Bob Protocol.

## Role
[Agent's mission and responsibilities]

## Command Interface
[Commands this agent responds to]

## Triggers (optional)
[Invocation phrases not already clear from the command interface]

## Requires (optional)
[Prerequisite shared skills; link to their canonical instructions]

## State Management Protocol (CRITICAL)
See instructions here -> agents/skills/bob-protocol/SKILL.md

**<Persona> Tweaks:**
- **State File**: `agents/<name>/state.md` (Context, Current Task, Next Steps sections).
- [Any persona-specific state or handoff overrides]

## Via Integration
See instructions here -> agents/skills/via/SKILL.md

**<Persona> Tweaks:**
- [Any persona-specific via query patterns or constraints]

<!-- RUBRIC-START -->
## Check — PERSONA SKILL

Before approving a new or materially revised persona `SKILL.md`, check every item. The result is **PASS** only when all items pass; otherwise record **FAIL** with the unmet item and fix it before sign-off.

- [ ] **Purpose and activation:** Frontmatter has only supported fields (`name`, `description` at minimum); name matches the persona directory, and description says what the agent does and when to use it.
- [ ] **Distinct role:** Responsibilities and decision authority are explicit, useful, and do not duplicate or contradict another persona’s ownership.
- [ ] **Actionable behavior:** Instructions define how to handle the persona’s common tasks, expected outputs, and relevant completion or review gates; vague traits alone are not used as procedure.
- [ ] **Boundaries and judgment:** Scope, escalation, user-question, and approval rules are clear where consequential; routine choices follow project convention.
- [ ] **Protocol and dependencies:** Required shared skills are named and linked to canonical files; state, chat, and handoff rules follow the shared protocol without copying it unnecessarily.
- [ ] **Tool and repository fit:** Commands, paths, and integrations exist in this repository and are used only for work that needs them; no assumed project capability is invented.
- [ ] **Consistency:** No contradictory, stale, or repeated instructions; persona-specific overrides are clearly identified.
- [ ] **Usability and size:** Headings make instructions scannable, examples clarify non-obvious behavior, and detailed reference material is linked instead of bloating the main skill.
- [ ] **Behavior check:** At least one representative request can be followed from activation through a verifiable result without guessing about role, next action, or handoff.

Validate supported frontmatter, repository paths and commands, behavior instructions, and the packaged copy.
<!-- RUBRIC-END -->
