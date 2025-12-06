# Neo MCP Service

**Tool Pattern**: `mcp__neo__*`

**Purpose**: Handles software implementation, fixing bugs, and low-level technical execution as a service.

**Role**: 💻 Software Engineer - Implementation, debugging, and coding

## CRITICAL: Chat Log Protocol

**EVERY time you use a Neo MCP command, you MUST log it to `chat-log.md`:**

```markdown
[TIMESTAMP] [Neo] mcp__neo__command parameter="value"
[TIMESTAMP] [Neo] Result: [brief summary of outcome]
```

## CRITICAL: Working Directory Constraint

**All file operations MUST be confined to the project root directory and subdirectories.**
- ✅ Work with files at or below the current working directory
- ❌ Never access files outside the project directory
- ✅ Use relative paths from project root

## Primary Commands

- `neo__implement` - Implements a feature, user story, or specific code task based on a provided plan and acceptance criteria.
- `neo__fix` - Debugs and fixes an issue described in a bug report or error log.
- `neo__test` - Writes and runs unit or integration tests for a specific function, class, or module.
- `neo__refactor` - Refactors a specific part of the codebase to improve its structure, performance, or clarity without changing its external behavior.
- `neo__init_python_project` - Initializes a complete Python project with modern tooling, structure, and configuration.

## When to Use

- For all well-defined coding tasks, such as implementing a feature from a user story or fixing a specific bug.
- When you need to add test coverage to a particular part of the code.
- To execute a planned refactoring.

## CRITICAL: Work in Short Sprints

**Implement one small piece at a time. Hand off to Trin or Oracle frequently.**
- ✅ Implement one function or file, then request verification
- ❌ Don't implement entire features in one go
- ✅ After each incremental change, delegate to Trin for verification
- ✅ Record decisions with Oracle after each significant change

## Collaboration with Other Agents

Neo works with other agents during implementation:

- `mcp__oracle__ask` - Query coding patterns, API usage, or established conventions
- `mcp__oracle__record` - Document implementation decisions and lessons learned
- `mcp__morpheus__decide` - Request architectural guidance on complex decisions
- `mcp__trin__verify` - Request testing and verification after implementation
- `mcp__trin__repro` - Get help reproducing bugs
- `mcp__mouse__update_task` - Update task progress during implementation

## Fallback

None. This service represents the core software engineering implementation capability.

## neo__init_python_project - Detailed Specification

**Purpose**: Bootstrap a complete Python project with modern best practices, tooling, and structure.

**Parameters**:
- `project_name` (required) - Name of the project (used for package name and pyproject.toml)
- `description` (optional) - Short project description. Default: "A Python project"
- `author` (optional) - Author name. Default: "Team"
- `python_version` (optional) - Minimum Python version. Default: "3.11"

**What This Command Creates**:

### 1. Project Structure
```
./
├── .venv/                    # Virtual environment (created and activated)
├── src/
│   └── {project_name}/
│       ├── __init__.py
│       ├── main.py           # Entry point with example CLI
│       └── hello.py          # Example module with hello_world()
├── tests/
│   ├── __init__.py
│   └── test_hello.py         # Example test for hello_world()
├── .vscode/
│   └── launch.json           # Debug configurations
├── pyproject.toml            # Project metadata and dependencies
├── .gitignore                # Python-specific gitignore
└── README.md                 # Basic project documentation
```

### 2. pyproject.toml Configuration
- Uses modern `[build-system]` with `hatchling`
- Defines `[project]` with name, version, description, dependencies
- Includes `[project.scripts]` for CLI entry point
- Adds `[tool.pytest.ini_options]` for test configuration
- Configures `[tool.ruff]` for linting (formatting, quality, complexity, duplication, errors)
- Configures `[tool.mypy]` for type checking

### 3. Development Tools Installed
- **ruff** - Ultra-fast linter covering:
  - Code formatting (replaces black)
  - Code quality checks (replaces flake8)
  - Complexity analysis (replaces mccabe)
  - Import sorting (replaces isort)
  - Error detection (pyflakes)
- **pytest** - Testing framework
- **mypy** - Static type checker

### 4. VS Code Configuration (.vscode/launch.json)
- **Python: Current File** - Debug current file
- **Python: Main Module** - Run main.py with debugger
- **Python: Pytest** - Debug tests

### 5. Example Code Generated

**src/{project_name}/hello.py**:
```python
def hello_world(name: str = "World") -> str:
    """Return a greeting message.

    Args:
        name: Name to greet. Defaults to "World".

    Returns:
        Greeting message string.
    """
    return f"Hello, {name}!"
```

**src/{project_name}/main.py**:
```python
import sys
from .hello import hello_world

def main() -> int:
    """Main entry point."""
    name = sys.argv[1] if len(sys.argv) > 1 else "World"
    print(hello_world(name))
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**tests/test_hello.py**:
```python
from {project_name}.hello import hello_world

def test_hello_world_default():
    assert hello_world() == "Hello, World!"

def test_hello_world_custom_name():
    assert hello_world("Alice") == "Hello, Alice!"
```

### 6. Post-Setup Commands Run
1. `python -m venv .venv` - Create virtual environment
2. `.venv/Scripts/activate` (Windows) or `source .venv/bin/activate` (Unix)
3. `pip install -e ".[dev]"` - Install project in editable mode with dev dependencies
4. `ruff check .` - Verify no linting errors
5. `mypy src/` - Verify type checking passes
6. `pytest` - Verify tests pass

### 7. Usage After Setup

**Run the application**:
```bash
.venv/Scripts/python -m {project_name}.main
# or
{project_name}  # If installed with pip
```

**Run tests**:
```bash
.venv/Scripts/pytest
```

**Format and lint**:
```bash
.venv/Scripts/ruff format .
.venv/Scripts/ruff check . --fix
```

**Type check**:
```bash
.venv/Scripts/mypy src/
```

## Example Usage

```
# Example: Initialize a new Python project
mcp__neo__init_python_project project_name="myapp" description="My awesome application" author="John Doe"

# Example: Implementing a feature
mcp__neo__implement story="US-123: Create the TagDiagnosticsService with methods get_tag_status() and read_ndef()."

# Example: Fixing a bug
mcp__neo__fix bug_report="The application crashes with a NullPointerException in `provision.py` line 42 when the tag is removed mid-operation."

# Example: Adding tests
mcp__neo__test module="src/ntag424_sdm_provisioner/crypto/aes.py"
```

## Benefits

- **Task-Oriented**: Focuses the LLM on a single, well-defined coding task, improving success rates.
- **Clear Handoffs**: Provides a clear interface for services like Morpheus to delegate implementation work.
- **Separation of Concerns**: Separates the "what" (from Morpheus/Cypher) from the "how" (implemented by Neo).
