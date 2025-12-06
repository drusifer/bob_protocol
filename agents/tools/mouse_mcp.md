# Mouse MCP Service

**Tool Pattern**: `mcp__mouse__*`

**Purpose**: Manages the sprint, tracks tasks, and reports on team velocity as a service.

**Role**: 🐭 Scrum Master - Sprint coordination, task tracking, and metrics

## CRITICAL: Chat Log Protocol

**EVERY time you use a Mouse MCP command, you MUST log it to `chat-log.md`:**

```markdown
[TIMESTAMP] [Mouse] mcp__mouse__command parameter="value"
[TIMESTAMP] [Mouse] Result: [brief summary of outcome]
```

## CRITICAL: Working Directory Constraint

**All file operations MUST be confined to the project root directory and subdirectories.**
- ✅ Work with files at or below the current working directory
- ❌ Never access files outside the project directory
- ✅ Use relative paths from project root

## Primary Commands

- `mouse__plan_sprint` - Creates a new sprint plan, breaking down user stories into specific, trackable tasks.
- `mouse__status` - Provides a real-time status report of the current sprint, showing what's to do, in progress, blocked, and done.
- `mouse__update_task` - Updates the status of a specific task in the sprint board (e.g., moves it from 'in_progress' to 'done').
- `mouse__velocity` - Reports on the team's historical and current velocity to aid in future planning.
- `mouse__identify_blockers` - Scans the current sprint board to identify and flag any tasks that are blocked.

## When to Use

- At the beginning of a sprint to create a task board.
- Daily, to get a status update or run a "stand-up".
- Whenever a developer finishes a task, to update the board.
- During sprint retrospectives, to analyze performance.

## CRITICAL: Work in Short Sprints

**Track progress frequently. Keep status updates lightweight.**
- ✅ Quick status updates after each agent action
- ❌ Don't spend cycles generating elaborate reports
- ✅ Update one task status, then hand back to working agents
- ✅ Flag blockers immediately and delegate resolution

## Collaboration with Other Agents

Mouse coordinates the team's workflow:

- Receives `mcp__mouse__update_task` from all agents as they complete work
- `mcp__cypher__prioritize` - Request backlog prioritization for sprint planning
- `mcp__morpheus__plan` - Request estimates for sprint planning
- `mcp__oracle__record` - Document sprint retrospective findings
- `mcp__trin__report` - Request quality metrics for sprint reviews

## Fallback

None. This service is the single source of truth for sprint progress.

## Example Usage

```
# Example: Planning a sprint
mcp__mouse__plan_sprint stories=["US-123", "US-124"]

# Example: Getting the daily status
mcp__mouse__status

# Example: Marking a task as complete
mcp__mouse__update_task task_id="T-01" new_status="done"
```

## Benefits

- **Visibility**: Provides a clear, real-time view of the team's work and progress.
- **Process Automation**: Automates the mechanics of sprint management, such as updating task boards and generating reports.
- **Data-Driven Planning**: Uses historical velocity data to make future sprint planning more accurate.
