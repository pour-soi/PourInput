# PourInput v1.2.0 — Generic Mouse Mode & Chinese UI

Release date: 2026-07-09

Repository: `pour-soi/PourInput`

Based on: `TomBadash/Mouser`

Maintainer: `pour-soi`

## Summary

PourInput v1.2.0 adds Generic Mouse Mode for standard Windows mouse buttons and completes the English / Simplified Chinese application and documentation experience.

Generic Mouse Mode is Windows-only, disabled by default, and enabled manually in Settings. It works without a connected supported Logitech mouse and supports Middle Button, Side Button 1, and Side Button 2 with separate Click Action and Long Press Action mappings.

The application can now switch the visible UI between English and Simplified Chinese from Settings. English remains the default when no saved preference exists, and the selected language is saved and restored on the next launch.

## Highlights

- Added Generic Mouse Mode for standard Windows middle and side-button events.
- Added Middle Button support.
- Added Side Button 1 and Side Button 2 support.
- Added Click + Long Press Multi-Action support for all three generic buttons.
- Kept existing Logitech-specific controls available without duplicate middle-button or side-button entries.
- Added English / Simplified Chinese application language switching.
- Added persistent saved language preference.
- Completed the Simplified Chinese application UI.
- Replaced the corrupted Chinese README with complete Simplified Chinese documentation.

## Generic Mouse Mode Notes

- Generic Mouse Mode is Windows-only.
- It is disabled by default and enabled manually in Settings.
- It does not require a connected supported Logitech mouse.
- It supports Middle Button, Side Button 1, and Side Button 2.
- All three supported buttons support Click Action and Long Press Action.
- Multiple standard mice cannot currently have separate generic mappings because standard Windows mouse events are not distinguished by physical source device.
- Left-button remapping, right-button remapping, scroll up/down remapping, and arbitrary extra mouse buttons are not supported by Generic Mouse Mode.

## Language Notes

- Supported languages are English and Simplified Chinese.
- English remains the default when no saved preference exists.
- The selected language is saved and restored on the next launch.
- Language switching changes visible UI labels without changing internal action IDs, button keys, mappings, or profile data.
- Existing user mappings remain compatible.

## Release Policy

Windows remains the only official release target for v1.2.0.

The public GitHub Release should contain only:

- `PourInput-v1.2.0-Windows.zip`
- `pourinput-v1.2.0-update.json`

macOS and Linux CI/build validation may remain, but public macOS and Linux release packages are not part of the official v1.2.0 release.

## Validation

This release is covered by focused tests for:

- Update manifest and version metadata behavior.
- Locale manager translations.
- Configuration migration and saved language defaults.
- Backend/UI label behavior.
- Generic Mouse Mode button visibility and mapping behavior.
- Engine handling for generic middle and side-button click / long-press actions.
- Device layout behavior.

## Known Limitations

- Windows remains the only official release target.
- Generic Mouse Mode is Windows-only.
- Generic Mouse Mode supports Middle Button, Side Button 1, and Side Button 2 only.
- Generic Mouse Mode cannot currently distinguish multiple standard mice by physical source device.
- Device support still depends on firmware, operating system exposure, and HID++ features.
- Some devices may be detected but expose only partial controls.
- Double Click is planned but not implemented yet.
- Long Press timeout defaults to 300 ms and is not editable in the UI yet.
- Macro support and sequential actions are not implemented yet.
