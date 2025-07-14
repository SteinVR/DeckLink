import threading
import time


# AICODE-NOTE: Stub translation loop to be replaced in later tasks


def start_translation_loop(stop_event: threading.Event | None) -> None:
    """Run a placeholder translation loop.

    Parameters
    ----------
    stop_event : threading.Event | None
        Event used to signal when the loop should exit. If ``None`` the loop
        runs indefinitely until interrupted.
    """
    if stop_event is None:
        stop_event = threading.Event()

    while not stop_event.is_set():
        time.sleep(0.1)
