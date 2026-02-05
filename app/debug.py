from hashlib import sha256
from time import sleep
from typing import List
from app.core import Interval, Training, Workout
import threading

# Setup training
training = Training(
    "my run",
    max_rounds=2,
    intervals=[Interval("Warmup", 5), Interval("Pushups", 5), Interval("Cool down", 5)],
)

# Create the timer
workout = Workout()

stop_event = threading.Event()


def workout_loop(workout: Workout, training: List[Interval]):
    previous_state = None  # keep track of last displayed state

    for state in workout.run(training):
        if stop_event.is_set():
            break

        current_state = sha256(
            f"{state.interval_name}{state.remaining_seconds}{state.status}".encode(
                "utf-8"
            )
        ).hexdigest()

        if current_state != previous_state:
            print(
                f"Interval: {state.interval_name}, "
                f"Time left: {state.remaining_seconds}s "
                f"({state.remaining_hh:02d}:{state.remaining_mm:02d}:{state.remaining_ss:02d}), "
                f"Round: {state.current_round} of {state.max_rounds}, "
                f"Duration: {state.duration:.3f}, "
                f"Status: {state.status}, "
            )
            previous_state = current_state

        sleep(0.01)


thread = threading.Thread(target=workout_loop, args=(workout, training), daemon=True)

thread.start()

try:
    while thread.is_alive():
        cmd = input("Press input: \n").strip().lower()
        if cmd == "r":
            workout.start()
            continue
        if cmd == "s":
            print("STOPPED....")
            workout.stop()
            # workout.reset()

except KeyboardInterrupt:
    print("Stopping...")
    stop_event.set()
    thread.join()

print("Cleanup done.")
