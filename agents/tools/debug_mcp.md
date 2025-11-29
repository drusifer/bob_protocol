# Debug MCP

**Tool Pattern:** `mcp__debug__*`

## Purpose
Advanced debugging, tracing, and profiling capabilities.

## Primary Commands

- `debug__trace` - Trace code execution paths
- `debug__profile` - Performance profiling and analysis
- `debug__inspect` - Inspect runtime state and variables
- `debug__breakpoint` - Set conditional breakpoints
- `debug__watch` - Watch variable changes
- `debug__memory` - Memory usage analysis

## When to Use

- Complex debugging scenarios
- Performance optimization
- Understanding execution flow
- Memory leak detection
- Runtime state inspection

## Fallback

Print statements, manual logging, basic profiling

## Example Usage

```
# Check for MCP
[Look for mcp__debug__trace]

# With MCP
mcp__debug__trace function="process_apdu" depth=5

# Without MCP (fallback)
Add print statements manually
```

## Benefits

- Detailed execution traces
- Performance profiling
- Runtime inspection
- Conditional breakpoints
- Memory analysis
- Call stack visualization
