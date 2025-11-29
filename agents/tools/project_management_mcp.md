# Project Management MCP

**Tool Pattern:** `mcp__pm__*`

## Purpose
Strategic project planning and roadmap management.

## Primary Commands

- `pm__roadmap` - Visualize product roadmap
- `pm__dependencies` - Track feature dependencies
- `pm__prioritize` - Apply prioritization frameworks (RICE, MoSCoW)
- `pm__timeline` - Generate project timelines
- `pm__risks` - Risk assessment and tracking

## When to Use

- Strategic product planning
- Feature prioritization
- Dependency tracking
- Roadmap visualization
- Risk management

## Fallback

Manual tracking in markdown files

## Example Usage

```
# Check for MCP
[Look for mcp__pm__roadmap]

# With MCP
mcp__pm__roadmap view="quarterly"

# Without MCP (fallback)
Manually maintain roadmap in docs/
```

## Benefits

- Visual roadmaps
- Automated prioritization
- Dependency graphs
- Timeline generation
- Risk tracking
