from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import asyncio

from fastapi.staticfiles import StaticFiles


from app.core import Interval, Workout, Training
from app.model import (
    TrainingCreate,
    TrainingResponse,
    UpdateWorkoutRequest,
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

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")



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
    action = request.action.lower()
    timer = app.state.timer

    if action == "start":
        timer.start()
    elif action == "stop":
        timer.stop()
    elif action == "pause":
        timer.pause()
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    return WorkoutResponse(status=timer.status())


@app.get("/workout/events")
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
