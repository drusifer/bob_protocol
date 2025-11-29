# Filesystem MCP

**Tool Pattern:** `mcp__filesystem__*`

## Purpose
Advanced file operations with better error handling, validation, and metadata support.

## Primary Commands

- `filesystem__read` - Read files with encoding detection
- `filesystem__write` - Create/update files with validation
- `filesystem__list` - Browse directory structure
- `filesystem__search` - Search files by name or content
- `filesystem__move` - Move/rename files safely
- `filesystem__tree` - Visualize directory hierarchy
- `filesystem__watch` - Monitor file changes

## When to Use

- ALL file read/write operations (preferred over standard Read/Write)
- Directory browsing and organization
- File searching and navigation
- Safe file moves and renames

## Fallback

Standard Claude Code tools: Read, Write, Glob, Edit

## Example Usage

```
# Check for MCP
[Look for mcp__filesystem__read]

# With MCP
mcp__filesystem__read path="/path/to/file.md"

# Without MCP (fallback)
Read file_path="/path/to/file.md"
```

## Benefits

- Automatic encoding detection
- Better error messages
- File metadata (size, modified date)
- Safe atomic writes
- Path validation
