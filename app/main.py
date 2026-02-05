from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import asyncio

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from app.core import Interval, Workout, Training
from app.model import (
    TrainingCreate,
    TrainingResponse,
    UpdateWorkoutRequest,
    WorkoutAction,
    WorkoutResponse,
)
from app.util import to_model, to_training_resp


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    training = Training(
        name="My Workout",
        intervals=[
            Interval("Roll", 300),
            Interval("Climb", 60),
        ],
        max_rounds=10,
    )
    app.state.training = training

    # Create a single shared Workout timer
    app.state.timer = Workout()

    yield
    # shutdown (cleanup if needed)


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.post("/training", response_model=TrainingResponse)
async def create_training(payload: TrainingCreate):
    training = to_model(payload)
    app.state.training = training
    return to_training_resp(training)


@app.get("/training", response_model=TrainingResponse)
async def get_training():
    return to_training_resp(app.state.training)


@app.post("/timer", response_model=WorkoutResponse)
async def update_timer(request: UpdateWorkoutRequest):
    try:
        # Convert string to enum (case-insensitive)
        action = WorkoutAction[request.action.upper()]
        timer = app.state.timer

        if action == WorkoutAction.START:
            timer.start()
        elif action == WorkoutAction.STOP:
            timer.stop()
        elif action == WorkoutAction.PAUSE:
            timer.pause()
        else:
            raise HTTPException(status_code=400, detail="Invalid action")

    except KeyError:
        # This will trigger if the string doesn't match any enum member
        raise HTTPException(status_code=400, detail="Invalid action")

    return WorkoutResponse(status=timer.get_state())


@app.get("/workout")
async def interval_events():
    """
    SSE endpoint streaming interval timer updates.
    """
    # Example training setup

    training = app.state.training

    async def event_generator():
        for event in app.state.timer.run(training=training):
            # SSE format
            yield f"data: {event.model_dump_json()}\n\n"
            await asyncio.sleep(0.1)  # control update frequency

    return StreamingResponse(event_generator(), media_type="text/event-stream")
