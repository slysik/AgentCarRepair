# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an AI Car Repair Assistant web application - a Flask-based chat interface for car repair assistance using OpenAI's GPT models. The application connects to OpenAI API services to provide conversational car troubleshooting and repair guidance.

## Development Commands

### Setup and Installation
```bash
# Initial setup (automated)
python setup.py

# Windows batch launcher
run_agentrepair.bat

# Windows PowerShell launcher (recommended)
.\run_agentrepair.ps1

# Manual dependency installation
pip install -r requirements-agentrepair.txt
```

### Running the Application
```bash
# Start the web server
python AgentRepair.py

# Application runs on http://localhost:5000
```

### Environment Configuration
Create `.env` file with required OpenAI credentials:
```env
OPENAI_API_KEY=your-openai-api-key
FLASK_SECRET_KEY=your-secret-key-for-sessions (optional)
FLASK_DEBUG=False (optional)
```

## Architecture Overview

### Core Components
- **AgentRepair.py**: Main Flask web application with routes for chat interface, API endpoints, and OpenAI integration
- **OpenAI Integration**: Uses `openai` SDK for GPT model communication with direct API authentication
- **Session Management**: Maintains conversation history and user state across interactions
- **Templates**: HTML templates for chat interface (`chat.html`), landing page (`landing.html`), and error handling (`error.html`)

### Key Routes and APIs
- `/` - Main chat interface (GET)
- `/api/chat` - Process user messages and return agent responses (POST)
- `/api/status` - Health check and configuration validation (GET)
- `/api/new-conversation` - Reset conversation thread (POST)

### Authentication Flow
1. OpenAI API key validation from environment variables
2. OpenAI client initialization with authenticated connection
3. Direct API communication with GPT-4o-mini model
4. Conversation context and session management

### Dependencies Architecture
- **Flask ecosystem**: Flask, Werkzeug, Jinja2, MarkupSafe for web framework
- **OpenAI SDK**: `openai` for GPT model integration and API communication
- **HTTP Libraries**: `requests`, `urllib3` for API connectivity
- **Optional**: `python-dotenv` for environment variable management

## OpenAI API Requirements

### Required API Resources
- Valid OpenAI API account with active subscription
- API key with sufficient credits for GPT model usage
- Internet connectivity for API access

### API Configuration
- Model: GPT-4o-mini (cost-effective for production use)
- Max tokens: 1000 per request
- Temperature: 0.7 for balanced creativity and consistency

## Development Workflow

### Testing Configuration
- Use `/api/status` endpoint to validate Azure connection and environment setup
- Check console logs for detailed error messages and connection status
- Verify `.env` configuration using `setup.py` validation

### Error Handling Patterns
- Comprehensive try-catch blocks around OpenAI API operations
- User-friendly error messages with configuration guidance
- Rate limiting and authentication error handling
- Session cleanup on API failures

### HTML Response Formatting
- GPT responses automatically converted to HTML format
- Conversation history maintained across sessions
- Real-time status updates through AJAX calls

## Security Considerations
- Never commit `.env` files to version control
- OpenAI API keys should be rotated regularly
- Flask secret key required for secure session management
- All API operations use authenticated OpenAI client
- Monitor API usage to prevent unexpected charges