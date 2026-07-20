# PourInput v1.3.4

Release date: 2026-07-19

Repository: `pour-soi/PourInput`

## Highlights

PourInput v1.3.4 completes the device-specific MX Master 3 Back and Forward path on Windows, including native-event suppression, reliable physical-hold state, and packaged screenshot clipboard delivery.

## Fixed

- Fixed MX Master 3 Back and Forward mappings still allowing native browser navigation.
- Added targeted suppression of matching Windows XBUTTON events while preserving Generic Mouse Mode separation.
- Fixed transient HID++ empty-state reports splitting one physical hold into multiple logical presses.
- Physical release is now confirmed using the matching Windows XBUTTON UP event.
- Fixed full-screen screenshot-to-clipboard delivery in packaged Windows builds using durable native `CF_DIB`.
- Prevented duplicate screenshot actions during a continuous side-button hold.
- Improved persistent diagnostics for HID++, suppression, action execution, screenshot capture, and clipboard delivery.

## Hardware validation

- Verified with a real Logitech MX Master 3 connected over Bluetooth with Generic Mouse Mode disabled.
- Confirmed Back CID `0x0053` and Forward CID `0x0056` reach their independent selected actions while matching native browser events remain suppressed.
- Confirmed a continuous Forward hold produces one logical DOWN, one action, no premature release, and one logical UP after the matching Windows XBUTTON UP.
- Confirmed full-screen screenshots remain available as native `CF_DIB` clipboard data and paste successfully into Paint.
- Logitech receiver transport has not yet been validated.
- Logitech Options and Options+ coexistence has not yet been validated.

## Compatibility

- Windows remains the only official public release target.
- Existing profiles, configuration storage, input timing, supported devices, and updater behavior remain compatible.
- Generic Mouse Mode continues to support Middle Button, Side Button 1 (Back), and Side Button 2 (Forward).

## Checksums

The official Windows ZIP SHA-256 is provided in `PourInput-v1.3.4-Windows.zip.sha256` and in `pourinput-v1.3.4-update.json`.
