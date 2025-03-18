# Generate refined flow based on feedback from analysis.py
from generation.flow import get_flow
from generation.symbol import get_symbol
from generation.task import get_task
from utils.load_requirement import get_reqstring
from utils.regex import extract_flow
from utils.configure import get_generator_prompt, get_workplace
from utils.prompt import ask_openai
from utils.dump import dump
from string import Template
import json

prompt_format = Template('''
Analyze the requirement description to identify potential logical dependencies among tasks, then generate an updated task execution sequence while considering both intra-actor and inter-actor dependencies. The new flow should reflect revisions based on the provided revision advice.

Input Parameters
Requirement Description:
$REQUIREMENT

Symbol Definitions (JSON Format):
$FORMATTASK

Original Flow Description (JSON Format):
$FLOW

Revision Advice:
$REVISION

Apply Revision Advice to Modify the Flow
Apply necessary modifications while maintaining logical consistency.
If tasks need to be added, removed, or reordered, ensure the changes align with the overall logical structure of the process.
Validate that all modifications adhere to the constraints outlined in the requirement description.
Step 2: Construct the Updated Task Execution Flow
Establish cross-actor task dependencies as per the requirement description and revision advice.
Output Format
{
    "flow": [
        ("from_task", "to_task")
    ]
}
A concise explanation justifying:
The revised task execution order.
How each rule in the output constraints is followed.
''')

dump_filename = 'revised_flow.json'

default_rules = [
    '''
    - List every task in Symbol Definitions.
    - Verify that every task defined in Symbol Definitions is included in the sequence.
    - If a task is missing from the requirement description, infer its logical placement.
    ''',
    '''
    - For each actor (e.g., A, B, C, etc.), their designated start node (e.g., A-st, B-st, C-st) must be present in the flow.  
    - The path starting from each actor's start node must connect to all events initiated by that actor. In other words, if actor A performs actions x, y, and z, then A-st, x, y, and z must be connected in the flow.
    ''',
    '''
    - Recognize looping behaviors and ensure they are properly modeled (e.g., Task → Timer Event → Task if repetition is required). 
    - A loop should contain a backward edge. It should ends with its start task.
    - If looping tasks exist, explicitly define the loop with forward and backward connections, ensuring proper termination based on the defined stopping condition.
    '''
]


def get_symbolstring():
    symbol = get_symbol()
    json_str = json.dumps(symbol, separators=(',', ':'))
    json_str = json_str.replace('\n', '').replace('\r', '')

    return json_str


def get_formatted_prompt(revision):
    try:
        reqstring = get_reqstring()
        flowstring = get_flow()
        symbols = get_symbol()
        tasks = get_task()

        task_mapping = {task[0]: task[1] for task in tasks["tasks"]}

        for task in symbols['tasks']:
            task_id = task[2]
            if task_id in task_mapping:
                task.append(task_mapping[task_id])

        symbols['tasks'].extend(
            [[actor[1], f'start node of actor {actor[0]}', f'{actor[1]}-st', 'start node'] for actor in symbols['actors']])

        ftaskstring = json.dumps(symbols, separators=(',', ':'))
        ftaskstring = ftaskstring.replace('\n', '').replace('\r', '')

        return prompt_format.substitute(REQUIREMENT=reqstring, FORMATTASK=ftaskstring,
                                        FLOW=flowstring,
                                        REVISION=revision)
    except Exception as e:
        print(f'Error:{e}')


def generate_flow(revision):
    sys_prompt = get_generator_prompt()
    ret = ask_openai(system=sys_prompt, prompt=get_formatted_prompt(revision))
    print(ret)
    data = extract_flow(ret)
    dump(data, dump_filename)


if __name__ == '__main__':
    # print(get_formatted_prompt(default_rules[1]))
    generate_flow(default_rules[1])
