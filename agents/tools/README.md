# MCP Tools Documentation

This directory contains centralized documentation for all Model Control Protocol (MCP) tools used by BobProtocol personas.

## What are MCP Tools?

MCP tools provide enhanced capabilities when available, with automatic fallback to standard Claude Code tools. They're completely optional - the system works perfectly without them.

## Available Tools

### Core Integration
- **[mcp_protocol.md](mcp_protocol.md)** - Integration protocol, priority system, verification

### File & Documentation
- **[filesystem_mcp.md](filesystem_mcp.md)** - Advanced file operations with validation
- **[search_mcp.md](search_mcp.md)** - Semantic search across documentation
- **[markdown_mcp.md](markdown_mcp.md)** - Markdown processing, TOC generation, validation

### Development
- **[git_mcp.md](git_mcp.md)** - Enhanced version control with rich context
- **[testing_mcp.md](testing_mcp.md)** - Test execution, coverage, mutation testing
- **[debug_mcp.md](debug_mcp.md)** - Advanced debugging, tracing, profiling
- **[code_analysis_mcp.md](code_analysis_mcp.md)** - Code quality, smell detection, metrics

### Editing & Refactoring
- **[editor_mcp.md](editor_mcp.md)** - Bulk editing, refactoring, templates

### Project Management
- **[task_management_mcp.md](task_management_mcp.md)** - Sprint tracking, task coordination
- **[project_management_mcp.md](project_management_mcp.md)** - Roadmap, prioritization frameworks
- **[metrics_mcp.md](metrics_mcp.md)** - Team analytics, velocity tracking

## Tool Format

Each tool documentation file contains:
- **Purpose** - What the tool does
- **Primary Commands** - Main operations with descriptions
- **When to Use** - Specific use cases
- **Fallback** - What to use when MCP unavailable
- **Example Usage** - Code examples showing MCP vs fallback
- **Benefits** - Why use MCP over standard tools

## Configuration

**Location:** `.claude/mcp.json` (workspace root)

**Check installed MCPs:**
```bash
claude mcp list
```

**Install MCP servers:**
```bash
claude mcp add filesystem
claude mcp add git
claude mcp add testing
# etc...
```

## Integration Protocol

All personas follow this protocol:

1. **Check** - Look for `mcp__*__*` tools
2. **Use** - If available, use MCP for enhanced functionality
3. **Fallback** - If unavailable, use standard tools
4. **Document** - Note which approach was used in state files

See [mcp_protocol.md](mcp_protocol.md) for complete details.

## Persona-to-Tool Mappings

### Primary Tool Assignments

- **Bob (PE):** Filesystem, Editor
- **Cypher (PM):** Filesystem, Project Management
- **Morpheus (SE):** Code Analysis, Filesystem
- **Neo (SWE):** Filesystem, Debug
- **Oracle (INFO):** Filesystem, Search
- **Trin (QA):** Testing, Code Analysis
- **Mouse (SM):** Task Management, Metrics

### Secondary Tools

All personas use:
- Git MCP (version control)
- Filesystem MCP (when not primary)

See `agents/MCP_INTEGRATION_SUMMARY.md` for complete mappings.

## Adding New Tools

1. Create `new_tool_mcp.md` in this directory
2. Follow the standard format (see existing files)
3. Add reference to relevant persona files
4. Update this README
5. Update `MCP_INTEGRATION_SUMMARY.md`

## Quick Examples

**Filesystem MCP:**
```
# With MCP
mcp__filesystem__search pattern="*.py" path="src/"

# Without (fallback)
Glob pattern="src/**/*.py"
```

**Testing MCP:**
```
# With MCP
mcp__test__coverage path="tests/" format="html"

# Without (fallback)
Bash: pytest tests/ --cov --cov-report=html
```

**Search MCP:**
```
# With MCP
mcp__search__semantic query="authentication patterns"

# Without (fallback)
Grep pattern="authentication.*pattern" output_mode="content"
```

---

**See Also:**
- `agents/bob.docs/HELP.md` - Complete system reference
- `agents/bob.docs/BOB_SYSTEM_PROTOCOL.md` - Full protocol
- `agents/MCP_INTEGRATION_SUMMARY.md` - Integration overview
