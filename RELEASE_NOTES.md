# PourInput v1.3.5

Release date: 2026-09-05

This Windows maintenance release protects saved mouse customizations and improves startup reliability.

## Fixed

- Preserve user mouse mappings when the existing configuration cannot be safely read or validated at startup.
- Block unverified or fallback configuration from being saved by unrelated settings and update operations.
- Isolate automated tests from the user's real configuration.
- Improve configuration validation and safe startup behavior.
- Improve input backend startup, shutdown, and recovery reliability.

## Validation

- Completed five application restart cycles and a real Windows reboot with physical mouse-button checks.
- Verified preservation of profiles and custom mappings, including buttons intentionally assigned no action.
- Verified invalid-configuration protection and settings/update save paths in isolated tests.

## Windows download

- `PourInput-v1.3.5-Windows.zip`
- `PourInput-v1.3.5-Windows.zip.sha256`
- `pourinput-v1.3.5-update.json`

ZIP SHA-256: `36033EDABCFEC79B4FEA513DB8C99C06A9509DA9EFE8B367316F7DCD93E5CB9D`

The Windows executable reports version 1.3.5 and was built from commit `b8d529033fc80bcb283520188215b8297acea474`. The release tag adds only release preparation changes. The validated archive is preserved unchanged; its bundled documentation predates these release notes. These release notes and the update manifest describe v1.3.5.
