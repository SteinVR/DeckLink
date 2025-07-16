import importlib
import os
import sys


def test_log_file_created(tmp_path, monkeypatch):
    log_path = tmp_path / "decklink.log"
    monkeypatch.setenv("DECKLINK_LOG_FILE", str(log_path))
    if "decklink_app" in sys.modules:
        del sys.modules["decklink_app"]
    import decklink_app  # noqa: F401
    importlib.reload(decklink_app)
    assert log_path.exists()


