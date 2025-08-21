#!/usr/bin/env python3
"""
Azure AI Foundry AgentCarRepair Web Application

A Flask-based web application that provides an interactive chat interface to communicate
with Azure AI Foundry agents specifically designed for car repair assistance and troubleshooting.

This application serves as a web frontend for Azure AI Foundry agent services, allowing users
to engage in conversational interactions with AI agents that can help diagnose car problems,
provide repair guidance, and offer automotive advice.

Key Features:
    - Web-based chat interface for car repair assistance
    - Integration with Azure AI Foundry agent services
    - Session management for maintaining conversation context
    - Real-time message formatting with HTML support
    - Status monitoring and health checks
    - Environment configuration validation
    - Responsive design for desktop and mobile devices

Prerequisites:
    - Python 3.8 or higher
    - Azure subscription with AI Foundry project
    - Service principal with appropriate permissions
    - Azure AI agent configured for car repair assistance

Environment Variables Required:
    - AZURE_CLIENT_ID: Service principal client ID
    - AZURE_CLIENT_SECRET: Service principal secret
    - AZURE_TENANT_ID: Azure tenant ID
    - AZURE_ENDPOINT: Azure AI Foundry project endpoint
    - AZURE_AGENT_ID: ID of the car repair agent
    - FLASK_SECRET_KEY: Secret key for Flask sessions (optional)

Usage:
    python AgentRepair.py

The application will start a web server on http://localhost:5000

Author: James Morantus
Date: August 19, 2025
Version: 1.0.0
License: MIT
"""

import os
import json
import re
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any

# Flask web framework imports
from flask import Flask, render_template, request, jsonify, session

# Azure AI and authentication imports
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.ai.agents.models import ListSortOrder

# Environment variable management (optional dependency)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables.")

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this')

def format_message_content(text: str) -> str:
    """
    Format message content with proper HTML formatting for paragraphs and lists.
    
    This function processes plain text messages from the AI agent and converts them
    into properly formatted HTML for display in the web interface. It handles:
    - Converting line breaks to proper paragraph tags
    - Detecting and formatting bullet points and numbered lists
    - Cleaning up excessive whitespace and line breaks
    - Preserving the structure and readability of the agent's responses
    
    Args:
        text (str): The raw text message from the AI agent
        
    Returns:
        str: HTML-formatted text ready for display in the web interface
        
    Example:
        Input: "Here are the steps:\n- Check the engine\n- Look at the battery"
        Output: "<p>Here are the steps:</p><ul><li>Check the engine</li><li>Look at the battery</li></ul>"
    """
    if not text:
        return ""
    
    # Clean up the text
    text = text.strip()
    
    # Split into lines and process
    lines = text.split('\n')
    formatted_lines = []
    in_list = False
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append('<br>')
            continue
        
        # Check for bullet points (various formats)
        bullet_patterns = [
            r'^[-*•]\s+(.+)',  # - * • bullets
            r'^\d+\.\s+(.+)',  # numbered lists
            r'^[a-zA-Z]\.\s+(.+)',  # lettered lists
            r'^[ivx]+\.\s+(.+)',  # roman numerals
        ]
        
        is_bullet = False
        for pattern in bullet_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                if not in_list:
                    formatted_lines.append('<ul>')
                    in_list = True
                formatted_lines.append(f'<li>{match.group(1)}</li>')
                is_bullet = True
                break
        
        if not is_bullet:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            
            # Format as paragraph
            if line:
                formatted_lines.append(f'<p>{line}</p>')
    
    # Close any open list
    if in_list:
        formatted_lines.append('</ul>')
    
    # Join all formatted lines
    formatted_text = ''.join(formatted_lines)
    
    # Clean up multiple consecutive <br> tags
    formatted_text = re.sub(r'(<br>\s*){2,}', '<br><br>', formatted_text)
    
    # Remove <br> at the beginning or end
    formatted_text = re.sub(r'^<br>|<br>$', '', formatted_text)
    
    return formatted_text

def create_credential(debug: bool = False) -> DefaultAzureCredential | ClientSecretCredential:
    """
    Create Azure credential for authentication with Azure AI Foundry services.
    
    This function attempts to create the appropriate Azure credential based on
    available environment variables. It first tries to use service principal
    authentication (recommended for production), and falls back to default
    Azure credential chain if service principal credentials are not available.
    
    The default credential chain tries multiple authentication methods in order:
    1. Environment variables (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)
    2. Managed Identity (if running on Azure)
    3. Azure CLI credentials (if logged in via az login)
    4. Visual Studio Code credentials
    5. Azure PowerShell credentials
    
    Args:
        debug (bool): If True, prints authentication method being used
        
    Returns:
        DefaultAzureCredential | ClientSecretCredential: Configured Azure credential object
        
    Raises:
        ValueError: If no valid authentication method is available
        
    Example:
        credential = create_credential(debug=True)
    """
    # Try service principal first
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID')
    
    if all([client_id, client_secret, tenant_id]):
        if debug:
            print("🔐 Using service principal authentication")
        
        return ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
    else:
        if debug:
            print("🔐 Using default Azure credential")
        
        return DefaultAzureCredential()

def get_project_client() -> AIProjectClient:
    """
    Create and return an Azure AI Project client instance.
    
    This function creates a client for interacting with Azure AI Foundry project services.
    The client is configured with the appropriate credentials and endpoint URL.
    
    Returns:
        AIProjectClient: Configured AI Project client for making API calls
        
    Raises:
        ValueError: If AZURE_ENDPOINT environment variable is not set
        azure.core.exceptions.ClientAuthenticationError: If authentication fails
        
    Example:
        project_client = get_project_client()
        agents = project_client.agents.list()
    """
    endpoint = os.getenv('AZURE_ENDPOINT')
    if not endpoint:
        raise ValueError("AZURE_ENDPOINT environment variable is required")
    
    return AIProjectClient(
        credential=create_credential(),
        endpoint=endpoint
    )

def validate_environment() -> Tuple[bool, List[str]]:
    """
    Validate that all required environment variables are set.
    
    This function checks for the presence of all environment variables required
    for the application to function properly. It's called during application
    startup and can be used for health checks.
    
    Required environment variables:
        - AZURE_CLIENT_ID: Service principal client ID
        - AZURE_CLIENT_SECRET: Service principal secret
        - AZURE_TENANT_ID: Azure tenant ID
        - AZURE_ENDPOINT: Azure AI Foundry project endpoint URL
        - AZURE_AGENT_ID: ID of the car repair agent to use
    
    Returns:
        Tuple[bool, List[str]]: A tuple containing:
            - bool: True if all variables are set, False otherwise
            - List[str]: List of missing variable names (empty if all are set)
            
    Example:
        is_valid, missing = validate_environment()
        if not is_valid:
            print(f"Missing variables: {missing}")
    """
    required_vars = ['AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID', 'AZURE_ENDPOINT', 'AZURE_AGENT_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        return False, missing_vars
    return True, []

@app.route('/')
def index():
    """
    Render the main chat interface page.
    
    This is the primary endpoint for the web application. It validates the
    environment configuration before rendering the chat interface. If any
    required environment variables are missing, it displays an error page
    with instructions for proper configuration.
    
    Returns:
        str: Rendered HTML template (either chat.html or error.html)
        
    HTTP Status Codes:
        200: Success - chat interface loaded
        500: Server error - missing configuration
    """
    # Validate environment
    is_valid, missing_vars = validate_environment()
    if not is_valid:
        return render_template('error.html', 
                             error="Missing Environment Variables",
                             details=f"Required variables: {', '.join(missing_vars)}")
    
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages with the AI agent.
    
    This endpoint processes user messages and communicates with the Azure AI Foundry
    agent to generate responses. It manages conversation threads, maintains session
    state, and formats responses for display in the web interface.
    
    Request Format:
        POST /api/chat
        Content-Type: application/json
        Body: {"message": "user message text"}
    
    Response Format:
        Success (200): {
            "response": "formatted HTML response",
            "raw_response": "original agent response",
            "thread_id": "conversation thread ID",
            "timestamp": "ISO format timestamp"
        }
        Error (400/500): {
            "error": "error description"
        }
    
    Session Management:
        - Creates new conversation threads as needed
        - Maintains thread ID in Flask session
        - Handles thread persistence across requests
    
    Returns:
        Response: JSON response with agent reply or error details
        
    HTTP Status Codes:
        200: Success - agent responded
        400: Bad Request - empty message
        500: Server Error - Azure API issues, agent failures, etc.
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get or create project client
        project = get_project_client()
        
        # Get agent ID from environment variable
        agent_id = os.getenv('AZURE_AGENT_ID')
        if not agent_id:
            return jsonify({'error': 'AZURE_AGENT_ID environment variable is required'}), 500
        

        
        try:
            agent = project.agents.get_agent(agent_id)
        except Exception as e:
            return jsonify({'error': f'Failed to get agent: {str(e)}'}), 500
        
        # Create or get thread from session
        thread_id = session.get('thread_id')
        if not thread_id:
            try:
                thread = project.agents.threads.create()
                thread_id = thread.id
                session['thread_id'] = thread_id
            except Exception as e:
                return jsonify({'error': f'Failed to create thread: {str(e)}'}), 500
        
        # Create user message
        try:
            message = project.agents.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_message
            )
        except Exception as e:
            return jsonify({'error': f'Failed to create message: {str(e)}'}), 500
        
        # Process the run
        try:
            run = project.agents.runs.create_and_process(
                thread_id=thread_id,
                agent_id=agent.id
            )
        except Exception as e:
            return jsonify({'error': f'Failed to process run: {str(e)}'}), 500
        
        if run.status == "failed":
            return jsonify({'error': f'Agent run failed: {run.last_error}'}), 500
        
        # Get messages
        try:
            messages = project.agents.messages.list(thread_id=thread_id, order=ListSortOrder.DESCENDING)
            
            # Get the latest assistant message (first one since we're using DESCENDING order)
            assistant_response = ""
            raw_response = ""
            for message in messages:
                if message.role == "assistant" and message.text_messages:
                    raw_response = message.text_messages[-1].text.value
                    assistant_response = format_message_content(raw_response)
                    break
            
            return jsonify({
                'response': assistant_response,
                'raw_response': raw_response,
                'thread_id': thread_id,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({'error': f'Failed to get messages: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/new-conversation', methods=['POST'])
def new_conversation():
    """
    Start a new conversation by clearing the current thread.
    
    This endpoint allows users to start fresh conversations by removing
    the thread ID from the session. The next message will create a new
    conversation thread with the AI agent.
    
    Request Format:
        POST /api/new-conversation
        
    Response Format:
        Success (200): {
            "message": "New conversation started"
        }
    
    Returns:
        Response: JSON confirmation message
        
    HTTP Status Codes:
        200: Success - session cleared
    """
    session.pop('thread_id', None)
    return jsonify({'message': 'New conversation started'})

@app.route('/api/status')
def status():
    """
    Check system status and configuration.
    
    This endpoint provides health check functionality and system status information.
    It validates environment configuration, tests Azure connectivity, and returns
    diagnostic information useful for troubleshooting.
    
    The endpoint performs the following checks:
    1. Environment variable validation
    2. Azure authentication test
    3. Agent connectivity verification
    4. Session state information
    
    Response Format:
        Success (200): {
            "status": "ok",
            "message": "Connected successfully",
            "agent_id": "agent-id-string",
            "endpoint": "azure-endpoint-url",
            "thread_id": "current-thread-id-or-none"
        }
        Error (400/500): {
            "status": "error",
            "message": "error description"
        }
    
    Returns:
        Response: JSON status information
        
    HTTP Status Codes:
        200: Success - all systems operational
        400: Client Error - missing configuration
        500: Server Error - Azure connectivity issues
    """
    try:
        is_valid, missing_vars = validate_environment()
        
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': f'Missing environment variables: {", ".join(missing_vars)}'
            }), 400
        
        # Test connection to Azure
        try:
            project = get_project_client()
            agent_id = os.getenv('AZURE_AGENT_ID')
            if not agent_id:
                return jsonify({
                    'status': 'error',
                    'message': 'AZURE_AGENT_ID environment variable is missing'
                }), 400
            
            agent = project.agents.get_agent(agent_id)
            
            return jsonify({
                'status': 'ok',
                'message': 'Connected successfully',
                'agent_id': agent.id,
                'endpoint': os.getenv('AZURE_ENDPOINT', 'not-set'),
                'thread_id': session.get('thread_id', 'none')
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Failed to connect to Azure AI Foundry: {str(e)}'
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'System error: {str(e)}'
        }), 500

if __name__ == '__main__':
    """
    Application entry point.
    
    This section handles application startup, including:
    - Environment validation
    - Startup logging
    - Development server configuration
    - Error handling for missing configuration
    
    The application will exit with code 1 if required environment
    variables are missing, displaying helpful setup instructions.
    """
    print("🚀 Starting Azure AI Foundry AgentCarRepair Web Application")
    print(f"📅 Application started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Validate environment on startup
    is_valid, missing_vars = validate_environment()
    if not is_valid:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set these in your .env file:")
        for var in missing_vars:
            print(f"   {var}=your-{var.lower().replace('_', '-')}")
        print("\n📖 For detailed setup instructions, visit the error page at http://localhost:5000")
        print("   after starting the application with minimal configuration.")
        exit(1)
    
    print("✅ Environment validation passed")
    print("🌐 Starting AgentCarRepair web server at http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    
    # Run with debug mode based on environment
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    if debug_mode:
        print("🐛 Debug mode enabled")
    
    try:
        app.run(debug=debug_mode, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Application failed to start: {str(e)}")
        exit(1)
