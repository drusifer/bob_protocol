# Editor MCP

**Tool Pattern:** `mcp__editor__*`

## Purpose
Structured editing operations for bulk updates and formatting.

## Primary Commands

- `editor__search_replace` - Bulk find and replace across files
- `editor__insert` - Insert text at specific locations
- `editor__format` - Apply consistent formatting
- `editor__refactor` - Safe refactoring operations
- `editor__template` - Apply templates to files

## When to Use

- Bulk updates across multiple files
- Systematic refactoring
- Consistent formatting application
- Template-based file generation
- Safe rename operations

## Fallback

Standard Edit tool with manual operations

## Example Usage

```
# Check for MCP
[Look for mcp__editor__search_replace]

# With MCP
mcp__editor__search_replace pattern="old_name" replacement="new_name" scope="agents/"

# Without MCP (fallback)
Multiple Edit tool calls
```

## Benefits

- Bulk operations
- Safe refactoring
- Consistent formatting
- Template application
- Preview before apply
