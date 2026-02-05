from typing import Annotated, List, Optional


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

# Constrained string for hex colors
HexColor = Annotated[str, Field(pattern=r"^#?[0-9A-Fa-f]{6}$")]


class IntervalCreate(BaseModel):
    name: str
    time_seconds: int = Field(gt=0)
    color: HexColor = "#FFFFFF"

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "example": {"name": "Warmup", "time_seconds": 30, "color": "#FF0000"}
        },
    }



class IntervalResponse(BaseModel):
    name: str
    time_seconds: int
    remaining: int
    color: str

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "example": {"name": "Warmup", "time_seconds": 30, "remaining": 10, "color": "#FF0000"}
        },
    }


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

    model_config = {"extra": "forbid"}



class WorkoutResponse(BaseModel):
    status: WorkoutStatus

    model_config = {"extra": "forbid"}

class UpdateWorkoutRequest(BaseModel):
    action: WorkoutAction

    model_config = {"extra": "forbid"}


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

    model_config = {"extra": "forbid"}
