"""
Configuration management utilities.

This module provides functions to load and access configuration settings
from YAML files, including workplace directory paths and generator prompts.
"""

from pathlib import Path
import yaml


def load_configure():
    """
    Load configuration from configure.yml file.

    Returns:
        Dictionary containing configuration or empty dict if file not found
    """
    # Get the project root directory (one level up from utils/)
    project_root = Path(__file__).parent.parent
    config_path = project_root / "configure.yml"
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config: dict = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        print(f"Error:{config_path} not found.")
        return {}


def get_key(key):
    """
    Get a specific key from configuration.

    Args:
        key: Configuration key to retrieve

    Returns:
        Value of the key or None if not found
    """
    try:
        config = load_configure()
        key_name = config.get(key)
        if key_name:
            return key_name
        else:
            raise KeyError(f'{key} does not exist')
    except (FileNotFoundError, KeyError, yaml.YAMLError) as e:
        print(f'Error:{e}')


def get_workplace():
    """
    Get workplace directory path from configuration.

    Returns:
        Path to workplace directory
    """
    # Get the project root directory (one level up from utils/)
    project_root = Path(__file__).parent.parent
    workplace = get_key("WORKPLACE")
    if workplace is None:
        print("WORKPLACE not found in configure.yml, using default 'workplace'")
        workplace = "workplace"
    workplace_path = project_root / workplace
    return workplace_path


def get_generator_prompt():
    """
    Get generator prompt from configuration.

    Returns:
        Generator prompt string or default prompt if not found
    """
    ret = get_key("GENERATOR_PROMPT")
    if ret is None:
        print("GENERATOR_PROMPT not found in configure.yml, using default prompt")
        ret = "You are an expert in Business Process Management (BPM) and process analysis."
    return ret
