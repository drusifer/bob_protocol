# Markdown MCP

**Tool Pattern:** `mcp__markdown__*`

## Purpose
Advanced markdown processing, validation, and formatting.

## Primary Commands

- `markdown__toc` - Auto-generate table of contents
- `markdown__validate` - Check markdown syntax and structure
- `markdown__format` - Apply consistent formatting
- `markdown__links` - Verify link integrity
- `markdown__preview` - Generate preview
- `markdown__convert` - Convert to other formats

## When to Use

- Documentation grooming
- TOC generation
- Link validation
- Markdown quality checks
- Format consistency

## Fallback

Manual markdown editing and validation

## Example Usage

```
# Check for MCP
[Look for mcp__markdown__toc]

# With MCP
mcp__markdown__toc file="README.md" depth=3

# Without MCP (fallback)
Manually create TOC
```

## Benefits

- Auto TOC generation
- Link checking
- Syntax validation
- Consistent formatting
- Format conversion
