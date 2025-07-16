import logging
import os
import sys


_LOG_FILE = os.environ.get("DECKLINK_LOG_FILE", "/tmp/decklink.log")


def _setup_logging() -> None:
    """Configure root logging to stdout and a file."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(_LOG_FILE),
        ],
    )
    logging.captureWarnings(True)


def _log_uncaught_exception(exc_type, exc, tb) -> None:
    logging.getLogger(__name__).critical(
        "Uncaught exception", exc_info=(exc_type, exc, tb)
    )


_setup_logging()

sys.excepthook = _log_uncaught_exception

