# setup_sandbox.ps1
# Creates a self-contained test environment in a 'test_sandbox' directory.

# Stop script on first error
$ErrorActionPreference = 'Stop'

# Define the sandbox directory
$sandboxDir = "test_sandbox"

# Create the sandbox directory, continuing silently if it already exists.
if (-not (Test-Path -Path $sandboxDir)) {
    New-Item -ItemType Directory -Path $sandboxDir
    Write-Host "Created directory: $sandboxDir"
}

# --- Copy Configuration ---
$mcpSource = ".mcp.json"
$mcpDest = Join-Path $sandboxDir $mcpSource
Write-Host "Copying $mcpSource to $mcpDest..."
Copy-Item -Path $mcpSource -Destination $mcpDest -Force

# --- Copy Service Definitions ---
$toolsSource = "agents/tools"
$toolsDest = Join-Path $sandboxDir "agents/tools"

# Ensure the destination parent directory exists
New-Item -ItemType Directory -Path (Split-Path $toolsDest) -Force | Out-Null

Write-Host "Recursively copying $toolsSource to $toolsDest..."
Copy-Item -Path $toolsSource -Destination $toolsDest -Recurse -Force

# --- Copy Startup Instructions ---
$startupSource = "SANDBOX_STARTUP.md"
$startupDest = Join-Path $sandboxDir $startupSource
Write-Host "Copying $startupSource to $startupDest..."
Copy-Item -Path $startupSource -Destination $startupDest -Force

# --- Create Empty Chat Log ---
$chatLogFile = Join-Path $sandboxDir "chat-log.md"
$chatLogContent = @"
# Agent Collaboration Chat Log

This file tracks all MCP command usage by agents in this environment.

**Format**: `[TIMESTAMP] [AGENT_NAME] mcp__agent__command parameter="value"`

---

"@

Write-Host "Creating chat log file: $chatLogFile..."
Set-Content -Path $chatLogFile -Value $chatLogContent

# --- Create Test Scenario File ---
$scenarioFile = Join-Path $sandboxDir "test_scenario.md"
$scenarioContent = @"
# Test Scenario: Basic Workflow

This scenario validates the core planning-to-implementation loop.

## Getting Started

1. **Read SANDBOX_STARTUP.md** - Understand the agent system
2. **Read chat-log.md** - See what's been done (initially empty)
3. **Execute the workflow below** - Test agent collaboration

## Test Workflow: Create a Simple File

### 1. Define the Feature (Cypher)
\`\`\`
mcp__cypher__define_feature request="Create a file named 'hello.txt' with the content 'Hello from BobProtocol!'"
\`\`\`
Log to chat-log.md

### 2. Plan the Implementation (Morpheus)
\`\`\`
mcp__morpheus__plan story="Create hello.txt file with greeting"
\`\`\`
Log to chat-log.md

### 3. Implement (Neo)
\`\`\`
mcp__neo__implement task="Create hello.txt with content 'Hello from BobProtocol!'"
\`\`\`
Log to chat-log.md

### 4. Verify (Trin)
\`\`\`
mcp__trin__verify feature="hello.txt file creation"
\`\`\`
Log to chat-log.md

### 5. Document (Oracle)
\`\`\`
mcp__oracle__record decision="File creation pattern: Use UTF-8 encoding for all text files"
\`\`\`
Log to chat-log.md

## Expected Outcome

- hello.txt exists with correct content
- chat-log.md contains all 5 MCP command entries
- Each agent logged their command and result
"@

Write-Host "Creating test scenario file: $scenarioFile..."
Set-Content -Path $scenarioFile -Value $scenarioContent

Write-Host ""
Write-Host "✅ Sandbox created successfully in '$sandboxDir'"
Write-Host ""
Write-Host "📋 Files created:"
Write-Host "  - $sandboxDir/.mcp.json (MCP configuration)"
Write-Host "  - $sandboxDir/agents/tools/ (Agent MCP definitions)"
Write-Host "  - $sandboxDir/SANDBOX_STARTUP.md (LLM startup instructions)"
Write-Host "  - $sandboxDir/chat-log.md (Agent collaboration log)"
Write-Host "  - $sandboxDir/test_scenario.md (Test workflow)"
Write-Host ""
Write-Host "🚀 Next: Open SANDBOX_STARTUP.md in the test_sandbox directory to begin!"
