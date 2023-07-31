import os

from typing import List

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from .plan import plan
from .tool import Tool
from .github import GithubRepo
from .agent import CodeAgent
from .workspace import Workspace, tools

app = FastAPI()

@app.post("/", response_class=PlainTextResponse)
def index(repoUrl: str, prompt: str):
    gh = GithubRepo(repoUrl, os.getenv('GITHUB_API_KEY'))
    workspace = Workspace(gh)
    workspace_tools = tools(workspace)
    agent_plan = plan(workspace_tools, prompt, debug=True)
    agent = CodeAgent(workspace_tools, prompt, agent_plan, debug=True)
    agent.run()
    return workspace.diff()

# For Fly.io
@app.get("/healthcheck")
def healthcheck():
     return {"status": "ok"}

