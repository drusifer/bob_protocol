# BobProtocol: Persona-as-a-Service

> A development system that orchestrates a team of specialized AI agents, exposed as a suite of powerful MCP services.

## What is BobProtocol?

BobProtocol has evolved into a **Persona-as-a-Service (PaaS)** architecture. Instead of a single AI agent switching roles, each of the 7 specialized personas is now a dedicated **MCP Service** with a clear, command-driven API.

This makes the system more robust, predictable, and automatable. You no longer have conversations to coax a persona into action; you directly command a specialized service to perform a task.

## The Service Team

| Persona | Role | Service Name | Purpose |
|---------|------|--------------|---------|
| 👔 **Bob** | Prompt Engineer | `mcp__bob__*` | Agent creation and system metaprogramming |
| 📋 **Cypher** | Product Manager | `mcp__cypher__*` | Manages requirements, user stories, and PRDs |
| 🧠 **Morpheus** | Tech Lead | `mcp__morpheus__*` | Provides architecture, planning, and design decisions |
| 💻 **Neo** | Software Engineer | `mcp__neo__*` | Handles implementation, debugging, and testing |
| 📚 **Oracle** | Knowledge Officer | `mcp__oracle__*` | Manages the documentation and knowledge base |
| 🛡️ **Trin** | QA Engineer | `mcp__trin__*` | Ensures quality and verifies features |
| 🐭 **Mouse** | Scrum Master | `mcp__mouse__*` | Coordinates sprints, tasks, and metrics |

## Core Concept

The old `*chat` workflow is now deprecated. To interact with the system, you invoke a persona's commands directly using the MCP tool pattern.

**The command structure is:**
`mcp__<persona_name>__<command> [parameters...]`

For example, to ask the Oracle a question, you would use:
`mcp__oracle__ask question="What is the established pattern for TUI development?"`

### Shorthand Guide
For easier use, a set of command shorthands has been created (e.g., `morph plan` instead of `mcp__morpheus__plan`).

**Please see the [SHORTHAND_GUIDE.md](SHORTHAND_GUIDE.md) for a full list of aliases.**

## Getting Started

The best place to start is the new **[USER_GUIDE.md](USER_GUIDE.md)**. It provides a comprehensive overview of the new architecture, the available services, and a step-by-step workflow example.

## Key Features

### 🎯 Persona-as-a-Service
Each persona is a dedicated tool with a specific API. This makes their behavior predictable and allows you to compose them into powerful, automated workflows.

### 📚 Centralized Knowledge
The **Oracle** service acts as the team's long-term memory. It manages a searchable knowledge base of architectural decisions, lessons learned, and project documentation.

### 🤖 Self-Improving System
The **Bob** service can modify the prompts and protocols of the other services, allowing the system to learn and improve over time.

### 🛠️ Integrated Workflow
The services are designed to work together, creating a seamless development process:
- **Cypher** defines *what* to build.
- **Morpheus** designs *how* to build it.
- **Neo** builds it.
- **Trin** verifies that it's built correctly.
- **Mouse** tracks the progress of the build.
- **Oracle** remembers everything.
- **Bob** improves the builders.

## File Structure

```
BobProtocol/
├── README.md                    # You are here
├── USER_GUIDE.md                # The primary guide for the new PaaS architecture
│
├── agents/
│   ├── tools/                  # MCP service definitions
│   │   ├── morpheus_mcp.md    # Morpheus service commands
│   │   ├── neo_mcp.md         # Neo service commands
│   │   └── ... (and so on for each persona)
│   │
│   └── [persona].docs/        # Each persona's internal state files
│       ├── context.md
│       ├── current_task.md
│       └── next_steps.md
│
└── .mcp.json                    # MCP service registry
```

## Testing the System

This project includes a sandboxed environment for safely testing and experimenting with the Persona-as-a-Service system. You can create an isolated copy of the configuration, run tests, and then clean it up with simple scripts.

For detailed instructions, please see the **[TESTING_GUIDE.md](TESTING_GUIDE.md)**.

## Example Workflow: Building a Feature

### 1. Define the Feature
Use the **Cypher** service to translate a request into a formal user story.
```bash
mcp__cypher__define_feature request="Users need a button that shows the tag's UID."
```

### 2. Create an Implementation Plan
Ask the **Morpheus** service to create a technical plan.
```bash
mcp__morpheus__plan story="US-124: As a user, I can press a button to view the tag's UID."
```

### 3. Implement the Feature
Delegate the implementation work to the **Neo** service.
```bash
mcp__neo__implement task="Implement a 'Show UID' button on the main TUI screen."
```

### 4. Verify the Feature
Use the **Trin** service to verify that the implementation meets the acceptance criteria.
```bash
mcp__trin__verify feature="US-124: Show UID Button"
```

## Service Command Cheat Sheet

This is a high-level overview. For detailed parameters, see the documentation for each service in `agents/tools/`.

- **`mcp__bob__*`**
  - `reprompt`: Updates a service's prompt.
  - `learn`: Establishes a new global standard.

- **`mcp__cypher__*`**
  - `define_feature`: Creates user stories from a request.
  - `prioritize`: Prioritizes the backlog.

- **`mcp__morpheus__*`**
  - `plan`: Creates a technical plan for a feature.
  - `decide`: Makes an architectural decision.
  - `review`: Reviews code or documents.

- **`mcp__neo__*`**
  - `init_python_project`: Initializes a complete Python project with modern tooling (pyproject.toml, ruff, pytest, mypy, VS Code config)
  - `implement`: Implements a feature or task.
  - `fix`: Fixes a bug.
  - `test`: Writes unit tests.

- **`mcp__oracle__*`**
  - `ask`: Answers questions from the knowledge base.
  - `record`: Records a decision or lesson.
  - `distill`: Summarizes a document.

- **`mcp__trin__*`**
  - `verify`: Verifies a feature or fix.
  - `report`: Reports on quality and test coverage.
  - `repro`: Reproduces a bug.

- **`mcp__mouse__*`**
  - `plan_sprint`: Creates a sprint plan.
  - `status`: Reports on sprint progress.
  - `update_task`: Updates a task's status.

---

**Welcome to the new BobProtocol.** Let's build something great together! 🚀
