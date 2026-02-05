import pytest

from app.core import Interval
from app.core import Training


@pytest.fixture
def intervals():
    return [
        Interval("Work", 60),
        Interval("Rest", 30),
    ]


def test_training_initialization(intervals):
    training = Training("Morning", intervals, max_rounds=3)

    assert training.get_name() == "Morning"
    assert training.get_current_round() == 0
    assert training.get_max_rounds() == 3
    assert training.get_current_interval() == intervals[0]


def test_name_must_be_provided(intervals):
    with pytest.raises(ValueError, match="name must be provided"):
        Training(None, intervals)


def test_intervals_must_be_provided():
    with pytest.raises(ValueError, match="inverall must be provided"):
        Training("Test", [])

    with pytest.raises(ValueError):
        Training("Test", None)


def test_max_rounds_must_be_positive(intervals):
    with pytest.raises(ValueError, match="max_rounds must be positive number"):
        Training("Test", intervals, max_rounds=-1)


def test_next_interval_moves_forward(intervals):
    training = Training("Test", intervals)

    next_interval = training.next_interval()

    assert next_interval == intervals[1]
    assert training.get_current_interval() == intervals[1]
    assert training.get_current_round() == 0


def test_next_interval_wraps_and_increments_round(intervals):
    training = Training("Test", intervals)

    training.next_interval()  # move to index 1
    training.next_interval()  # wrap back to index 0

    assert training.get_current_interval() == intervals[0]
    assert training.get_current_round() == 1


def test_multiple_rounds_increment_correctly(intervals):
    training = Training("Test", intervals)

    # 2 intervals → 1 round
    training.next_interval()
    training.next_interval()

    # another full cycle
    training.next_interval()
    training.next_interval()

    assert training.get_current_round() == 2


def test_reset_all_resets_intervals_and_state(intervals):
    training = Training("Test", intervals)

    intervals[0].set_remaining_seconds(10)
    intervals[1].set_remaining_seconds(5)

    training.next_interval()
    training.next_interval()  # complete one round

    training.reset_all()

    assert training.get_current_round() == 0
    assert training.get_current_interval() == intervals[0]
    assert intervals[0].get_remaining_seconds() == 60.0
    assert intervals[1].get_remaining_seconds() == 30.0


def test_is_finished_false_when_max_rounds_none(intervals):
    training = Training("Open", intervals)

    for _ in range(10):
        training.next_interval()

    assert training.is_finished() is False


def test_is_finished_when_max_rounds_reached(intervals):
    training = Training("Limited", intervals, max_rounds=2)

    # Each full cycle increments round
    training.next_interval()
    training.next_interval()  # round 1

    assert training.is_finished() is False

    training.next_interval()
    training.next_interval()  # round 2

    assert training.is_finished() is True
