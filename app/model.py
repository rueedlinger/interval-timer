from typing import List, Optional


from pydantic import BaseModel, Field

from enum import Enum


class WorkoutAction(str, Enum):
    START = "start"
    STOP = "stop"
    PAUSE = "pause"


class WorkoutStatus(str, Enum):
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    STOPPED = "stopped"


class IntervalCreate(BaseModel):
    name: str
    time_seconds: int = Field(gt=0)
    color: str = "FFFFFF"

    model_config = {
        "json_schema_extra": {
            "example": {"name": "Warmup", "time_seconds": 30, "color": "#FF0000"}
        }
    }


class IntervalResponse(BaseModel):
    name: str
    time_seconds: int
    remaining: int
    color: str


class TrainingCreate(BaseModel):
    name: str
    max_rounds: Optional[int] = Field(default=None, ge=1)
    intervals: List[IntervalCreate]

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "My Training",
                "max_rounds": 3,
                "intervals": [
                    {"name": "Warmup", "time_seconds": 30, "color": "#FF0000"},
                    {"name": "Work", "time_seconds": 60, "color": "#00FF00"},
                ],
            }
        }
    }


class TrainingResponse(BaseModel):
    name: str
    max_rounds: Optional[int]
    current_round: int
    intervals: List[IntervalResponse]


class WorkoutResponse(BaseModel):
    status: WorkoutStatus


class UpdateWorkoutRequest(BaseModel):
    action: WorkoutAction


class IntervalEvent(BaseModel):
    interval_name: str
    status: WorkoutStatus
    remaining_seconds: int
    remaining_hh: int
    remaining_mm: int
    remaining_ss: int
    current_round: int
    max_rounds: Optional[int]
    duration: float
    paused: float = 0.0
