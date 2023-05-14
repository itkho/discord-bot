from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import RedirectResponse

from bot import run_disord_client

app = FastAPI()

is_bot_up: bool = False


@app.get("/")
def home():
    return {"Bot status": "UP" if is_bot_up else "DOWN"}


@app.get("/start-bot")
def start_bot(background_tasks: BackgroundTasks, force: bool = False):
    global is_bot_up
    if force or not is_bot_up:
        background_tasks.add_task(run_disord_client)
        is_bot_up = True
    return RedirectResponse(url="/")
