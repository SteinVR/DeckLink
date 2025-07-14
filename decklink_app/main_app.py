"""DeckLink application entrypoint."""

from __future__ import annotations

import argparse
import logging
import signal
import threading
from typing import Optional

from . import gadget_manager as gm
from . import input_translator


_logger = logging.getLogger(__name__)


class AppController:
    """Manage the translation thread and stop event."""

    def __init__(self) -> None:
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None

    def start(self) -> threading.Thread:
        """Start the translator loop in a background thread."""
        if self.thread and self.thread.is_alive():
            return self.thread

        self.thread = threading.Thread(
            target=input_translator.start_translation_loop,
            args=(self.stop_event,),
            daemon=True,
        )
        self.thread.start()
        return self.thread

    def stop(self) -> None:
        """Signal the translator loop to stop and wait for it."""
        if not self.thread:
            return
        self.stop_event.set()
        self.thread.join()
        self.thread = None
        self.stop_event.clear()


_controller = AppController()


def setup() -> int:
    """Initialize the USB gadget."""
    try:
        gm.gadget_setup()
        gm.function_enable("joystick")
    except Exception as exc:  # noqa: BLE001
        _logger.error("Setup failed: %s", exc)
        return 1
    return 0


def run() -> int:
    """Start the translation loop in a background thread."""
    _controller.start()

    def _signal_handler(
        signum: int, frame: Optional[object]
    ) -> None:  # noqa: D401
        _controller.stop()

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)
    return 0


def stop() -> int:
    """Stop the translation loop."""
    _controller.stop()
    return 0


def destroy() -> int:
    """Tear down the USB gadget."""
    try:
        gm.gadget_destroy()
    except Exception as exc:  # noqa: BLE001
        _logger.error("Destroy failed: %s", exc)
        return 1
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="decklink")
    parser.add_argument("action", choices=["setup", "run", "stop", "destroy"])
    args = parser.parse_args(argv)

    if args.action == "setup":
        return setup()
    if args.action == "run":
        return run()
    if args.action == "stop":
        return stop()
    if args.action == "destroy":
        return destroy()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
