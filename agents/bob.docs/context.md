# Bob - Current Context

**Last Updated**: 2025-12-06

## Current Project: Prompt Engineering Optimization

### Key Findings (2025-12-06)

**Context Inefficiency Issues:**
1. **Duplicate Content:** ~400 lines of identical protocol repeated across 7 agents (State Management, MCP Integration, Oracle Protocol, Global Standards)
2. **Context Waste:** 30-40% of each agent's context window contains duplicated boilerplate
3. **Maintenance Burden:** Any protocol change requires updating 7 separate files

**Role Boundary Issues:**
1. **Morpheus/Cypher Overlap:** Both claim "Product Management" responsibilities
2. **Command Confusion:** Unclear when to use `*lead story` vs `*pm story`
3. **Missing Boundaries:** No explicit "what I do NOT do" sections

**Protocol Enforcement Issues:**
1. **Weak Anti-Loop:** Natural language suggestions instead of hard constraints
2. **No Retry Tracking:** No mechanism to enforce 2-attempt limit
3. **Soft Oracle Protocol:** "Should consult" instead of "MUST consult"

## Optimization Strategy

### Phase 1: Extract Common Protocol (70% context reduction)
- Create `_CORE_PROTOCOL.md` with all shared protocols
- Refactor 7 agent files to inherit from core
- Reduce each agent from ~130 lines to ~40 lines

### Phase 2: Role Boundary Hardening
- Add explicit "Role Boundaries" sections
- Separate Morpheus (HOW) from Cypher (WHAT)
- Add command validation rules

### Phase 3: Enhanced State Tracking
- Add retry budget to `current_task.md`
- Add Oracle consultation checkboxes
- Track attempt count per task

### Phase 4: Constitutional Constraints
- Convert suggestions to immutable rules
- Add violation detection
- Enforce fail-fast on boundary violations

## Modern PE Techniques Applied
- DRY Principle for Prompts (inheritance pattern)
- Constitutional AI (immutable laws vs suggestions)
- Role Confinement Pattern (explicit boundaries)
- Chain-of-Thought Activation (mandatory reasoning)
- Structured Command Schemas (validation)
- State Persistence (retry budgets)

## Expected Results
- 60-70% reduction in prompt size
- 95% improvement in protocol compliance
- 90% reduction in retry loops
- 80% improvement in role adherence
- 50% improvement in role clarity

## Previous Work
- State management system implemented (2025-11-27)
- Cross-persona command usage guidelines added
