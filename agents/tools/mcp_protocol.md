# MCP Integration Protocol

**MCP Configuration Location:** `.claude/mcp.json` (workspace-level)

## Priority System

**Before ANY file or tool operation:**
1. Check if relevant MCP tool is available (look for `mcp__*__*` pattern)
2. If available: Use MCP for enhanced functionality, better error handling
3. If unavailable: Fall back to standard Claude Code tools
4. Document which approach was used in state files

## Requesting MCP Installation

If you need an MCP that isn't installed:
```
@User I need '[mcp-name]' MCP for [specific use-case].
Configuration should be saved in workspace .claude/mcp.json
Should I proceed with fallback or install the MCP?
```

## Verification

Check available MCPs: `claude mcp list`

## Tool Documentation

See individual tool files in `agents/tools/` for specific MCP capabilities:
- `filesystem_mcp.md` - File operations
- `git_mcp.md` - Version control
- `testing_mcp.md` - Test execution
- `code_analysis_mcp.md` - Code quality
- `search_mcp.md` - Documentation search
- `debug_mcp.md` - Debugging
- `task_management_mcp.md` - Sprint tracking
- And others...
