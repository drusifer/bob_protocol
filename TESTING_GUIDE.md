# Testing Guide: The Sandboxed Environment

This guide explains how to use the sandboxed test environment to safely experiment with the Persona-as-a-Service (PaaS) system.

## 1. What is the Sandbox?

The sandbox is an isolated directory named `test_sandbox` that contains a copy of all the necessary configurations for the PaaS system. It allows you to run commands and test workflows without any risk of modifying or polluting your main project's configuration.

When you are finished, the entire sandbox can be deleted with a single command.

## 2. How to Use the Sandbox

Using the sandbox is a three-step process: **Setup**, **Test**, and **Teardown**.

### Step 1: Setup
To create the sandboxed environment, navigate to the project root in your PowerShell terminal and run the setup script:

```powershell
.\setup_sandbox.ps1
```
This command will create the `test_sandbox/` directory and populate it with copies of the `.mcp.json` file and the `agents/tools/` service definitions. It also creates a `test_scenario.md` file inside the sandbox with an example workflow.

### Step 2: Run Your Test
You can now work within the sandbox. The recommended way is to open a new terminal or `cd` into the directory:

```powershell
cd test_sandbox
```
Once inside, you can issue MCP commands as you normally would. You can follow the `test_scenario.md` file or try your own commands. For example:

```
# (Inside the test_sandbox directory)

# Ask Morpheus to create a plan
morph plan "Create a file named 'hello.txt' with the content 'hello from the sandbox'."

# Ask Neo to implement the plan
neo implement task="Create the 'hello.txt' file."
```
Any files created or modified by these commands will be contained within the `test_sandbox/` directory, leaving your main project files completely untouched.

### Step 3: Teardown
When you are finished with your testing, navigate back to the project root and run the teardown script:

```powershell
# (From the project root directory)
.\teardown_sandbox.ps1
```
This script will prompt you for confirmation and then completely and safely delete the `test_sandbox/` directory and all its contents.
```