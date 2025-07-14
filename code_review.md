# Code Review Report – DeckLink (14 Jul 2025)

## Summary
This review captures critical findings after integrating `source_*` codebases into the self‑contained DeckLink project. Items are ordered by severity.

| Area | Issue | Impact | Suggested fix |
|------|-------|--------|---------------|
| **Dev Ops** | `Dockerfile` and CI workflow (`.github/workflows/ci.yml`) were initially missing. | No reproducible builds or automated linting/tests in PRs. | **Resolved:** required files added to repository. |
| **Runtime dependency** | `decklink_app/gadget_manager.py#create_function_hid()` still reads HID reports from `source_GadgetDeck/HID Descriptors/*`. | Violates “no functional link to `source_*`”; crashes once sources are removed. | **Resolved:** descriptors moved to `decklink_app/descriptors/` and code/tests updated. |
| **Shell function disable** | `function_disable('shell')` calls `systemctl start getty@…` and skips `remove_function('acm.shell')`. | Leaves orphaned services & symlinks; prevents re‑enable. | **Resolved:** now stops the service, removes the function and reactivates if needed. |
| **`gadget_destroy()` robustness** | Lacks initial `gadget.deactivate()` and uses unguarded `os.rmdir()`. | Partial clean‑up bricks the gadget until reboot. | **Resolved:** function now deactivates first and ignores missing paths. |
| **Unit tests** | Tests rely on old descriptor location, will fail after move. | CI failures. | **Resolved:** tests updated to use package-relative descriptor paths. |
| **Code hygiene** | Duplicate brightness logic, magic constants, and no logging. | Hard to maintain & debug. | Extract helpers, define constants, add `logging`. |

### Priority
1. **Runtime descriptor path**
2. **Shell disable bug**
3. **Robust cleanup**

Addressing these unblock a working USB‑gadget MVP. Subsequent commits can tackle Dev Ops gaps and hygiene improvements.

