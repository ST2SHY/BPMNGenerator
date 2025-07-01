"""
Refine sequence flows based on revision advice using LLM.
"""

import json
import os
from utils.agent import generate_prompt_from_config
from utils.configure import get_workplace
from generation.task import generate_task_with_extra

# Configuration and file path constants
REFINE_SEQ_CONFIG_PATH = "generation/config/refine_seq.json"
SEQ_OUTPUT_FILE = "seq_output.json"
SYMBOL_OUTPUT_FILE = "symbol_output.json"
REVISION_FILE = "revision.txt"
REFINED_SEQ_OUTPUT_FILE = "revised_seq_output.json"


def generate_refined_sequence():
    """
    Read requirement, task data, sequence output, and revision advice, then call LLM to generate refined control_flow and message_flow.
    The result will be saved to workplace/revised_seq_output.json.
    """
    workplace = get_workplace()
    # Read requirement
    req_path = os.path.join(workplace, 'req.txt')
    with open(req_path, 'r', encoding='utf-8') as f:
        requirement = f.read().strip()
    # Generate formattask (same as in seq.py)
    formattask_data = generate_task_with_extra()
    formattask = json.dumps(formattask_data, ensure_ascii=False, indent=2)
    # Read seq_output.json
    seq_path = os.path.join(workplace, SEQ_OUTPUT_FILE)
    with open(seq_path, 'r', encoding='utf-8') as f:
        seq_data = json.load(f)
        flow = json.dumps(seq_data.get('extracted_output',
                          seq_data), ensure_ascii=False)
    # Read revision.txt
    revision_path = os.path.join(workplace, REVISION_FILE)
    with open(revision_path, 'r', encoding='utf-8') as f:
        revision_advice = f.read().strip()
    # Assemble input
    input_vars = {
        "REQUIREMENT": requirement,
        "FORMATTASK": formattask,
        "FLOW": flow,
        "REVISION": revision_advice
    }
    config_path = REFINE_SEQ_CONFIG_PATH
    result = generate_prompt_from_config(config_path, input_vars)
    # Save result
    output_path = os.path.join(workplace, REFINED_SEQ_OUTPUT_FILE)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Refined sequence saved to: {output_path}")
    return result


if __name__ == '__main__':
    generate_refined_sequence()
