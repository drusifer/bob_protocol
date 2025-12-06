# teardown_sandbox.ps1
# Deletes the 'test_sandbox' directory and all its contents.

# Stop script on first error
$ErrorActionPreference = 'Stop'

# Define the sandbox directory
$sandboxDir = "test_sandbox"

# Check if the directory exists before proceeding
if (-not (Test-Path -Path $sandboxDir)) {
    Write-Host "Sandbox directory '$sandboxDir' not found. Nothing to do."
    exit
}

# --- Confirmation Prompt ---
# The -AsSecureString option is not used here as we just need a simple y/n
$choice = Read-Host -Prompt "Are you sure you want to permanently delete the '$sandboxDir' directory and all its contents? [y/n]"

# --- Deletion Logic ---
if ($choice -eq 'y' -or $choice -eq 'Y') {
    Write-Host "Deleting sandbox..."
    try {
        Remove-Item -Path $sandboxDir -Recurse -Force
        Write-Host ""
        Write-Host "✅ Sandbox removed successfully."
    } catch {
        Write-Error "An error occurred while deleting the sandbox: $_"
        exit 1
    }
} else {
    Write-Host "Teardown cancelled."
}
