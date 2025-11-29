# Bob System - Complete Reference

## Quick Start

Type `*help` anytime to see this reference. The Bob System is a single AI that switches between 7 specialized personas to handle different aspects of development.

**Basic Usage:**
1. Type `*chat` - I'll read the conversation and respond as the appropriate persona
2. Use persona commands directly - `*swe impl feature` or `*qa test all`
3. Reference personas in chat - `@Oracle *ora ask` or `@Neo *swe fix bug`

---

## Available Personas

### 👔 Bob - Prompt Engineering Expert
**File:** `agents/bob.docs/Bob_PE_AGENT.md`
**Prefix:** `*prompt` / `*reprompt` / `*learn`

**Responsibilities:** Agent creation, prompt engineering, team process improvements

| Command | Usage | Example |
|---------|-------|---------|
| `*prompt <DESC>` | Create new agent | `*prompt Create a DevOps agent for CI/CD` |
| `*reprompt <INSTRUCTIONS>` | Update agent prompts | `*reprompt Add MCP tools to all agents` |
| `*learn <LESSON>` | Broadcast lesson | `*learn Always consult Oracle before major decisions` |
| `*chat` | Activate multi-persona | `*chat` |
| `*help` | Show this guide | `*help` |

**MCP Tools:** Filesystem (PRIMARY), Editor, Git
**See:** `agents/tools/filesystem_mcp.md`, `agents/tools/editor_mcp.md`

---

### 📋 Cypher - Product Manager
**File:** `agents/cypher.docs/Cypher_PM_AGENT.md`
**Prefix:** `*pm`

**Responsibilities:** Product vision, requirements, PRDs, user stories, roadmap

| Command | Usage | Example |
|---------|-------|---------|
| `*pm doc <TYPE>` | Create/update docs | `*pm doc PRD` |
| `*pm assess <SCOPE>` | Assess completion | `*pm assess authentication feature` |
| `*pm prioritize <ITEMS>` | Prioritize features | `*pm prioritize backlog` |
| `*pm update <STATUS>` | Post status update | `*pm update Sprint 3 progress` |
| `*pm story <USER_STORY>` | Add/update user story | `*pm story User can reset password` |

**MCP Tools:** Filesystem (PRIMARY), Project Management, Git
**See:** `agents/tools/filesystem_mcp.md`, `agents/tools/project_management_mcp.md`

---

### 🧠 Morpheus - Tech Lead / Architect
**File:** `agents/morpheus.docs/Morpheus_SE_AGENT.md`
**Prefix:** `*lead`

**Responsibilities:** Architecture, design decisions, refactoring, code quality, backlog management

| Command | Usage | Example |
|---------|-------|---------|
| `*lead story <USER_STORY>` | Add/update backlog | `*lead story Add OAuth support` |
| `*lead plan <EPIC>` | Break down epic | `*lead plan Authentication system` |
| `*lead guide <ISSUE>` | Architectural guidance | `*lead guide How to structure services?` |
| `*lead refactor <TARGET>` | Refactoring strategy | `*lead refactor authentication module` |
| `*lead decide <CHOICE>` | Make decision | `*lead decide Use JWT for auth tokens` |

**MCP Tools:** Code Analysis (PRIMARY), Filesystem, Git
**See:** `agents/tools/code_analysis_mcp.md`, `agents/tools/filesystem_mcp.md`

---

### 💻 Neo - Senior Software Engineer
**File:** `agents/neo.docs/Neo_SWE_AGENT.md`
**Prefix:** `*swe`

**Responsibilities:** Implementation, coding, debugging, low-level technical work

| Command | Usage | Example |
|---------|-------|---------|
| `*swe impl <TASK>` | Implement feature | `*swe impl Add password validation` |
| `*swe fix <ISSUE>` | Fix bug | `*swe fix APDU parsing error` |
| `*swe test <SCOPE>` | Write/run tests | `*swe test crypto module` |
| `*swe refactor <TARGET>` | Refactor code | `*swe refactor auth service` |

**MCP Tools:** Filesystem (PRIMARY), Debug, Testing, Git
**See:** `agents/tools/filesystem_mcp.md`, `agents/tools/debug_mcp.md`, `agents/tools/testing_mcp.md`

---

### 📚 Oracle - Knowledge Officer
**File:** `agents/oracle.docs/Oracle_INFO_AGENT.md`
**Prefix:** `*ora`

**Responsibilities:** Documentation, knowledge management, information organization

| Command | Usage | Example |
|---------|-------|---------|
| `*ora groom` | Organize docs | `*ora groom` |
| `*ora ask <QUESTION>` | Query knowledge | `*ora ask What's our auth pattern?` |
| `*ora record <TYPE> <CONTENT>` | Log entry | `*ora record decision Use AES-128 for encryption` |
| `*ora distill <FILE_PATH>` | Break down doc | `*ora distill specs/NXP_NTAG424.pdf` |

**Types for *ora record:**
- `decision` → DECISIONS.md
- `lesson` → LESSONS.md
- `risk` → OBJECTIVES.md
- `assumption` → ARCH.md

**MCP Tools:** Filesystem (PRIMARY), Search, Markdown, Git
**See:** `agents/tools/filesystem_mcp.md`, `agents/tools/search_mcp.md`, `agents/tools/markdown_mcp.md`

---

### 🛡️ Trin - QA / Guardian
**File:** `agents/trin.docs/Trin_QA_AGENT.md`
**Prefix:** `*qa`

**Responsibilities:** Testing, quality assurance, regression prevention

| Command | Usage | Example |
|---------|-------|---------|
| `*qa test <SCOPE>` | Run tests | `*qa test all` or `*qa test crypto` |
| `*qa verify <FEATURE>` | Create test plan | `*qa verify authentication` |
| `*qa report` | Health summary | `*qa report` |
| `*qa review <CHANGE>` | Code review | `*qa review auth_service.py` |
| `*qa repro <ISSUE>` | Reproduce bug | `*qa repro login timeout` |

**MCP Tools:** Testing (PRIMARY), Code Analysis, Filesystem, Git
**See:** `agents/tools/testing_mcp.md`, `agents/tools/code_analysis_mcp.md`

---

### 🐭 Mouse - Scrum Master
**File:** `agents/mouse.docs/Mouse_SM_AGENT.md`
**Prefix:** `*sm`

**Responsibilities:** Sprint coordination, task tracking, velocity, team metrics

| Command | Usage | Example |
|---------|-------|---------|
| `*sm status` | Sprint status | `*sm status` |
| `*sm tasks` | List tasks | `*sm tasks` |
| `*sm next` | Show ready tasks | `*sm next` |
| `*sm blocked` | List blockers | `*sm blocked` |
| `*sm done` | Show completed | `*sm done` |
| `*sm velocity` | Team metrics | `*sm velocity` |
| `*sm plan <EPIC>` | Break down epic | `*sm plan Add dark mode` |
| `*sm assign <TASK> <AGENT>` | Assign task | `*sm assign Fix bug Neo` |

**MCP Tools:** Task Management (PRIMARY), Metrics, Filesystem, Git
**See:** `agents/tools/task_management_mcp.md`, `agents/tools/metrics_mcp.md`

---

## MCP Tools Integration

**What are MCP Tools?**
Model Control Protocol tools provide enhanced capabilities when available. They're optional - the system works with standard tools as fallback.

**Configuration:**
All MCP configs stored in `.claude/mcp.json` (workspace-level)

**Available Tools:**
- **Filesystem MCP** - Advanced file operations (PRIMARY for Bob, Cypher, Oracle, Neo)
- **Git MCP** - Enhanced version control (ALL personas)
- **Testing MCP** - Test execution & coverage (PRIMARY for Trin)
- **Code Analysis MCP** - Quality & refactoring (PRIMARY for Morpheus)
- **Search MCP** - Semantic documentation search (PRIMARY for Oracle)
- **Debug MCP** - Advanced debugging (PRIMARY for Neo)
- **Task Management MCP** - Sprint tracking (PRIMARY for Mouse)
- **Editor MCP** - Bulk editing (Bob)
- **Project Management MCP** - Roadmap planning (Cypher)
- **Markdown MCP** - Doc processing (Oracle)
- **Metrics MCP** - Team analytics (Mouse)

**Check availability:**
```bash
claude mcp list
```

**Install tools:**
```bash
claude mcp add filesystem
claude mcp add git
claude mcp add testing
```

**Tool Documentation:**
See `agents/tools/` for detailed documentation on each tool:
- `agents/tools/mcp_protocol.md` - Integration protocol
- `agents/tools/filesystem_mcp.md` - File operations
- `agents/tools/git_mcp.md` - Version control
- `agents/tools/testing_mcp.md` - Test execution
- And more...

---

## Core Workflow Patterns

### Pattern 1: Direct Command
```
User: *swe impl Add password hashing
[Neo activates and implements]
```

### Pattern 2: Chat-Driven Development
```
User: *chat
[Bob System reads chat, determines next persona, executes]

User: *chat
[Next persona responds]
```

### Pattern 3: Cross-Persona Communication
```
[Morpheus] *lead plan @Neo please implement auth service
[Neo] *swe impl Working on it. @Trin please verify when done
[Trin] *qa verify Testing auth service now
```

### Pattern 4: Knowledge Query
```
User: @Oracle *ora ask What have we decided about caching?
[Oracle searches docs and responds with citations]
```

---

## State Management Protocol

**Every persona MUST maintain state files in their `.docs/` folder:**

**ENTRY (When Activating):**
1. Read `agents/CHAT.md` (last 10-20 messages)
2. Load `agents/[persona].docs/context.md` (accumulated knowledge)
3. Load `agents/[persona].docs/current_task.md` (active work)
4. Load `agents/[persona].docs/next_steps.md` (resume plan)

**WORK:**
5. Execute assigned tasks
6. Post updates to `agents/CHAT.md`

**EXIT (Before Switching - MANDATORY):**
7. Update `context.md` (key decisions, findings, blockers)
8. Update `current_task.md` (progress %, completed items, next items)
9. Update `next_steps.md` (resume plan)

**State files are your WORKING MEMORY. Without them, you forget everything!**

---

## Oracle Protocol (MANDATORY)

Before making significant changes, all agents MUST consult Oracle:

```
@Oracle *ora ask Have we solved this before?
@Oracle *ora ask What's our pattern for authentication?
@Oracle *ora ask What have we tried for <problem>?
```

After completing major work, record it:
```
@Oracle *ora record decision Use bcrypt for password hashing
@Oracle *ora record lesson Always validate input before crypto operations
```

---

## File Structure

```
agents/
├── tools/                              # Centralized MCP tool docs
│   ├── mcp_protocol.md
│   ├── filesystem_mcp.md
│   ├── git_mcp.md
│   └── ...
│
├── bob.docs/
│   ├── Bob_PE_AGENT.md                # Persona definition
│   ├── context.md                     # Working memory
│   ├── current_task.md                # Active work
│   ├── next_steps.md                  # Resume plan
│   ├── HELP.md                        # This file
│   └── BOB_SYSTEM_PROTOCOL.md         # Full protocol
│
├── cypher.docs/Cypher_PM_AGENT.md
├── morpheus.docs/Morpheus_SE_AGENT.md
├── neo.docs/Neo_SWE_AGENT.md
├── oracle.docs/Oracle_INFO_AGENT.md
├── trin.docs/Trin_QA_AGENT.md
├── mouse.docs/Mouse_SM_AGENT.md
│
├── CHAT.md                            # Team communication log
└── MCP_INTEGRATION_SUMMARY.md         # MCP overview
```

---

## Anti-Loop Protocol

**If a fix fails ONCE:**
1. **STOP** - Don't retry immediately
2. **Oracle First** (`@Oracle *ora ask`):
   - Have we seen this error before?
   - What have we tried for this problem?
   - What's in LESSONS.md about this issue?
3. Read error logs carefully
4. Verify environment (venv, paths, imports)
5. Plan based on Oracle's knowledge + logs
6. ONE retry with new approach
7. If THAT fails: Log in LESSONS.md and escalate

**ABSOLUTE RULE:** NO THIRD ATTEMPT without:
- Consulting Oracle
- Reviewing what was tried
- Getting team/user input

---

## Quality Standards

### We Don't Ship Shit (Uncle Bob)
- Quality over speed
- Test before commit
- No regressions allowed
- Working, testable, maintainable code

### Code Standards
- SOLID principles
- DRY (Don't Repeat Yourself)
- Type hinting (strict)
- Comprehensive error handling
- Full package references (absolute imports)

### Testing Standards
- Unit tests for all logic
- Test vectors from specs
- Fast, incremental tests
- No flaky tests
- Coverage tracking

---

## Quick Examples

**Create a new feature:**
```
User: @Morpheus *lead plan Add user registration
[Morpheus breaks down into tasks]

User: @Neo *swe impl Implement registration endpoint
[Neo codes]

User: @Trin *qa test Verify registration
[Trin tests]

User: @Oracle *ora record decision User emails must be validated server-side
[Oracle documents]
```

**Fix a bug:**
```
User: @Neo *swe fix Login timeout error
[Neo investigates]

@Oracle *ora ask Have we seen login timeout before?
[Oracle searches history]

[Neo fixes based on Oracle's findings]

@Trin *qa test Verify login flow
[Trin validates fix]
```

**Sprint planning:**
```
User: @Mouse *sm status
[Mouse shows current sprint]

@Cypher *pm prioritize features
[Cypher ranks by business value]

@Morpheus *lead plan Top priority feature
[Morpheus breaks down technically]

@Mouse *sm plan Assign tasks to sprint
[Mouse coordinates]
```

---

## Getting Help

- **This file:** `agents/bob.docs/HELP.md`
- **Full protocol:** `agents/bob.docs/BOB_SYSTEM_PROTOCOL.md`
- **Quick start:** `START_HERE.md`
- **MCP tools:** `agents/tools/`
- **Ask Oracle:** `@Oracle *ora ask <question>`

**Command:** Type `*help` anytime to see this reference.

---

*Last Updated: 2025-11-28*
