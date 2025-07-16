import os
import sys
from types import SimpleNamespace
from unittest import mock
import pytest


sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)


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
    with (
        mock.patch.object(gm, "gadget", gadget),
        mock.patch.object(gm, "create_function_hid") as create_fn,
        mock.patch.object(gm, "chmod_hidg") as chmod,
    ):
        gm.function_enable("joystick")

    gadget.deactivate.assert_called_once()
    create_fn.assert_called_once_with(
        "joystick",
        "joystick.txt",
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
    with (
        mock.patch.object(gm, "gadget", gadget),
        mock.patch.object(gm, "remove_function") as remove_fn,
        mock.patch.object(gm, "chmod_hidg") as chmod,
        mock.patch(
            "decklink_app.gadget_manager.os.scandir",
            return_value=[entry],
        ),
    ):
        gm.function_disable("joystick")

    gadget.deactivate.assert_called_once()
    remove_fn.assert_called_once_with("hid.joystick")
    gadget.activate.assert_called_once()
    chmod.assert_called_once()


def test_function_disable_shell():
    gadget = mock.MagicMock()
    usb_function = mock.MagicMock(port_num=1)
    entry = mock.MagicMock()
    entry.is_symlink.return_value = False
    with (
        mock.patch.object(gm, "gadget", gadget),
        mock.patch(
            "decklink_app.gadget_manager.usb_gadget.USBFunction",
            return_value=usb_function,
        ) as usb_cls,
        mock.patch.object(gm, "remove_function") as remove_fn,
        mock.patch("decklink_app.gadget_manager.subprocess.call") as sub_call,
        mock.patch("decklink_app.gadget_manager.os.scandir", return_value=[]),
        mock.patch.object(gm, "chmod_hidg") as chmod,
    ):
        gm.function_disable("shell")

    sub_call.assert_called_once_with(
        ["systemctl", "stop", "getty@ttyGS1.service"]
    )  # noqa: E501
    usb_cls.assert_called_once_with(gadget, "acm.shell")
    remove_fn.assert_called_once_with("acm.shell")
    gadget.activate.assert_not_called()
    chmod.assert_not_called()


def test_validate_hid_device_missing():
    with mock.patch("decklink_app.gadget_manager.glob.glob", return_value=[]):
        with pytest.raises(FileNotFoundError):
            gm.validate_hid_device()

def test_gadget_destroy_removes_dirs():
    gadget = mock.MagicMock(
        path="/gadget",
        configs=Node(path="/configs"),
        functions=Node(path="/functions"),
        strings=Node(path="/strings"),
    )
    gadget.__getitem__.side_effect = lambda key: getattr(gadget, key)
    scandir_side = [
        [Node(path="/configs/c.1")],  # configs
        [],  # functions in config
        [Node(path="/configs/c.1/strings/en")],  # strings in config
        [Node(path="/functions/hid.joystick")],
        [Node(path="/strings/en")],
    ]
    with (
        mock.patch.object(gm, "gadget", gadget),
        mock.patch("decklink_app.gadget_manager.os.scandir", side_effect=scandir_side),
        mock.patch(
            "decklink_app.gadget_manager.usb_gadget.ConfigFS",
            side_effect=lambda p: Node(path=p, strings=Node(path=f"{p}/strings")),
        ),
        mock.patch("decklink_app.gadget_manager.os.remove") as rm,
        mock.patch("decklink_app.gadget_manager.os.rmdir") as rmdir,
    ):
        gm.gadget_destroy()
    rm.assert_not_called()
    assert rmdir.call_count >= 1


def test_create_function_hid_from_file(tmp_path):
    desc_path = tmp_path / "d.txt"
    desc_path.write_text("data")
    descriptor = mock.MagicMock()
    descriptor.get_input_report_size.return_value = Node(byte=8)
    descriptor.data = b"abc"
    with (
        mock.patch.object(gm.hid_parser.ReportDescriptor, "from_str", return_value=descriptor) as from_str,
        mock.patch.object(gm, "gadget"),
        mock.patch("decklink_app.gadget_manager.usb_gadget.HIDFunction") as hid_cls,
    ):
        gm.create_function_hid("mouse", str(desc_path))
    from_str.assert_called_once()
    hid_cls.assert_called_once()


def test_create_function_hid_from_list():
    descriptor = mock.MagicMock()
    descriptor.get_input_report_size.return_value = Node(byte=8)
    descriptor.data = b"abc"
    with (
        mock.patch("decklink_app.gadget_manager.hid_parser.ReportDescriptor", return_value=descriptor) as desc_cls,
        mock.patch.object(gm, "gadget"),
        mock.patch("decklink_app.gadget_manager.usb_gadget.HIDFunction") as hid_cls,
    ):
        gm.create_function_hid("kbd", [1, 2, 3])
    desc_cls.assert_called_once_with([1, 2, 3])
    hid_cls.assert_called_once()


def test_remove_function():
    gadget = Node(
        configs=Node(
            **{"c.1": Node(**{"hid.joystick": Node(path="/config/hid.joystick")})}
        ),
        functions=Node(**{"hid.joystick": Node(path="/func")}),
    )
    gadget.__getitem__ = lambda self, key: getattr(self, key)
    with (
        mock.patch.object(gm, "gadget", gadget),
        mock.patch("decklink_app.gadget_manager.os.unlink") as unlink,
        mock.patch("decklink_app.gadget_manager.os.rmdir") as rmdir,
    ):
        gm.remove_function("hid.joystick")
    unlink.assert_called_once_with("/config/hid.joystick")
    rmdir.assert_called_once_with("/func")


def test_chmod_hidg():
    with (
        mock.patch("decklink_app.gadget_manager.glob.glob", return_value=["/dev/hidg0"]),
        mock.patch("decklink_app.gadget_manager.subprocess.call") as call,
    ):
        gm.chmod_hidg()
    call.assert_called_once_with(["chmod", "0666", "/dev/hidg0"])


def test_validate_hid_device_success():
    with mock.patch("decklink_app.gadget_manager.glob.glob", return_value=["/dev/hidg0"]):
        gm.validate_hid_device()
