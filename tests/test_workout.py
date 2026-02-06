import pytest
import time

from app.core import Interval, Training, Workout
from app.model import WorkoutStatus  # adjust import path as needed


@pytest.fixture
def training():
    return Training(
        name="My Workout",
        intervals=[
            Interval("Roll", 2),
            Interval("Climb", 1),
        ],
        max_rounds=1,
    )


def test_workout_state_change(training):
    workout = Workout()

    workout.run(training=training)
    assert WorkoutStatus.STOPPED == workout.get_state()

    workout.start()
    assert WorkoutStatus.RUNNING == workout.get_state()

    workout.pause()
    assert WorkoutStatus.PAUSED == workout.get_state()

    workout.stop()
    assert WorkoutStatus.STOPPED == workout.get_state()


def test_run_workflow(training):
    workout = Workout()
    workout.start()
    for event in workout.run(training=training):
        # print(event)
        time.sleep(0.01)
        if event.status == WorkoutStatus.COMPLETED:
            assert int(event.duration) == 3
            assert event.current_round == 1
            assert event.max_rounds == 1
            assert event.paused == 0
            break
