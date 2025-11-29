# Task Management MCP

**Tool Pattern:** `mcp__tasks__*`

## Purpose
Advanced task tracking, sprint coordination, and team metrics.

## Primary Commands

- `tasks__list` - List tasks with filters and sorting
- `tasks__status` - Get detailed task status and progress
- `tasks__metrics` - Generate velocity and cycle time metrics
- `tasks__dependencies` - Visualize task dependencies
- `tasks__burndown` - Generate sprint burndown charts
- `tasks__assign` - Track and manage task assignments

## When to Use

- Sprint status reporting
- Task tracking and coordination
- Velocity calculations
- Dependency management
- Burndown chart generation
- Team workload balancing

## Fallback

Manual task.md parsing with Read/Edit tools

## Example Usage

```
# Check for MCP
[Look for mcp__tasks__status]

# With MCP
mcp__tasks__status filter="in_progress"

# Without MCP (fallback)
Read task.md and parse manually
```

## Benefits

- Automated task parsing
- Rich status reporting
- Dependency visualization
- Velocity tracking
- Burndown charts
- Assignment management
