# Project Architecture: DeckLink

## 1. Overview

DeckLink is a SteamOS application for the Steam Deck that enables it to function as a standard USB game controller when connected to a host PC via a USB-C cable. The project's core mission is to combine the user-friendly, game-mode-native interface of the "Deckpad" project with the direct USB hardware emulation technology from the "GadgetDeck" project, eliminating the need for LAN-based solutions like VirtualHere.

---

## 2. Core Concepts & Domain Terminology

- **libcomposite:** The Linux Kernel's USB Gadget Framework, which allows the Steam Deck to emulate various USB devices. This is the core technology we are using.
- **USB Gadget:** The virtual USB device being emulated by the Steam Deck.
- **HID (Human Interface Device):** The specific type of USB device class we are emulating. For this project, it's a composite device that acts as a standard gamepad/joystick.
- **Steam Input:** The native SteamOS service that provides access to the physical controls of the Steam Deck. This is our source of truth for controller state.
- **Game Mode UI:** The user interface, which runs in a full-screen terminal. It's built using shell scripts and ASCII art tools (`figlet`) to feel native to the Steam Deck's gaming environment.

---

## 3. Goals and Non-Goals

### Goals
- **MVP Goal:** Develop a single, launchable application in Steam Game Mode that successfully emulates a USB gamepad via a direct USB-C connection.
- Replicate the core user experience of "Deckpad": a simple, clear ASCII interface, automatic screen dimming, and disabling of the system's sleep mode during operation.
- Utilize the `libcomposite` framework via the logic adapted from "GadgetDeck".
- Ensure the emulated controller is recognized as a standard generic gamepad on a host PC without special drivers.

### Non-Goals
- A complex graphical UI (e.g., using PyQt5). The MVP will use a terminal-based UI only.
- A sophisticated installer with a GUI. The initial installation will be handled by a shell script.

---

## 4. High-Level Architecture

The system is a hybrid application composed of a shell script frontend and a Python backend.
1.  A **Bash script (`main.sh`)** serves as the main entry point and lifecycle manager. It handles the UI, user interaction, system state changes (brightness, sleep), and process control.
2.  The Bash script invokes a **Python backend** to manage the low-level USB emulation and input translation. The backend is split into two main logical parts.

---

## 5. Technology Stack

- **Language:** Bash, Python 3
- **UI:** `bash`, `figlet`, `xinput`
- **Backend Logic:** `python-usb-gadget`, `steamworkspy`
- **Core Technology:** Linux `libcomposite` framework
- **System Integration:** `sudo` for permissions, `systemctl` for service management, `polkit` for permissions rules.

---

## 6. Component Breakdown

### 6.1. UI & Lifecycle Manager (`main.sh`)
- **Source:** Based on `Deckpad/deckpad.sh` and `Deckpad/functions.sh`.
- **Responsibility:**
    - Render the ASCII UI in a full-screen terminal.
    - Request `sudo` permissions.
    - Manage system state: dim screen, disable/enable sleep.
    - Detect user input (screen tap) to trigger shutdown.
    - Invoke the Python Backend (`main_app.py`) with appropriate arguments (`setup`, `run`, `destroy`).
    - Ensure graceful shutdown and cleanup.

### 6.2. Gadget Orchestrator (`gadget_manager.py`)
- **Source:** Refactored from `gadget-deck-manager.py`.
- **Responsibility:**
    - Provide Python functions to programmatically control the USB gadget lifecycle.
    - `setup()`: Creates the USB gadget configuration in `/sys/kernel/config/usb_gadget/`.
    - `enable_gamepad()`: Creates and links the HID function for the gamepad.
    - `destroy()`: Cleans up all created configurations and functions.
    - This component will be refactored from a command-line tool into an importable Python module.

### 6.3. Input Translator (`input_translator.py`)
- **Source:** Based on the core loop in `GadgetDeck/__main__.py`.
- **Responsibility:**
    - Initialize the Steamworks API to connect to Steam Input.
    - In a continuous loop, read the state of the Steam Deck's controls (joysticks, buttons, triggers).
    - Translate this state into the raw HID report format.
    - Write the HID report to the appropriate device file (e.g., `/dev/hidg0`) to send it to the host PC.

---

## 7. Data Model

The primary data is the controller state, which flows from Steam Input to the HID device. The HID report for the gamepad will consist of:
- **Analog Axes:** Values for Left Stick X/Y, Right Stick X/Y, Left Trigger, Right Trigger.
- **Digital Buttons:** A bitmask representing the state (pressed/not pressed) of all digital buttons (A, B, X, Y, D-Pad, Bumpers, etc.).

---

## 8. Key Workflows

### 8.1. Application Startup
1. User launches "DeckLink" from Steam Game Mode.
2. `main.sh` starts, clears the screen, and displays the welcome UI.
3. It requests `sudo` password.
4. On success, it calls `python3 main_app.py setup`. This configures and enables the USB gadget.
5. `main.sh` dims the screen and disables sleep.
6. It then calls `python3 main_app.py run` in the background. This starts the input translation loop.
7. The UI now shows the "Running" screen, waiting for a screen tap to exit.

### 8.2. Application Shutdown
1. User taps the designated area on the screen.
2. `main.sh` detects the tap via `xinput`.
3. It kills the background `main_app.py run` process.
4. It calls `python3 main_app.py destroy` to safely disable and remove the USB gadget.
5. It restores screen brightness and re-enables the system's sleep mode.
6. The script prints a shutdown message and exits, returning the user to the Steam UI.

---

## 9. Infrastructure and Deployment (DevOps)

- **Installation:** A `setup.sh` script will handle installation. It will copy files to a designated directory (e.g., `/usr/share/decklink`), set permissions, install Python dependencies, and configure `polkit` rules to allow passwordless `sudo` for specific commands if possible.
- **Local Setup:** The project will not require complex building, but will depend on system packages like `figlet` and `xinput`.

---

## 10. Coding Conventions

- **Python:** Adhere to PEP 8. Use `black` for formatting if possible.
- **Shell:** Use `shellcheck` to ensure scripts are robust and free of common errors.
- **Comments:** Use `AICODE-` prefixes for agent-specific notes, tasks, and questions.