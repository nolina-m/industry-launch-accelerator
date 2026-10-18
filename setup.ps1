# Industry Launch Accelerator: one-time setup for Windows (PowerShell).
# What it does: finds Python 3.10 or newer, creates a private Python
# environment in .venv\, installs the libraries, and checks which data
# sources are available.
#
# Usage:  powershell -ExecutionPolicy Bypass -File .\setup.ps1
#         powershell -ExecutionPolicy Bypass -File .\setup.ps1 -Dev   (also installs test tools)

param([switch]$Dev)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

function Fail($msg) {
    Write-Host ""
    Write-Host "[X] $msg" -ForegroundColor Red
    exit 1
}

Write-Host "Industry Launch Accelerator setup"
Write-Host "---------------------------------"

# 1. Find a Python that is 3.10 or newer.
$check = "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
$python = $null
$candidates = @("py -3", "python", "python3")
foreach ($candidate in $candidates) {
    $c = $candidate.Split(" ")
    $exe = $c[0]
    $extra = @()
    if ($c.Length -gt 1) { $extra = $c[1..($c.Length - 1)] }
    if (Get-Command $exe -ErrorAction SilentlyContinue) {
        & $exe @extra -c $check 2>$null
        if ($LASTEXITCODE -eq 0) { $python = $c; break }
    }
}

if (-not $python) {
    Fail ("Python 3.10 or newer was not found.`n" +
          "    Install it from https://www.python.org/downloads/ (click the yellow Download button).`n" +
          "    In the installer, tick 'Add python.exe to PATH' before clicking Install Now.`n" +
          "    Then close and reopen PowerShell and run this script again.")
}
$pyExe = $python[0]
$pyArgs = @()
if ($python.Length -gt 1) { $pyArgs = $python[1..($python.Length - 1)] }
$version = & $pyExe @pyArgs --version
Write-Host "[1/4] Found $version"

# 2. Create the private environment (.venv) if it does not exist yet.
$venvPy = Join-Path ".venv" "Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Host "[2/4] Creating a private Python environment in .venv\ ..."
    & $pyExe @pyArgs -m venv .venv
    if ($LASTEXITCODE -ne 0) { Fail "Could not create .venv." }
} else {
    Write-Host "[2/4] Private Python environment already exists (.venv\)"
}

# 3. Install libraries.
Write-Host "[3/4] Installing libraries (this can take a minute the first time) ..."
& $venvPy -m pip install --quiet --upgrade pip
if ($Dev) {
    & $venvPy -m pip install --quiet -r requirements-dev.txt
} else {
    & $venvPy -m pip install --quiet -r requirements.txt
}
if ($LASTEXITCODE -ne 0) { Fail "Installing libraries failed. Check your internet connection and try again." }

# 4. Check which data sources are available.
if (Test-Path "scripts\connectors\check.py") {
    Write-Host "[4/4] Checking data sources ..."
    & $venvPy scripts\connectors\check.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    (Some data sources could not be reached. That is OK; research continues without them.)"
    }
} else {
    Write-Host "[4/4] Data source check not available yet (skipped)"
}

Write-Host ""
Write-Host "[OK] Setup complete." -ForegroundColor Green
Write-Host "Next: open this folder in your coding agent (Claude Code, Codex, Cursor or similar)"
Write-Host "and say: start a new launch called <name>"
