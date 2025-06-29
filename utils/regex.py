"""
Regular expression utilities for text processing.

This module provides regex functions for extracting
structured data from text responses.
"""

import re
import json
from typing import Dict, Any, List


def extract_symbol(text: str) -> Dict[str, Any]:
    """
    Extract symbol information from text using regex patterns.

    Args:
        text: Input text to extract symbols from

    Returns:
        Dictionary containing extracted symbols
    """
    result = {}

    # Extract actors pattern
    actors_pattern = r'actors:\s*\[(.*?)\]'
    actors_match = re.search(actors_pattern, text, re.DOTALL)
    if actors_match:
        try:
            actors_str = actors_match.group(1)
            # Parse actors list
            actors = []
            # Simple parsing for (name, symbol) format
            actor_matches = re.findall(r'\(([^,]+),\s*([^)]+)\)', actors_str)
            for name, symbol in actor_matches:
                actors.append((name.strip(), symbol.strip()))
            result['actors'] = actors
        except Exception as e:
            print(f"Error parsing actors: {e}")

    # Extract tasks pattern
    tasks_pattern = r'tasks:\s*\[(.*?)\]'
    tasks_match = re.search(tasks_pattern, text, re.DOTALL)
    if tasks_match:
        try:
            tasks_str = tasks_match.group(1)
            # Parse tasks list
            tasks = []
            # Simple parsing for (actor, description, symbol) format
            task_matches = re.findall(
                r'\(([^,]+),\s*([^,]+),\s*([^)]+)\)', tasks_str)
            for actor, description, symbol in task_matches:
                tasks.append(
                    (actor.strip(), description.strip(), symbol.strip()))
            result['tasks'] = tasks
        except Exception as e:
            print(f"Error parsing tasks: {e}")

    return result
