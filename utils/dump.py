"""
Data dump utilities for BPMN generation.

This module provides common functions for reading/writing data files
and managing the dump functionality across different generation modules.
"""

import json
import os
from typing import Dict, Any, Callable, Optional
from utils.configure import get_workplace


# Global dump setting - can be moved to external config file later
ENABLE_DUMP = True


def get_data_from_file_or_generate(output_file: str, generate_func: Callable, description: str) -> Dict[str, Any]:
    """
    Generic function to get data either from file or by generating.

    This function implements the common pattern of checking if dump is enabled,
    reading from file if possible, and falling back to generation if needed.

    Args:
        output_file: Output file name to read from
        generate_func: Function to call for generating new data
        description: Description for logging purposes

    Returns:
        Dictionary containing the data
    """
    if ENABLE_DUMP:
        # Read from existing output file
        workplace = get_workplace()
        file_path = os.path.join(workplace, output_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                extracted_output = data.get('extracted_output', {})
                print(f"Loaded {description} from: {file_path}")
                return extracted_output
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(
                f"Failed to load {description} from file: {e}, generating new {description}...")
            return generate_func()
    else:
        # Generate new data
        return generate_func()


def save_result_with_extra(result: Dict[str, Any], output_file: str, description: str,
                           extra_key: Optional[str] = None, extra_value: Any = None) -> None:
    """
    Save result to file with extra data if dump is enabled.

    Args:
        result: Result dictionary to save
        output_file: Output file name
        description: Description for the save operation
        extra_key: Key for extra data
        extra_value: Value for extra data
    """
    if ENABLE_DUMP:
        workplace = get_workplace()
        output_path = os.path.join(workplace, output_file)

        # Read existing file content if it exists
        existing_data = {}
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # File doesn't exist or is invalid, start with empty dict

        # Merge the new result with existing data
        merged_data = existing_data.copy()
        merged_data.update(result)

        # If extra data is provided, add it to the extra section
        if extra_key and extra_value is not None:
            if 'extra' not in merged_data:
                merged_data['extra'] = {}
            merged_data['extra'][extra_key] = extra_value

        # Write the merged data to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)

        print(f"{description} completed. Results saved to: {output_path}")


def save_result(result: Dict[str, Any], output_file: str, description: str) -> None:
    """
    Save result to file if dump is enabled.

    Args:
        result: Result dictionary to save
        output_file: Output file name
        description: Description for the save operation
    """
    save_result_with_extra(result, output_file, description)


def set_dump_enabled(enabled: bool) -> None:
    """
    Set the global dump enabled state.

    Args:
        enabled: Whether dump functionality should be enabled
    """
    global ENABLE_DUMP
    ENABLE_DUMP = enabled


def is_dump_enabled() -> bool:
    """
    Get the current dump enabled state.

    Returns:
        Whether dump functionality is currently enabled
    """
    return ENABLE_DUMP
