import os
import sys
from unittest import mock

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)

sys.modules.setdefault("steamworks", mock.MagicMock())

import decklink_app.main_app as main_app  # noqa: E402


def test_main_setup_ok():
    with (
        mock.patch.object(main_app.gm, "gadget_setup") as setup_fn,
        mock.patch.object(main_app.gm, "function_enable") as enable_fn,
    ):
        assert main_app.main(["setup"]) == 0
        setup_fn.assert_called_once()
        enable_fn.assert_called_once_with("joystick")


def test_main_setup_error():
    with (
        mock.patch.object(
            main_app.gm,
            "gadget_setup",
            side_effect=RuntimeError,
        ),
        mock.patch.object(main_app.gm, "function_enable") as enable_fn,
    ):
        assert main_app.main(["setup"]) == 1
        enable_fn.assert_not_called()


def test_run_dispatches_controller_start():
    with mock.patch.object(main_app._controller, "start") as start_fn:
        assert main_app.main(["run"]) == 0
        start_fn.assert_called_once()


def test_stop_dispatches_controller_stop():
    with mock.patch.object(main_app._controller, "stop") as stop_fn:
        assert main_app.main(["stop"]) == 0
        stop_fn.assert_called_once()


def test_destroy_calls_gadget_destroy():
    with mock.patch.object(main_app.gm, "gadget_destroy") as destroy_fn:
        assert main_app.main(["destroy"]) == 0
        destroy_fn.assert_called_once()


def test_destroy_error():
    with mock.patch.object(
        main_app.gm,
        "gadget_destroy",
        side_effect=RuntimeError,
    ):
        assert main_app.main(["destroy"]) == 1
