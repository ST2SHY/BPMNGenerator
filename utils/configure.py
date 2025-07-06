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


def get_nested_key(section, key):
    """
    Get a specific key from a nested section in configuration.

    Args:
        section: Section name (e.g., 'GENERATION', 'VERIFICATION', 'OUTPUT_FILES')
        key: Configuration key to retrieve

    Returns:
        Value of the key or None if not found
    """
    try:
        config = load_configure()
        section_data = config.get(section, {})
        key_name = section_data.get(key)
        if key_name:
            return key_name
        else:
            raise KeyError(f'{section}.{key} does not exist')
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


def get_generation_config_path(config_name):
    """
    Get generation module configuration path.

    Args:
        config_name: Configuration name (e.g., 'SYMBOL_CONFIG_PATH', 'TASK_CONFIG_PATH')

    Returns:
        Configuration path or default path if not found
    """
    path = get_nested_key("GENERATION", config_name)
    if path is None:
        print(f"{config_name} not found in configure.yml, using default path")
        # Default paths mapping
        default_paths = {
            "SYMBOL_CONFIG_PATH": "generation/config/symbol.json",
            "TASK_CONFIG_PATH": "generation/config/task.json",
            "SEQ_CONFIG_PATH": "generation/config/seq.json",
            "GATE_CONFIG_PATH": "generation/config/gate.json",
            "REFINE_SEQ_CONFIG_PATH": "generation/config/refine_seq.json"
        }
        return default_paths.get(config_name, "generation/config/default.json")
    return path


def get_verification_config_path(config_name):
    """
    Get verification module configuration path.

    Args:
        config_name: Configuration name (e.g., 'CTL_CONFIG_PATH', 'DEFAULT_PETRI_NET_FILE', 'UNIFICATION_CONFIG_PATH')

    Returns:
        Configuration path or default path if not found
    """
    path = get_nested_key("VERIFICATION", config_name)
    if path is None:
        print(f"{config_name} not found in configure.yml, using default path")
        # Default paths mapping
        default_paths = {
            "CTL_CONFIG_PATH": "verification/config/ctl.json",
            "DEFAULT_PETRI_NET_FILE": "bpmn_output_petri_net.pnml",
            "UNIFICATION_CONFIG_PATH": "benchmark/config/unification.json"
        }
        return default_paths.get(config_name, "verification/config/default.json")
    return path


def get_output_file_name(file_name):
    """
    Get output file name from configuration.

    Args:
        file_name: File name key (e.g., 'SYMBOL_OUTPUT_FILE', 'TASK_OUTPUT_FILE', 'STANDARD_CTL_CONSTRAINTS_FILE', 'UNIFICATION_OUTPUT_FILE', 'BENCHMARK_SYMBOL_OUTPUT_FILE', 'TARGET_SYMBOL_OUTPUT_FILE')

    Returns:
        Output file name or default name if not found
    """
    name = get_nested_key("OUTPUT_FILES", file_name)
    if name is None:
        print(f"{file_name} not found in configure.yml, using default name")
        # Default file names mapping
        default_files = {
            "SYMBOL_OUTPUT_FILE": "symbol_output.json",
            "TASK_OUTPUT_FILE": "task_output.json",
            "SEQ_OUTPUT_FILE": "seq_output.json",
            "GATE_OUTPUT_FILE": "gate_output.json",
            "REFINED_SEQ_OUTPUT_FILE": "revised_seq_output.json",
            "CTL_OUTPUT_FILE": "ctl_output.json",
            "REVISION_FILE": "revision.txt",
            "STANDARD_CTL_CONSTRAINTS_FILE": "standard_ctl_constraints.json",
            "UNIFICATION_OUTPUT_FILE": "unification_output.json",
            "BENCHMARK_SYMBOL_OUTPUT_FILE": "benchmark_symbol_output.json",
            "TARGET_SYMBOL_OUTPUT_FILE": "target_symbol_output.json"
        }
        return default_files.get(file_name, "default_output.json")
    return name


def get_petri_net_config(config_name):
    """
    Get Petri net configuration value.

    Args:
        config_name: Configuration name (e.g., 'DEFAULT_OUTPUT_FILE', 'PNML_NAMESPACE')

    Returns:
        Configuration value or default value if not found
    """
    value = get_nested_key("PETRI_NET", config_name)
    if value is None:
        print(f"{config_name} not found in configure.yml, using default value")
        # Default values mapping
        default_values = {
            "DEFAULT_OUTPUT_FILE": "bpmn_output_petri_net.pnml",
            "PNML_NAMESPACE": "http://www.pnml.org/version-2009/grammar/pnmlcoremodel",
            "NET_ID": "bpmn_converted_net",
            "PAGE_ID": "page1",
            "NET_TYPE": "http://www.pnml.org/version-2009/grammar/pnmlcoremodel",
            "BPMN_INPUT_FILES": ["bpmn_output.bpmn", "workflow.bpmn", "process.bpmn", "model.bpmn"]
        }
        return default_values.get(config_name, "default_value")
    return value


def get_naming_convention(convention_name):
    """
    Get naming convention value.

    Args:
        convention_name: Convention name (e.g., 'TRANSITION_PREFIX', 'PLACE_PREFIX')

    Returns:
        Convention value or default value if not found
    """
    value = get_nested_key("NAMING_CONVENTIONS", convention_name)
    if value is None:
        print(f"{convention_name} not found in configure.yml, using default value")
        # Default naming conventions mapping
        default_conventions = {
            "TRANSITION_PREFIX": "t_",
            "PLACE_PREFIX": "p_",
            "PRE_PLACE_PREFIX": "p_pre_",
            "POST_PLACE_PREFIX": "p_post_",
            "START_PLACE_PREFIX": "p_start_",
            "END_PLACE_PREFIX": "p_end_",
            "MESSAGE_PLACE_PREFIX": "p_msg_",
            "ARC_PREFIX": "arc_"
        }
        return default_conventions.get(convention_name, "default_")
    return value
