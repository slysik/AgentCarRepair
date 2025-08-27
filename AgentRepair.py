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
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict, Any

# Flask web framework imports
from flask import Flask, render_template, request, jsonify, session

# OpenAI imports
import openai
from openai import OpenAI

# Setup logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variable management (optional dependency)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables.")

# PostgreSQL Vector Database imports
try:
    from postgres_vector_db import PostgresVectorDB, SearchFilters, create_postgres_vector_db
    POSTGRES_AVAILABLE = True
    logger.info("PostgreSQL vector database support available")
except ImportError as e:
    POSTGRES_AVAILABLE = False
    logger.warning(f"PostgreSQL vector database not available: {e}")
    logger.warning("Falling back to JSON-based knowledge base")

# Initialize Flask application with static file serving
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this')

# Simple file-based cache for parts search results
PARTS_CACHE_FILE = 'parts_search_cache.json'
CACHE_EXPIRY_HOURS = 1

def load_parts_cache() -> Dict[str, Any]:
    """Load parts search cache from file"""
    try:
        if os.path.exists(PARTS_CACHE_FILE):
            with open(PARTS_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load parts cache: {str(e)}")
    return {}

def save_parts_cache(cache_data: Dict[str, Any]):
    """Save parts search cache to file"""
    try:
        with open(PARTS_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save parts cache: {str(e)}")

def get_cached_parts_search(cache_key: str) -> Optional[Dict[str, Any]]:
    """Get cached parts search result if still valid"""
    cache_data = load_parts_cache()
    
    if cache_key in cache_data:
        cached_item = cache_data[cache_key]
        cache_time = datetime.fromisoformat(cached_item.get('timestamp', ''))
        expiry_time = cache_time + timedelta(hours=CACHE_EXPIRY_HOURS)
        
        if datetime.now() < expiry_time:
            logger.info(f"Using cached parts search for: {cache_key}")
            return cached_item.get('data')
        else:
            # Remove expired cache
            del cache_data[cache_key]
            save_parts_cache(cache_data)
            logger.info(f"Cache expired for: {cache_key}")
    
    return None

def cache_parts_search(cache_key: str, data: Dict[str, Any]):
    """Cache parts search result with timestamp"""
    cache_data = load_parts_cache()
    
    cache_data[cache_key] = {
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    
    # Clean up old cache entries (keep only last 100)
    if len(cache_data) > 100:
        # Sort by timestamp and keep newest 100
        sorted_items = sorted(
            cache_data.items(),
            key=lambda x: x[1].get('timestamp', ''),
            reverse=True
        )
        cache_data = dict(sorted_items[:100])
    
    save_parts_cache(cache_data)
    logger.info(f"Cached parts search for: {cache_key}")

def is_parts_related_query(message: str) -> bool:
    """Detect if user query is asking about finding/buying car parts"""
    parts_keywords = [
        'need a new', 'need to replace', 'where to buy', 'find parts',
        'replacement cost', 'how much for', 'part price', 'buy a',
        'order a', 'purchase', 'find a used', 'used parts',
        'junkyard', 'scrapyard', 'salvage', 'oem parts',
        'aftermarket', 'parts store', 'auto parts', 'where can i buy',
        'cost', 'price of', 'how much does', 'where to find'
    ]
    
    message_lower = message.lower()
    
    # Check for direct parts keywords
    if any(keyword in message_lower for keyword in parts_keywords):
        return True
    
    # Check if message contains specific part names (likely asking about buying/pricing)
    part_patterns = [
        'alternator', 'starter', 'battery', 'headlight', 'taillight', 
        'mirror', 'bumper', 'brake', 'tire', 'wheel', 'engine',
        'transmission', 'radiator', 'compressor', 'converter', 'airbag'
    ]
    
    # If asking about cost/price AND mentions a part, likely parts-related
    if any(cost_word in message_lower for cost_word in ['cost', 'price', 'much', 'buy', 'find']):
        if any(part in message_lower for part in part_patterns):
            return True
    
    return False

def extract_part_name_from_query(message: str) -> Optional[str]:
    """Extract the part name from a user query"""
    message_lower = message.lower()
    
    # Common part names and their patterns
    part_patterns = {
        'alternator': ['alternator'],
        'starter': ['starter', 'starter motor'],
        'battery': ['battery'],
        'headlight': ['headlight', 'head light', 'headlamp'],
        'taillight': ['taillight', 'tail light', 'rear light'],
        'mirror': ['mirror', 'side mirror'],
        'bumper': ['bumper'],
        'hood': ['hood', 'bonnet'],
        'door': ['door'],
        'wheel': ['wheel', 'rim'],
        'tire': ['tire', 'tyre'],
        'brake': ['brake', 'brake pad', 'brake rotor'],
        'engine': ['engine', 'motor'],
        'transmission': ['transmission', 'gearbox'],
        'radiator': ['radiator'],
        'ac compressor': ['ac compressor', 'a/c compressor', 'air conditioning compressor'],
        'catalytic converter': ['catalytic converter', 'cat converter'],
        'airbag': ['airbag', 'air bag'],
        'seat': ['seat'],
        'steering wheel': ['steering wheel']
    }
    
    # Look for part patterns in the message
    for part_name, patterns in part_patterns.items():
        for pattern in patterns:
            if pattern in message_lower:
                return part_name
    
    # If no specific part found, try to extract from common phrases
    if 'new ' in message_lower:
        # Look for "need a new [part]" patterns
        import re
        match = re.search(r'need a new (\w+)', message_lower)
        if match:
            return match.group(1)
    
    return None

def format_message_content(text: str) -> str:
    """
    Enhanced format message content with visual elements, emojis, and styled HTML.
    
    This function processes AI responses and converts them into visually engaging HTML
    with emoji formatting, styled boxes, and enhanced readability. It handles:
    - Converting emoji numbered lists (1️⃣, 2️⃣, 3️⃣)
    - Creating warning and tip boxes
    - Formatting section headers with emojis
    - Converting bullet points to styled lists
    - Adding manual image references
    - Preserving emoji-rich formatting
    
    Args:
        text (str): The raw text message from the AI agent
        
    Returns:
        str: Enhanced HTML-formatted text with visual elements
        
    Example:
        Input: "[WARNING] Hot engine parts [/WARNING]\n1️⃣ Check the oil level"
        Output: "<div class='warning-box'>⚠️ <strong>Warning:</strong> Hot engine parts</div>..."
    """
    if not text:
        return ""
    
    # Clean up the text
    text = text.strip()
    
    # Enhanced formatting with visual elements
    # 1. Format warning boxes
    text = re.sub(
        r'\[WARNING\](.+?)\[/WARNING\]', 
        r'<div class="warning-box">⚠️ <strong>Warning:</strong>\1</div>', 
        text, 
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # 2. Format tip boxes
    text = re.sub(
        r'\[TIP\](.+?)\[/TIP\]', 
        r'<div class="tip-box">💡 <strong>Pro Tip:</strong>\1</div>', 
        text, 
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # 3. Format cost estimates
    text = re.sub(
        r'\[COST\](.+?)\[/COST\]', 
        r'<div class="cost-box">💰 <strong>Cost Estimate:</strong>\1</div>', 
        text, 
        flags=re.DOTALL | re.IGNORECASE
    )
    
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
        
        # Check for emoji numbered steps first (1️⃣, 2️⃣, 3️⃣)
        emoji_step_match = re.match(r'^([1-9]️⃣)\s+(.+)', line)
        if emoji_step_match:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(f'<div class="emoji-step">{emoji_step_match.group(1)} {emoji_step_match.group(2)}</div>')
            continue
        
        # Check for section headers with emojis (🔧 Engine Repair, 📍 Location, etc.)
        header_match = re.match(r'^([🎨🔧⚠️💡📍⏱️🔥💰✅🚗📖📌🎯📚🛠️🔍🔋])\s+(.+)', line)
        if header_match:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(f'<div class="section-header">{header_match.group(1)} {header_match.group(2)}</div>')
            continue
        
        # Check for bullet points (various formats)
        bullet_patterns = [
            r'^▶️\s+(.+)',       # ▶️ bullets (check first)
            r'^[-*•]\s+(.+)',    # - * • bullets
            r'^\d+\.\s+(.+)',    # numbered lists
            r'^[a-zA-Z]\.\s+(.+)',  # lettered lists
            r'^[ivx]+\.\s+(.+)',  # roman numerals
        ]
        
        is_bullet = False
        for pattern in bullet_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                if not in_list:
                    formatted_lines.append('<ul class="emoji-list">')
                    in_list = True
                # Handle ▶️ bullets specially
                if pattern.startswith(r'^\▶️'):
                    content = f'▶️ {match.group(1)}'
                else:
                    # Add ▶️ if not already present for other bullet types
                    content = match.group(1)
                    if not content.startswith('▶️'):
                        content = f'▶️ {content}'
                formatted_lines.append(f'<li>{content}</li>')
                is_bullet = True
                break
        
        if not is_bullet:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            
            # Check for bold headers (text ending with :)
            if line.endswith(':') and len(line) < 100:
                formatted_lines.append(f'<div class="bold-header">{line}</div>')
            # Format as paragraph
            elif line:
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

# Global PostgreSQL vector database instance
_postgres_vector_db = None

def get_postgres_vector_db() -> Optional[PostgresVectorDB]:
    """
    Get or create PostgreSQL vector database instance
    
    Returns:
        PostgresVectorDB instance or None if not available
    """
    global _postgres_vector_db
    
    if not POSTGRES_AVAILABLE:
        return None
    
    if _postgres_vector_db is None:
        try:
            _postgres_vector_db = create_postgres_vector_db()
            logger.info("PostgreSQL vector database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL vector database: {e}")
            return None
    
    return _postgres_vector_db

def load_volvo_knowledge_base() -> Optional[Dict]:
    """
    Load Volvo XC60 knowledge base from JSON file.
    
    Returns:
        Dict: Volvo knowledge base or None if file doesn't exist
    """
    try:
        kb_path = "volvo_xc60_kb.json"
        if os.path.exists(kb_path):
            with open(kb_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Warning: Could not load Volvo knowledge base: {e}")
        return None

def is_volvo_related(message: str) -> bool:
    """
    Check if the user message is related to Volvo vehicles.
    
    Args:
        message (str): User's message
        
    Returns:
        bool: True if message contains Volvo-related keywords
    """
    volvo_keywords = [
        'volvo', 'xc60', 'xc90', 'xc40', 's60', 's90', 'v60', 'v90',
        'sensus', 'pilot assist', 'blis', 'city safety', 'swedish',
        'gothenburg', 'scandinavian'
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in volvo_keywords)

def get_volvo_context(user_message: str, use_postgres: bool = True) -> str:
    """
    Extract relevant Volvo context based on user message.
    
    This function has been upgraded to use PostgreSQL vector database for intelligent
    semantic search when available, falling back to JSON-based search when needed.
    
    Args:
        user_message (str): User's message
        use_postgres (bool): Whether to attempt using PostgreSQL vector database
        
    Returns:
        str: Relevant Volvo context
    """
    # Try PostgreSQL vector database first (if available)
    if use_postgres and POSTGRES_AVAILABLE:
        try:
            vector_db = get_postgres_vector_db()
            if vector_db:
                logger.debug("Using PostgreSQL vector database for Volvo context")
                
                # Create search filters for Volvo XC60
                filters = SearchFilters(
                    vehicle_id='volvo_xc60_2021',
                    min_similarity=0.7,
                    max_results=8
                )
                
                # Get relevant context using semantic search
                context = vector_db.get_relevant_context(
                    query=user_message,
                    max_tokens=3000,
                    filters=filters
                )
                
                if context:
                    return context
                else:
                    logger.info("No relevant context found in PostgreSQL, falling back to JSON")
                    
        except Exception as e:
            logger.error(f"Error accessing PostgreSQL vector database: {e}")
            logger.info("Falling back to JSON-based context")
    
    # Fallback to original JSON-based approach
    logger.debug("Using JSON-based Volvo context (fallback)")
    volvo_kb = load_volvo_knowledge_base()
    
    if not volvo_kb:
        return ""
        
    context_parts = []
    message_lower = user_message.lower()
    
    # Add vehicle information
    vehicle_info = volvo_kb.get('vehicle', {})
    context_parts.append(f"VEHICLE: {vehicle_info.get('year')} {vehicle_info.get('make')} {vehicle_info.get('model')}")
    
    # Add relevant specifications
    specs = volvo_kb.get('specifications', {}).get('quick_reference', {})
    context_parts.append("KEY SPECIFICATIONS:")
    for key, value in specs.items():
        context_parts.append(f"- {key.replace('_', ' ').title()}: {value}")
    
    # Add maintenance info if maintenance-related keywords
    maintenance_keywords = ['oil', 'service', 'maintenance', 'filter', 'brake', 'tire', 'pressure']
    if any(keyword in message_lower for keyword in maintenance_keywords):
        maintenance = volvo_kb.get('maintenance_schedule', [])
        if maintenance:
            context_parts.append("\nMAINTENANCE SCHEDULE:")
            for item in maintenance[:5]:  # Limit to first 5 items
                context_parts.append(f"- {item.get('item', '').title()}: {item.get('interval', 'Check manual')}")
    
    # Add diagnostic tips if problem-related keywords
    problem_keywords = ['problem', 'issue', 'error', 'warning', 'light', 'fault', 'not working']
    if any(keyword in message_lower for keyword in problem_keywords):
        tips = volvo_kb.get('diagnostic_tips', [])
        if tips:
            context_parts.append("\nVOLVO DIAGNOSTIC TIPS:")
            for tip in tips[:4]:  # Limit to first 4 tips
                context_parts.append(f"- {tip}")
    
    # Add common issues if relevant
    common_issues = volvo_kb.get('common_issues', [])
    if common_issues:
        context_parts.append("\nCOMMON VOLVO XC60 ISSUES:")
        for issue in common_issues[:3]:  # Limit to first 3 issues
            context_parts.append(f"- {issue}")
    
    return "\n".join(context_parts)

def create_car_repair_prompt(user_message: str, conversation_history: List[Dict[str, str]] = None, parts_data: List[Dict] = None) -> List[Dict[str, str]]:
    """
    Create a prompt for the OpenAI API with car repair context, including Volvo-specific information and parts data.
    
    This function creates a conversation prompt that includes system instructions
    for car repair assistance and the user's message history. If the message is
    Volvo-related, it includes specific Volvo XC60 knowledge from the manual.
    If parts_data is provided, it includes available parts information.
    
    Args:
        user_message (str): The user's current message
        conversation_history (List[Dict[str, str]]): Previous conversation messages
        parts_data (List[Dict]): Optional used parts data from car-part.com
    
    Returns:
        List[Dict[str, str]]: Formatted messages for OpenAI API
    """
    # Base system prompt with visual formatting instructions
    base_system_content = """You are an expert automotive mechanic and car repair assistant. Your role is to help users diagnose car problems, provide repair guidance, and offer automotive advice with engaging visual formatting.

VISUAL FORMATTING REQUIREMENTS:
🎨 Use emojis for visual appeal and clarity:
   • 🔧 Tools and equipment
   • ⚠️ Warnings and cautions 
   • 💡 Pro tips and insights
   • 📍 Part locations and positions
   • ⏱️ Time estimates
   • 🔥 Temperature warnings
   • 💰 Cost estimates
   • ✅ Completion checkmarks
   • 🚗 Vehicle-specific info
   • 📖 Reference materials

📝 Format instructions with numbered emojis: 1️⃣, 2️⃣, 3️⃣ instead of plain numbers
📌 Use section headers with relevant emojis
🎯 Create visually distinct warning and tip boxes using [WARNING] and [TIP] tags
📚 Always include direct manual link: [View Complete XC60 Manual](https://www.volvocars.com/us/support/manuals)

FORBIDDEN PHRASES - NEVER say:
❌ "Check the owner's manual"
❌ "Refer to your vehicle's owner's manual" 
❌ "Consult your manual"
❌ "See your owner's manual"

Instead, provide the specific information directly and include the manual link for additional details.

Guidelines:
- Always prioritize safety first with clear ⚠️ warnings
- Provide step-by-step instructions with emoji numbering
- Explain technical terms in simple language
- Suggest when professional help is needed
- Ask clarifying questions to better diagnose issues
- Provide cost estimates with 💰 emoji
- Cover all car makes and models
- Include both DIY solutions and professional repair options
- Make responses visually engaging and easy to scan

When responding:
1️⃣ Acknowledge the user's problem with appropriate emoji
2️⃣ Ask clarifying questions if needed
3️⃣ Provide possible diagnoses
4️⃣ Suggest troubleshooting steps with clear formatting
5️⃣ Recommend next actions (DIY or professional)
6️⃣ Include safety warnings with ⚠️ symbols
7️⃣ Add manual reference link for comprehensive information"""

    # Check if message is Volvo-related and add specific context
    if is_volvo_related(user_message):
        volvo_context = get_volvo_context(user_message)
        if volvo_context:
            base_system_content += f"""

VEHICLE-SPECIFIC INFORMATION AVAILABLE:
{volvo_context}

Use this information to provide accurate, model-specific guidance for this Volvo XC60. 
Reference the owner's manual information when relevant and emphasize Volvo-specific 
procedures, specifications, and known issues."""

    # TODO(human): Restart Flask app to activate visual enhancements and /api/manual-link endpoint
    # Add parts availability information if provided
    if parts_data and len(parts_data) > 0:
        base_system_content += f"""

USED PARTS AVAILABLE:
I found {len(parts_data)} used parts available for your 2021 Volvo XC60:

"""
        for i, part in enumerate(parts_data[:5]):  # Limit to top 5 results
            price = part.get('price', 'Price unavailable')
            condition = part.get('condition', 'Condition unknown')
            mileage = part.get('mileage', 'Mileage unknown')
            distance = part.get('distance', 'Location unknown')
            seller = part.get('seller_name', 'Seller info unavailable')
            
            base_system_content += f"{i+1}. {price} ({condition}) - {mileage} - {distance}\n   Seller: {seller}\n"
            
        base_system_content += """
When discussing parts replacement, mention these available used parts with their prices and locations. 
Emphasize cost savings compared to new parts while noting the importance of part condition and seller reputation.
Provide both DIY installation guidance and professional installation recommendations."""
    
    system_message = {
        "role": "system",
        "content": base_system_content
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
        
        # Check if user is asking about parts and auto-search if so
        parts_data = None
        if is_parts_related_query(user_message) and is_volvo_related(user_message):
            logger.info(f"Detected parts query for Volvo: {user_message}")
            
            # Extract part name from query
            part_name = extract_part_name_from_query(user_message)
            if part_name:
                try:
                    # Import and search for parts
                    from car_part_scraper import search_parts_sync
                    parts_data = search_parts_sync(part_name)
                    logger.info(f"Found {len(parts_data)} parts for {part_name}")
                except Exception as e:
                    logger.warning(f"Parts search failed: {str(e)}")
        
        # Create prompt with conversation context and parts data if available
        messages = create_car_repair_prompt(user_message, conversation_history[-10:], parts_data)
        
        try:
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Using GPT-4o-mini for cost efficiency
                messages=messages,
                max_tokens=1500,  # Increased for parts data
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

@app.route('/api/search-parts', methods=['POST'])
def search_parts():
    """
    Search for used auto parts for 2021 Volvo XC60 using car-part.com
    
    This endpoint integrates with car-part.com to find affordable used parts
    for the Volvo XC60. It provides real-time pricing and availability data
    to complement the manual-based repair guidance.
    
    Request Format:
        POST /api/search-parts
        Content-Type: application/json
        {
            "part_name": "alternator",
            "zip_code": "90210" (optional)
        }
        
    Response Format:
        Success (200): {
            "success": true,
            "part_name": "alternator",
            "results_count": 5,
            "parts": [
                {
                    "part_name": "Alternator",
                    "price": "$125",
                    "condition": "Used",
                    "mileage": "85k miles",
                    "location": "Los Angeles, CA",
                    "distance": "15 miles away",
                    "seller_name": "ABC Auto Recyclers",
                    "seller_phone": "(555) 123-4567",
                    "part_id": "part_12345",
                    "description": "OEM Volvo alternator in good condition"
                }
            ],
            "search_time": "2.3s",
            "cached": false
        }
        
        Error (400/500): {
            "success": false,
            "error": "Error message"
        }
    
    Returns:
        Response: JSON with parts data or error message
        
    HTTP Status Codes:
        200: Success - parts found
        400: Bad Request - invalid input
        500: Server Error - search failed
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body must be JSON'
            }), 400
            
        part_name = data.get('part_name')
        if part_name is None:
            part_name = ''
        elif isinstance(part_name, str):
            part_name = part_name.strip()
        else:
            part_name = str(part_name).strip()
            
        if not part_name:
            return jsonify({
                'success': False,
                'error': 'part_name is required'
            }), 400
            
        zip_code = data.get('zip_code') or ''
        if isinstance(zip_code, str):
            zip_code = zip_code.strip() or None
        else:
            zip_code = str(zip_code).strip() if zip_code is not None else None
        
        # Import the scraper (lazy import to avoid startup issues)
        try:
            from car_part_scraper import search_parts_sync
        except ImportError as e:
            return jsonify({
                'success': False,
                'error': 'Parts search service unavailable. Please ensure Playwright is installed.'
            }), 500
        
        # Check cache first
        cache_key = f"parts_{part_name}_{zip_code or 'any'}".lower().replace(' ', '_')
        cached_result = get_cached_parts_search(cache_key)
        
        if cached_result:
            cached_result['cached'] = True
            return jsonify(cached_result), 200
        
        # Perform search
        start_time = time.time()
        
        try:
            parts_data = search_parts_sync(part_name, zip_code)
            search_time = round(time.time() - start_time, 1)
            
            # Format response
            response = {
                'success': True,
                'part_name': part_name,
                'results_count': len(parts_data),
                'parts': parts_data,
                'search_time': f"{search_time}s",
                'cached': False,
                'zip_code': zip_code
            }
            
            # Cache the result for 1 hour
            cache_parts_search(cache_key, response)
            
            return jsonify(response), 200
            
        except Exception as scraper_error:
            logger.error(f"Parts scraper error: {str(scraper_error)}")
            return jsonify({
                'success': False,
                'error': f'Failed to search parts: {str(scraper_error)}'
            }), 500
            
    except Exception as e:
        logger.error(f"Parts search endpoint error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/manual-link')
def get_manual_link():
    """
    Provide direct links to Volvo XC60 manual resources
    
    Returns:
        Response: JSON with manual links and references
        
    HTTP Status Codes:
        200: Success - manual links provided
    """
    try:
        manual_info = {
            'success': True,
            'manual_links': {
                'online_manual': 'https://www.volvocars.com/us/support/manuals',
                'volvo_support': 'https://www.volvocars.com/us/support',
                'xc60_specific': 'https://www.volvocars.com/us/cars/xc60',
                'maintenance_guide': 'https://www.volvocars.com/us/support/maintenance'
            },
            'quick_references': {
                'oil_capacity': '6.1 quarts (5.8 liters) with filter',
                'tire_pressure': 'Front: 36 PSI, Rear: 35 PSI',
                'fuel_capacity': '18.8 gallons (71 liters)',
                'engine_type': 'T5 2.0L 4-cylinder turbo'
            },
            'emergency_contacts': {
                'volvo_roadside': '1-800-63-VOLVO',
                'volvo_customer_care': '1-800-458-1552'
            }
        }
        
        return jsonify(manual_info), 200
        
    except Exception as e:
        logger.error(f"Manual link endpoint error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve manual information: {str(e)}'
        }), 500

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
            
            # Check PostgreSQL vector database status
            postgres_status = {
                'available': POSTGRES_AVAILABLE,
                'connected': False,
                'stats': None,
                'error': None
            }
            
            if POSTGRES_AVAILABLE:
                try:
                    vector_db = get_postgres_vector_db()
                    if vector_db:
                        postgres_status['connected'] = True
                        postgres_status['stats'] = vector_db.get_database_stats()
                except Exception as e:
                    postgres_status['error'] = str(e)
            
            return jsonify({
                'status': 'ok',
                'message': 'Connected successfully',
                'model': 'gpt-4o-mini',
                'conversation_id': session.get('conversation_id', 'none'),
                'messages_count': len(conversation_history),
                'database': postgres_status
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
