import pytest

from app.core import Interval  # adjust import path as needed


def test_interval_initialization():
    interval = Interval(name="Work", time_seconds=3600, color="#FF0000")

    assert interval.get_name() == "Work"
    assert interval.get_color() == "#FF0000"
    assert interval.get_remaining_seconds() == 3600.0


def test_default_color():
    interval = Interval(name="Break", time_seconds=60)

    assert interval.get_color() == "#FFFFFF"


def test_time_seconds_must_be_positive():
    with pytest.raises(ValueError, match="time_seconds must be positive"):
        Interval(name="Invalid", time_seconds=0)

    with pytest.raises(ValueError):
        Interval(name="Invalid", time_seconds=-10)


def test_name_must_be_provided():
    with pytest.raises(ValueError, match="name must be provided"):
        Interval(name=None, time_seconds=60)


def test_reset_restores_initial_time():
    interval = Interval(name="Test", time_seconds=120)
    interval.set_remaining_seconds(30)

    interval.reset()

    assert interval.get_remaining_seconds() == 120.0


def test_set_remaining_seconds():
    interval = Interval(name="Test", time_seconds=100)
    interval.set_remaining_seconds(42.5)

    assert interval.get_remaining_seconds() == 42.5


@pytest.mark.parametrize(
    "remaining_seconds, expected_hms",
    [
        (0, (0, 0, 0)),
        (59, (0, 0, 59)),
        (60, (0, 1, 0)),
        (3661, (1, 1, 1)),
        (7322.9, (2, 2, 2)),  # float truncation
    ],
)
def test_get_remaining_hms(remaining_seconds, expected_hms):
    interval = Interval(name="Test", time_seconds=10000)
    interval.set_remaining_seconds(remaining_seconds)

    assert interval.get_remaining_hms() == expected_hms
