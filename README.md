# Azure AI Foundry AgentCarRepair Web Application

A Flask-based web application that provides an interactive chat interface for car repair assistance using Azure AI Foundry agents.

## 🚗 Overview

This application serves as a web frontend for Azure AI Foundry agent services, specifically designed for automotive troubleshooting and repair guidance. Users can engage in conversational interactions with AI agents that help diagnose car problems, provide repair instructions, and offer automotive advice.

## ✨ Features

- **Interactive Chat Interface**: Modern, responsive web UI for seamless conversations
- **Azure AI Integration**: Direct connection to Azure AI Foundry agent services
- **Session Management**: Maintains conversation context across multiple messages
- **Real-time Formatting**: Automatically formats agent responses with proper HTML
- **Status Monitoring**: Built-in health checks and system status reporting
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices
- **Error Handling**: Comprehensive error handling with helpful user feedback

## 🛠️ Prerequisites

### Azure Requirements
- Azure Data Lake Storage (ADLS Gen2)
- Azure AI Search 
- Azure subscription with AI Foundry project
- Service principal with appropriate permissions
- Azure AI agent configured for car repair assistance
- Download Free Car Manuals here: https://www.allcarmanuals.com/makesmodels.html

### System Requirements
- Python 3.8 or higher
- pip package manager
- Modern web browser

### Required Permissions
Your service principal needs the following Azure roles:
- `Cognitive Services Contributor` on the AI Foundry project
- `Reader` role on the resource group

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
# Azure Authentication
AZURE_CLIENT_ID=your-service-principal-client-id
AZURE_CLIENT_SECRET=your-service-principal-secret
AZURE_TENANT_ID=your-azure-tenant-id

# Azure AI Foundry
AZURE_ENDPOINT=https://your-endpoint.services.ai.azure.com/api/projects/your-project
AZURE_AGENT_ID=your-car-repair-agent-id

# Flask Configuration (Optional)
FLASK_SECRET_KEY=your-secret-key-for-sessions
FLASK_DEBUG=False
```

### Getting Azure Credentials

1. **Create Service Principal**:
   ```bash
   az ad sp create-for-rbac --name "AgentCarRepair" --role "Cognitive Services Contributor"
   ```

2. **Get AI Foundry Project Details**:
   - Navigate to your Azure AI Foundry project
   - Copy the endpoint URL from the project overview
   - Note your agent ID from the agents section

3. **Set Permissions**:
   - Assign `Cognitive Services Contributor` role to your service principal
   - Ensure access to the AI Foundry project resources

## 🚀 Running the Application

### Development Mode
```bash
python AgentRepair.py
```

### Production Mode
```bash
# Using Gunicorn (Linux/macOS)
gunicorn -w 4 -b 0.0.0.0:5000 AgentRepair:app

# Using Waitress (Windows/Cross-platform)
waitress-serve --host=0.0.0.0 --port=5000 AgentRepair:app
```

The application will be available at: `http://localhost:5000`

## 📱 Usage

### Web Interface
1. Open your browser to `http://localhost:5000`
2. Start typing your car-related questions
3. The AI agent will provide repair guidance and troubleshooting steps
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
- **Azure AI Client**: Manages communication with AI Foundry services
- **Session Management**: Maintains conversation state
- **Message Formatting**: Converts agent responses to HTML
- **Error Handling**: Provides user-friendly error messages

### File Structure
```
AgentCarRepair/
├── AgentRepair.py              # Main application file
├── requirements-agentrepair.txt # Python dependencies
├── README.md                   # This documentation
├── .env                        # Environment variables (create this)
├── templates/
│   ├── chat.html              # Main chat interface
│   └── error.html             # Error page template
├── run_agentrepair.bat        # Windows batch file
└── run_agentrepair.ps1        # PowerShell script
```

## 🐛 Troubleshooting

### Common Issues

#### Missing Environment Variables
- **Error**: "Missing Environment Variables"
- **Solution**: Create `.env` file with all required variables
- **Check**: Run `/api/status` endpoint to verify configuration

#### Authentication Failures
- **Error**: "Failed to connect to Azure AI Foundry"
- **Solution**: Verify service principal credentials and permissions
- **Check**: Test Azure CLI: `az account show`

#### Agent Not Found
- **Error**: "Failed to get agent"
- **Solution**: Verify `AZURE_AGENT_ID` is correct
- **Check**: List agents in Azure AI Foundry portal

#### Connection Timeouts
- **Error**: "Request timeout"
- **Solution**: Check network connectivity and Azure service status
- **Check**: Azure status page for service outages

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
- Use Azure Key Vault for production secrets
- Rotate service principal credentials regularly

### Network Security
- Use HTTPS in production deployments
- Configure firewall rules appropriately
- Consider VPN or private endpoints for sensitive deployments

### Application Security
- Keep all dependencies updated
- Use strong Flask secret keys
- Implement rate limiting for production use

## 🚀 Production Deployment

### Azure App Service
1. Create Azure App Service instance
2. Configure application settings (environment variables)
3. Deploy code using Git or ZIP deployment
4. Configure custom domain and SSL

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements-agentrepair.txt .
RUN pip install -r requirements-agentrepair.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "AgentRepair:app"]
```

### Environment-Specific Configuration
- Use separate service principals for dev/staging/production
- Configure different agent IDs for different environments
- Use Azure Application Insights for monitoring

## 📊 Monitoring and Maintenance

### Health Checks
- Use `/api/status` endpoint for health monitoring
- Monitor Azure AI Foundry service quotas and usage
- Set up alerts for authentication failures

### Performance Monitoring
- Monitor response times and error rates
- Track Azure AI service usage and costs
- Use Application Insights for detailed telemetry

### Updates and Maintenance
- Regularly update Python dependencies
- Monitor Azure AI Foundry service updates
- Test application functionality after updates

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:
- How to set up your development environment
- Coding standards and best practices  
- How to submit pull requests
- Issue reporting guidelines

### Quick Contributing Steps
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with proper documentation
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **📖 Documentation**: Check [README.md](README.md) and [DOCUMENTATION.md](DOCUMENTATION.md)
- **🐛 Bug Reports**: Use our [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md)
- **💡 Feature Requests**: Use our [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md)
- **❓ Questions**: Use our [Configuration Help Template](.github/ISSUE_TEMPLATE/configuration_help.md)
- **💬 Discussions**: Join our [GitHub Discussions](https://github.com/yourusername/AgentCarRepair/discussions)

### Community
- ⭐ Star this repository if you find it helpful
- 🐛 Report bugs and issues
- 💡 Suggest new features
- 📖 Improve documentation
- 🔧 Submit pull requests

## 📊 Project Status

![GitHub release (latest by date)](https://img.shields.io/github/v/release/yourusername/AgentCarRepair)
![GitHub](https://img.shields.io/github/license/yourusername/AgentCarRepair)
![GitHub issues](https://img.shields.io/github/issues/yourusername/AgentCarRepair)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/AgentCarRepair)
![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/AgentCarRepair)

### Build Status
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/yourusername/AgentCarRepair/AgentCarRepair%20CI/CD%20Pipeline)

## 📚 Additional Resources

- [Azure AI Foundry Documentation](https://docs.microsoft.com/en-us/azure/ai-foundry/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Azure Identity Library](https://docs.microsoft.com/en-us/python/api/azure-identity/)
- [Azure AI Projects SDK](https://docs.microsoft.com/en-us/python/api/azure-ai-projects/)
- [Project Changelog](CHANGELOG.md)

## 🔄 Version History

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes, features, and fixes.

---

**Last Updated**: August 19, 2025  
**Version**: 1.0.0
