# DeckLink

DeckLink turns the Steam Deck into a standard USB game controller that can be used on any PC. It combines a small bash UI with a Python backend to emulate a generic gamepad via the Linux USB gadget subsystem.

## Installation

1. **Set a sudo password** on your Steam Deck. [SteamDeckTips guide](https://steamdecktips.com/blog/how-to-set-a-password-for-your-steam-deck-user-in-desktop-mode)
2. **Enable USB Dual Role Device** in the BIOS:
   - Power off the Deck completely.
   - Hold **Volume Up** and press the power button to enter the BIOS setup utility.
   - Using the D‑pad, navigate to `Advanced` → `USB Configuration` → `USB Dual Role Device`.
   - Press **A** and select **DRD (Dual Role Data)**.
   - Choose **Save & Exit** to reboot.
3. Clone this repository on the Deck and run the installer:

```bash
cd ~/DeckLink
sudo ./install.sh
```

The script installs system packages and Python dependencies, copies `decklink_app/` and `main.sh` to `/usr/share/decklink` (or `$DESTDIR` if set) and makes the script executable.

## Usage

Launch DeckLink from a terminal or a Steam shortcut:

```bash
/usr/share/decklink/main.sh
```

Connect the Deck to your PC via USB‑C. The host should detect a generic gamepad automatically. In Steam on the host PC, enable **Generic gamepad configuration support** in the controller settings.

## Steam Integration

To start DeckLink from Game Mode:

1. In Desktop Mode, open Steam and choose **Add a Non‑Steam Game**.
2. Browse to `/usr/share/decklink/main.sh` and add it to your library.
3. In Game Mode, edit the controller layout for DeckLink and enable **Touchscreen Native Support** under *Action Sets → Default → Add Always‑On command*.
4. Launch the shortcut from your library.

## Troubleshooting

- **Deck not detected**: verify the BIOS setting above and try reconnecting the cable.
- **Permission errors**: ensure you ran the installer with `sudo` and that system packages installed correctly.
- **No response on the host**: check that Steam's *Generic gamepad configuration support* is enabled and try a different USB‑C cable.

DeckLink should now allow your Steam Deck to act as a simple USB controller for any host PC.
