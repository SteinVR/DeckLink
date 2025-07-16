import os
import sys
import threading
from types import SimpleNamespace
from unittest import mock

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)

sys.modules["steamworks"] = mock.MagicMock()
sys.modules["usb_gadget"] = mock.MagicMock()

import decklink_app.input_translator as it  # noqa: E402


class DummyAnalog(SimpleNamespace):
    pass


class DummyDigital(SimpleNamespace):
    pass


def test_translation_loop_one_iteration():
    stop_event = threading.Event()

    steam = mock.MagicMock()
    steam.Input = mock.MagicMock()
    steam.Input.GetConnectedControllers.return_value = [1]
    steam.Input.GetActionSetHandle.return_value = "aset"
    steam.Input.GetAnalogActionHandle.side_effect = lambda name: f"a_{name}"
    steam.Input.GetDigitalActionHandle.side_effect = lambda name: f"d_{name}"

    analog_returns = {
        "a_JoyLeft": DummyAnalog(x=1, y=-2),
        "a_JoyRight": DummyAnalog(x=3, y=-4),
        "a_TrigLeft": DummyAnalog(x=5, y=0),
        "a_TrigRight": DummyAnalog(x=6, y=0),
    }
    # fmt: off
    steam.Input.GetAnalogActionData.side_effect = (
        lambda c, h: analog_returns[h]
    )
    # fmt: on

    digital_returns = {
        f"d_{name}": DummyDigital(bState=i % 2)
        for i, name in enumerate(it.DIGITAL_ACTIONS)
    }
    # fmt: off
    steam.Input.GetDigitalActionData.side_effect = (
        lambda c, h: digital_returns[h]
    )
    # fmt: on

    hid_fn = mock.MagicMock(device="/dev/hidg0")

    with (
        mock.patch.object(it, "STEAMWORKS", return_value=steam),
        mock.patch.object(
            it.usb_gadget,
            "HIDFunction",
            return_value=hid_fn,
        ) as hid_cls,
        mock.patch.object(it.usb_gadget, "JoystickGadget") as js_cls,
    ):
        js_instance = js_cls.return_value

        def sleep_patch(_):
            stop_event.set()

        with mock.patch.object(it.time, "sleep", side_effect=sleep_patch):
            it.start_translation_loop(stop_event)

    hid_cls.assert_called_once_with(it.gm.gadget, "joystick")
    js_cls.assert_called_once_with(hid_fn.device, 2, 2, 24)
    js_instance.set_joystick.assert_any_call(0, 1, 2)
    js_instance.set_joystick.assert_any_call(1, 3, 4)
    # fmt: off
    js_instance.set_trigger.assert_has_calls(
        [mock.call(0, 5), mock.call(1, 6)]
    )
    # fmt: on
    assert js_instance.set_button.call_count == len(it.DIGITAL_ACTIONS)
    js_instance.update.assert_called_once()


def test_missing_action_set_exits():
    stop_event = threading.Event()
    steam = mock.MagicMock()
    steam.Input = mock.MagicMock()
    steam.Input.GetConnectedControllers.return_value = []
    steam.Input.GetActionSetHandle.return_value = 0

    with (
        mock.patch.object(it, "STEAMWORKS", return_value=steam),
        mock.patch.object(it.usb_gadget, "HIDFunction"),
        mock.patch.object(it.usb_gadget, "JoystickGadget"),
    ):
        it.start_translation_loop(stop_event)
    steam.Input.GetActionSetHandle.assert_called_once_with(it.ACTION_SET_NAME)


def test_retry_initialization_and_shutdown(monkeypatch):
    stop_event = threading.Event()
    steam_good = mock.MagicMock()
    steam_good.Input = mock.MagicMock()
    steam_good.Input.GetConnectedControllers.return_value = []
    steam_good.Input.GetActionSetHandle.return_value = 0
    steam_good.action_set = 1

    def steam_factory():
        if steam_factory.calls == 0:
            steam_factory.calls += 1
            raise RuntimeError("fail")
        return steam_good

    steam_factory.calls = 0
    monkeypatch.setattr(it, "STEAMWORKS", lambda: steam_factory())

    with (
        mock.patch.object(it.usb_gadget, "HIDFunction"),
        mock.patch.object(it.usb_gadget, "JoystickGadget"),
        mock.patch.object(
            it.time,
            "sleep",
            side_effect=lambda *_: stop_event.set(),
        ),
    ):
        it.start_translation_loop(stop_event)
    assert steam_factory.calls == 1
    steam_good.shutdown.assert_called()


def test_missing_action_handle_exits():
    stop_event = threading.Event()
    steam = mock.MagicMock()
    steam.Input = mock.MagicMock()
    steam.Input.GetConnectedControllers.return_value = []
    steam.Input.GetActionSetHandle.return_value = 1
    steam.Input.GetAnalogActionHandle.return_value = 0

    with (
        mock.patch.object(it, "STEAMWORKS", return_value=steam),
        mock.patch.object(it.usb_gadget, "HIDFunction"),
        mock.patch.object(it.usb_gadget, "JoystickGadget"),
    ):
        it.start_translation_loop(stop_event)
    steam.Input.GetAnalogActionHandle.assert_called()
