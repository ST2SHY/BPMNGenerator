"""
Load requirement from file.

This module provides functions to load business requirements
from text files for BPMN generation.
"""

import os
from utils.configure import get_workplace


def get_reqstring():
    """
    Load requirement string from req.txt file.

    Returns:
        String containing the business requirement
    """
    workplace = get_workplace()
    req_path = os.path.join(workplace, "req.txt")

    try:
        with open(req_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Warning: Requirement file not found at {req_path}")
        return "Default requirement: User submits order, system processes it."
    except Exception as e:
        print(f"Error reading requirement file: {e}")
        return "Error loading requirement."
