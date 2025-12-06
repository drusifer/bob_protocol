# setup_sandbox.ps1
# Creates a self-contained test environment for BobProtocol v2.0

# Stop script on first error
$ErrorActionPreference = 'Stop'

# Define the sandbox directory
$sandboxDir = "test_sandbox"

Write-Host "🔧 Setting up BobProtocol v2.0 Test Sandbox..." -ForegroundColor Cyan
Write-Host ""

# Create the sandbox directory
if (-not (Test-Path -Path $sandboxDir)) {
    New-Item -ItemType Directory -Path $sandboxDir | Out-Null
    Write-Host "✅ Created directory: $sandboxDir" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Directory exists: $sandboxDir" -ForegroundColor Yellow
}

# --- Copy Core Protocol ---
$coreSource = "agents/_CORE_PROTOCOL.md"
$coreDest = Join-Path $sandboxDir "agents/_CORE_PROTOCOL.md"

# Ensure the destination parent directory exists
New-Item -ItemType Directory -Path (Join-Path $sandboxDir "agents") -Force | Out-Null

Write-Host "📋 Copying Core Protocol: $coreSource..."
Copy-Item -Path $coreSource -Destination $coreDest -Force

# --- Copy Agent Personas ---
$agentFolders = @("bob.docs", "neo.docs", "morpheus.docs", "trin.docs", "oracle.docs", "mouse.docs", "cypher.docs")

Write-Host "👥 Copying Agent Personas..."
foreach ($folder in $agentFolders) {
    $source = "agents/$folder"
    $dest = Join-Path $sandboxDir "agents/$folder"

    if (Test-Path -Path $source) {
        # Copy only the main agent file (not state files)
        $agentFile = Get-ChildItem -Path $source -Filter "*_AGENT.md" | Select-Object -First 1
        if ($agentFile) {
            New-Item -ItemType Directory -Path $dest -Force | Out-Null
            Copy-Item -Path $agentFile.FullName -Destination $dest -Force
            Write-Host "  ✓ Copied $($agentFile.Name)" -ForegroundColor Gray
        }
    }
}

# --- Copy BOB_SYSTEM_PROTOCOL.md ---
$protocolSource = "agents/bob.docs/BOB_SYSTEM_PROTOCOL.md"
$protocolDest = Join-Path $sandboxDir "agents/bob.docs/BOB_SYSTEM_PROTOCOL.md"
Write-Host "📖 Copying System Protocol..."
Copy-Item -Path $protocolSource -Destination $protocolDest -Force

# --- Copy State Templates ---
Write-Host "📝 Copying State Templates..."
$templates = @("_template_current_task.md", "_template_context.md", "_template_next_steps.md")
foreach ($template in $templates) {
    $source = "agents/$template"
    $dest = Join-Path $sandboxDir "agents/$template"
    if (Test-Path -Path $source) {
        Copy-Item -Path $source -Destination $dest -Force
        Write-Host "  ✓ Copied $template" -ForegroundColor Gray
    }
}

# --- Create CHAT.md ---
$chatFile = Join-Path $sandboxDir "agents/CHAT.md"
$chatContent = @"
# Team Chat Log

**Protocol:** Messages are ALWAYS APPENDED at the END (newest at bottom).

**Format:** ``[TIMESTAMP] [PERSONA_NAME] *command action <details>``

---

[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [System] Sandbox initialized. Ready for *chat workflow.

"@

Write-Host "💬 Creating CHAT.md..."
Set-Content -Path $chatFile -Value $chatContent

# --- Create Test Scenario File ---
$scenarioFile = Join-Path $sandboxDir "TEST_SCENARIO.md"
$scenarioContent = @"
# BobProtocol v2.0 Test Scenario

This scenario validates the optimized multi-persona workflow with role boundaries.

## System Architecture (v2.0)

**Inheritance Structure:**
``````
_CORE_PROTOCOL.md (shared protocols)
    ↓
    ├─ Bob_PE_AGENT.md
    ├─ Neo_SWE_AGENT.md
    ├─ Morpheus_SE_AGENT.md
    ├─ Trin_QA_AGENT.md
    ├─ Oracle_INFO_AGENT.md
    ├─ Mouse_SM_AGENT.md
    └─ Cypher_PM_AGENT.md
``````

## Role Separation

| Persona | Focus | Commands |
|---------|-------|----------|
| Cypher | WHAT + WHY | ``*pm story``, ``*pm doc`` |
| Morpheus | HOW (Technical) | ``*lead decide``, ``*lead plan`` |
| Mouse | WHEN + WHO | ``*sm status``, ``*sm plan`` |
| Neo | Implementation | ``*swe impl``, ``*swe fix`` |
| Trin | Quality | ``*qa test``, ``*qa verify`` |
| Oracle | Knowledge | ``*ora ask``, ``*ora record`` |
| Bob | Meta-System | ``*prompt``, ``*reprompt`` |

## Test Workflow: Create a Simple Feature

### Step 1: User Request
``````
User: I need a feature that greets users with a friendly message
``````

### Step 2: Trigger Chat Workflow
``````
User: *chat
``````

### Expected Flow:

1. **Bob reads CHAT.md** (bottom)
2. **Bob identifies: Cypher should define the feature**
3. **Bob switches to Cypher persona**
4. **Cypher creates user story:**
   ``````
   [TIMESTAMP] [Cypher] *pm story US-1: As a user, I want a greeting message
   - Business value: Friendly UX
   - Acceptance: Message says "Hello from BobProtocol!"
   ``````
5. **Cypher switches back to Bob**
6. **User:** ``*chat`` (continue)
7. **Bob identifies: Morpheus should plan technical approach**
8. **Bob switches to Morpheus persona**
9. **Morpheus plans:**
   ``````
   [TIMESTAMP] [Morpheus] *lead plan Create hello.txt file
   @Neo *swe impl Create hello.txt with greeting message
   ``````
10. **Continue with:** Neo implements → Trin verifies → Oracle records

## Testing Role Boundaries

### Test 1: Neo Receives Architecture Question
``````
User: @Neo Should we use Redis or in-memory caching?

Expected:
Neo: ❌ Architecture decisions are outside my role.
     → @Morpheus *lead decide Should we use Redis or in-memory?
``````

### Test 2: Morpheus Receives Requirement
``````
User: @Morpheus We need a dashboard feature

Expected:
Morpheus: ❌ Defining WHAT to build is outside my role.
          → @Cypher *pm story Please define requirements for dashboard
``````

## Success Criteria

- ✅ Personas inherit from _CORE_PROTOCOL.md
- ✅ Role boundaries are enforced
- ✅ CHAT.md messages appended at END
- ✅ State files loaded/saved correctly
- ✅ Oracle consulted when required
- ✅ No infinite loops (retry budget enforced)

## Running the Test

1. Open this sandbox directory in your LLM environment
2. Read ``agents/bob.docs/BOB_SYSTEM_PROTOCOL.md``
3. Execute ``*chat`` command
4. Observe persona switching and role enforcement
5. Check ``agents/CHAT.md`` for proper logging

"@

Write-Host "📋 Creating test scenario..."
Set-Content -Path $scenarioFile -Value $scenarioContent

# --- Create README ---
$readmeFile = Join-Path $sandboxDir "README.md"
$readmeContent = @"
# BobProtocol v2.0 Test Sandbox

This is an isolated testing environment for the BobProtocol multi-persona system.

## What's Included

- **Core Protocol:** ``agents/_CORE_PROTOCOL.md`` (280 lines of shared protocols)
- **7 Agent Personas:** Bob, Neo, Morpheus, Trin, Oracle, Mouse, Cypher
- **System Protocol:** ``agents/bob.docs/BOB_SYSTEM_PROTOCOL.md``
- **State Templates:** Enhanced with retry budgets and Oracle tracking
- **Chat Log:** ``agents/CHAT.md`` for team communication

## Key Features (v2.0)

✅ **Context Efficiency** - 52% reduction via inheritance
✅ **Role Boundaries** - Explicit "What I Do NOT Do" sections
✅ **Constitutional AI** - Immutable rules (ORACLE_FIRST_LAW, etc.)
✅ **Anti-Loop Protocol** - Retry budget enforcement
✅ **Enhanced State** - Oracle tracking, boundary checks

## Quick Start

1. **Read the protocol:** ``agents/bob.docs/BOB_SYSTEM_PROTOCOL.md``
2. **Review test scenario:** ``TEST_SCENARIO.md``
3. **Trigger workflow:** Use ``*chat`` command
4. **Monitor:** Check ``agents/CHAT.md`` for conversation flow

## Testing Checklist

- [ ] Personas inherit from _CORE_PROTOCOL.md
- [ ] Role boundaries enforced (delegation messages appear)
- [ ] CHAT.md appends at END (not beginning)
- [ ] State files loaded on ENTRY
- [ ] State files saved on EXIT
- [ ] Oracle First Law followed
- [ ] Retry budget prevents loops

## Cleanup

Run ``../teardown_sandbox.ps1`` to remove this test environment.

---

**BobProtocol Version:** 2.0
**Created:** $(Get-Date -Format 'yyyy-MM-dd')
"@

Write-Host "📖 Creating README..."
Set-Content -Path $readmeFile -Value $readmeContent

# --- Success Message ---
Write-Host ""
Write-Host "✅ Sandbox created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Structure:" -ForegroundColor Cyan
Write-Host "  $sandboxDir/"
Write-Host "  ├── README.md (Start here!)"
Write-Host "  ├── TEST_SCENARIO.md (Test workflow)"
Write-Host "  └── agents/"
Write-Host "      ├── _CORE_PROTOCOL.md (Shared protocols)"
Write-Host "      ├── CHAT.md (Team communication)"
Write-Host "      ├── bob.docs/Bob_PE_AGENT.md + BOB_SYSTEM_PROTOCOL.md"
Write-Host "      ├── neo.docs/Neo_SWE_AGENT.md"
Write-Host "      ├── morpheus.docs/Morpheus_SE_AGENT.md"
Write-Host "      ├── trin.docs/Trin_QA_AGENT.md"
Write-Host "      ├── oracle.docs/Oracle_INFO_AGENT.md"
Write-Host "      ├── mouse.docs/Mouse_SM_AGENT.md"
Write-Host "      └── cypher.docs/Cypher_PM_AGENT.md"
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. cd $sandboxDir"
Write-Host "  2. Read README.md"
Write-Host "  3. Read TEST_SCENARIO.md"
Write-Host "  4. Test with: *chat"
Write-Host ""
