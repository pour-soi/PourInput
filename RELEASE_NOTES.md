# PourInput v1.0.0

Release date: 2026-07-08

Repository: `pour-soi/PourInput`

Based on: `TomBadash/Mouser`

Maintainer: `pour-soi`

## Summary

PourInput v1.0.0 is the first official release of PourInput, a customized fork of TomBadash/Mouser.

It adds a generic Multi-Action Button framework so supported mouse buttons can use separate Click and Long Press actions. The goal is simple: one physical button can now cover a primary action and a secondary action without adding button-specific timing code for every new control.

This release also finalizes the PourInput application identity, Windows executable metadata, updater metadata, installer metadata, and release package naming.

## New Features

- Generic Multi-Action Button framework
- Mode Shift Click and Long Press mappings
- Back Button Click and Long Press mappings
- Forward Button Click and Long Press mappings
- Generic dispatcher shared by supported buttons
- Config migration for long-press mappings
- UI for Click Action and Long Press Action
- Versioned Windows release packaging
- Consistent PourInput naming and pour-soi maintainer metadata
- Official `PourInput-v1.0.0-Windows.zip` release artifact

## Documentation

- Clearer README sections for features, installation, screenshots, supported devices, roadmap, and credits.
- Supported-device notes now call out the currently cataloged Logitech families and the HID++ requirements behind button remapping.
- Credits now explicitly acknowledge the original Mouser project and its contributors.
- Repository presentation now includes logo placement, release badges, ordered screenshots, cautious device support tables, and clearer known limitations.

## Bug Fixes

- Mode Shift HID diversion is synchronized after mapping changes.
- Mode Shift diversion now considers both click and long-press mappings.

## Files Modified

- `core/config.py`
- `core/engine.py`
- `core/update_installer.py`
- `core/updater.py`
- `core/version.py`
- `core/startup.py`
- `PourInput.spec`
- `main_qml.py`
- `ui/backend.py`
- `ui/qml/Main.qml`
- `ui/qml/MousePage.qml`
- `ui/locale_manager.py`
- `tests/test_backend.py`
- `tests/test_config.py`
- `tests/test_engine.py`
- `tests/test_smart_shift.py`
- `README.md`
- `README_CN.md`
- `CHANGELOG.md`
- `RELEASE_NOTES.md`
- `scripts/create_release.ps1`

## Tests Passed

- `python -m unittest tests.test_engine tests.test_config.ConfigMigrationTests tests.test_backend.BackendDeviceLayoutTests.test_connected_device_supported_buttons_filter_mapping_list`
- `python -m unittest tests.test_smart_shift tests.test_mouse_hook tests.test_hid_gesture tests.test_logi_devices tests.test_device_layouts`
- `python -m unittest tests.test_main_qml_policy tests.test_main_qml_shortcuts tests.test_locale_manager`
- `python -m compileall core ui tests`

## Known Limitations

- Double Click is planned but not implemented yet.
- Long Press timeout defaults to 300 ms and is not editable in the UI yet.
- Timeout is global, not per button.
- Macro support and sequential actions are not implemented yet.
- Windows is the only official release target for v1.0.0.
- macOS support is planned but not officially available.
- Device support depends on each mouse exposing compatible HID++ controls.

## How To Test

1. Launch `PourInput.exe`.
2. Open the Mouse page.
3. Configure Back:
   - Click Action -> Browser Back
   - Long Press Action -> Copy
4. Configure Forward:
   - Click Action -> Browser Forward
   - Long Press Action -> Paste
5. Configure Mode Shift:
   - Click Action -> Screenshot Region -> Clipboard
   - Long Press Action -> Switch Scroll Mode
6. Press and release under 300 ms to test Click Action.
7. Hold for at least 300 ms, then release, to test Long Press Action.
