# Test Plan: TP-01 - Sandboxed Test Environment

- **Feature ID**: US-125
- **Test Lead**: Trin
- **Status**: Draft

## 1. Objective
To verify that the sandboxed test environment can be created, used, and destroyed according to the acceptance criteria defined in the feature specification.

## 2. Test Cases

---
### **TC-01: Verify Setup Script Execution**
- **Objective**: Ensure the setup script correctly creates the sandbox directory and populates it with the required files.
- **Steps**:
    1. From the project root, execute the `.\setup_sandbox.ps1` script.
- **Expected Results**:
    1. A directory named `test_sandbox` is created in the project root.
    2. The `test_sandbox` directory contains a file named `.mcp.json`.
    3. The `test_sandbox` directory contains a subdirectory `agents/tools/`.
    4. The `test_sandbox/agents/tools/` directory contains copies of all `*_mcp.md` files.
    5. The `test_sandbox` directory contains a file named `test_scenario.md`.
    6. The console displays a "Sandbox created successfully" message.

---
### **TC-02: Verify Teardown Script Execution (Confirm)**
- **Objective**: Ensure the teardown script correctly removes the sandbox directory after user confirmation.
- **Pre-condition**: TC-01 must have been executed successfully.
- **Steps**:
    1. From the project root, execute the `.\teardown_sandbox.ps1` script.
    2. When prompted for confirmation, input `y` and press Enter.
- **Expected Results**:
    1. The `test_sandbox` directory is completely removed from the project root.
    2. The console displays a "Sandbox removed successfully" message.

---
### **TC-03: Verify Teardown Script Execution (Cancel)**
- **Objective**: Ensure the teardown script does nothing if the user cancels the operation.
- **Pre-condition**: TC-01 must have been executed successfully.
- **Steps**:
    1. From the project root, execute the `.\teardown_sandbox.ps1` script.
    2. When prompted for confirmation, input `n` and press Enter.
- **Expected Results**:
    1. The `test_sandbox` directory is NOT removed.
    2. The console displays a "Teardown cancelled" message.
    3. (Cleanup) Manually run the teardown script again, confirming with `y`, to complete the test.

---
### **TC-04: Verify Documentation**
- **Objective**: Ensure the documentation for the testing feature is present and correct.
- **Steps**:
    1. Read the contents of `TESTING_GUIDE.md`.
    2. Read the contents of `README.md`.
- **Expected Results**:
    1. `TESTING_GUIDE.md` exists and contains clear instructions for the setup, test, and teardown process.
    2. `README.md` contains a "Testing the System" section that correctly links to `TESTING_GUIDE.md`.

---
## 3. Test Environment
- **System**: Windows (as scripts are `.ps1`)
- **Tools**: PowerShell terminal
