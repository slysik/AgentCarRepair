# ============================================================================
# Azure AI Foundry AgentCarRepair Web Application - PowerShell Launcher
# 
# This PowerShell script provides an easy way to start the AgentCarRepair 
# application on Windows systems. It performs comprehensive setup and validation:
# 1. Validates PowerShell execution policy
# 2. Checks Python installation and version
# 3. Installs/updates required dependencies
# 4. Validates environment configuration
# 5. Starts the web application with proper error handling
#
# Requirements:
# - PowerShell 5.1 or higher
# - Python 3.8 or higher installed and in PATH
# - pip package manager available
# - Execution policy allowing script execution
#
# Usage:
#   .\run_agentrepair.ps1
#   or right-click and "Run with PowerShell"
#
# The application will be available at: http://localhost:5000
# ============================================================================

# Script parameters and settings
param(
    [switch]$SkipDependencyInstall = $false,
    [switch]$Verbose = $false
)

# Set error handling
$ErrorActionPreference = "Stop"

# Function to write colored output
function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White",
        [string]$Prefix = ""
    )
    
    if ($Prefix) {
        Write-Host "$Prefix " -NoNewline -ForegroundColor $Color
        Write-Host $Message
    } else {
        Write-Host $Message -ForegroundColor $Color
    }
}

# Function to write step headers
function Write-Step {
    param([string]$StepNumber, [string]$Description)
    Write-Host ""
    Write-ColoredOutput "Step $StepNumber : $Description" "Cyan" "📋"
}

# Function to check PowerShell version
function Test-PowerShellVersion {
    Write-Step "1" "Checking PowerShell Environment"
    
    $psVersion = $PSVersionTable.PSVersion
    Write-Host "   PowerShell Version: $($psVersion.Major).$($psVersion.Minor)"
    Write-Host "   Platform: $($PSVersionTable.Platform ?? 'Windows PowerShell')"
    
    if ($psVersion.Major -lt 5) {
        Write-ColoredOutput "PowerShell 5.1 or higher is recommended" "Yellow" "⚠️ "
    } else {
        Write-ColoredOutput "PowerShell version is compatible" "Green" "✅"
    }
    
    return $true
}

# Function to check Python installation
function Test-PythonInstallation {
    Write-Step "2" "Validating Python Installation"
    
    try {
        # Check if Python is available
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python command failed"
        }
        
        Write-Host "   $pythonVersion"
        
        # Extract version numbers
        if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            $patch = [int]$Matches[3]
            
            Write-Host "   Detected Version: $major.$minor.$patch"
            Write-Host "   Minimum Required: 3.8.0"
            
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
                throw "Python 3.8 or higher is required"
            }
            
            Write-ColoredOutput "Python version is compatible" "Green" "✅"
            return $true
        } else {
            throw "Could not parse Python version"
        }
        
    } catch {
        Write-ColoredOutput "ERROR: Python is not installed or not in PATH" "Red" "❌"
        Write-Host ""
        Write-Host "📝 To fix this issue:"
        Write-Host "   1. Download Python from https://python.org"
        Write-Host "   2. Install Python with 'Add to PATH' option checked"
        Write-Host "   3. Restart PowerShell and try again"
        Write-Host ""
        return $false
    }
}

# Function to install dependencies
function Install-Dependencies {
    if ($SkipDependencyInstall) {
        Write-Step "3" "Skipping Dependency Installation (--SkipDependencyInstall)"
        return $true
    }
    
    Write-Step "3" "Installing/Updating Dependencies"
    
    $requirementsFile = "requirements-agentrepair.txt"
    
    if (-not (Test-Path $requirementsFile)) {
        Write-ColoredOutput "ERROR: $requirementsFile not found" "Red" "❌"
        return $false
    }
    
    try {
        Write-Host "   Installing packages from $requirementsFile..."
        
        if ($Verbose) {
            pip install -r $requirementsFile --upgrade
        } else {
            pip install -r $requirementsFile --quiet --upgrade
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColoredOutput "Dependencies installed successfully" "Green" "✅"
            return $true
        } else {
            throw "pip install failed with exit code $LASTEXITCODE"
        }
        
    } catch {
        Write-ColoredOutput "ERROR: Failed to install required packages" "Red" "❌"
        Write-Host ""
        Write-Host "📝 Possible solutions:"
        Write-Host "   1. Check internet connection"
        Write-Host "   2. Update pip: python -m pip install --upgrade pip"
        Write-Host "   3. Run PowerShell as Administrator"
        Write-Host "   4. Use --SkipDependencyInstall to skip this step"
        Write-Host ""
        return $false
    }
}

# Function to check environment configuration
function Test-EnvironmentConfiguration {
    Write-Step "4" "Checking Environment Configuration"
    
    $envFile = ".env"
    $templateFile = ".env.template"
    
    if (-not (Test-Path $envFile)) {
        Write-ColoredOutput "WARNING: .env file not found" "Yellow" "⚠️ "
        Write-Host ""
        
        if (Test-Path $templateFile) {
            Write-Host "📝 Setup instructions:"
            Write-Host "   1. Copy template: Copy-Item '$templateFile' '$envFile'"
            Write-Host "   2. Edit $envFile with your Azure credentials"
            Write-Host "   3. See README.md for detailed configuration guide"
        } else {
            Write-Host "📝 Please create a $envFile file with your Azure configuration"
        }
        
        Write-Host ""
        Write-Host "Required environment variables:"
        $requiredVars = @(
            "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID",
            "AZURE_ENDPOINT", "AZURE_AGENT_ID"
        )
        foreach ($var in $requiredVars) {
            Write-Host "   - $var"
        }
        
        Write-Host ""
        Write-ColoredOutput "Application will start but may show configuration errors" "Yellow" "💡"
        return $false
    } else {
        Write-ColoredOutput ".env file found" "Green" "✅"
        
        # Optionally validate env file content
        try {
            $envContent = Get-Content $envFile
            $configuredVars = ($envContent | Where-Object { $_ -match "^[A-Z_]+=.+" }).Count
            Write-Host "   Configuration entries found: $configuredVars"
        } catch {
            Write-Host "   Could not read .env file content"
        }
        
        return $true
    }
}

# Function to start the application
function Start-Application {
    Write-Step "5" "Starting Web Application"
    
    Write-Host ""
    Write-ColoredOutput "🌐 Web application will be available at: http://localhost:5000" "Green"
    Write-ColoredOutput "🛑 Press Ctrl+C to stop the server" "Yellow"
    Write-ColoredOutput "📖 Check README.md for usage instructions" "Cyan"
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-ColoredOutput "🎯 Application Starting..." "Cyan"
    Write-Host "============================================" -ForegroundColor Cyan
    
    try {
        python AgentRepair.py
        return $true
    } catch {
        Write-ColoredOutput "ERROR: Failed to start web application" "Red" "❌"
        Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to show summary and next steps
function Show-Summary {
    param([bool]$Success)
    
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    if ($Success) {
        Write-ColoredOutput "🛑 Application Stopped" "Yellow"
    } else {
        Write-ColoredOutput "❌ Setup Failed" "Red"
    }
    Write-Host "============================================" -ForegroundColor Cyan
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "📅 Session ended: $timestamp"
    Write-Host ""
    
    Write-Host "💡 Next steps:"
    if ($Success) {
        Write-Host "   - Configuration looks good!"
        Write-Host "   - Check console output for any warnings"
        Write-Host "   - Visit http://localhost:5000 to use the application"
    } else {
        Write-Host "   - Resolve the issues mentioned above"
        Write-Host "   - Run this script again: .\run_agentrepair.ps1"
        Write-Host "   - Check README.md for detailed troubleshooting"
    }
    
    Write-Host ""
    Write-Host "� Resources:"
    Write-Host "   - README.md: Complete documentation"
    Write-Host "   - .env.template: Configuration examples"
    Write-Host "   - setup.py: Automated setup script"
    Write-Host ""
}

# Main execution block
try {
    # Script header
    Write-Host "============================================" -ForegroundColor Cyan
    Write-ColoredOutput "🚗 Azure AI Foundry AgentCarRepair" "Cyan"
    Write-ColoredOutput "   Car Repair Assistant Web Application" "Cyan"
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "📅 Started: $timestamp"
    Write-Host "💻 Platform: Windows PowerShell"
    Write-Host "📂 Directory: $(Get-Location)"
    
    if ($Verbose) {
        Write-Host "🔧 Verbose mode enabled"
    }
    
    # Execute setup steps
    $success = $true
    
    if (-not (Test-PowerShellVersion)) { $success = $false }
    if (-not (Test-PythonInstallation)) { $success = $false }
    if (-not (Install-Dependencies)) { $success = $false }
    
    # Environment check is informational, doesn't fail the process
    Test-EnvironmentConfiguration | Out-Null
    
    if ($success) {
        Start-Application | Out-Null
    } else {
        Write-Host ""
        Write-ColoredOutput "Cannot start application due to setup issues" "Red" "❌"
    }
    
    Show-Summary -Success $success
    
} catch {
    Write-Host ""
    Write-ColoredOutput "💥 Unexpected error: $($_.Exception.Message)" "Red"
    Write-Host "Stack trace:" -ForegroundColor Yellow
    Write-Host $_.ScriptStackTrace -ForegroundColor Yellow
    Show-Summary -Success $false
} finally {
    # Pause for user input unless in non-interactive mode
    if (-not $env:CI -and -not $env:GITHUB_ACTIONS) {
        Write-Host ""
        Read-Host "Press Enter to exit"
    }
}
