"""Translate Steam Input events to HID reports."""

from __future__ import annotations

import logging
import threading
import time

from steamworks import STEAMWORKS
import usb_gadget

from . import gadget_manager as gm


ACTION_SET_NAME = "InGameControls"
ANALOG_ACTIONS = (
    "JoyLeft",
    "JoyRight",
    "TrigLeft",
    "TrigRight",
)
DIGITAL_ACTIONS = (
    "A",
    "B",
    "X",
    "Y",
    "UP",
    "DOWN",
    "LEFT",
    "RIGHT",
    "BumpLeft",
    "BumpRight",
    "Menu",
    "Start",
    "JoyPressLeft",
    "JoyPressRight",
    "BackLeftTop",
    "BackLeftBottom",
    "BackRightTop",
    "BackRightBottom",
)

JOYSTICK_COUNT = 2
TRIGGER_COUNT = 2
BUTTON_COUNT = 24

_logger = logging.getLogger(__name__)


def _get_controller(steam: STEAMWORKS) -> tuple[list[int], int | None]:
    controllers = steam.Input.GetConnectedControllers()
    if not controllers:
        return [], None
    for controller in controllers:
        steam.Input.ActivateActionSet(controller, steam.action_set)
    return controllers, controllers[0]


def start_translation_loop(stop_event: threading.Event | None) -> None:
    """Run the Steam Input translation loop."""

    if stop_event is None:
        stop_event = threading.Event()

    hid = usb_gadget.HIDFunction(gm.gadget, "joystick")
    js_gadget = usb_gadget.JoystickGadget(
        hid.device,
        JOYSTICK_COUNT,
        TRIGGER_COUNT,
        BUTTON_COUNT,
    )

    steam = None
    retry_count = 0
    max_retries = 3
    while not stop_event.is_set() and retry_count < max_retries:
        try:
            steam = STEAMWORKS()
            steam.initialize()
            steam.Input.Init()

            steam.action_set = steam.Input.GetActionSetHandle(ACTION_SET_NAME)
            if not steam.action_set:
                _logger.error("Steam action set %s not found", ACTION_SET_NAME)
                return
            steam.analog_handles = {
                name: steam.Input.GetAnalogActionHandle(name)
                for name in ANALOG_ACTIONS
            }
            steam.digital_handles = {
                name: steam.Input.GetDigitalActionHandle(name)
                for name in DIGITAL_ACTIONS
            }
            if any(h == 0 for h in steam.analog_handles.values()) or any(
                h == 0 for h in steam.digital_handles.values()
            ):
                _logger.error("Required Steam Input actions missing")
                return

            controllers, controller = _get_controller(steam)

            while not stop_event.is_set():
                steam.Input.RunFrame()
                if not controller:
                    controllers, controller = _get_controller(steam)
                    time.sleep(0.016)
                    continue

            analog_data = {
                name: steam.Input.GetAnalogActionData(controller, handle)
                for name, handle in steam.analog_handles.items()
            }
            digital_data = {
                name: steam.Input.GetDigitalActionData(
                    controller,
                    handle,
                ).bState
                for name, handle in steam.digital_handles.items()
            }

            js_gadget.set_joystick(
                0,
                analog_data["JoyLeft"].x,
                -analog_data["JoyLeft"].y,
            )
            js_gadget.set_joystick(
                1,
                analog_data["JoyRight"].x,
                -analog_data["JoyRight"].y,
            )
            js_gadget.set_trigger(0, analog_data["TrigLeft"].x)
            js_gadget.set_trigger(1, analog_data["TrigRight"].x)
            for i, btn in enumerate(DIGITAL_ACTIONS):
                js_gadget.set_button(i, digital_data[btn])
            js_gadget.update()

            time.sleep(0.016)

        except Exception as exc:  # noqa: BLE001
            retry_count += 1
            _logger.warning(
                "Steam initialization failed, retry %s/%s: %s",
                retry_count,
                max_retries,
                exc,
            )
            time.sleep(2)
        else:
            break

    if steam is not None:
        try:
            if steam is not None:
                shutdown = getattr(steam, "shutdown", None)
                if callable(shutdown):
                    shutdown()
                input_shutdown = getattr(steam.Input, "Shutdown", None)
                if callable(input_shutdown):
                    input_shutdown()
        except Exception as exc:  # noqa: BLE001
            _logger.error("Steam Input shutdown failed: %s", exc)
