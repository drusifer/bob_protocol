# Feature Definition: Sandboxed Test Environment

- **ID**: US-125
- **Status**: Defined
- **Author**: Cypher
- **Stakeholder**: Developer

## 1. User Story

As a developer, I want to test the new Persona-as-a-Service protocol in an isolated subdirectory, so that I can experiment with commands and workflows without polluting or altering the main project configuration.

## 2. Acceptance Criteria

1.  A dedicated directory (e.g., `test_sandbox/`) can be created to house the test environment.
2.  The test environment must be a self-contained copy of the necessary PaaS configuration files.
3.  It must be possible to issue `mcp` commands within the context of the sandbox.
4.  Actions performed within the sandbox must not affect the root project's configuration files (e.g., `.mcp.json`).
5.  Clear, simple instructions must be provided for setting up and tearing down the test environment.

## 3. High-Level Implementation Plan (For Morpheus)

This section outlines the recommended steps for the technical implementation of this feature.

### Task 1: Create Setup Script
- **Action**: Create a script (e.g., `setup_sandbox.ps1` for Windows) that automates the following:
    1. Creates a new directory named `test_sandbox`.
    2. Copies the root `.mcp.json` file into `test_sandbox/`.
    3. Copies the entire `agents/tools/` directory into `test_sandbox/agents/tools/`.
    4. Creates a placeholder `test_scenario.md` file inside `test_sandbox/` to guide the test.

### Task 2: Create Teardown Script
- **Action**: Create a script (e.g., `teardown_sandbox.ps1` for Windows) that automates the following:
    1. Deletes the `test_sandbox/` directory and all its contents.

### Task 3: Create Test Scenario
- **Action**: The `test_scenario.md` file should contain a simple, representative workflow to confirm the sandbox is working.
- **Example Scenario**:
    ```markdown
    # Test Scenario: Basic Workflow

    This scenario validates the core planning-to-implementation loop.

    ## 1. Plan a Feature
    # Use the Morpheus service to create a plan.
    morph plan "Create a dummy file named 'test.txt' with the content 'hello world'."

    ## 2. Implement the Feature
    # Use the Neo service to execute the plan.
    neo implement task="Create 'test.txt' with 'hello world' content."
    ```

### Task 4: Update Documentation
- **Action**: Create a new `TESTING_GUIDE.md` file explaining how to use the setup and teardown scripts and how to run a test scenario.
- Link to this new guide from the main `README.md`.
