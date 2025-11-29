# Metrics MCP

**Tool Pattern:** `mcp__metrics__*`

## Purpose
Advanced analytics and team performance metrics.

## Primary Commands

- `metrics__velocity` - Calculate team velocity trends
- `metrics__cycle_time` - Measure task completion time
- `metrics__blockers` - Track blocker frequency and duration
- `metrics__quality` - Track quality metrics (test pass rate, coverage)
- `metrics__throughput` - Measure work throughput
- `metrics__predict` - Forecast based on historical data

## When to Use

- Sprint retrospectives
- Performance analysis
- Capacity planning
- Quality tracking
- Predictive planning

## Fallback

Manual calculation from task.md and git logs

## Example Usage

```
# Check for MCP
[Look for mcp__metrics__velocity]

# With MCP
mcp__metrics__velocity period="last_6_sprints"

# Without MCP (fallback)
Manually calculate from task.md
```

## Benefits

- Automated calculations
- Trend analysis
- Predictive analytics
- Quality tracking
- Visual charts
- Historical comparison
