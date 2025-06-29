"""
Result combination utilities.

This module provides functions to combine and merge different types of results
with intelligent deduplication capabilities.
"""

from typing import Any, Dict, List


def combine_results(result1: Any, result2: Any) -> Any:
    """
    Recursively combine two results based on their types.

    Args:
        result1: First result to combine
        result2: Second result to combine

    Returns:
        Combined result
    """
    # If both are strings, concatenate them
    if isinstance(result1, str) and isinstance(result2, str):
        return result1 + "\n" + result2

    # If both are lists, concatenate them with deduplication
    elif isinstance(result1, list) and isinstance(result2, list):
        combined = result1.copy()

        for item2 in result2:
            # Check if this item already exists in combined list
            is_duplicate = False

            for existing_item in combined:
                if _is_duplicate_item(existing_item, item2):
                    is_duplicate = True
                    break

            # Only add if not a duplicate
            if not is_duplicate:
                combined.append(item2)

        return combined

    # If both are dictionaries, merge them recursively
    elif isinstance(result1, dict) and isinstance(result2, dict):
        combined = result1.copy()
        for key, value in result2.items():
            if key in combined:
                # Recursively combine if both have the same key
                combined[key] = combine_results(combined[key], value)
            else:
                # Add new key
                combined[key] = value
        return combined

    # If types don't match, return the second result
    else:
        return result2


def _is_duplicate_item(item1: Any, item2: Any) -> bool:
    """
    Check if two items are duplicates based on symbol fields.

    Args:
        item1: First item to compare
        item2: Second item to compare

    Returns:
        True if items are duplicates, False otherwise
    """
    # If both are dictionaries, check symbol fields
    if isinstance(item1, dict) and isinstance(item2, dict):
        # Get all symbol-related fields
        symbol_fields = []
        for key in item1.keys():
            if 'symbol' in key.lower():
                symbol_fields.append(key)

        # If no symbol fields found, compare all fields
        if not symbol_fields:
            return item1 == item2

        # Check if all symbol fields match
        for field in symbol_fields:
            if field in item1 and field in item2:
                if item1[field] != item2[field]:
                    return False
            elif field in item1 or field in item2:
                # One has the field, the other doesn't
                return False

        # All symbol fields match
        return True

    # If both are lists, compare elements
    elif isinstance(item1, list) and isinstance(item2, list):
        if len(item1) != len(item2):
            return False
        return all(_is_duplicate_item(elem1, elem2) for elem1, elem2 in zip(item1, item2))

    # For other types, use direct comparison
    else:
        return item1 == item2


def merge_results(*results: Any) -> Any:
    """
    Merge multiple results together using combine_results.

    Args:
        *results: Variable number of results to merge

    Returns:
        Merged result
    """
    if not results:
        return None

    if len(results) == 1:
        return results[0]

    # Start with the first result and combine with each subsequent result
    merged = results[0]
    for result in results[1:]:
        merged = combine_results(merged, result)

    return merged
