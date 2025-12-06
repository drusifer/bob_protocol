# Roadmap & Sprint Plan: Sandboxed Test Environment

- **Feature**: US-125: Sandboxed Test Environment
- **Lead**: Morpheus
- **Status**: Planned

## 1. Roadmap

This feature will be implemented in a single sprint.

- **Sprint 1: Sandbox Implementation**: Implement the core functionality for creating, using, and destroying the sandboxed test environment.

## 2. Sprint 1 Plan

**Goal**: A user can run a setup script to create a self-contained test environment, execute a test scenario within it, and run a teardown script to clean it up.

**Task Breakdown**: The following tasks are now defined and ready for implementation.

---
### **Task ID: T-01: Create Setup Script**
- **Status**: To Do
- **Description**: Create a new PowerShell script named `setup_sandbox.ps1` in the project root.
- **Implementation Details**:
    - The script must create a directory named `test_sandbox`.
    - It must copy the root `.mcp.json` file into `test_sandbox/`.
    - It must perform a recursive copy of the `agents/tools` directory to `test_sandbox/agents/tools/`.
    - It must create a new file `test_sandbox/test_scenario.md` with the content defined in the feature specification.
    - The script should print a "Sandbox created successfully" message upon completion.

---
### **Task ID: T-02: Create Teardown Script**
- **Status**: To Do
- **Description**: Create a new PowerShell script named `teardown_sandbox.ps1` in the project root.
- **Implementation Details**:
    - The script must completely remove the `test_sandbox` directory and all its contents.
    - It should include a confirmation prompt (e.g., "Are you sure you want to delete the sandbox?") to prevent accidental deletion.
    - The script should print a "Sandbox removed successfully" message upon completion.

---
### **Task ID: T-03: Create Testing Guide**
- **Status**: To Do
- **Description**: Create a new documentation file named `TESTING_GUIDE.md` in the project root.
- **Implementation Details**:
    - The guide must explain the purpose of the sandboxed environment.
    - It must provide clear instructions on how to execute `setup_sandbox.ps1` and `teardown_sandbox.ps1`.
    - It must explain how a developer would run a test scenario inside the sandbox.

---
### **Task ID: T-04: Update Main README**
- **Status**: To Do
- **Description**: Modify the root `README.md` to link to the new testing guide.
- **Implementation Details**:
    - Add a new section (e.g., "Testing the System") to the `README.md`.
    - This section should include a link to the `TESTING_GUIDE.md`.

---

## 3. Next Steps

The plan is now complete. The next action is to delegate these tasks to the implementation service.

**@Neo**, you are assigned to implement tasks T-01, T-02, T-03, and T-04.
Please begin with **T-01: Create Setup Script**.
