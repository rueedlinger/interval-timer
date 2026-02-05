import time
from typing import List, Optional, Tuple
from app.model import IntervalEvent, WorkoutStatus


class Interval:
    def __init__(self, name: str, time_seconds: int, color: str = "#FFFFFF") -> None:
        if time_seconds <= 0:
            raise ValueError("time_seconds must be positive")

        if name is None:
            raise ValueError("name must be provided")

        self._name: str = name
        self._color: str = color
        self._time_seconds: int = time_seconds
        self._remaining_seconds: float = float(time_seconds)

    def get_color(self) -> str:
        return self._color

    def get_name(self) -> str:
        return self._name

    def reset(self) -> None:
        self._remaining_seconds = float(self._time_seconds)

    def set_remaining_seconds(self, remaining_seconds: float) -> None:
        self._remaining_seconds = remaining_seconds

    def get_remaining_hms(self) -> Tuple[int, int, int]:
        hh = int(self._remaining_seconds) // 3600
        mm = (int(self._remaining_seconds) % 3600) // 60
        ss = int(self._remaining_seconds) % 60
        return hh, mm, ss

    def get_remaining_seconds(self) -> float:
        return self._remaining_seconds

    def get_time_seconds(self) -> float:
        return self._time_seconds


class Training:
    def __init__(
        self, name: str, intervals: List[Interval], max_rounds: Optional[int] = None
    ) -> None:
        if name is None:
            raise ValueError("name must be provided")

        if max_rounds is not None and max_rounds < 0:
            raise ValueError("max_rounds must be positive number")

        if intervals is None or len(intervals) == 0:
            raise ValueError("inverall must be provided")

        self._name: str = name
        self._intervals: List[Interval] = []
        self._current_index: int = 0
        self._current_round: int = 0
        self._max_rounds: Optional[int] = max_rounds
        self._intervals = intervals

    def get_name(self) -> str:
        return self._name

    def get_current_round(self) -> int:
        return self._current_round

    def get_max_rounds(self) -> int:
        return self._max_rounds

    def get_current_interval(self) -> Interval:
        return self._intervals[self._current_index]

    def next_interval(self) -> Interval:
        if self._intervals is None or len(self._intervals) == 0:
            raise ValueError("No Intveral given")

        self._current_index = (self._current_index + 1) % len(self._intervals)

        # If we wrapped back to the start, increment the round counter
        if self._current_index == 0:
            self._current_round += 1

        return self._intervals[self._current_index]

    def get_intervals(self):
        for item in self._intervals:
            yield item

    def reset_all(self) -> None:
        for interval in self._intervals:
            interval.reset()
        self._current_index = 0
        self._current_round = 0

    def is_finished(self) -> bool:
        if self._max_rounds is None:
            return False

        if self._current_round >= self._max_rounds:
            return True

        return False


class Workout:
    def __init__(self) -> None:
        self._state: WorkoutStatus = WorkoutStatus.STOPPED

    def stop(self) -> None:
        self._state = WorkoutStatus.STOPPED

    def start(self) -> None:
        self._state = WorkoutStatus.RUNNING

    def pause(self) -> None:
        self._state = WorkoutStatus.PAUSED

    def get_state(self) -> WorkoutStatus:
        return self._state

    def run(self, training: Training):
        # workout loop
        paused_total: float = 0.0
        duration_total: float = 0.0
        while True:
            if self._state == WorkoutStatus.STOPPED:
                training.reset_all()
                yield self._create_event(
                    current_interval=training.get_current_interval(),
                    training=training,
                    duration=paused_total,
                    paused=duration_total,
                    status=self._state,
                )
                continue

            if self._state == WorkoutStatus.COMPLETED:
                yield self._create_event(
                    current_interval=training.get_current_interval(),
                    training=training,
                    duration=duration_total,
                    paused=paused_total,
                    status=self._state,
                )
                continue

            paused_total = 0.0
            duration_total = 0.0
            start_time = time.time()
            training.reset_all()

            interval = training.get_current_interval()

            while not training.is_finished():
                if self._state == WorkoutStatus.STOPPED:
                    break

                interval.reset()
                interval_remaining = interval.get_remaining_seconds()
                last_tick = time.time()

                while interval_remaining > 0:
                    if self._state == WorkoutStatus.STOPPED:
                        break

                    now = time.time()
                    delta = now - last_tick
                    last_tick = now

                    interval_remaining -= delta
                    interval.set_remaining_seconds(interval_remaining)
                    duration_total = time.time() - start_time
                    yield self._create_event(
                        current_interval=interval,
                        training=training,
                        duration=duration_total,
                        paused=paused_total,
                        status=self._state,
                    )

                interval = training.next_interval()
                if training.is_finished():
                    self._state = WorkoutStatus.COMPLETED

            duration_total = time.time() - start_time
            yield self._create_event(
                current_interval=interval,
                training=training,
                duration=duration_total,
                paused=paused_total,
                status=self._state,
            )

    def _create_event(
        self,
        current_interval: Interval,
        training: Training,
        duration: float,
        paused: float,
        status: WorkoutStatus,
    ) -> IntervalEvent:
        hh, mm, ss = current_interval.get_remaining_hms()
        return IntervalEvent(
            interval_name=current_interval.get_name(),
            remaining_seconds=int(current_interval.get_remaining_seconds()),
            remaining_hh=hh,
            remaining_mm=mm,
            remaining_ss=ss,
            current_round=training._current_round,
            max_rounds=training.get_max_rounds(),
            duration=duration,
            paused=paused,
            status=status,
        )
