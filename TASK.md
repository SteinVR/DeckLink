# DeckLink MVP: Task List

## Phase 1: Foundation & Refactoring
- [X] **Task-00: Setup DevOps Environment.**
    - Create a `Dockerfile` based on `archlinux:latest` that installs all system and python dependencies needed for the project.
    - Create a GitHub Actions workflow file at `.github/workflows/ci.yml`.
    - The workflow should run on every push and pull request.
    - It must perform linting for both Shell (`shellcheck`) and Python (`black`, `flake8`) code.

- [X] **Task-01: Set up project structure.**
    - Create a new Git repository.
    - Create directories: `decklink_app`, `source_deckpad`, `source_gadgetdeck`.
    - Copy the original source code of both projects into their respective `source_*` directories.

- [X] **Task-02: Refactor `gadget-deck-manager.py` into an importable module.**
    - Create a new file `decklink_app/gadget_manager.py`.
    - Move the core logic (`gadget_setup`, `function_enable`, `function_disable`, `gadget_destroy`) from the original script into this new file as Python functions.
    - Remove the `argparse` command-line handling. The functions should accept parameters directly.

## Phase 2: UI & Lifecycle Management

- [ ] **Task-03: Create the main lifecycle script `main.sh`.**
    - Copy `deckpad.sh` and `functions.sh` into the project's root.
    - Rename `deckpad.sh` to `main.sh`.
    - Remove all logic related to `VirtualHere`.
    - Add placeholder function calls for `setup`, `run`, and `destroy` stages which will later invoke the Python backend.

## Phase 3: Integration & Core Logic

- [ ] **Task-04: Create the main Python application entrypoint `main_app.py`.**
    - This script will be the "glue" between the shell script and the Python modules.
    - It should parse command-line arguments (`setup`, `run`, `destroy`).
    - `setup` argument: should import and call the setup functions from `gadget_manager.py`.
    - `destroy` argument: should import and call the cleanup functions from `gadget_manager.py`.
    - `run` argument: should import and call the main input loop from `input_translator.py`.

- [ ] **Task-05: Adapt the input translation logic into `input_translator.py`.**
    - Create `decklink_app/input_translator.py`.
    - Copy the core `while True:` loop and related setup from `GadgetDeck/__main__.py` into a function, e.g., `start_translation_loop()`.
    - Ensure it can be cleanly started and stopped (it will be terminated by `main.sh`).

## Phase 4: Finalization & Packaging

- [ ] **Task-06: Create a basic `install.sh` script.**
    - The script should handle copying the application files to a system directory.
    - It should install necessary Python packages from a `requirements.txt` file.
    - It should install system dependencies like `figlet`.
    - It should make `main.sh` executable.

- [ ] **Task-07: Write the user-facing `README.md`.**
    - Document the project's purpose.
    - Provide clear, step-by-step installation and usage instructions for the end-user.