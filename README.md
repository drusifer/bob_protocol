# BobProtocol

> A multi-persona AI development system that orchestrates specialized agents for collaborative software development.

## What is BobProtocol?

BobProtocol is an innovative system where a single AI dynamically switches between **7 specialized personas**, each an expert in their domain. Instead of managing multiple separate agents, you interact with one intelligent system that knows when to be a Product Manager, Software Engineer, QA Tester, or any other role your project needs.

Think of it as having an entire development team available through simple commands.

## The Team

| Persona | Role | Expertise | Command Prefix |
|---------|------|-----------|----------------|
| 👔 **Bob** | Prompt Engineer | Agent creation, team process | `*prompt`, `*reprompt`, `*learn` |
| 📋 **Cypher** | Product Manager | Requirements, roadmap, PRDs | `*pm` |
| 🧠 **Morpheus** | Tech Lead | Architecture, design decisions | `*lead` |
| 💻 **Neo** | Software Engineer | Implementation, debugging | `*swe` |
| 📚 **Oracle** | Knowledge Officer | Documentation, knowledge base | `*ora` |
| 🛡️ **Trin** | QA Engineer | Testing, quality assurance | `*qa` |
| 🐭 **Mouse** | Scrum Master | Sprint coordination, metrics | `*sm` |

## Quick Start

### 1. Get Help
```bash
*help
```
Shows complete command reference with examples for all personas.

### 2. Start a Conversation
```bash
*chat
```
The system reads the conversation context and responds as the appropriate persona.

### 3. Direct Commands
```bash
*swe impl Add password validation
*qa test all
*ora ask What's our authentication pattern?
```
Use commands directly to activate specific personas.

## How It Works

### Chat-Driven Development
```
User: @Morpheus *lead plan Add user authentication

[Morpheus analyzes and creates plan]
Morpheus: Breaking down into tasks:
  1. Password hashing (bcrypt)
  2. Session management (JWT)
  3. Login endpoint
@Neo please implement, @Trin verify when done

User: *chat

[Neo activates]
Neo: Implementing authentication service...
[Codes the solution]
Done! @Trin ready for testing

User: *chat

[Trin activates]
Trin: Running test suite... ✅ All tests passing
```

### Cross-Persona Collaboration
```
@Oracle *ora ask Have we decided on caching strategy?
→ Oracle searches knowledge base, provides answer

@Morpheus *lead refactor authentication
→ Morpheus analyzes code, suggests refactoring

@Neo *swe impl Apply refactoring
→ Neo implements changes

@Trin *qa test Verify no regressions
→ Trin runs full test suite
```

## Key Features

### 🎯 Specialized Expertise
Each persona is a domain expert with specific tools and knowledge:
- **Morpheus** knows architecture patterns and SOLID principles
- **Neo** specializes in implementation and debugging
- **Trin** ensures quality and prevents regressions
- **Oracle** maintains institutional knowledge

### 🔄 Persistent Memory
Every persona maintains state files:
- `context.md` - Working memory, decisions, findings
- `current_task.md` - Active work and progress
- `next_steps.md` - Resume plan for next activation

**No context loss between switches!**

### 🛠️ MCP Tools Integration
Optional Model Control Protocol tools enhance capabilities:
- **Filesystem MCP** - Advanced file operations
- **Testing MCP** - Coverage analysis, mutation testing
- **Code Analysis MCP** - Automated smell detection
- **Search MCP** - Semantic documentation search
- **Debug MCP** - Advanced debugging and profiling
- And more...

All tools have automatic fallback to standard operations.

### 📚 Knowledge Management
Oracle maintains a searchable knowledge base:
- `DECISIONS.md` - Architectural decisions
- `LESSONS.md` - Best practices learned
- `ARCH.md` - System architecture
- `OBJECTIVES.md` - Goals and risks

### 🚫 Anti-Loop Protection
Built-in safeguards prevent infinite retry loops:
1. First failure → Stop and consult Oracle
2. Review what's been tried
3. One retry with new approach
4. Second failure → Log and escalate

## File Structure

```
BobProtocol/
├── README.md                    # You are here
├── START_HERE.md               # Quick start guide
│
├── agents/
│   ├── tools/                  # MCP tool documentation
│   │   ├── README.md
│   │   └── *_mcp.md           # Individual tool docs
│   │
│   ├── bob.docs/              # Bob (Prompt Engineering)
│   │   ├── Bob_PE_AGENT.md
│   │   ├── HELP.md            # Complete reference (use *help)
│   │   ├── BOB_SYSTEM_PROTOCOL.md
│   │   └── context.md, current_task.md, next_steps.md
│   │
│   ├── [persona].docs/        # Other personas
│   │
│   ├── CHAT.md                # Team communication log
│   ├── DOCUMENTATION_INDEX.md # Documentation map
│   └── MCP_INTEGRATION_SUMMARY.md
│
└── .claude/
    └── mcp.json               # MCP configuration (optional)
```

## Real-World Examples

### Building a Feature
```bash
# Product planning
*pm doc PRD
[Cypher writes Product Requirements Document]

# Technical planning
*lead plan User registration system
[Morpheus breaks down into tasks]

# Implementation
*swe impl Registration endpoint
[Neo codes the feature]

# Testing
*qa test registration
[Trin verifies all works]

# Documentation
*ora record decision Email validation required server-side
[Oracle documents the decision]
```

### Debugging a Problem
```bash
# Check history
*ora ask Have we seen timeout errors before?
[Oracle searches past solutions]

# Fix implementation
*swe fix Login timeout
[Neo debugs and fixes]

# Verify fix
*qa test Login flow
[Trin validates]

# Record learning
*ora record lesson Always set connection timeout to 30s
[Oracle saves for future reference]
```

### Sprint Planning
```bash
# Current status
*sm status
[Mouse shows sprint progress]

# Prioritize work
*pm prioritize backlog
[Cypher ranks by business value]

# Technical breakdown
*lead plan Top priority feature
[Morpheus creates technical tasks]

# Assign work
*sm assign tasks
[Mouse coordinates sprint]
```

## Core Principles

### 🏆 Quality First
**"We don't ship shit."** - Uncle Bob
- Test before commit
- No regressions allowed
- Working, testable, maintainable code

### 🔍 Oracle First
Before major decisions, consult Oracle:
```bash
*ora ask What's our pattern for [problem]?
*ora ask Have we solved this before?
```

### 💾 State Management
All personas must save state before switching:
- Entry: Load context, current task, next steps
- Work: Execute and update CHAT.md
- Exit: Save all state files (MANDATORY)

### 🔄 Short Iterations
- Keep CHAT.md entries brief (1-3 lines)
- Detailed content goes in persona.docs/
- Oracle checkpoints every 3-5 steps

## Getting Started

1. **Read This File** ✅ You're doing it!
2. **Quick Start**: [START_HERE.md](START_HERE.md)
3. **Get Help**: Type `*help` or read [HELP.md](agents/bob.docs/HELP.md)
4. **Full Protocol**: [BOB_SYSTEM_PROTOCOL.md](agents/bob.docs/BOB_SYSTEM_PROTOCOL.md)
5. **MCP Tools**: [tools/README.md](agents/tools/README.md)

## Installation

BobProtocol is a prompt-based system that works with Claude Code. No installation required!

**Optional: MCP Tools Enhancement**
```bash
# Check available MCPs
claude mcp list

# Install recommended tools
claude mcp add filesystem
claude mcp add git
claude mcp add testing

# Configuration saved to .claude/mcp.json
```

## Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Introduction (this file) |
| [START_HERE.md](START_HERE.md) | Minimal onboarding |
| [HELP.md](agents/bob.docs/HELP.md) | Complete reference (`*help`) |
| [BOB_SYSTEM_PROTOCOL.md](agents/bob.docs/BOB_SYSTEM_PROTOCOL.md) | Full protocol |
| [DOCUMENTATION_INDEX.md](agents/DOCUMENTATION_INDEX.md) | Documentation map |
| [MCP_INTEGRATION_SUMMARY.md](agents/MCP_INTEGRATION_SUMMARY.md) | MCP overview |
| [tools/](agents/tools/) | MCP tool documentation |

## FAQ

**Q: Do I need to install anything?**
A: No! BobProtocol is a prompt system. MCP tools are optional enhancements.

**Q: How do I know which persona to use?**
A: Use `*chat` and the system decides, or use direct commands like `*swe impl` or `*qa test`.

**Q: What if I forget a command?**
A: Type `*help` for complete reference with examples.

**Q: How does the system remember context?**
A: Each persona maintains state files (context.md, current_task.md, next_steps.md).

**Q: Can I add new personas?**
A: Yes! Use `*prompt Create a [role] agent` and Bob will create one using templates.

**Q: What are MCP tools?**
A: Optional enhancements for advanced features. The system works perfectly without them.

## Command Cheat Sheet

```bash
# Help & System
*help                          # Show complete reference
*chat                          # Activate multi-persona mode

# Bob (Prompt Engineering)
*prompt <desc>                 # Create new agent
*reprompt <instructions>       # Update agents
*learn <lesson>                # Broadcast lesson

# Cypher (Product Manager)
*pm doc <type>                 # Create PRD/docs
*pm prioritize                 # Prioritize features

# Morpheus (Tech Lead)
*lead plan <epic>              # Break down work
*lead refactor <target>        # Refactoring strategy
*lead decide <choice>          # Make decision

# Neo (Software Engineer)
*swe impl <task>               # Implement feature
*swe fix <issue>               # Fix bug
*swe test <scope>              # Run tests

# Oracle (Knowledge Officer)
*ora ask <question>            # Query knowledge
*ora record <type> <content>   # Log decision/lesson
*ora groom                     # Organize docs

# Trin (QA)
*qa test <scope>               # Run tests
*qa verify <feature>           # Create test plan
*qa report                     # Health summary

# Mouse (Scrum Master)
*sm status                     # Sprint status
*sm velocity                   # Team metrics
*sm blocked                    # List blockers
```

## Contributing

To add new personas or enhance existing ones:
1. Use templates in `agents/_template_*.md`
2. Follow state management protocol
3. Document MCP tools if applicable
4. Update HELP.md with new commands

## Philosophy

BobProtocol embodies these principles:

**🎭 Separation of Concerns**
Each persona has distinct responsibilities. No overlap.

**🧠 Institutional Memory**
Oracle maintains knowledge. Nothing is forgotten.

**⚡ Short Iterations**
Quick cycles with Oracle checkpoints. No deep dives without checking.

**✅ Quality Gates**
Trin ensures no regressions. If tests fail, it's not done.

**📖 Documentation First**
Oracle records decisions. Future you will thank current you.

## License

This is a prompt engineering system. Use it, modify it, share it!

## Support

- Type `*help` for command reference
- Read `START_HERE.md` for quick start
- Consult `HELP.md` for complete guide
- Ask Oracle: `*ora ask <your question>`

---

**Welcome to BobProtocol.** Let's build something great together! 🚀
