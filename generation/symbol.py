# Generate symbol table
from utils.load_requirement import get_reqstring
from utils.regex import extract_symbol
from utils.configure import get_generator_prompt, get_workplace
from utils.prompt import ask_openai
from utils.dump import dump
from string import Template
import json

prompt_format = Template('''
Here is a BPM (Business Process Management) requirement:

$REQUIREMENT

Your task is to analyze the given requirement and perform the following steps:

1. **Identify Actors**:
   - Extract all distinct actors mentioned in the requirement.
   - Assign a unique symbol to each actor (e.g., Actor1: A, Actor2: B, etc.).

2. **Define Activities or Actions**:
   - Identify all distinct activities or actions within the requirement.
   - **If a task description contains multiple actions, split them into separate tasks**. 
   - Pay special attention to phrases that indicate multiple actions, such as:
     - Compound verbs (e.g., "selects a pizza and places an order" → **split into** "selects a pizza" and "places an order").
     - Sequential actions (e.g., "A does X before Y" → **split into** separate tasks for X and Y).
     - Conditions (e.g., "A does X if Y" → **split into** tasks for X and Y).

3. **Assign Unique Symbols**:
   - Assign a unique symbol to each activity or action (e.g., Task1: T1, Task2: T2, etc.), ensuring each task is distinct.

4. **Map Activities to Actors**:
   - For each identified activity or action, specify the actor(s) responsible for performing it.

5. **Output the Results**:

   Present the analysis in the following format:
   ```json
   {  
     "actors": [(actor_name, symbol)],  
     "tasks": [
       (actor_symbol, task_description, task_symbol)
     ]  
   }

Explain the Reasons:

Provide a concise explanation for the identification and mapping of actors and tasks.
Justify why each actor and task was assigned in the way described.
Make sure the symbols are clear and the relationships between actors and tasks are logical. If there are ambiguities, explain your assumptions.
''')

dump_filename = 'symbol_table.json'


def get_formatted_prompt():
    try:
        reqstring = get_reqstring()
        return prompt_format.substitute(REQUIREMENT=reqstring)
    except Exception as e:
        print(f'Error:{e}')


def get_symbol():
    try:
        workplace = get_workplace()
        with open(workplace / 'dump' / dump_filename, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f'Error:{e}')


def update_symbol(data):
    dump(data, dump_filename)


def generate_symbol():
    sys_prompt = get_generator_prompt()
    ret = ask_openai(system=sys_prompt, prompt=get_formatted_prompt())
    print(ret)
    data = extract_symbol(ret)
    update_symbol(data)


if __name__ == '__main__':
    print(get_formatted_prompt())
    # generate_symbol()
