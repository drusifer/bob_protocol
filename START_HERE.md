# Quick Start: Persona-as-a-Service

This file provides the absolute minimum to get started with the new Persona-as-a-Service (PaaS) architecture.

For a comprehensive explanation and examples, please read the new **[USER_GUIDE.md](USER_GUIDE.md)**.

## Core Concept

The old, conversational `*chat` protocol has been replaced. Personas are now specialized **MCP Services** that you command directly. This is a more powerful and predictable way to work.

The command syntax is:
`mcp__<persona_name>__<command> [parameters...]`

## Example Minimal Workflow

Instead of a long conversation, you now issue direct commands to get things done.

### 1. Plan a feature
Use the **Morpheus** service to create a technical plan.
```bash
mcp__morpheus__plan story="US-124: As a user, I can press a button to view the tag's UID."
```

### 2. Implement the plan
Use the **Neo** service to execute the implementation task from the plan.
```bash
mcp__neo__implement task="Implement a 'Show UID' button on the main TUI screen."
```

## Starting a New Python Project

Neo can bootstrap a complete Python project with modern tooling:
```bash
mcp__neo__init_python_project project_name="myapp" description="My application"
```

This creates:
- Project structure (src/, tests/)
- pyproject.toml with dependencies
- Virtual environment (.venv)
- Linting tools (ruff for formatting, quality, complexity, duplication, errors)
- Type checking (mypy)
- Testing (pytest)
- VS Code debug configuration
- Example code (main.py, hello.py, test_hello.py)

## Available Services

A full list of services and their commands is in the main **[README.md](README.md)**. For a detailed reference on any service, see its documentation file in `agents/tools/`.

- `mcp__morpheus__*` (Architecture & Planning)
- `mcp__neo__*` (Implementation & Bug Fixing)
- `mcp__trin__*` (Quality Assurance)
- `mcp__oracle__*` (Knowledge & Documentation)
- `mcp__cypher__*` (Product Requirements)
- `mcp__mouse__*` (Sprint Management)
- `mcp__bob__*` (System Metaprogramming)


## Running tests (Windows)
Always activate the venv in the workspace before running tests:

```powershell
# In workspace root
. .\.venv\Scripts\Activate.ps1
.venv\Scripts\python.exe -m pytest -v
```

## Documentation Quick Reference

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | High-level overview of the PaaS system. |
| [USER_GUIDE.md](USER_GUIDE.md) | **The main user guide.** Start here for a full explanation. |
| [`agents/tools/`](./agents/tools/) | Directory containing the detailed definition for each MCP service. |
