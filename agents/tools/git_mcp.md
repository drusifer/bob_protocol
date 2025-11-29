# Git MCP

**Tool Pattern:** `mcp__git__*`

## Purpose
Enhanced git operations with rich context and better integration.

## Primary Commands

- `git__status` - Get working directory status with details
- `git__diff` - View changes with syntax highlighting
- `git__log` - Review commit history with filters
- `git__blame` - See who changed specific lines
- `git__commit` - Create commits with validation
- `git__branch` - Manage branches
- `git__stats` - Generate contribution statistics
- `git__activity` - Track team activity patterns
- `git__bisect` - Find regression introduction point

## When to Use

- Version control operations
- Code review workflows
- Tracking changes over time
- Understanding code evolution
- Sprint metrics (commit history)

## Fallback

Standard Bash git commands via Bash tool

## Example Usage

```
# Check for MCP
[Look for mcp__git__diff]

# With MCP
mcp__git__diff path="src/" staged=true

# Without MCP (fallback)
Bash: git diff --staged src/
```

## Benefits

- Rich formatted output
- Better error handling
- Integrated with file operations
- Statistical analysis built-in
- Smart filtering and searching
