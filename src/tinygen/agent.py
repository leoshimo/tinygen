from .tool import Tool, describe_tools
import openai
from typing import Optional, Callable, List
from .extract import extract_action, Action
from .debug import print_message
import ast

MAX_TURNS = 10

class CodeAgent:
    """
    Agent that leverages a set of tool to execute a plan for some specific programming task
    """

    def __init__(self, tools: List[Tool], task: str, plan: str, debug=False):
        self.tools = tools
        self.messages = CodeAgent._create_messages(tools, task, plan)
        self.debug = debug

    def run(self):
        """
        Execute agent to completion
        """
        turns = 0

        if self.debug:
            for m in self.messages:
                print_message(m)

        while turns < MAX_TURNS:
            turns += 1

            resp = openai.ChatCompletion.create(model="gpt-4", temperature=0, messages=self.messages)
            assistant_msg = resp.choices[0].message
            self.messages.append({
                'role': 'assistant',
                'content': assistant_msg['content']
            })

            if self.debug:
                print_message(assistant_msg)

            action = extract_action(assistant_msg)
            if not action:
                self.messages.append({ 
                    'role': 'user', 
                    'content': 'The response must contain "ACTION: TOOL ARGS" as where TOOL is one of described tools and ARGS is arguments to pass to tool as a Python List of strings'
                })
                continue

            if action.name == "DONE":
                return

            tool = self._resolve_tool(self.tools, action)
            if not tool:
                self.messages.append({ 
                    'role': 'user', 
                    'content': 'The tool {} does not exist'.format(action.name)
                })
                continue

            result = tool()
            self.messages.append({
                'role': 'user',
                'content': 'RESULT: {}'.format(result)
            })

    def _create_messages(tools: List[Tool], task: str, plan: str) -> List[dict]:
        system_prompt = """You exist in an environment where you can interact with the file system using distinct tools below:
    
{tool_descriptions}

Given a programming task and a step-by-step sequence of actions using the tools described above, the objective is to complete the task.
The arguments passed to a tool should be a Python list of strings.

Each assistant response should be formatted as follows:

OBSERVATION: <Observation about preceding user message in context of accomplishing the programming task>
THOUGHT: <Thought on next step to accomplish programming task, following the step-by-step sequence of the plan.
ACTION: <Specifies one of above tool to use with arguments to pass to tools>

When the task is completed, the ACTION should be "ACTION: DONE"

Examples:

OBSERVATION: The user provided a programming task to "Add Hello World to the bottom of the README file", with the plan to find the file, open the file, then writing to file.
THOUGHT: First, I should find the README file.
ACTION: find ["README"]

RESULT: ['./README.md']

OBSERVATION: There is a file named "./README.md" at path "./README.md"
THOUGHT: Next, I should open the file I found.
ACTION: open ["./README.md"]

RESULT: # README\nThis project is used as an example file

OBSERVATION: The README.md file contains the text above.
THOUGHT: I should append to the file using the write tool using the existing contents and "Hello World" string
ACTION: write ["./README.md", "# README\nThis project is used as an example file\nHello World"]

RESULT: OK

OBSERVATION: The README.md file was updated.
THOUGHT: I have updated the README.md file. The task is complete.
ACTION: DONE
        """.format(tool_descriptions=describe_tools(tools))

        user_msg = """The Task: {task}
{plan}""".format(task=task, plan=plan)

        return [
            { 'role': 'system', 'content': system_prompt },
            { 'role': 'user', 'content': user_msg },
        ]

    def _resolve_tool(self, tools: List[Tool], action: Action) -> Optional[Callable[[], str]]:
        if not action:
            return None
        tool = next((t for t in tools if action.name == t.name), None)
        if not tool:
            return None
        return lambda : tool.call(action.args)
    

