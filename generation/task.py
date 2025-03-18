# Generate Task
from generation.symbol import get_symbol, update_symbol
from utils.load_requirement import get_reqstring
from utils.regex import extract_tasktype
from utils.configure import get_generator_prompt, get_workplace
from utils.prompt import ask_openai
from utils.dump import dump
from string import Template
import json

prompt_format = Template('''
Translate the tasks based on the provided requirements and symbols.

Input:
Requirement:
$REQUIREMENT

Symbol Table:
$SYMBOL

Classify each task into one of the following types:
- 'action': A task that involves an activity actively performed by an actor.
- 'message receiver': A task that waits to receive a message from another actor.
- 'timer': A task that involves waiting for a time-based event before execution.

### Translation Rules:
1. Preserve all action tasks as they are.
2. For tasks that is not 'message receiver' and involve receiving messages, create an additional message receiver task with `-r1` appended to its symbol.
3. For tasks that is not 'timer' but involve time-based triggers, create a separate timer task with `-t1` appended to its symbol.
4. If a task can only happen after receiving a certain event, explicitly create a message receiver task.

Output Format:
The output should follow this structure:
{
  "tasks": [
    (symbol, type)
  ]
}
Note: Do not add double quotes around symbol or type. The output should contain the symbols and types directly without quotes.

Explanation:
For each task:

Explain why it was classified as a 'receiver', 'timer', or 'action' task.
Justify the use of the symbol for each task and clarify why a suffix like -r1 (for message-receiver) or -t1 (for timer) was added during translation.
''')

dump_filename = 'task.json'


def get_symbolstring():
    symbol = get_symbol()
    json_str = json.dumps(symbol, separators=(',', ':'))
    json_str = json_str.replace('\n', '').replace('\r', '')

    return json_str


def get_formatted_prompt():
    try:
        reqstring = get_reqstring()
        symstring = get_symbolstring()
        return prompt_format.substitute(REQUIREMENT=reqstring, SYMBOL=symstring)
    except Exception as e:
        print(f'Error:{e}')


def get_task():
    try:
        workplace = get_workplace()
        with open(workplace / 'dump' / dump_filename, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f'Error:{e}')


def update_symbollist(data):
    symbol_list = get_symbol()
    task_list = symbol_list.get('tasks')
    for sym, type in data.get('tasks'):
        if '-' in sym and not any(s == sym for _, _, s in task_list):
            pre, _ = sym.split('-')
            for actor, _, symbol in task_list:
                if symbol == pre:
                    task_list.append(
                        (actor, f'{symbol} related {type} event', sym))
                    break
    update_symbol(symbol_list)


def generate_task():
    sys_prompt = get_generator_prompt()
    ret = ask_openai(system=sys_prompt, prompt=get_formatted_prompt())
    print(ret)
    data = extract_tasktype(ret)
    # data = get_task()
    update_symbollist(data)
    dump(data, dump_filename)


if __name__ == '__main__':
    generate_task()
