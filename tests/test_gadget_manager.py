import sys
from types import SimpleNamespace
from unittest import mock

sys.modules.setdefault("hid_parser", mock.MagicMock())
sys.modules.setdefault("usb_gadget", mock.MagicMock())

import decklink_app.gadget_manager as gm  # noqa: E402


class Node(SimpleNamespace):
    def __getitem__(self, key):
        return getattr(self, key)


def test_gadget_setup():
    strings = Node()
    config_strings = Node()
    config = Node(strings=Node(**{"0x409": config_strings}))
    gadget = Node(
        strings=Node(**{"0x409": strings}),
        configs=Node(**{"c.1": config}),
    )

    with mock.patch.object(gm, "gadget", gadget):
        result = gm.gadget_setup()

    assert result is config
    assert gadget.idVendor == "0x1d6b"
    assert strings.serialnumber == "0123456789"
    assert config_strings.configuration == "Steam Deck Configuration"


def test_function_enable_joystick():
    gadget = mock.MagicMock()
    with mock.patch.object(gm, "gadget", gadget), mock.patch.object(
        gm, "create_function_hid"
    ) as create_fn, mock.patch.object(gm, "chmod_hidg") as chmod:
        gm.function_enable("joystick")

    gadget.deactivate.assert_called_once()
    create_fn.assert_called_once_with(
        "joystick",
        "HID Descriptors/joystick.txt",
    )
    gadget.activate.assert_called_once()
    chmod.assert_called_once()


def test_function_disable_joystick():
    config = Node(path="/config")
    gadget = mock.MagicMock()

    def side_effect(key):
        return {"configs": Node(**{"c.1": config})}[key]

    gadget.__getitem__.side_effect = side_effect
    entry = mock.MagicMock()
    entry.is_symlink.return_value = True
    with mock.patch.object(gm, "gadget", gadget), mock.patch.object(
        gm, "remove_function"
    ) as remove_fn, mock.patch.object(gm, "chmod_hidg") as chmod, mock.patch(
        "decklink_app.gadget_manager.os.scandir", return_value=[entry]
    ):
        gm.function_disable("joystick")

    gadget.deactivate.assert_called_once()
    remove_fn.assert_called_once_with("hid.joystick")
    gadget.activate.assert_called_once()
    chmod.assert_called_once()
