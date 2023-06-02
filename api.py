from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from bot import run_disord_client

app = FastAPI()

is_bot_up: bool = False

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    global is_bot_up
    return templates.TemplateResponse(
        "index.html",
        context={"request": request, "is_bot_up": is_bot_up},
    )


class Payload(BaseModel):
    force: bool = False


@app.post("/start-bot")
def start_bot(background_tasks: BackgroundTasks, payload: Payload):
    global is_bot_up
    if payload.force or not is_bot_up:
        background_tasks.add_task(run_disord_client)
        is_bot_up = True
    return {"is_bot_up": is_bot_up}
