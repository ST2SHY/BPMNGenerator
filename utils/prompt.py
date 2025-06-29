"""
OpenAI API integration utilities for prompt handling and LLM communication.

This module provides functions to load secrets, initialize OpenAI client,
and send requests to OpenAI API for text generation.
"""

from pathlib import Path
import yaml
from openai import OpenAI


def load_secrets(filepath):
    """
    Load secrets from YAML file

    Args:
        filepath: Path to secrets file

    Returns:
        Dictionary containing secrets or empty dict if file not found
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            secrets = yaml.safe_load(file)
            return secrets
    except FileNotFoundError:
        print(f"Error:{filepath} not found.")
        return {}


def load_client():
    """
    Load OpenAI client from secrets

    Returns:
        OpenAI client instance or None if error occurs
    """
    try:
        path = Path(__file__).parent
        # Go up one level from utils/ to project root
        secrets = load_secrets(path.parent / ".secret.yml")
        api_key = secrets.get("API_KEY")
        if api_key:
            return OpenAI(
                api_key=api_key,
            )
        else:
            raise KeyError('API_KEY does not exist')
    except (FileNotFoundError, KeyError, yaml.YAMLError) as e:
        print(f'Error:{e}')
        return None


def ask_openai(system, prompt, model='gpt-4o-mini', max_tokens=6000):
    """
    Send request to OpenAI API

    Args:
        system: System message content
        prompt: User message content
        model: Model to use (default: gpt-4o-mini)
        max_tokens: Maximum tokens in response (default: 1000)

    Returns:
        Response content from OpenAI or None if error occurs
    """
    try:
        client = load_client()
        if client:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens
            )
        else:
            raise ImportError('openai is not imported')
        return response.choices[0].message.content
    except (ImportError, KeyError, FileNotFoundError) as e:
        print(f'Error:{e}')
        return None


if __name__ == "__main__":
    # Test ask_openai function
    print("Testing ask_openai function...")

    # Test system and user messages
    system_message = "You are a helpful assistant that provides concise answers."
    user_message = "What is the capital of France?"

    print(f"System message: {system_message}")
    print(f"User message: {user_message}")
    print("-" * 50)

    # Call ask_openai
    response = ask_openai(system_message, user_message)

    if response:
        print("Response received:")
        print(response)
    else:
        print("No response received. Check your API key and configuration.")

    print("-" * 50)
    print("Test completed.")
