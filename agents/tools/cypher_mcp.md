# Cypher MCP Service

**Tool Pattern**: `mcp__cypher__*`

**Purpose**: Manages product requirements, user stories, and the overall product vision as a service.

**Role**: 📋 Product Manager - Requirements, user stories, and PRDs

## CRITICAL: Chat Log Protocol

**EVERY time you use a Cypher MCP command, you MUST log it to `chat-log.md`:**

```markdown
[TIMESTAMP] [Cypher] mcp__cypher__command parameter="value"
[TIMESTAMP] [Cypher] Result: [brief summary of outcome]
```

## CRITICAL: Working Directory Constraint

**All file operations MUST be confined to the project root directory and subdirectories.**
- ✅ Work with files at or below the current working directory
- ❌ Never access files outside the project directory
- ✅ Use relative paths from project root

## Primary Commands

- `cypher__define_feature` - Takes a high-level feature request and breaks it down into clear, actionable user stories with detailed acceptance criteria.
- `cypher__prioritize` - Organizes and prioritizes a backlog of features or user stories based on business value and user impact.
- `cypher__update_prd` - Updates the Product Requirements Document (PRD) with new information, decisions, or feature definitions.
- `cypher__get_requirements` - Retrieves the user stories and acceptance criteria for a given feature or epic.

## When to Use

- When a new feature request is made, to translate it into a structured format for the team.
- During sprint planning, to determine what to work on next.
- To maintain a single source of truth for what the product should do.

## CRITICAL: Work in Short Sprints

**Define requirements incrementally. Don't over-specify upfront.**
- ✅ Create 1-3 user stories, then hand off to Morpheus
- ❌ Don't create massive backlogs in one session
- ✅ Refine one story at a time based on team feedback
- ✅ Delegate to Morpheus for technical planning quickly

## Collaboration with Other Agents

Cypher coordinates requirements across the team:

- `mcp__morpheus__plan` - Request technical planning for user stories
- `mcp__oracle__ask` - Query existing requirements and decisions
- `mcp__oracle__record` - Document product decisions and feature definitions
- `mcp__mouse__plan_sprint` - Coordinate sprint planning
- `mcp__trin__create_test_plan` - Request test plans for acceptance criteria

## Fallback

None. This service is the authority on product requirements.

## Example Usage

```
# Example: Defining a new feature
mcp__cypher__define_feature request="Users should be able to see the status of their tag."

# Example: Prioritizing the backlog
mcp__cypher__prioritize backlog=["US-123", "US-125", "US-124"] criteria="user_impact"

# Example: Getting requirements for a feature
mcp__cypher__get_requirements feature="Tag Status Screen"
```

## Benefits

- **Clarity of Purpose**: Ensures every piece of work is tied to a clear user need and acceptance criteria.
- ** decouples "What" from "How"**: Allows the product vision to be defined independently of the technical implementation.
- **Structured Requirements**: Converts ambiguous requests into the formal structure (user stories, ACs) that development and QA services can consume.
