import glob
import os
import subprocess
from typing import Union

import hid_parser
import usb_gadget

DESCRIPTORS_DIR = os.path.join(os.path.dirname(__file__), "descriptors")


gadget = usb_gadget.USBGadget("gadget-deck")


def gadget_setup():
    """Set up the USB gadget and return its configuration."""
    gadget.idVendor = "0x1d6b"
    gadget.idProduct = "0x0104"
    gadget.bcdDevice = "0x0100"
    gadget.bcdUSB = "0x0200"

    strings = gadget["strings"]["0x409"]
    strings.serialnumber = "0123456789"
    strings.manufacturer = "Valve"
    strings.product = "Steam Deck"

    config = gadget["configs"]["c.1"]
    config.bmAttributes = "0x80"
    config.MaxPower = "250"
    config["strings"]["0x409"].configuration = "Steam Deck Configuration"
    return config


def gadget_destroy():
    """Remove the gadget and all of its functions."""
    try:
        gadget.deactivate()
    except FileNotFoundError:
        pass

    for config in os.scandir(gadget["configs"].path):
        config = usb_gadget.ConfigFS(config.path)
        for function in os.scandir(config.path):
            if function.is_symlink():
                os.remove(function.path)
        for language in os.scandir(config["strings"].path):
            os.rmdir(language.path)
        os.rmdir(config.path)

    for function in os.scandir(gadget["functions"].path):
        os.rmdir(function.path)

    for language in os.scandir(gadget["strings"].path):
        os.rmdir(language.path)

    try:
        os.rmdir(gadget.path)
    except FileNotFoundError:
        pass


def create_function_hid(
    name: str, report: Union[str, list[int]], protocol=0, subclass=0
):
    """Create and link an HID function to the gadget."""
    if isinstance(report, str):
        if not os.path.isabs(report):
            report = os.path.join(DESCRIPTORS_DIR, report)
        with open(report, "rt") as f:
            descriptor = hid_parser.ReportDescriptor.from_str(f.read())
    else:
        descriptor = hid_parser.ReportDescriptor(report)
    hid = usb_gadget.HIDFunction(gadget, name)
    hid.protocol = str(protocol)
    hid.subclass = str(subclass)
    hid.report_length = str(descriptor.get_input_report_size().byte)
    hid.report_desc = bytes(descriptor.data)
    gadget.link(hid, gadget["configs"]["c.1"])
    return hid


def remove_function(name: str):
    """Unlink and remove a function."""
    os.unlink(gadget["configs"]["c.1"][name].path)
    os.rmdir(gadget["functions"][name].path)


def function_enable(function: str, activate: bool = True):
    """Enable a gadget function."""
    gadget.deactivate()
    if function in ("joystick", "mouse", "keyboard"):
        create_function_hid(function, f"{function}.txt")
        if activate:
            gadget.activate()
        chmod_hidg()
    if function == "mtp":
        f = usb_gadget.USBFunction(gadget, "ffs.mtp")
        gadget.link(f, gadget["configs"]["c.1"])
        os.mkdir("/dev/ffs-mtp")
        subprocess.call(["mount", "-t", "functionfs", "mtp", "/dev/ffs-mtp"])
        if activate:
            gadget.activate()
    if function == "shell":
        f = usb_gadget.USBFunction(gadget, "acm.shell")
        gadget.link(f, gadget["configs"]["c.1"])
        if activate:
            gadget.activate()
        cmd = ["systemctl", "start", f"getty@ttyGS{f.port_num}.service"]
        subprocess.call(cmd)


def function_disable(function: str, activate: bool = True):
    """Disable a gadget function."""
    gadget.deactivate()
    if function in ("joystick", "mouse", "keyboard"):
        remove_function(f"hid.{function}")
    if function == "mtp":
        subprocess.call(["umount", "/dev/ffs-mtp"])
        os.rmdir("/dev/ffs-mtp")
        remove_function("ffs.mtp")
    if function == "shell":
        f = usb_gadget.USBFunction(gadget, "acm.shell")
        cmd = ["systemctl", "stop", f"getty@ttyGS{f.port_num}.service"]
        subprocess.call(cmd)
        remove_function("acm.shell")
    linked_functions = [
        f for f in os.scandir(gadget["configs"]["c.1"].path) if f.is_symlink()
    ]
    if activate and linked_functions:
        gadget.activate()
        chmod_hidg()


def chmod_hidg():
    """Set permissions on hidg devices."""
    for dev in glob.glob("/dev/hidg*"):
        subprocess.call(["chmod", "0666", dev])
