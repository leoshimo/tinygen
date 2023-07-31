from typing import Optional, List
import re
from dataclasses import dataclass
import ast

ACTION_PAT = re.compile('ACTION: (\w*)( (.*))?$')

@dataclass
class Action:
    """
    Data class for actions extracted from message
    """
    name: str
    args: List[str]

def extract_action(msg: dict) -> Optional[Action]:
    match = ACTION_PAT.search(msg['content'])
    if not match:
        return None
    name = match[1].strip()
    args_str = match[3]
    args = ast.literal_eval(args_str) if args_str else []
    if not isinstance(args, list):
        return None
    return Action(name, args)

