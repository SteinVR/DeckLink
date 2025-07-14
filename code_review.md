# Code Review Report – DeckLink (14 Jul 2025)

## Summary
This review captures critical findings after integrating `source_*` codebases into the self‑contained DeckLink project. Items are ordered by severity.

| Area | Issue | Impact | Suggested fix |
|------|-------|--------|---------------|
| **Dev Ops** | `Dockerfile` and CI workflow (`.github/workflows/ci.yml`) are missing, yet Task‑00 is ticked. | No reproducible builds or automated linting/tests in PRs. | Commit the missing files or mark the task incomplete. |
| **Runtime dependency** | `decklink_app/gadget_manager.py#create_function_hid()` still reads HID reports from `source_GadgetDeck/HID Descriptors/*`. | Violates “no functional link to `source_*`”; crashes once sources are removed. | Copy descriptors into `decklink_app/descriptors/` and update code & tests to use package‑relative paths. |
| **Shell function disable** | `function_disable('shell')` calls `systemctl start getty@…` and skips `remove_function('acm.shell')`. | Leaves orphaned services & symlinks; prevents re‑enable. | Use `systemctl stop …`, then `remove_function('acm.shell')`, followed by conditional `gadget.activate()`. |
| **`gadget_destroy()` robustness** | Lacks initial `gadget.deactivate()` and uses unguarded `os.rmdir()`. | Partial clean‑up bricks the gadget until reboot. | Deactivate first; wrap removals in `try/except FileNotFoundError`. |
| **Unit tests** | Tests rely on old descriptor location, will fail after move. | CI failures. | Parametrize path via fixture or `importlib.resources`. |
| **Code hygiene** | Duplicate brightness logic, magic constants, and no logging. | Hard to maintain & debug. | Extract helpers, define constants, add `logging`. |

### Priority
1. **Runtime descriptor path**
2. **Shell disable bug**
3. **Robust cleanup**

Addressing these unblock a working USB‑gadget MVP. Subsequent commits can tackle Dev Ops gaps and hygiene improvements.

