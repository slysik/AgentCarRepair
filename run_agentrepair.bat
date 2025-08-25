@echo off
REM ============================================================================
REM AI Car Repair Assistant Web Application - Windows Batch Launcher
REM 
REM This batch file provides an easy way to start the AI Car Repair Assistant
REM on Windows systems. It performs the following tasks:
REM 1. Validates Python installation
REM 2. Installs required dependencies
REM 3. Checks environment configuration
REM 4. Starts the web application
REM
REM Requirements:
REM - Python 3.8 or higher installed and in PATH
REM - pip package manager available
REM - .env file with OpenAI API key (optional for startup)
REM
REM Usage:
REM   Double-click this file or run from command prompt: run_agentrepair.bat
REM
REM The application will be available at: http://localhost:5000
REM ============================================================================

echo ============================================
echo 🚗 AI Car Repair Assistant
echo    OpenAI-Powered Automotive Help
echo ============================================
echo.
echo 📅 Started at: %date% %time%
echo 💻 Platform: Windows
echo.

echo 🔍 Step 1: Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo 📝 To fix this:
    echo    1. Download Python from https://python.org
    echo    2. Install Python with "Add to PATH" option checked
    echo    3. Restart command prompt and try again
    echo.
    pause
    exit /b 1
)
echo ✅ Python is available

echo.
echo 📦 Step 2: Installing/updating required packages...
pip install -r requirements-agentrepair.txt --quiet --upgrade
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to install required packages
    echo.
    echo 📝 Possible solutions:
    echo    1. Check internet connection
    echo    2. Update pip: python -m pip install --upgrade pip
    echo    3. Try running as administrator
    echo.
    pause
    exit /b 1
)
echo ✅ Dependencies installed successfully

echo.
echo ⚙️ Step 3: Checking environment configuration...
if not exist .env (
    echo ⚠️  WARNING: .env file not found
    echo.
    echo 📝 Environment setup needed:
    echo    1. Copy .env.template to .env
    echo    2. Add your OpenAI API key
    echo    3. See README.md for detailed instructions
    echo.
    echo 💡 The application will start but may show configuration errors
    echo    Visit http://localhost:5000 for setup instructions
    echo.
) else (
    echo ✅ .env file found
)

echo.
echo 🚀 Step 4: Starting web application...
echo.
echo 🌐 Landing page: http://localhost:5000
echo 💬 Chat interface: http://localhost:5000/chat
echo 🛑 Press Ctrl+C to stop the server
echo 📖 Check README.md for usage instructions
echo.
echo ============================================
echo 🎯 Application Starting...
echo ============================================

REM Start the Python application
python AgentRepair.py

echo.
echo ============================================
echo 🛑 Application Stopped
echo ============================================
echo 📅 Stopped at: %date% %time%
echo.
echo 💡 Tips:
echo    - If you encountered errors, check the output above
echo    - For configuration help, see README.md
echo    - Get OpenAI API key at: https://platform.openai.com/api-keys
echo    - For troubleshooting, visit the /api/status endpoint
echo.

pause
