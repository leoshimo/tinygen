from typing import List

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from .plan import plan
from .tool import Tool

app = FastAPI()

@app.get("/", response_class=PlainTextResponse)
def index(prompt: str):
    return plan(tools(), prompt)

# For flyio
@app.get("/healthcheck")
def healthcheck():
     return {"status": "ok"}

