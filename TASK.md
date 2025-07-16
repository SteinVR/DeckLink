# DeckLink MVP Task List

## ✅ Completed Foundation

| ID | Task | Status |
|----|------|--------|
| 00 | - [X] DevOps bootstrap (`Dockerfile`, CI workflow) | **Done** |
| 01 | - [X] Baseline project structure (`decklink_app`, `source_*`) | **Done** |
| 02 | - [X] Extract `gadget_manager.py` module | **Done** |

> *No action required on these items until regression issues appear.*

---

## 🚀 Phase 2 – Integration, UI & Packaging

All remaining work is consolidated into one phase so that each task feeds directly into the next and we can aim for a single "vertical slice" MVP build.

| ID | Task | Notes |
|----|------|-------|
| 03 | - [X] **Lifecycle Shell Script** – create `main.sh` to wrap UI + sudo flow<br>Replace all VirtualHere logic with stub calls to the Python backend. | Use ASCII/figlet splash just like Deckpad. |
| 04 | - [X] **Python Entrypoint** – implement `main_app.py` to glue the shell script with backend modules (`setup`, `run`, `destroy`). | Must import, not shell‑exec, `decklink_app` functions. |
| 05 | - [X] **Input Translator** – port core loop into `decklink_app/input_translator.py`, exposing `start_translation_loop()`. | **Done** - PR reviewed, needs minor fixes (error handling, constants). |
| 06 | - [X] **Installer** – write `install.sh` to copy files, install deps and mark `main.sh` executable. | Must not copy any `source_*` content into final build. |
| 07 | - [X] **User‑facing Docs** – draft `README.md` with install & usage instructions. | Include BIOS DRD toggle, sudo setup, and expected host‑PC behaviour. |

### Acceptance Criteria

- **No runtime dependency on `source_*`** directories. Any borrowed assets are copied to `decklink_app/` or `share/`.
- `make lint && pytest` passes inside the DevOps container.
- `./main.sh` launched from Steam Game Mode emulates a *generic gamepad* that is detected by Windows/Linux without extra drivers.