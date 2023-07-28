from fastapi import FastAPI

from tinygen.hello import hello_world

app = FastAPI()


@app.get("/")
async def index():
    return {"message": hello_world()}
