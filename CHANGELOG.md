# Changelog

All notable changes to PourInput are documented here.

This project uses Semantic Versioning.

## Unreleased

## v1.3.4 - 2026-07-19

### Fixed

- Fixed MX Master 3 Back and Forward mappings still allowing native browser navigation.
- Added targeted suppression of matching Windows XBUTTON events while preserving Generic Mouse Mode separation.
- Fixed transient HID++ empty-state reports splitting one physical hold into multiple logical presses.
- Physical release is now confirmed using the matching Windows XBUTTON UP event.
- Fixed full-screen screenshot-to-clipboard delivery in packaged Windows builds using durable native `CF_DIB`.
- Prevented duplicate screenshot actions during a continuous side-button hold.
- Improved persistent diagnostics for HID++, suppression, action execution, screenshot capture, and clipboard delivery.

### Validation

- Verified with a real Logitech MX Master 3 connected over Bluetooth and Generic Mouse Mode disabled.
- Confirmed native Back/Forward suppression, immediate mapping execution, durable screenshot clipboard delivery, and correlated physical release in a packaged Windows build.

## v1.3.3 - 2026-07-19

### Fixed

- Fixed MX Master 3 Back and Forward shortcut changes not taking effect.
- Added dedicated Logitech HID++ routes for Back CID `0x0053` and Forward CID `0x0056`.
- Fixed a reconnect loop caused by adding and removing side-button HID++ diverts during connection refresh.
- Kept MX Master 3 device-specific mappings separate from Generic Mouse Mode.
- Side-button mappings now apply immediately, remain profile-specific, and persist after restart.

### Validation

- Verified with a real Logitech MX Master 3 connected over Bluetooth.
- Confirmed stable HID++ diversion and independent Back and Forward action execution with Generic Mouse Mode disabled.

## v1.3.2 - 2026-07-17

### Fixed

- Fixed MX Master 3 side-button mappings in Generic Mouse Mode.
- Fixed the UI/runtime XBUTTON namespace mismatch that could save a mapping outside the active Generic Mouse Mode route.
- Fixed QML focus restoration when reopening the main window from the system tray.
- Fixed a missing Qt `Slot` import that prevented the application from starting.

### Improved

- Hardened Windows XBUTTON routing around immutable binding generations, dispatch leases, and retirement synchronization.
- Improved queue-overflow lifecycle handling and isolated multi-action press state across route and generation changes.
- Improved shutdown behavior for hook workers and retired callbacks.
- Improved locale-aware font fallback while preserving platform-appropriate system fonts.

### Validation

- Verified with a real Logitech MX Master 3 connected over Bluetooth.
- Logitech receiver transport remains to be validated.
- Logitech Options and Options+ coexistence remains to be validated.

## v1.3.1 - 2026-07-15

### Fixed

- Fixed Generic Mouse localization refresh after language switching.
- Corrected Side Button 1 (Back) and Side Button 2 (Forward) presentation labels.
- Fixed several remaining localized presentation labels.
- Improved localization consistency across the interface.

### Documentation

- Improved GitHub repository homepage.
- Added dedicated English and Simplified Chinese screenshots.
- Updated screenshot documentation and packaging references.

## v1.3.0 - 2026-07-14

### Changed

- Redesigned the desktop interface around a consistent PourInput visual system while preserving existing input and mapping behavior.
- Replaced legacy application identity artwork with finalized PourInput branding across Windows, macOS, Linux, the tray, and repository presentation.
- Refined navigation, profiles, settings, controls, spacing, typography, light/dark themes, and high-DPI presentation.

### Documentation

- Added the Pour product-family design system, component reference, brand asset guidelines, screenshot standards, and release visual checklist.
- Added architecture, event flow, profile, mapping, settings, state-management, QML, and project-structure references.
- Simplified and aligned the English and Simplified Chinese README homepages and download instructions.

## v1.2.1 — 2026-07-09

### Fixed

- Corrected the device status shown when Generic Mouse Mode is active without a supported Logitech mouse.
- Added distinct status states for Logitech connection, Generic Mouse Mode readiness, and no supported mouse detected.
- Kept Logitech connection state separate from Generic Mouse Mode readiness.

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
