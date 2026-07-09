# Changelog

All notable changes to PourInput are documented here.

This project uses Semantic Versioning.

## Unreleased

## v1.2.0 — 2026-07-09

### Added

- Generic Mouse Mode for standard Windows mouse buttons.
- Middle Button support.
- Side Button 1 and Side Button 2 support.
- Click + Long Press Multi-Action for all three generic buttons.
- Generic Mouse Mode operation without a supported Logitech mouse.
- English / Simplified Chinese application language switching.
- Persistent saved language preference.
- Complete Simplified Chinese application UI.
- Complete Simplified Chinese GitHub documentation.
- Added a Windows single-instance guard so duplicate PourInput processes cannot create competing low-level mouse hooks.

### Fixed

- Corrected Generic Mouse Mode button visibility without a Logitech connection.
- Restored correct runtime Generic Mouse Mode OFF behavior: disabling the mode removes generic mouse callbacks and blocking, returning buttons to native middle-click and Back / Forward behavior.
- Prevented stale XBUTTON interception after Generic Mouse Mode is disabled.
- Corrected Generic Mouse Mode CI regression coverage across platforms.

## v1.1.0 - 2026-07-08

### Changed

- Added the capability-based device support architecture so runtime HID++ evidence can enable or limit device features more safely.
- Documented the capability-based device support architecture, including HID++-detected feature enablement and the distinction between tested and experimental devices.

### Documentation

- Polished the README for the first official PourInput release.
- Added clearer screenshots, supported devices, roadmap, and credits sections.
- Replaced the corrupted Chinese README text with a readable PourInput overview.
- Refined repository presentation with logo placement, release badges, screenshot captions, support tables, and clearer known limitations.

## v1.0.0 - 2026-07-08

### Added

- Published the first official PourInput release.
- Promoted the Windows release package to `PourInput-v1.0.0-Windows.zip`.
- Updated application, updater, installer, package, and executable metadata to version 1.0.0.

### Documentation

- Reworked the README for a public open-source release.
- Added clearer project positioning, installation, usage, build, packaging, roadmap, known issue, and contribution guidance.
- Added repository community documents and GitHub pull request guidance.
- Updated issue templates to use PourInput naming consistently.
- Replaced stale upstream release links in the Chinese README.

## Initial Development Release - 2026-07-06

### Added

- Added generic Multi-Action Button framework.
- Added Click and Long Press support.
- Added Mode Shift Click and Long Press support.
- Added Back Button Click and Long Press support.
- Added Forward Button Click and Long Press support.
- Added generic dispatcher shared by supported multi-action buttons.
- Added config migration for long-press mappings and default 300 ms threshold.
- Added UI sections for Click Action and Long Press Action.
- Added versioned Windows release packaging.
- Added release notes and open-source release documentation.
- Standardized project metadata as PourInput.
- Set release repository metadata to pour-soi/PourInput.

### Fixed

- Improved HID diversion synchronization for Mode Shift remapping.
- Ensured Mode Shift diversion also applies when only the long-press slot is configured.
- Replaced placeholder maintainer metadata with pour-soi.

### Known Limitations

- Double Click is not implemented yet.
- Long-press timeout is global and not editable in the UI yet.
- Per-button timeout is not implemented yet.
- Macro and sequential actions are not implemented yet.
