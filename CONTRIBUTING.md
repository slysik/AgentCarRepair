# Contributing to Azure AI Foundry AgentCarRepair

First off, thank you for considering contributing to AgentCarRepair! It's people like you that make this project better for everyone.

## 🎯 How Can I Contribute?

### Reporting Bugs 🐛

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** to demonstrate the steps
- **Describe the behavior you observed** and what behavior you expected
- **Include screenshots** if applicable
- **Include your environment details**:
  - Python version
  - Operating system
  - Azure AI Foundry configuration
  - Browser (if web interface issue)

### Suggesting Enhancements 💡

Enhancement suggestions are welcome! Please provide:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List some other applications where this enhancement exists** (if applicable)

### Code Contributions 🛠️

#### Development Setup

1. **Fork the repository** and clone your fork:
   ```bash
   git clone https://github.com/yourusername/AgentCarRepair.git
   cd AgentCarRepair
   ```

2. **Set up your development environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux  
   source venv/bin/activate
   
   pip install -r requirements-agentrepair.txt
   ```

3. **Configure your environment**:
   ```bash
   cp .env.template .env
   # Edit .env with your Azure credentials
   ```

4. **Run the setup validation**:
   ```bash
   python setup.py
   ```

#### Making Changes

1. **Create a new branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes** following our coding standards (see below)

3. **Test your changes thoroughly**:
   ```bash
   # Run the application
   python AgentRepair.py
   
   # Test different scenarios
   # - Normal chat functionality
   # - Error handling
   # - Configuration validation
   ```

4. **Update documentation** if needed:
   - Update README.md for new features
   - Add docstrings to new functions
   - Update .env.template if new environment variables are added

#### Pull Request Process

1. **Update the version** if applicable (in AgentRepair.py docstring)

2. **Create a pull request** with:
   - Clear title and description
   - Reference to any related issues
   - Screenshots for UI changes
   - Testing steps

3. **Ensure your PR**:
   - Passes all existing functionality tests
   - Includes appropriate documentation updates
   - Follows the coding standards below

## 📝 Coding Standards

### Python Code Style

- **Follow PEP 8** for Python code style
- **Use type hints** for function parameters and return values
- **Write comprehensive docstrings** for all functions and classes
- **Keep functions focused** and single-purpose
- **Use meaningful variable names**

Example:
```python
def process_user_message(message: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Process a user message and return the agent's response.
    
    Args:
        message (str): The user's input message
        thread_id (Optional[str]): Existing conversation thread ID
        
    Returns:
        Dict[str, Any]: Response containing agent reply and metadata
        
    Raises:
        ValueError: If message is empty or invalid
        AzureAPIError: If Azure service call fails
    """
```

### Frontend Code (HTML/CSS/JavaScript)

- **Use semantic HTML** elements
- **Follow responsive design** principles
- **Include accessibility features** (ARIA labels, alt text)
- **Comment complex JavaScript** logic
- **Use consistent indentation** (2 spaces for HTML/CSS/JS)

### Documentation Standards

- **Write clear, concise documentation**
- **Include code examples** where helpful
- **Use proper Markdown formatting**
- **Keep documentation up-to-date** with code changes
- **Explain the "why" not just the "what"**

## 🧪 Testing Guidelines

### Manual Testing Checklist

- [ ] Application starts without errors
- [ ] Chat interface loads properly
- [ ] Messages send and receive correctly
- [ ] Error handling works (try invalid inputs)
- [ ] New conversation functionality works
- [ ] Status endpoint returns correct information
- [ ] Environment validation catches missing variables

### Test Scenarios

1. **Happy Path Testing**:
   - Normal chat conversation
   - Starting new conversations
   - Checking status

2. **Error Path Testing**:
   - Missing environment variables
   - Invalid Azure credentials
   - Network connectivity issues
   - Empty messages

3. **Browser Testing** (for UI changes):
   - Chrome, Firefox, Edge, Safari
   - Mobile responsiveness
   - Different screen sizes

## 🔧 Development Tools

### Recommended Extensions (VS Code)

- Python extension
- Pylint
- Black Formatter
- GitLens
- Thunder Client (for API testing)

### Useful Commands

```bash
# Format code
black AgentRepair.py

# Lint code
pylint AgentRepair.py

# Type checking
mypy AgentRepair.py

# Security check
pip-audit

# Update dependencies
pip list --outdated
```

## 📋 Commit Message Guidelines

Use clear and meaningful commit messages:

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

Examples:
```
feat: add conversation export functionality
fix: handle timeout errors in Azure API calls
docs: update setup instructions for new users
style: format code with black formatter
```

## 🔒 Security Considerations

### Sensitive Information

- **Never commit** `.env` files or secrets
- **Use environment variables** for all configuration
- **Sanitize user inputs** to prevent injection attacks
- **Follow Azure security best practices**

### Reporting Security Issues

If you find a security vulnerability, please **DO NOT** open a public issue. Instead:

1. Email the maintainers privately
2. Provide detailed information about the vulnerability
3. Wait for confirmation before disclosing publicly

## 📞 Getting Help

### Documentation Resources

- **README.md** - Complete setup and usage guide
- **DOCUMENTATION.md** - Quick reference
- **Code comments** - Inline documentation
- **Azure AI Foundry docs** - Official Azure documentation

### Communication

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and community chat
- **Pull Request comments** - For code review discussions

### Development Questions

Before asking questions:

1. Check existing documentation
2. Search closed issues and PRs
3. Try the troubleshooting steps in README.md

When asking questions, include:
- What you're trying to achieve
- What you've already tried
- Your environment details
- Relevant error messages

## 🎉 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- README.md acknowledgments section

Thank you for contributing to AgentCarRepair! Your efforts help make automotive AI assistance more accessible to everyone.

---

**Questions?** Feel free to open an issue or start a discussion. We're here to help!

*Last updated: August 19, 2025*
