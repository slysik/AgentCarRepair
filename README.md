# AI Car Repair Assistant Web Application

A Flask-based web application that provides an interactive chat interface for car repair assistance using OpenAI's GPT models.

## 🚗 Overview

This application serves as a web frontend for OpenAI API services, specifically designed for automotive troubleshooting and repair guidance. Users can engage in conversational interactions with AI that helps diagnose car problems, provide repair instructions, and offer automotive advice.

![Complete App](RepairAgent-Screenshot.png)


## ✨ Features

- **Interactive Chat Interface**: Modern, responsive web UI for seamless conversations
- **OpenAI Integration**: Direct connection to OpenAI GPT models for intelligent responses
- **Session Management**: Maintains conversation context across multiple messages
- **Real-time Formatting**: Automatically formats agent responses with proper HTML
- **Status Monitoring**: Built-in health checks and OpenAI API connectivity reporting
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices
- **Error Handling**: Comprehensive error handling with helpful user feedback

## 🛠️ Prerequisites

### Car Repair Manuals
- Download Free Car Manuals [here](https://www.allcarmanuals.com/makesmodels.html)

### Tools
- [VS Code](https://code.visualstudio.com/download)

### API Requirements
- [OpenAI API account](https://platform.openai.com/signup) and API key
- OpenAI API credits for GPT model usage

### System Requirements
- Python 3.8 or higher
- pip package manager
- Modern web browser

### Required Setup
- Valid OpenAI API key with sufficient credits
- Internet connection for API access 

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/AgentCarRepair.git
cd AgentCarRepair
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements-agentrepair.txt
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Flask Configuration (Optional)
FLASK_SECRET_KEY=your-secret-key-for-sessions
FLASK_DEBUG=False
```

### Getting OpenAI Credentials

**Get OpenAI API Key**:
   - Sign up at [OpenAI Platform](https://platform.openai.com/signup)
   - Navigate to [API Keys](https://platform.openai.com/account/api-keys)
   - Create a new secret key
   - Copy the key for use in your `.env` file

## 🚀 Running the Application

### Development Mode
```bash
python AgentRepair.py
```
## 📱 Usage

### Web Interface
1. Open your browser to `http://localhost:5001`
2. Start typing your car-related questions
3. The OpenAI GPT model will provide repair guidance and troubleshooting steps
4. Use the control buttons to:
   - Start new conversations
   - Check system status
   - Clear chat history

### API Endpoints

#### Chat with Agent
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "My car won't start, what should I check?"
}

or

curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "My car won'\''t start, what should I check?"}''
```

#### Status Check
```bash
GET /api/status
```

#### New Conversation
```bash
POST /api/new-conversation
```

## 🏗️ Architecture

### Components
- **Flask Web Server**: Handles HTTP requests and responses
- **OpenAI Client**: Manages communication with OpenAI API services
- **Session Management**: Maintains conversation context across messages
- **Message Formatting**: Converts AI responses to HTML for display
- **Error Handling**: Comprehensive error handling with user-friendly messages

```
## 🐛 Troubleshooting

### Common Issues

#### Missing Environment Variables
- **Error**: "Missing Environment Variables"
- **Solution**: Create `.env` file with all required variables
- **Check**: Run `/api/status` endpoint to verify configuration

#### API Authentication Failures
- **Error**: "Invalid OpenAI API key" or "Failed to connect to OpenAI API"
- **Solution**: Verify your OpenAI API key is correct and active
- **Check**: Test your key at [OpenAI Platform](https://platform.openai.com/)

#### Rate Limit Errors
- **Error**: "API rate limit exceeded"
- **Solution**: Check your OpenAI usage limits and billing status
- **Check**: Monitor usage at [OpenAI Usage](https://platform.openai.com/usage)

#### Connection Timeouts
- **Error**: "Request timeout" or "Failed to get AI response"
- **Solution**: Check network connectivity and OpenAI service status
- **Check**: [OpenAI Status Page](https://status.openai.com/) for service outages

### Debug Mode
Enable debug mode for detailed error information:
```env
FLASK_DEBUG=True
```

### Logging
Check console output for detailed error messages and system status.

## 🔒 Security Considerations

### Environment Variables
- Never commit `.env` files to version control
- Use secure environment variable management in production
- Rotate OpenAI API keys regularly
- Monitor API usage to prevent unexpected charges

## 📚 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenAI Pricing](https://openai.com/pricing)

---

**Last Updated**: August 25, 2025  
**Version**: 2.0.0  
**Current Implementation**: OpenAI GPT-4o-mini
