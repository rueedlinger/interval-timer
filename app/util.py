from app.core import Interval, Training
from app.model import IntervalResponse, TrainingCreate, TrainingResponse


def to_training_resp(training: Training) -> TrainingResponse:
    return TrainingResponse(
        name=training.get_name(),
        max_rounds=training.get_max_rounds(),
        current_round=training.get_current_round(),
        intervals=[
            IntervalResponse(
                name=i.get_name(),
                time_seconds=i.get_time_seconds(),
                remaining=i.get_remaining_seconds(),
                color=i.get_color(),
            )
            for i in training.get_intervals()
        ],
    )


def to_model(training: TrainingCreate) -> Training:
    return Training(
        name=training.name,
        max_rounds=training.max_rounds,
        intervals=[
            Interval(name=i.name, time_seconds=i.time_seconds, color=i.color)
            for i in training.intervals
        ],
    )
