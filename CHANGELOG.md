# Changelog

All notable changes to PourInput are documented here.

This project uses Semantic Versioning.

## Unreleased

### Documentation

- Reworked the README for a public open-source release.
- Added clearer project positioning, installation, usage, build, packaging, roadmap, known issue, and contribution guidance.
- Added repository community documents and GitHub pull request guidance.
- Updated issue templates to use PourInput naming consistently.
- Replaced stale upstream release links in the Chinese README.

## v0.1.0 - 2026-07-06

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
