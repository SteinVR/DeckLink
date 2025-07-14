import os
import sys
import threading
from types import SimpleNamespace
from unittest import mock

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)

sys.modules.setdefault("steamworks", mock.MagicMock())

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
    steam.Input.GetAnalogActionData.side_effect = lambda c, h: analog_returns[h]

    digital_returns = {
        f"d_{name}": DummyDigital(bState=i % 2)
        for i, name in enumerate(it.DIGITAL_ACTIONS)
    }
    steam.Input.GetDigitalActionData.side_effect = lambda c, h: digital_returns[h]

    hid_fn = mock.MagicMock(device="/dev/hidg0")

    with (
        mock.patch.object(it, "STEAMWORKS", return_value=steam),
        mock.patch.object(it.usb_gadget, "HIDFunction", return_value=hid_fn) as hid_cls,
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
    js_instance.set_trigger.assert_has_calls([mock.call(0, 5), mock.call(1, 6)])
    assert js_instance.set_button.call_count == len(it.DIGITAL_ACTIONS)
    js_instance.update.assert_called_once()
