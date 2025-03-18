# Generate Flow
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
Analyze the requirement description to identify potential logical dependencies among tasks, then generate the direct sequence of task execution while considering both intra-actor and inter-actor dependencies.  
Input:
1. Requirement Description:  
   $REQUIREMENT

2. Symbol Definitions (JSON Format):  
   $FORMATTASK

#### Step-by-Step Instructions  

1. Analyze `REQUIREMENT Description` to extract task dependencies.  
   - Identify any implicit or explicit execution order constraints, including repeating (looping) behaviors.
   - If a task repeats until a condition is met, ensure the loop is modeled explicitly (e.g., Task → Timer Event → Task).
   - Consider both actor-specific sequences and cross-actor dependencies (e.g., if one actor's task depends on another actor's task).
   - Ensure that each actor’s tasks are fully connected, meaning that if an actor performs multiple tasks, they must be linked in sequence.
   - Ensure that each actor's start node (e.g., A-st, B-st) is included and connects to its first assigned task.
   - Every task defined in Symbol Definitions must be included in the execution order. If a task is not explicitly mentioned in Requirement Description, infer its logical placement based on its role and dependencies.

2. Construct the task execution order based on logical dependencies.  
   - Each actor has a unique start node (A-st, B-st, etc.), which links to its first assigned task.
   - Maintain correct intra-actor task sequences and ensure that all tasks assigned to an actor form a connected execution path, including cycles for repeated tasks.
   - If a task repeats based on a condition (e.g., a timer event triggering repeated actions), explicitly define the loop with both forward and backward connections.
   - Ensure loops terminate properly based on the stopping condition defined in the requirement.
   - stablish inter-actor task connections when required by Requirement Description.
   - Ensure that every task from Symbol Definitions appears in the execution sequence (no task is omitted).  

3. Generate the output in the following format:  
{
    "flow": [
        [<actor_symbol>, [("from_task", "to_task")]]
    ],
    "message_flow(inter-actor)": [
        ["from_actor", "to_actor", "from_task", "to_task"]
    ]
}
Output constraints:
   - Each actor's tasks must form a fully connected subgraph.
   - The logical execution order is maintained, including cross-actor dependencies.
   - Each actor starts from its designated start node (A-st, B-st).
   - No task in Symbol Definitions is omitted.
Provide a concise explanation for the generated sequence, justifying intra-actor and inter-actor dependencies.
And how every rule in output constraints is obeyed.
''')

dump_filename = 'flow.json'


def get_symbolstring():
    symbol = get_symbol()
    json_str = json.dumps(symbol, separators=(',', ':'))
    json_str = json_str.replace('\n', '').replace('\r', '')

    return json_str


def get_formatted_prompt():
    try:
        reqstring = get_reqstring()
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

        return prompt_format.substitute(REQUIREMENT=reqstring, FORMATTASK=ftaskstring)
    except Exception as e:
        print(f'Error:{e}')


def get_flow():
    try:
        workplace = get_workplace()
        with open(workplace / 'dump' / dump_filename, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f'Error:{e}')


def generate_flow():
    sys_prompt = get_generator_prompt()
    ret = ask_openai(system=sys_prompt, prompt=get_formatted_prompt())
    print(ret)
    data = extract_flow(ret)
    dump(data, dump_filename)


if __name__ == '__main__':
    # print(get_formatted_prompt())
    generate_flow()
