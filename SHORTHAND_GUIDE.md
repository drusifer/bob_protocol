TL;DR: Use `*fix`, `*impl`, `*plan sprint` for full workflow chains. Use `*chat @Persona *command` for direct single-persona control. All triggers listed below.

# Shorthand Guide — Skill Triggers

## Loop Commands (Multi-Persona Chains)

Use these when you want a full automated workflow, not a single-persona response.

| Command | Chain | Description |
|---------|-------|-------------|
| `*fix <bug>` | Neo → Trin → Morpheus | Investigate, fix, test, and review |
| `*impl <feature>` | Neo → Trin → Morpheus | TDD implementation + UAT + code review |
| `*qa <thing>` | Trin → Morpheus | Test and review without reimplementation |
| `*review <thing>` | Morpheus → Trin | Architecture and quality review |
| `*plan sprint` | Cypher → Smith → Morpheus → Mouse | Full sprint planning with review gates |

---

## Direct Skill Triggers

Invoke a persona directly — bypasses `*chat` routing.

### Neo — Software Engineer
| Trigger | Action |
|---------|--------|
| `*swe impl <task>` | Implement a feature (TDD) |
| `*swe fix <issue>` | Diagnose and fix a bug |
| `*swe test <scope>` | Write and run tests |
| `*swe refactor <target>` | Refactor without changing behaviour |

### Morpheus — Tech Lead
| Trigger | Action |
|---------|--------|
| `*lead arch <topic>` | Architecture review or decision |
| `*lead plan <story>` | Create technical implementation plan |
| `*lead decide <choice>` | Make and record an architectural decision |
| `*lead guide <area>` | Provide technical guidance |
| `*lead refactor <target>` | Plan a refactoring strategy |
| `*lead review <target>` | Review code for architecture alignment |

### Trin — QA Guardian
| Trigger | Action |
|---------|--------|
| `*qa test <scope>` | Run tests (`all`, `unit`, `integration`, or specific) |
| `*qa uat <phase>` | UAT — verify acceptance criteria for a phase |
| `*qa verify <feature>` | Verify a feature meets acceptance criteria |
| `*qa review <change>` | Code review for quality and correctness |
| `*qa report` | Summarise codebase health |
| `*qa repro <issue>` | Create a minimal reproduction of a bug |

### Oracle — Knowledge Officer
| Trigger | Action |
|---------|--------|
| `*ora ask <question>` | Query the knowledge base |
| `*ora record <type> <content>` | Log a decision, lesson, or finding |
| `*ora distill <file>` | Break down a large document with TL;DR + ToC |
| `*ora tldr [glob]` | Write/update TL;DR blocks in project files |
| `*ora groom` | Audit and organise the knowledge base |
| `*ora archive` | Archive old CHAT.md messages (>50-100 messages) |

### Cypher — Product Manager
| Trigger | Action |
|---------|--------|
| `*pm plan sprint` | Define sprint stories and acceptance criteria |
| `*pm story <request>` | Write user stories from a feature request |
| `*pm doc <topic>` | Create or update a PRD or product document |
| `*pm assess <scope>` | Assess feature readiness or completion status |
| `*pm prioritize` | Prioritize the backlog |
| `*pm update` | Post product status update |
| `*pm launch <sprint>` | Close sprint — announce, backlog retro feedback, update changelog |

### Mouse — Scrum Master
| Trigger | Action |
|---------|--------|
| `*sm plan sprint` | Break sprint into short phases (1-3 tasks each) |
| `*sm status` | Report current sprint progress |
| `*sm tasks` | List all active tasks |
| `*sm next` | Identify the next task to work on |
| `*sm blocked` | Report and triage a blocker |
| `*sm done <task>` | Mark a task complete |
| `*sm assign <task> <persona>` | Assign a task to a persona |
| `*sm velocity` | Report team velocity metrics |

### Smith — HCI Expert & UX Advocate
| Trigger | Action |
|---------|--------|
| `*user review <stories>` | Review user stories against HCI principles |
| `*user test <feature>` | Usability-test a feature by running the software |
| `*user consult <question>` | Quick, non-blocking UX opinion |
| `*user feedback <question>` | Deeper investigation of open UX/domain questions |
| `*user research <topic>` | Research comparable tools — ends with `@Oracle *ora record` |
| `*user story <id> <criteria>` | Co-author user-perspective acceptance criteria |
| `*user bug CMD:... \| EXPECTED:... \| ACTUAL:... \| UX ISSUE:...` | File a usability defect |
| `*user approve` | Approve a sprint review gate |
| `*user reject REASON:... \| FIX:...` | Block a sprint gate — both fields required |
| `*user blocked <reason>` | Signal gate cannot complete — escalates to Mouse |

### Bob — Prompt Engineer
| Trigger | Action |
|---------|--------|
| `*prompt <description>` | Create a new agent SKILL.md |
| `*reprompt <instructions>` | Update existing agent prompts |
| `*learn <lesson>` | Broadcast lesson to all agents |
| `*help` | Show full system reference |
| `*bob review <target>` | Review agent interactions and prompt effectiveness |

---

## `*chat` Routing Syntax

```
*chat <message>                    # auto-select persona
*chat @<Persona> *<command> <args> # direct invocation
```

### Examples
```
*chat fix the bug in parser.py
*chat @neo *swe fix bug in parser.py line 42
*chat @trin *qa test all
*chat @oracle *ora ask What's our DB pattern?
*chat @morpheus *lead decide REST vs GraphQL
*chat @cypher *pm story users need CSV export
*chat @mouse *sm status
*chat @bob *reprompt Neo needs to know about the new cache layer
*chat @smith *user review sprint stories
*chat @smith *user test the export command
```

---

## Sprint Cycle Quick Reference

```
*plan sprint
  → Cypher *pm plan sprint
  → [Smith *user approve]         ← gate
  → Morpheus *lead arch sprint
  → [Smith *user approve]         ← gate
  → Mouse *sm plan sprint
  → Morpheus *lead review sprint plan

Per phase (*impl <phase N>):
  → Neo *swe impl <phase>
  → Trin *qa uat <phase>
  → Morpheus *lead review <phase>
  → (fix loop if needed)

Sprint close:
  → Oracle *ora groom
  → Smith *user test + *user feedback
  → All *sprint retro             ← feeds backlog
  → Cypher *pm launch <sprint>
```

---

## Make Targets

```bash
make help                            # list all targets
make tldr                            # TL;DR from all project files
make chat MSG="..." PERSONA="..."    # post to CHAT.md
make test V=-vvv                     # run tests with full output
make diff_bob TARGET=<path>          # diff framework files with a project
make update_bob TARGET=<path>        # push framework updates to a project
make pull_bob SRC=<path>             # pull framework updates from a project
make install_bob TARGET=<path>       # fresh install into a project
make clean_bob                       # reset state files and symlinks
```
