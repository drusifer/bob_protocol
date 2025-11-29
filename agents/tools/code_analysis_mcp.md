# Code Analysis MCP

**Tool Pattern:** `mcp__analysis__*`

## Purpose
Automated code quality analysis, smell detection, and architectural insights.

## Primary Commands

- `analysis__complexity` - Measure cyclomatic complexity
- `analysis__dependencies` - Visualize module dependencies
- `analysis__smells` - Detect code smells automatically
- `analysis__metrics` - Generate comprehensive code quality metrics
- `analysis__coverage_gaps` - Identify untested code paths
- `analysis__duplication` - Find duplicate code

## When to Use

- Architectural reviews
- Refactoring planning
- Code quality assessment
- Finding testability issues
- Identifying technical debt

## Fallback

Manual code review using Read, Grep, and analysis

## Example Usage

```
# Check for MCP
[Look for mcp__analysis__smells]

# With MCP
mcp__analysis__smells path="src/" severity="medium"

# Without MCP (fallback)
Manual review with Grep for patterns
```

## Benefits

- Automated smell detection
- Complexity metrics
- Dependency visualization
- Coverage gap identification
- Duplication detection
- Actionable refactoring suggestions
