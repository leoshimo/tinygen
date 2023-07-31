import os
import re
from typing import List, Optional
from .debug import print_message

import openai

from .tool import Tool, describe_tools

openai.api_key = os.getenv("OPENAI_API_KEY")

CHECK_YES_PAT = re.compile(".*YES.*")
EXTRACT_PLAN_PAT = re.compile("PLAN:.*", re.IGNORECASE | re.DOTALL)


def plan(tools: List[Tool], task: str, debug=False) -> str:
    """
    Given a string task, returns a string that describes the plan
    """

    plan_str = None

    while not plan_str:
        plan_msgs = create_plan_msgs(tools, task)
        resp = openai.ChatCompletion.create(
            model="gpt-4", temperature=0.3, messages=plan_msgs
        )
        resp_plan_msg = resp.choices[0].message

        if debug:
            print_message(resp_plan_msg)

        if check_plan(plan_msgs, resp_plan_msg):
            plan_str = extract_plan(resp_plan_msg)

    return plan_str


def create_plan_msgs(tools: List[Tool], task: str) -> List[dict]:
    """
    Given programming task, returns set of chat completion messages to use LLM for planning
    """
    system_prompt = """You exist in an environment where you can interact with the file system using distinct tools below:
    
{tool_descriptions}


Given a programming goal, imagine three world class programming experts brainstorming a step-by-step plan that uses only the tools above. The arguments passed to a tool should be a Python list of strings.
Each step of the plan should specify the exact tool to use, and the parameters that should be passed to the tool as a list of strings in valid Python syntax.

Each expert shares their thoughts one at a time, considers what has been shared by other experts, then suggests a full step-by-step plan. The brainstorm repeats until the experts agree on step-by-step sequence to accomplish the programming goal. Output the step-by-step plan at the end of the response on a new line prefixed by "PLAN:"
    """.format(
        tool_descriptions=describe_tools(tools)
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "The Programming Task: " + task},
    ]


def check_plan(plan_msgs: List[dict], resp_msg: dict) -> bool:
    """
    Prompts LLM whether it is confident about the plan response RESP_MSG generated from PLAN_MSGS
    """

    msgs = plan_msgs + [
        resp_msg,
        {"role": "user", "content": 'Are you sure? Answer with only "YES" or "NO"'},
    ]
    resp = openai.ChatCompletion.create(model="gpt-4", messages=msgs)
    resp_msg = resp.choices[0].message

    return CHECK_YES_PAT.fullmatch(resp_msg.content) is not None


def extract_plan(resp_msg: dict) -> Optional[str]:
    """
    Given the response for plan, extract just the portion that describes steps of plan without reasoning
    """
    plan_match = EXTRACT_PLAN_PAT.search(resp_msg.content)
    return plan_match[0] if plan_match else None
