TL;DR: Use `*chat @Persona *command args` for explicit invocation, or just `*command args` as a direct skill trigger. All triggers listed below.

# Shorthand Guide — Skill Triggers

## Direct Skill Triggers

Invoke a persona directly without the `*chat` routing layer:

### Bob — Prompt Engineer
| Trigger | Action |
|---------|--------|
| `*new <description>` | Create a new agent from description |
| `*reprompt <instructions>` | Update existing agent prompts |
| `*learn <lesson>` | Broadcast lesson to all agents |
| `*help` | Show full system reference |

### Cypher — Product Manager
| Trigger | Action |
|---------|--------|
| `*pm story <request>` | Write user stories from a feature request |
| `*pm req <feature>` | Define requirements and acceptance criteria |
| `*pm prioritize` | Prioritize the backlog |
| `*pm update` | Post product status update |
| `*pm doc <topic>` | Create a PRD or product document |

### Morpheus — Tech Lead
| Trigger | Action |
|---------|--------|
| `*lead arch <topic>` | Architecture review or decision |
| `*lead plan <story>` | Create technical implementation plan |
| `*lead decide <choice>` | Make and record an architectural decision |
| `*lead guide <area>` | Provide technical guidance |
| `*lead refactor <target>` | Plan a refactoring strategy |

### Neo — Software Engineer
| Trigger | Action |
|---------|--------|
| `*swe impl <task>` | Implement a feature |
| `*swe fix <issue>` | Diagnose and fix a bug |
| `*swe test <scope>` | Write and run tests |
| `*swe refactor <target>` | Refactor code without changing behaviour |

### Oracle — Knowledge Officer
| Trigger | Action |
|---------|--------|
| `*ora ask <question>` | Query the knowledge base |
| `*ora record <type> <content>` | Log a decision, lesson, or finding |
| `*ora distill <file>` | Break down a large document with TL;DR + ToC |
| `*ora tldr <file or topic>` | Generate a TL;DR summary |
| `*ora groom` | Audit and organise the knowledge base |

### Trin — QA Guardian
| Trigger | Action |
|---------|--------|
| `*qa test <scope>` | Run tests (`all`, `unit`, `integration`, or specific) |
| `*qa verify <feature>` | Verify a feature meets acceptance criteria |
| `*qa review <change>` | Code review for quality and correctness |
| `*qa report` | Summarise codebase health |
| `*qa repro <issue>` | Create a minimal reproduction of a bug |

### Smith — Expert User & UX Advocate
| Trigger | Action |
|---------|--------|
| `*user review <stories>` | Review user stories and acceptance criteria |
| `*user test <feature>` | Usability-test a feature by running the software |
| `*user consult <question>` | Quick, non-blocking UX opinion |
| `*user feedback <question>` | Deeper investigation of open UX/domain questions |
| `*user research <topic>` | Research comparable tools — ends with `@Oracle *ora record` |
| `*user bug CMD: ... \| EXPECTED: ... \| ACTUAL: ... \| UX ISSUE: ...` | File a usability defect |
| `*user approve [gate]` | Approve a sprint review gate |
| `*user reject REASON: ... \| FIX: ...` | Block a sprint gate |
| `*user blocked <reason>` | Signal gate cannot be completed — escalates to Mouse |

### Mouse — Scrum Master
| Trigger | Action |
|---------|--------|
| `*sm status` | Report current sprint progress |
| `*sm plan <sprint>` | Create or update a sprint plan |
| `*sm tasks` | List all active tasks |
| `*sm next` | Identify and assign the next task |
| `*sm blocked` | Report and triage a blocker |
| `*sm done <task>` | Mark a task complete |
| `*sm assign <task> <persona>` | Assign a task to a persona |
| `*sm velocity` | Report team velocity metrics |

---

## `*chat` Routing Syntax

Use `*chat` to let the system auto-select a persona, or target one explicitly:

```
*chat <message>                    # auto-select persona
*chat @<Persona> *<command> <args> # direct invocation
```

### Examples
```
*chat fix the bug in parser.py
*chat @Neo *swe fix bug in parser.py line 42
*chat @Trin *qa test all
*chat @Oracle *ora ask What's our DB pattern?
*chat @Morpheus *lead decide REST vs GraphQL
*chat @Cypher *pm story users need CSV export
*chat @Mouse *sm status
*chat @Bob *reprompt Neo needs to know about the new cache layer
*chat @Smith *user review sprint stories
*chat @Smith *user test <feature>
```

---

## Common Make Targets

```bash
make help          # list all targets
make tldr          # show TL;DR from all project files
make test          # run full test suite
make lint          # run all quality checks
make coverage      # run tests with coverage report
```

Run `make help` in any project to see its full target list.
