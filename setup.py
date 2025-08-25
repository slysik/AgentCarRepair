#!/usr/bin/env python3
"""
AI Car Repair Assistant - Setup and Installation Script

This script helps you set up the AI Car Repair Assistant application by:
1. Checking Python version compatibility
2. Installing required dependencies
3. Validating OpenAI configuration
4. Testing the application setup

Usage:
    python setup.py

Requirements:
    - Python 3.8 or higher
    - pip package manager
    - Internet connection for package installation
    - OpenAI API key
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🔧 {text}")
    print(f"{'='*60}")

def print_step(step_num, text):
    """Print a formatted step."""
    print(f"\n📋 Step {step_num}: {text}")

def print_success(text):
    """Print a success message."""
    print(f"✅ {text}")

def print_warning(text):
    """Print a warning message."""
    print(f"⚠️  {text}")

def print_error(text):
    """Print an error message."""
    print(f"❌ {text}")

def check_python_version():
    """Check if Python version is compatible."""
    print_step(1, "Checking Python Version")
    
    version = sys.version_info
    min_version = (3, 8)
    
    print(f"   Current Python version: {version.major}.{version.minor}.{version.micro}")
    print(f"   Minimum required version: {min_version[0]}.{min_version[1]}")
    
    if version >= min_version:
        print_success("Python version is compatible")
        return True
    else:
        print_error(f"Python {min_version[0]}.{min_version[1]} or higher is required")
        print("   Please upgrade Python and try again.")
        return False

def check_pip():
    """Check if pip is available and get version."""
    print_step(2, "Checking pip Package Manager")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"   {result.stdout.strip()}")
        print_success("pip is available")
        return True
    except subprocess.CalledProcessError:
        print_error("pip is not available")
        print("   Please install pip and try again.")
        return False

def install_dependencies():
    """Install required dependencies from requirements file."""
    print_step(3, "Installing Dependencies")
    
    requirements_file = Path(__file__).parent / "requirements-agentrepair.txt"
    
    if not requirements_file.exists():
        print_error("requirements-agentrepair.txt file not found")
        return False
    
    try:
        print("   Installing packages from requirements-agentrepair.txt...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True, check=True)
        
        print_success("Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error("Failed to install dependencies")
        print(f"   Error: {e.stderr}")
        return False

def check_env_file():
    """Check if .env file exists and help create it."""
    print_step(4, "Checking Environment Configuration")
    
    env_file = Path(__file__).parent / ".env"
    template_file = Path(__file__).parent / ".env.template"
    
    if env_file.exists():
        print_success(".env file found")
        return True
    else:
        print_warning(".env file not found")
        
        if template_file.exists():
            print("   📝 A template file (.env.template) is available")
            print("   Please copy it to .env and fill in your OpenAI API key:")
            print(f"   copy {template_file.name} .env  (Windows)")
            print(f"   cp {template_file.name} .env    (macOS/Linux)")
        else:
            print("   Please create a .env file with your OpenAI configuration")
        
        print("\n   Required environment variables:")
        required_vars = [
            "OPENAI_API_KEY"
        ]
        optional_vars = [
            "FLASK_SECRET_KEY", "FLASK_DEBUG"
        ]
        for var in required_vars:
            print(f"   - {var} (required)")
        for var in optional_vars:
            print(f"   - {var} (optional)")
        
        return False

def test_imports():
    """Test if all required packages can be imported."""
    print_step(5, "Testing Package Imports")
    
    required_packages = [
        ("flask", "Flask web framework"),
        ("openai", "OpenAI Python SDK"),
    ]
    
    all_good = True
    
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} - {description}")
        except ImportError as e:
            print(f"   ❌ {package} - Failed to import: {e}")
            all_good = False
    
    # Test optional packages
    optional_packages = [
        ("dotenv", "Environment variable loading (optional)"),
    ]
    
    for package, description in optional_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} - {description}")
        except ImportError:
            print(f"   ⚠️  {package} - {description} - Not installed")
    
    if all_good:
        print_success("All required packages imported successfully")
    else:
        print_error("Some required packages failed to import")
    
    return all_good

def validate_openai_config():
    """Validate OpenAI configuration if .env file exists."""
    print_step(6, "Validating OpenAI Configuration")
    
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print_warning("Skipping - .env file not found")
        print("   Create and configure .env file, then run this script again")
        return False
    
    # Try to load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print("   📁 Loaded environment variables from .env file")
    except ImportError:
        print("   📁 Loading environment variables (python-dotenv not available)")
    
    required_vars = ["OPENAI_API_KEY"]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print_error(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print_success("All required environment variables are set")
        
        # Try to test OpenAI connection
        try:
            import openai
            from openai import OpenAI
            
            # Test API connection
            api_key = os.getenv('OPENAI_API_KEY')
            client = OpenAI(api_key=api_key)
            
            print("   🔐 Testing OpenAI API connection...")
            
            # Test with a simple API call
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10
            )
            
            print_success(f"Successfully connected to OpenAI API")
            print(f"   Model: gpt-4o-mini")
            print(f"   Test response received")
            return True
            
        except openai.AuthenticationError:
            print_error("Invalid OpenAI API key")
            print("   Please check your OPENAI_API_KEY in the .env file")
            return False
        except openai.RateLimitError:
            print_warning("API rate limit reached, but connection is valid")
            print("   Your API key is working correctly")
            return True
        except Exception as e:
            print_error(f"Failed to connect to OpenAI API: {str(e)}")
            print("   Please check your API key and internet connection")
            return False

def print_next_steps():
    """Print instructions for next steps."""
    print_header("Next Steps")
    
    print("🚀 Setup Complete! Here's what to do next:")
    print()
    print("1. 📝 Configure your environment:")
    print("   - Copy .env.template to .env (if not already done)")
    print("   - Add your OpenAI API key to the .env file")
    print("   - Get your API key from: https://platform.openai.com/api-keys")
    print()
    print("2. 🧪 Test the application:")
    print("   python AgentRepair.py")
    print()
    print("3. 🌐 Open your browser:")
    print("   Landing page: http://localhost:5000")
    print("   Chat interface: http://localhost:5000/chat")
    print()
    print("4. 📚 For detailed instructions, see:")
    print("   - README.md (comprehensive documentation)")
    print("   - .env.template (configuration examples)")
    print()
    print("🆘 Need help?")
    print("   - Check the troubleshooting section in README.md")
    print("   - Verify your OpenAI API key is valid")
    print("   - Ensure you have sufficient OpenAI API credits")

def main():
    """Main setup function."""
    print_header("AI Car Repair Assistant Setup")
    print("🛠️  This script will help you set up the AI car repair assistant application")
    print(f"📍 Platform: {platform.system()} {platform.release()}")
    print(f"📂 Working directory: {Path(__file__).parent}")
    
    # Run setup steps
    steps_passed = 0
    total_steps = 6
    
    if check_python_version():
        steps_passed += 1
    
    if check_pip():
        steps_passed += 1
    
    if install_dependencies():
        steps_passed += 1
    
    if check_env_file():
        steps_passed += 1
    
    if test_imports():
        steps_passed += 1
    
    if validate_openai_config():
        steps_passed += 1
    
    # Summary
    print_header("Setup Summary")
    print(f"📊 Steps completed: {steps_passed}/{total_steps}")
    
    if steps_passed == total_steps:
        print_success("Setup completed successfully!")
        print("🎉 Your AI Car Repair Assistant application is ready to run!")
    elif steps_passed >= 3:
        print_warning("Setup partially completed")
        print("⚙️  You can run the application, but some features may not work")
    else:
        print_error("Setup incomplete")
        print("🔧 Please resolve the issues above and run setup again")
    
    print_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error during setup: {e}")
        sys.exit(1)
