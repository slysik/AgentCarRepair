#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "openai",
#     "python-dotenv",
# ]
# ///

import os
import sys
from dotenv import load_dotenv


def prompt_llm(prompt_text, model="gpt-5"):
    """
    GPT-5 LLM prompting method with model selection.

    Args:
        prompt_text (str): The prompt to send to the model
        model (str): OpenAI model to use (default: gpt-5)

    Returns:
        str: The model's response text, or None if error
    """
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        # GPT-5 and O3 models have different parameter requirements
        if model.startswith(("gpt-5", "o3", "o1")):
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt_text}],
                max_completion_tokens=2000,
                # GPT-5 only supports temperature=1 (default)
            )
        else:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt_text}],
                max_tokens=2000,
                temperature=0.7,
            )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error with model {model}: {e}", file=sys.stderr)
        return None


def main():
    """Command line interface for GPT-5 prompting."""
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ./gpt5.py 'your prompt here'")
        print("  ./gpt5.py --model gpt-5-mini 'your prompt'")
        print("  ./gpt5.py --model o3-mini 'your prompt'")
        print("\nAvailable GPT-5 models:")
        print("  - gpt-5 (latest)")
        print("  - gpt-5-mini")
        print("  - gpt-5-nano")
        print("  - o3")
        print("  - o3-mini")
        print("  - o3-pro")
        return
    
    # Check for model flag
    if sys.argv[1] == "--model" and len(sys.argv) >= 4:
        model = sys.argv[2]
        prompt_text = " ".join(sys.argv[3:])
    else:
        model = "gpt-5"
        prompt_text = " ".join(sys.argv[1:])
    
    print(f"Using model: {model}")
    print("-" * 40)
    
    response = prompt_llm(prompt_text, model)
    if response:
        print(response)
    else:
        print(f"Error calling OpenAI API with model {model}")


if __name__ == "__main__":
    main()