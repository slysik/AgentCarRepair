#!/usr/bin/env python3
"""
AI Car Repair Assistant Web Application

A Flask-based web application that provides an interactive chat interface to communicate
with OpenAI's GPT models specifically designed for car repair assistance and troubleshooting.

This application serves as a web frontend for OpenAI API, allowing users
to engage in conversational interactions with AI that can help diagnose car problems,
provide repair guidance, and offer automotive advice.

Key Features:
    - Web-based chat interface for car repair assistance
    - Integration with OpenAI API
    - Session management for maintaining conversation context
    - Real-time message formatting with HTML support
    - Status monitoring and health checks
    - Modern landing page with responsive design
    - Responsive design for desktop and mobile devices

Prerequisites:
    - Python 3.8 or higher
    - OpenAI API key

Environment Variables Required:
    - OPENAI_API_KEY: Your OpenAI API key
    - FLASK_SECRET_KEY: Secret key for Flask sessions (optional)

Usage:
    python AgentRepair.py

The application will start a web server on http://localhost:5000

Author: James Morantus
Date: August 22, 2025
Version: 2.0.0
License: MIT
"""

import os
import json
import re
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any

# Flask web framework imports
from flask import Flask, render_template, request, jsonify, session

# OpenAI imports
import openai
from openai import OpenAI

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

def get_openai_client() -> OpenAI:
    """
    Create and return an OpenAI client instance.
    
    This function creates a client for interacting with OpenAI API services.
    The client is configured with the API key from environment variables.
    
    Returns:
        OpenAI: Configured OpenAI client for making API calls
        
    Raises:
        ValueError: If OPENAI_API_KEY environment variable is not set
        
    Example:
        client = get_openai_client()
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    return OpenAI(api_key=api_key)

def create_car_repair_prompt(user_message: str, conversation_history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
    """
    Create a prompt for the OpenAI API with car repair context.
    
    This function creates a conversation prompt that includes system instructions
    for car repair assistance and the user's message history.
    
    Args:
        user_message (str): The user's current message
        conversation_history (List[Dict[str, str]]): Previous conversation messages
    
    Returns:
        List[Dict[str, str]]: Formatted messages for OpenAI API
    """
    system_message = {
        "role": "system",
        "content": """You are an expert automotive mechanic and car repair assistant. Your role is to help users diagnose car problems, provide repair guidance, and offer automotive advice. 

Guidelines:
- Always prioritize safety first
- Provide step-by-step instructions when appropriate
- Explain technical terms in simple language
- Suggest when professional help is needed
- Ask clarifying questions to better diagnose issues
- Provide cost estimates when possible
- Cover all car makes and models
- Include both DIY solutions and professional repair options

When responding:
1. Acknowledge the user's problem
2. Ask clarifying questions if needed
3. Provide possible diagnoses
4. Suggest troubleshooting steps
5. Recommend next actions (DIY or professional)
6. Include safety warnings when relevant"""
    }
    
    messages = [system_message]
    
    # Add conversation history if available
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    return messages

def validate_environment() -> Tuple[bool, List[str]]:
    """
    Validate that all required environment variables are set.
    
    This function checks for the presence of all environment variables required
    for the application to function properly. It's called during application
    startup and can be used for health checks.
    
    Required environment variables:
        - OPENAI_API_KEY: OpenAI API key for accessing GPT models
    
    Returns:
        Tuple[bool, List[str]]: A tuple containing:
            - bool: True if all variables are set, False otherwise
            - List[str]: List of missing variable names (empty if all are set)
            
    Example:
        is_valid, missing = validate_environment()
        if not is_valid:
            print(f"Missing variables: {missing}")
    """
    required_vars = ['OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        return False, missing_vars
    return True, []

@app.route('/')
def index():
    """
    Render the landing page.
    
    This is the primary endpoint for the web application showing the
    modern landing page with features and call-to-action.
    
    Returns:
        str: Rendered HTML template (landing.html)
        
    HTTP Status Codes:
        200: Success - landing page loaded
    """
    return render_template('landing.html')

@app.route('/chat')
def chat_page():
    """
    Render the chat interface page.
    
    This endpoint validates the environment configuration before rendering 
    the chat interface. If any required environment variables are missing, 
    it displays an error page with instructions for proper configuration.
    
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
    Handle chat messages with the OpenAI API.
    
    This endpoint processes user messages and communicates with OpenAI's GPT models
    to generate car repair assistance responses. It maintains conversation history
    in the session and formats responses for display in the web interface.
    
    Request Format:
        POST /api/chat
        Content-Type: application/json
        Body: {"message": "user message text"}
    
    Response Format:
        Success (200): {
            "response": "formatted HTML response",
            "raw_response": "original AI response",
            "conversation_id": "conversation session ID",
            "timestamp": "ISO format timestamp"
        }
        Error (400/500): {
            "error": "error description"
        }
    
    Session Management:
        - Maintains conversation history in Flask session
        - Stores up to last 10 messages for context
    
    Returns:
        Response: JSON response with AI reply or error details
        
    HTTP Status Codes:
        200: Success - AI responded
        400: Bad Request - empty message
        500: Server Error - OpenAI API issues
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get or create OpenAI client
        try:
            client = get_openai_client()
        except ValueError as e:
            return jsonify({'error': str(e)}), 500
        
        # Get conversation history from session (limit to last 10 messages)
        conversation_history = session.get('conversation_history', [])
        
        # Create prompt with conversation context
        messages = create_car_repair_prompt(user_message, conversation_history[-10:])
        
        try:
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Using GPT-4o-mini for cost efficiency
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            # Extract the assistant's response
            raw_response = response.choices[0].message.content
            formatted_response = format_message_content(raw_response)
            
            # Update conversation history in session
            conversation_history.append({"role": "user", "content": user_message})
            conversation_history.append({"role": "assistant", "content": raw_response})
            
            # Keep only last 20 messages (10 exchanges) to manage session size
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
            
            session['conversation_history'] = conversation_history
            
            # Generate or get conversation ID
            conversation_id = session.get('conversation_id')
            if not conversation_id:
                conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                session['conversation_id'] = conversation_id
            
            return jsonify({
                'response': formatted_response,
                'raw_response': raw_response,
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat()
            })
            
        except openai.RateLimitError:
            return jsonify({'error': 'API rate limit exceeded. Please try again later.'}), 429
        except openai.APIError as e:
            return jsonify({'error': f'OpenAI API error: {str(e)}'}), 500
        except Exception as e:
            return jsonify({'error': f'Failed to get AI response: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/new-conversation', methods=['POST'])
def new_conversation():
    """
    Start a new conversation by clearing the conversation history.
    
    This endpoint allows users to start fresh conversations by removing
    the conversation history from the session. The next message will start
    a new conversation context.
    
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
    session.pop('conversation_history', None)
    session.pop('conversation_id', None)
    return jsonify({'message': 'New conversation started'})

@app.route('/api/status')
def status():
    """
    Check system status and configuration.
    
    This endpoint provides health check functionality and system status information.
    It validates environment configuration, tests OpenAI API connectivity, and returns
    diagnostic information useful for troubleshooting.
    
    The endpoint performs the following checks:
    1. Environment variable validation
    2. OpenAI API connectivity test
    3. Session state information
    
    Response Format:
        Success (200): {
            "status": "ok",
            "message": "Connected successfully",
            "model": "gpt-4o-mini",
            "conversation_id": "current-conversation-id-or-none",
            "messages_count": number_of_messages_in_history
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
        500: Server Error - OpenAI API connectivity issues
    """
    try:
        is_valid, missing_vars = validate_environment()
        
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': f'Missing environment variables: {", ".join(missing_vars)}'
            }), 400
        
        # Test connection to OpenAI API
        try:
            client = get_openai_client()
            
            # Test API with a simple request
            test_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10
            )
            
            conversation_history = session.get('conversation_history', [])
            
            return jsonify({
                'status': 'ok',
                'message': 'Connected successfully',
                'model': 'gpt-4o-mini',
                'conversation_id': session.get('conversation_id', 'none'),
                'messages_count': len(conversation_history)
            })
            
        except openai.AuthenticationError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid OpenAI API key'
            }), 401
        except openai.RateLimitError:
            return jsonify({
                'status': 'warning',
                'message': 'API rate limit reached but connection is valid'
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Failed to connect to OpenAI API: {str(e)}'
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
    
    The application will start even with missing configuration to show
    the landing page, but the chat functionality requires proper setup.
    """
    print("🚀 Starting AI Car Repair Assistant Web Application")
    print(f"📅 Application started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment but don't exit - let landing page show
    is_valid, missing_vars = validate_environment()
    if not is_valid:
        print(f"⚠️  Missing environment variables: {missing_vars}")
        print("   Landing page will work, but chat requires OpenAI API key")
        print("   Please set OPENAI_API_KEY in your .env file")
    else:
        print("✅ Environment validation passed")
    
    print("🌐 Starting AI Car Repair web server at http://localhost:5001")
    print("📄 Landing page: http://localhost:5001")
    print("💬 Chat interface: http://localhost:5001/chat")
    print("🛑 Press Ctrl+C to stop the server")
    
    # Run with debug mode based on environment
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    if debug_mode:
        print("🐛 Debug mode enabled")
    
    try:
        app.run(debug=debug_mode, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Application failed to start: {str(e)}")
        exit(1)
