#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def log_status_line(input_data, status_line_output, error_message=None):
    """Log status line event to logs directory."""
    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "status_line.json"

    # Read existing log data or initialize empty list
    if log_file.exists():
        with open(log_file, "r") as f:
            try:
                log_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                log_data = []
    else:
        log_data = []

    # Create log entry with input data and generated output
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "version": "v85",
        "input_data": input_data,
        "status_line_output": status_line_output,
    }

    if error_message:
        log_entry["error"] = error_message

    # Append the log entry
    log_data.append(log_entry)

    # Write back to file with formatting
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)


def get_session_data(session_id):
    """Get session data including agent name, prompts, and extras."""
    session_file = Path(f".claude/data/sessions/{session_id}.json")

    if not session_file.exists():
        return None, f"Session file {session_file} does not exist"

    try:
        with open(session_file, "r") as f:
            session_data = json.load(f)
            return session_data, None
    except Exception as e:
        return None, f"Error reading session file: {str(e)}"


def truncate_prompt(prompt, max_length=60):
    """Truncate prompt to specified length to save space for new components."""
    # Remove newlines and excessive whitespace
    prompt = " ".join(prompt.split())

    if len(prompt) > max_length:
        return prompt[: max_length - 3] + "..."
    return prompt


def get_prompt_icon(prompt):
    """Get icon based on prompt type."""
    if prompt.startswith("/"):
        return "⚡"
    elif "?" in prompt:
        return "❓"
    elif any(
        word in prompt.lower()
        for word in ["create", "write", "add", "implement", "build"]
    ):
        return "💡"
    elif any(word in prompt.lower() for word in ["fix", "debug", "error", "issue"]):
        return "🐛"
    elif any(word in prompt.lower() for word in ["refactor", "improve", "optimize"]):
        return "♻️"
    else:
        return "💬"


def format_cost(cost_data):
    """Format cost information compactly."""
    if not cost_data:
        return None
    
    total_cost = cost_data.get("total_cost_usd", 0)
    duration_ms = cost_data.get("total_duration_ms", 0)
    
    # Format cost: show in cents if under $1, otherwise show dollars
    if total_cost < 1.0:
        cost_str = f"{total_cost * 100:.1f}¢"
    else:
        cost_str = f"${total_cost:.2f}"
    
    # Format duration in seconds
    duration_s = duration_ms / 1000
    if duration_s < 60:
        duration_str = f"{duration_s:.1f}s"
    else:
        duration_str = f"{duration_s / 60:.1f}m"
    
    return f"{cost_str}/{duration_str}"


def get_context_size_info(input_data):
    """Attempt to extract context size information from available data."""
    # Try to get token information from transcript if available
    transcript_path = input_data.get("transcript_path")
    if transcript_path and Path(transcript_path).exists():
        try:
            # Read last few lines of transcript to look for token usage
            with open(transcript_path, 'r') as f:
                lines = f.readlines()
                # Check last 5 lines for token information
                for line in reversed(lines[-5:]):
                    try:
                        entry = json.loads(line.strip())
                        if 'usage' in entry:
                            usage = entry['usage']
                            input_tokens = usage.get('input_tokens', 0)
                            output_tokens = usage.get('output_tokens', 0)
                            total_tokens = input_tokens + output_tokens
                            if total_tokens > 0:
                                return f"{total_tokens//1000}k"
                    except:
                        continue
        except:
            pass
    
    # Fallback to version info
    version = input_data.get("version", "unknown")
    return f"v{version.replace('1.0.', '')}" if version.startswith("1.0.") else version


def format_extras(extras):
    """Format extras dictionary into a compact string."""
    if not extras:
        return None
    
    # Format each key-value pair
    pairs = []
    for key, value in extras.items():
        # Truncate value if too long
        str_value = str(value)
        if len(str_value) > 15:  # Reduced from 20 to save space
            str_value = str_value[:12] + "..."
        pairs.append(f"{key}:{str_value}")
    
    return " ".join(pairs)


def generate_status_line(input_data):
    """Generate the enhanced status line with cost and context info."""
    # Extract session ID from input data
    session_id = input_data.get("session_id", "unknown")

    # Get model name
    model_info = input_data.get("model", {})
    model_name = model_info.get("display_name", "Claude")

    # Get session data
    session_data, error = get_session_data(session_id)

    if error:
        # Log the error but show a default message with cost if available
        cost_info = format_cost(input_data.get("cost"))
        cost_part = f" | \033[33m💰 {cost_info}\033[0m" if cost_info else ""
        status_line = f"\033[36m[{model_name}]\033[0m \033[90m💭 No session data\033[0m{cost_part}"
        log_status_line(input_data, status_line, error)
        return status_line

    # Extract agent name, prompts, and extras
    agent_name = session_data.get("agent_name", "Agent")
    prompts = session_data.get("prompts", [])
    extras = session_data.get("extras", {})

    # Build status line components
    parts = []

    # Agent name - Bright Red
    parts.append(f"\033[91m[{agent_name}]\033[0m")

    # Model name - Blue
    parts.append(f"\033[34m[{model_name}]\033[0m")

    # Most recent prompt - shortened to make room for new components
    if prompts:
        current_prompt = prompts[-1]
        icon = get_prompt_icon(current_prompt)
        truncated = truncate_prompt(current_prompt, 50)  # Reduced from 100
        parts.append(f"{icon} \033[97m{truncated}\033[0m")
    else:
        parts.append("\033[90m💭 No prompts\033[0m")

    # Cost information - Yellow/Gold
    cost_info = format_cost(input_data.get("cost"))
    if cost_info:
        parts.append(f"\033[33m💰 {cost_info}\033[0m")

    # Context/Version information - Magenta
    context_info = get_context_size_info(input_data)
    if context_info:
        parts.append(f"\033[35m📊 {context_info}\033[0m")

    # Add extras if they exist - reduced priority, shown last
    if extras:
        extras_str = format_extras(extras)
        if extras_str:
            # Display extras in dim cyan with brackets
            parts.append(f"\033[36m[{extras_str}]\033[0m")

    # Join with separator
    status_line = " | ".join(parts)

    return status_line


def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())

        # Generate status line
        status_line = generate_status_line(input_data)

        # Log the status line event (without error since it's successful)
        log_status_line(input_data, status_line)

        # Output the status line (first line of stdout becomes the status line)
        print(status_line)

        # Success
        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully - output basic status
        print("\033[31m[Agent] [Claude] 💭 JSON Error\033[0m")
        sys.exit(0)
    except Exception as e:
        # Handle any other errors gracefully - output basic status
        print(f"\033[31m[Agent] [Claude] 💭 Error: {str(e)}\033[0m")
        sys.exit(0)


if __name__ == "__main__":
    main()