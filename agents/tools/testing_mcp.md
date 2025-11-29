# Testing MCP

**Tool Pattern:** `mcp__test__*`

## Purpose
Advanced test execution, coverage analysis, and quality metrics.

## Primary Commands

- `test__run` - Execute test suites with detailed reporting
- `test__coverage` - Generate coverage reports and identify gaps
- `test__watch` - Continuous test execution during development
- `test__debug` - Debug failing tests with enhanced diagnostics
- `test__mutation` - Mutation testing for test quality verification
- `test__benchmark` - Performance benchmarking and comparison

## When to Use

- Running test suites
- Coverage analysis
- Test debugging
- Performance testing
- Test quality assessment

## Fallback

Standard Bash pytest commands

## Example Usage

```
# Check for MCP
[Look for mcp__test__coverage]

# With MCP
mcp__test__coverage path="tests/" format="html"

# Without MCP (fallback)
Bash: pytest tests/ --cov --cov-report=html
```

## Benefits

- Detailed test reports
- Visual coverage analysis
- Mutation testing capabilities
- Performance benchmarking
- Better failure diagnostics
- Continuous watch mode
