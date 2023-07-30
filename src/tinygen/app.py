from typing import List

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from .plan import plan
from .tool import Tool

app = FastAPI()

def tools() -> List[Tool]:
    find_tool = Tool(
        "find",
        "find PATTERN returns a list of paths that match given PATTERN. PATTERN is a valid regular expression for Python's re.compile.",
        lambda arg: ["app.py", "main.py"],
    )

    search_tool = Tool(
        "search",
        "search QUERY returns a list of paths to files containing that match QUERY. QUERY is a regular string",
        lambda arg: ["app.py", "main.py"],
    )

    open_tool = Tool(
        "open",
        "open PATH returns contents of file at PATH.",
        lambda arg: ["app.py", "main.py"],
    )

    write_tool = Tool(
        "write",
        "write PATH CONTENT write CONTENT to the file at PATH. This overwrites existing content if any.",
        lambda arg: ["app.py", "main.py"],
    )
    return [find_tool, grep_tool, open_tool, write_tool]

@app.get("/", response_class=PlainTextResponse)
def index(prompt: str):
    return plan(tools(), prompt)

# For flyio
@app.get("/healthcheck")
def healthcheck():
     return {"status": "ok"}

