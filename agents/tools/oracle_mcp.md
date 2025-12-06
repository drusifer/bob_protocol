# Oracle MCP Service

**Tool Pattern**: `mcp__oracle__*`

**Purpose**: Manages the project's knowledge base, documentation, and symbol index as a service. Acts as the team's long-term memory.

**Role**: 📚 Knowledge Officer - Documentation and knowledge base management

## CRITICAL: Chat Log Protocol

**EVERY time you use an Oracle MCP command, you MUST log it to `chat-log.md`:**

```markdown
[TIMESTAMP] [Oracle] mcp__oracle__command parameter="value"
[TIMESTAMP] [Oracle] Result: [brief summary of outcome]
```

## CRITICAL: Working Directory Constraint

**All file operations MUST be confined to the project root directory and subdirectories.**
- ✅ Work with files at or below the current working directory
- ❌ Never access files outside the project directory
- ✅ Use relative paths from project root

## Primary Commands

- `oracle__ask` - Answers a question by searching all project documentation, including code, markdown files, and previous decisions.
- `oracle__record` - Records a new piece of information (e.g., an architectural decision, a lesson learned, a user request) into the appropriate knowledge base file.
- `oracle__groom` - Organizes, refactors, and de-duplicates content within the knowledge base to keep it clean and usable.
- `oracle__distill` - Summarizes a long document, chat history, or code file into key points and a concise summary.
- `oracle__index` - Scans the codebase and regenerates the `SYMBOL_INDEX.md` to keep it up-to-date.

## When to Use

- Before starting any task, to retrieve existing context, decisions, or code structure.
- After a decision is made, to ensure it is recorded for future reference.
- To understand the purpose of a piece of code or the history of a feature.
- When the documentation becomes messy or outdated.

## CRITICAL: Work in Short Sprints

**Respond to queries quickly. Record decisions immediately.**
- ✅ Answer questions with concise, relevant information
- ✅ Record one decision at a time
- ❌ Don't reorganize entire documentation in one session
- ✅ Hand back to requesting agent after each query/record operation

## Collaboration with Other Agents

Oracle supports all agents with knowledge:

- Responds to `mcp__oracle__ask` from any agent
- Accepts `mcp__oracle__record` requests from any agent
- `mcp__morpheus__review` - Request review of documentation structure
- `mcp__mouse__status` - Query project progress for documentation updates

## Fallback

None. This service is the single source of truth for project knowledge.

## Example Usage

```
# Example: Asking a question
mcp__oracle__ask question="What is the established pattern for handling async operations in the TUI?"

# Example: Recording a decision
mcp__oracle__record decision="All new TUI screens must use the WorkerManager to handle blocking I/O." file="DECISIONS.md"

# Example: Summarizing a file
mcp__oracle__distill file_path="agents/CHAT.md"
```

## Benefits

- **Reduces "Re-work"**: Prevents the team from re-solving problems or re-making decisions by providing historical context.
- **On-demand Knowledge**: Makes the project's entire knowledge base instantly searchable via a simple API call.
- **Structured Memory**: Ensures that important information is captured and stored in a structured, accessible way.
