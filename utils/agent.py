"""
Prompt template generation and LLM interaction utilities.

This module provides functions to load JSON configurations, generate prompts,
call LLM APIs, and extract structured output from responses.
"""

import json
import re
import os
from typing import Dict, List, Any

from utils.configure import get_generator_prompt
from utils.prompt import ask_openai


def load_config(file_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file

    Args:
        file_path: Configuration file path

    Returns:
        Configuration dictionary
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Configuration file not found: {file_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Configuration file format error: {file_path}") from exc


def inject_variables(prompt_template: str, variables: Dict[str, Any]) -> str:
    """
    Inject variables into prompt template

    Args:
        prompt_template: Original prompt template
        variables: Variable dictionary

    Returns:
        Prompt with injected variables
    """
    injected_prompt = prompt_template

    # Replace variable placeholders
    for var_name, var_value in variables.items():
        placeholder = f"${var_name}"
        if isinstance(var_value, str):
            injected_prompt = injected_prompt.replace(placeholder, var_value)
        else:
            # If it's a complex object, convert to JSON string
            injected_prompt = injected_prompt.replace(
                placeholder, json.dumps(var_value, ensure_ascii=False, indent=2))

    return injected_prompt


def clean_json_string(json_str: str) -> str:
    """
    Clean JSON string by removing comments and extra whitespace.

    Args:
        json_str: JSON string that may contain comments

    Returns:
        Cleaned JSON string without comments
    """
    # Remove single-line comments (// ...)
    lines = json_str.split('\n')
    cleaned_lines = []

    for line in lines:
        # Find the position of // comment
        comment_pos = line.find('//')
        if comment_pos != -1:
            # Keep only the part before the comment
            line = line[:comment_pos].rstrip()
        cleaned_lines.append(line)

    # Join lines back together
    cleaned_json = '\n'.join(cleaned_lines)

    # Remove multi-line comments (/* ... */)
    cleaned_json = re.sub(r'/\*.*?\*/', '', cleaned_json, flags=re.DOTALL)

    return cleaned_json


def extract_output_variables(response: str, output_vars: List[str]) -> Dict[str, Any]:
    """
    Extract specified output variables from LLM response

    Args:
        response: LLM response text
        output_vars: List of output variables to extract

    Returns:
        Dictionary of extracted variables
    """
    extracted_result = {}

    for var_name in output_vars:
        # Escape special characters in variable name
        escaped_var_name = re.escape(var_name)

        # First, try to extract JSON content from the response
        json_content = None
        try:
            # Try to find JSON object in the response
            json_start = response.find('{')
            json_end = response.rfind('}')
            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_content = response[json_start:json_end + 1]
                # Clean the JSON content to remove comments
                cleaned_json = clean_json_string(json_content)
                full_json = json.loads(cleaned_json)
                if var_name in full_json:
                    extracted_result[var_name] = full_json[var_name]
                    continue
        except (json.JSONDecodeError, TypeError, ValueError):
            pass  # Not a valid JSON object, continue with regex patterns

        # Try multiple patterns to match output variables (case insensitive)
        patterns = [
            # JSON array format with quotes
            rf'"{escaped_var_name}":\s*(\[.*?\])',
            # JSON object format with quotes
            rf'"{escaped_var_name}":\s*(\{{.*?\}})',
            rf'"{escaped_var_name}":\s*"([^"]*)"',  # String format with quotes
            # Other formats with quotes
            rf'"{escaped_var_name}":\s*([^,\n\r]+)',
            rf'{escaped_var_name}:\s*(\[.*?\])',  # No quotes array format
            rf'{escaped_var_name}:\s*(\{{.*?\}})',  # No quotes object format
            rf'{escaped_var_name}:\s*"([^"]*)"',  # No quotes string format
            rf'{escaped_var_name}:\s*([^,\n\r]+)',  # No quotes other format
            # Pattern for when variable appears in markdown format like "**Variable:**"
            # Markdown list format
            rf'\*\*{escaped_var_name}:\*\*\s*\n((?:- \[.*?\]\n?)+)',
            # Markdown section format
            rf'\*\*{escaped_var_name}:\*\*\s*\n(.*?)(?=\n\*\*|\n\n|\Z)',
            # Pattern for when variable appears in markdown format like "**Variable:**" with different list format
            # Markdown list format without brackets
            rf'\*\*{escaped_var_name}:\*\*\s*\n((?:- .*?\n?)+)',
        ]

        for pattern in patterns:
            try:
                match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
                if match:
                    if '**' in pattern:
                        # Handle markdown format
                        if r'((?:- \[.*?\]\n?)+)' in pattern:
                            # List format: extract all list items
                            list_text = match.group(1)
                            list_matches = re.findall(
                                r'- \[(.*?)\]', list_text)
                            if list_matches:
                                extracted_result[var_name] = [
                                    item.strip() for item in list_matches]
                                break
                        elif r'((?:- .*?\n?)+)' in pattern:
                            # List format without brackets: extract all list items
                            list_text = match.group(1)
                            list_matches = re.findall(
                                r'- (.*?)(?:\n|$)', list_text)
                            if list_matches:
                                extracted_result[var_name] = [
                                    item.strip() for item in list_matches]
                                break
                        else:
                            # Section format: extract the content
                            content = match.group(1).strip()
                            if content:
                                extracted_result[var_name] = content
                                break
                    else:
                        try:
                            # Clean the matched content to remove comments
                            matched_content = match.group(1).strip()
                            cleaned_content = clean_json_string(
                                matched_content)

                            # Try to parse as JSON
                            value = json.loads(cleaned_content)
                            extracted_result[var_name] = value
                            break
                        except json.JSONDecodeError:
                            # If not JSON, use string value directly
                            extracted_result[var_name] = matched_content
                            break
            except re.error as e:
                # If regex has error, skip this pattern
                print(f"Regex error {pattern}: {e}")
                continue

    return extracted_result


def generate_prompt_from_config(config_file_path: str, input_variables: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate prompt from configuration file and execute

    Args:
        config_file_path: Configuration file path
        input_variables: Input variable dictionary

    Returns:
        Dictionary containing output results
    """
    # 1. Load configuration file
    config = load_config(config_file_path)

    # 2. Validate required configuration fields
    required_fields = ['name', 'variables', 'prompt', 'output']
    for field in required_fields:
        if field not in config:
            raise ValueError(
                f"Configuration file missing required field: {field}")

    # 3. Validate input variables
    config_variables = config['variables']
    missing_vars = [
        var for var in config_variables if var not in input_variables]
    if missing_vars:
        raise ValueError(f"Missing required input variables: {missing_vars}")

    # 4. Build complete prompt
    prompt_template = config['prompt']

    # Add format requirements to prompt
    if 'format' in config:
        format_info = config['format']
        format_str = "\n\nOutput format requirements:\n"
        for key, value in format_info.items():
            if isinstance(value, str):
                format_str += f"- {key}: {value}\n"
            elif isinstance(value, list):
                format_str += f"- {key}: {', '.join(value)}\n"
            elif isinstance(value, dict):
                format_str += f"- {key}:\n"
                for sub_key, sub_value in value.items():
                    format_str += f"  - {sub_key}: {sub_value}\n"

        prompt_template += format_str

    # 5. Inject variables
    full_prompt = inject_variables(prompt_template, input_variables)

    # 6. Add task description and input variable template
    task_description = f"Task: {config['name']}\n\n"

    # Add input variable template
    input_template = "Input variables:\n"
    for var_name in config_variables:
        if var_name in input_variables:
            var_value = input_variables[var_name]
            if isinstance(var_value, str):
                input_template += f"{var_name}: {var_value}\n"
            else:
                input_template += f"{var_name}: {json.dumps(var_value, ensure_ascii=False, indent=2)}\n"
    input_template += "\n"

    full_prompt = task_description + input_template + full_prompt

    # 7. Call LLM
    response = ask_openai(system=get_generator_prompt(), prompt=full_prompt)

    # Check if response is None
    if response is None:
        raise ValueError("Failed to get response from LLM")

    # 8. Extract output variables
    output_vars = config['output']
    extracted_results = extract_output_variables(response, output_vars)

    # 9. Return results
    final_result = {
        'config_name': config['name'],
        'input_variables': input_variables,
        'full_prompt': full_prompt,
        'llm_response': response,
        'extracted_output': extracted_results
    }

    return final_result


def process_config_directory(config_dir: str, input_variables: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process all JSON files in configuration directory

    Args:
        config_dir: Configuration directory path
        input_variables: Input variable dictionary

    Returns:
        Processing results for all configurations
    """
    results = {}

    for filename in os.listdir(config_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(config_dir, filename)
            config_name = filename.replace('.json', '')

            try:
                config_result = generate_prompt_from_config(
                    file_path, input_variables)
                results[config_name] = config_result
            except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
                results[config_name] = {
                    'error': str(e),
                    'config_path': file_path
                }

    return results


# Usage example
if __name__ == "__main__":
    # Example: Process single configuration file
    config_path = "generation/config/symbol.json"
    input_vars = {
        "REQUIREMENT": "After user submits order, system verifies inventory, if sufficient then confirms order, otherwise notifies user of insufficient inventory."
    }

    try:
        result = generate_prompt_from_config(config_path, input_vars)
        print("Processing result:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"Processing failed: {e}")

    # Example: Process entire configuration directory
    # config_dir = "generation/config"
    # results = process_config_directory(config_dir, input_vars)
    # print("Directory processing result:")
    # print(json.dumps(results, ensure_ascii=False, indent=2))
