#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
# ]
# ///

"""
Enhanced SessionStart hook that checks for documentation updates.

This hook extends the existing session start functionality to:
1. Check if ai_docs are older than 7 days
2. Suggest updating documentation if needed
3. Optionally auto-update critical documentation
"""

import json
import sys
import requests
from pathlib import Path
from datetime import datetime, timedelta

def check_doc_freshness() -> dict:
    """Check if documentation files are getting stale."""
    ai_docs_dir = Path("ai_docs")
    if not ai_docs_dir.exists():
        return {"needs_update": False, "reason": "ai_docs directory not found"}
    
    # Check critical documentation files
    critical_docs = [
        "cc_hooks_docs.md",
        "anthropic_docs_subagents.md",
        "anthropic_custom_slash_commands.md",
    ]
    
    oldest_file = None
    oldest_age = timedelta(0)
    
    for doc_file in critical_docs:
        file_path = ai_docs_dir / doc_file
        if file_path.exists():
            file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_age > oldest_age:
                oldest_age = file_age
                oldest_file = doc_file
    
    # Consider stale if older than 7 days
    stale_threshold = timedelta(days=7)
    needs_update = oldest_age > stale_threshold
    
    return {
        "needs_update": needs_update,
        "oldest_file": oldest_file,
        "oldest_age_days": oldest_age.days,
        "threshold_days": stale_threshold.days,
    }

def check_anthropic_docs_updated() -> bool:
    """Check if Anthropic docs have been recently updated (simplified check)."""
    try:
        # This is a simplified check - in practice you might want to:
        # 1. Check Last-Modified headers
        # 2. Compare content hashes
        # 3. Use a more sophisticated change detection
        response = requests.head("https://docs.anthropic.com/en/docs/claude-code/hooks", timeout=10)
        return response.status_code == 200
    except:
        return False

def main():
    """Main hook execution."""
    try:
        # Read the SessionStart hook data
        input_data = json.loads(sys.stdin.read())
        
        # Perform documentation freshness check
        freshness_check = check_doc_freshness()
        
        if freshness_check["needs_update"]:
            print(f"📚 Documentation Update Suggestion")
            print(f"Your ai_docs appear to be {freshness_check['oldest_age_days']} days old.")
            print(f"Consider running: `uv run update_ai_docs.py --all`")
            print(f"Or use the slash command: `/update-docs all`")
            print("")
            
            # Check if we can determine if upstream docs changed
            if check_anthropic_docs_updated():
                print("✓ Anthropic documentation is accessible for updates")
            else:
                print("⚠ Could not verify Anthropic documentation accessibility")
            
            print("---")
        
        # Continue with normal session start processing
        # (You could include the original session_start.py logic here)
        
    except Exception as e:
        # Graceful error handling - don't break Claude Code startup
        print(f"Documentation check failed: {e}", file=sys.stderr)
    
    # Always exit successfully for SessionStart hooks
    sys.exit(0)

if __name__ == "__main__":
    main()