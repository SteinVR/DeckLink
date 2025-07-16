import os
import sys
from unittest import mock

import threading
import signal

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
        mock.patch.object(main_app.gm, "validate_hid_device") as validate_fn,
    ):
        assert main_app.main(["setup"]) == 0
        setup_fn.assert_called_once()
        enable_fn.assert_called_once_with("joystick")
        validate_fn.assert_called_once()


def test_main_setup_error():
    with (
        mock.patch.object(
            main_app.gm,
            "gadget_setup",
            side_effect=RuntimeError,
        ),
        mock.patch.object(main_app.gm, "function_enable") as enable_fn,
        mock.patch.object(main_app.gm, "validate_hid_device") as validate_fn,
    ):
        assert main_app.main(["setup"]) == 1
        enable_fn.assert_not_called()
        validate_fn.assert_not_called()


def test_main_setup_hid_validation_error():
    with (
        mock.patch.object(main_app.gm, "gadget_setup"),
        mock.patch.object(main_app.gm, "function_enable"),
        mock.patch.object(
            main_app.gm,
            "validate_hid_device",
            side_effect=FileNotFoundError,
        ),
    ):
        assert main_app.main(["setup"]) == 1


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


def test_app_controller_start_stop():
    controller = main_app.AppController()
    with mock.patch.object(
        main_app.input_translator,
        "start_translation_loop",
    ):
        t = controller.start()
        assert t.is_alive()
        controller.stop()
        assert controller.thread is None


def test_app_controller_restart_running_thread():
    controller = main_app.AppController()
    with mock.patch.object(
        main_app.input_translator,
        "start_translation_loop",
    ):
        t1 = controller.start()
        t2 = controller.start()
        assert t1 is t2
        controller.stop()


def test_app_controller_stop_no_thread():
    controller = main_app.AppController()
    controller.stop()
    assert controller.thread is None


def test_run_registers_signal_handlers():
    stop_event = threading.Event()
    controller = main_app.AppController()
    controller.stop_event = stop_event
    th = threading.Thread(target=lambda: None)
    controller.thread = th
    with (
        mock.patch.object(main_app, "_controller", controller),
        mock.patch.object(main_app.input_translator, "start_translation_loop"),
        mock.patch("signal.signal") as sig_fn,
    ):
        main_app.main(["run"])
    sig_fn.assert_any_call(signal.SIGINT, mock.ANY)
    sig_fn.assert_any_call(signal.SIGTERM, mock.ANY)


def test_main_invalid_action():
    assert main_app.main(["foo"]) == 1
