from typing import Union

from fastapi import BackgroundTasks, FastAPI

from bot import run_disord_client

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/start-bot")
def read_root(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_disord_client)
    return {"bot": "UP"}
