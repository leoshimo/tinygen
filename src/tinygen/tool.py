from dataclasses import dataclass
from typing import Callable, List


@dataclass
class Tool:
    name: str
    usage: str
    call: Callable[[str], str]


def describe_tools(tools: List[Tool]):
    return "\n\n".join(map(lambda t: t.usage, tools))
