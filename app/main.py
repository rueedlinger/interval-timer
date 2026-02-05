from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio


from app.core import Interval, Workout, Training
from app.model import TrainingCreate, TrainingResponse


app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    training = Training(
        name="My Workout",
        intervals=[
            Interval("Warmup", 5),
            Interval("Exercise", 10),
            Interval("Rest", 3),
        ],
        max_rounds=2,
    )
    app.state.training = training
    yield
    # shutdown (cleanup if needed)


@app.post("/training", response_model=TrainingResponse)
async def create_training(payload: TrainingCreate):
    training = Training(name=payload.name, max_rounds=payload.max_rounds)
    app.state.training = training
    return TrainingResponse(
        name=training.get_name(),
        max_rounds=training.get_max_rounds(),
        current_round=training.get_current_round(),
        intervals=[],
    )


@app.get("/workout/events")
async def interval_events():
    """
    SSE endpoint streaming interval timer updates.
    """
    # Example training setup

    training = app.state.training
    timer = Workout()

    async def event_generator():
        for event in timer.run(training=training):
            # SSE format
            yield f"data: {event.model_dump_json()}\n\n"
            await asyncio.sleep(0.5)  # control update frequency

    return StreamingResponse(event_generator(), media_type="text/event-stream")
