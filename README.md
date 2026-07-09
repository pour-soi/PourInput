<p align="center">
  <img src="images/logo.png" alt="PourInput logo" width="96">
</p>

# PourInput

**One Button. Two Actions.**

🌐 **English** | [简体中文](README_CN.md)

[![CI](https://github.com/pour-soi/PourInput/actions/workflows/ci.yml/badge.svg)](https://github.com/pour-soi/PourInput/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/pour-soi/PourInput?sort=semver)](https://github.com/pour-soi/PourInput/releases)
[![License](https://img.shields.io/github/license/pour-soi/PourInput)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](requirements.txt)

PourInput is an open-source mouse customization platform for advanced button actions and multi-action input.

Originally developed from [Mouser](https://github.com/TomBadash/Mouser), PourInput has evolved with its own Multi-Action system, capability-based device support, Generic Mouse Mode, English / Simplified Chinese UI switching, and independent roadmap.

Repository: `pour-soi/PourInput`

## Current Release

Current release: `v1.2.1`

Release date: `2026-07-09`

Release title: `v1.2.1 — Generic Mouse Status Fix`

Windows is the only officially released platform for v1.2.1. Public GitHub Release assets are limited to the Windows release package and the update manifest.

## Why PourInput?

Many mice expose useful extra controls, but not every workflow fits a single action per button. PourInput focuses on making supported mouse buttons more useful without hiding how the input path works.

Multi-Action allows one physical mouse button to perform different actions depending on how it is used. PourInput currently supports separate actions for Click Action and Long Press Action. For example, one side button can copy text when clicked and run Browser Forward when held.

Generic Mouse Mode allows standard Windows mouse middle and side buttons to use PourInput actions without requiring Logitech HID++ support or a connected supported Logitech mouse. Supported buttons can use different actions for click and long press, and disabling the mode restores their native middle-click and Back / Forward behavior.

Compared with Logitech Options+, PourInput is open source, scriptable, reviewable, and easier to inspect when debugging input behavior. It does not replace every Options+ feature; it is a focused tool for configurable button remapping and advanced button actions.

## Features

- **Multi-Action click / long-press support** - supported buttons can run one action when clicked and another action when held.
- **Generic Mouse Mode for standard Windows buttons** - Middle Button, Side Button 1, and Side Button 2 can be mapped to PourInput actions without Logitech HID++.
- **Generic Mouse Mode without a supported Logitech mouse** - the mode can expose supported standard mouse buttons even when no supported Logitech device is connected.
- **Runtime Generic Mouse Mode switching** - the mode is disabled by default, can be enabled manually in Settings, and returns supported buttons to native behavior when disabled.
- **Logitech controls remain available** - existing Logitech-specific controls continue to be available, and a supported Logitech mouse plus Generic Mouse Mode does not create duplicate middle-button or side-button entries.
- **English / Simplified Chinese application language switching** - users can change the visible UI language from Settings.
- **Saved language preference** - English is the default when no preference exists; the selected language is saved and restored on the next launch.
- **Compatible mappings and profiles** - language switching changes visible labels without changing internal action IDs, button keys, mappings, or profile data.
- **Capability-based device support foundations** - PourInput enables features according to what a device can actually do, rather than treating support as a simple brand-based yes/no list.
- **Logitech HID++ advanced features where supported** - supported Logitech devices may expose extra controls such as Mode Shift, SmartShift, adjustable DPI, battery reporting, gesture controls, and horizontal scroll.
- **Application-specific profiles** - automatically switch button mappings for different applications.
- **Built-in screenshot actions** - capture the full screen or a selected region to the clipboard or a file.
- **Portable Windows release** - no Python installation required for packaged builds.

## Download

Download the current Windows release from the [latest release page](https://github.com/pour-soi/PourInput/releases/latest).

Windows users should download:

```text
PourInput-v1.2.1-Windows.zip
```

Extract the downloaded archive before running PourInput.

## Installation

1. Download `PourInput-v1.2.1-Windows.zip` from the [latest release](https://github.com/pour-soi/PourInput/releases/latest).
2. Extract the zip file.
3. Run `PourInput-v1.2.1/PourInput.exe`.
4. Quit any other PourInput or PourInput build before launching this one.

The packaged Windows app includes the runtime files it needs. You do not need to install Python to use a release build.

## First Run

On first launch, PourInput creates its configuration automatically. English is used by default unless a saved language preference already exists.

Open Settings to enable Generic Mouse Mode or to change the application language.

## Usage

Open the Mouse page and select a supported button.

Each supported Multi-Action button can show:

- **Click Action**
- **Long Press Action**

Examples:

- Middle Button: Click -> Copy, Long Press -> Paste
- Side Button 1: Click -> Copy, Long Press -> Browser Forward
- Side Button 2: Click -> Paste, Long Press -> Browser Back
- Mode Shift on a supported Logitech device: Click -> Screenshot Region -> Clipboard, Long Press -> Switch Scroll Mode

A press shorter than 300 ms runs the Click Action. A press held for at least 300 ms runs the Long Press Action when released.

If no Long Press Action is configured, the button keeps the same behavior it had before the Multi-Action framework was added.

## Buttons and Actions

Generic Mouse Mode supports these standard Windows mouse buttons:

| Button | Supported slots |
|--------|-----------------|
| Middle Button | Click Action, Long Press Action |
| Side Button 1 | Click Action, Long Press Action |
| Side Button 2 | Click Action, Long Press Action |

Generic Mouse Mode does not support left-button remapping, right-button remapping, scroll up/down remapping, or arbitrary extra mouse buttons.

## Generic Mouse Mode

Generic Mouse Mode is Windows-only. It is disabled by default and must be enabled manually in Settings.

The mode works without a connected supported Logitech mouse. It listens for standard Windows middle-button and side-button events, then dispatches the configured PourInput Click Action or Long Press Action for Middle Button, Side Button 1, and Side Button 2.

Existing Logitech-specific controls remain available. When Generic Mouse Mode is enabled while a supported Logitech mouse is connected, PourInput avoids duplicate middle-button or side-button entries.

Multiple standard mice cannot currently have separate generic mappings because standard Windows mouse events are not distinguished by physical source device.

This is not universal support for every mouse, every mouse button, every operating system, or vendor-specific buttons that do not appear as standard Windows mouse events.

## Application Language Switching

PourInput supports:

- English
- Simplified Chinese

English remains the default when no saved preference exists. Users can change the language from Settings, and the selected language is saved and restored on the next launch.

The visible application UI switches language without changing internal action IDs, button keys, mappings, or profile data. Existing user mappings remain compatible.

## Supported Devices

PourInput uses capability-based device support. This means that PourInput enables features according to what a device can actually do, rather than treating support as a simple brand-based yes/no list. A mouse with standard Windows middle and side buttons can use Generic Mouse Mode, while a supported Logitech device may expose additional HID++ features.

Some Logitech controls must be both reprogrammable and divertable before PourInput can intercept them. If capability information is missing or incomplete, PourInput falls back conservatively to the existing catalog and generic button behavior rather than assuming full support.

### Tested Devices

| Device | Status |
|--------|--------|
| ZOWIE mouse with standard Windows middle and side buttons | Manually verified with Generic Mouse Mode on Windows |
| MX Master 3 | Tested for cataloged Multi-Action controls and HID++ capability detection |

### Experimental / Potentially Compatible

These devices are not claimed as officially supported unless they have been tested with PourInput. They may work when they expose matching standard Windows middle/side-button events or HID++ capabilities.

| Device | Notes |
|--------|-------|
| Standard Windows mice with middle and side buttons | Potentially compatible with Generic Mouse Mode for middle-button and side-button click and long-press actions |
| MX Master 3S | Expected to share many MX Master capabilities; needs user/device testing |
| M720 Triathlon | Potentially compatible where required HID++ controls are exposed |
| MX Anywhere series | Potentially compatible where required HID++ controls are exposed |
| MX Master 4 / 2S / original MX Master | Potentially compatible where required HID++ controls are exposed |
| Other Logitech HID++ devices | Potentially compatible when they expose matching reprogrammable, divertable controls |

Multi-Action support is available for Generic Mouse Mode middle/side buttons and for supported Logitech controls where those controls are exposed. Device-specific capabilities such as DPI, SmartShift, battery reporting, gesture controls, and horizontal scroll vary by device and firmware.

If your mouse is detected but a button is missing, open a device support request and include the device info JSON from the Mouse page.

## Compatibility

Existing user mappings remain compatible with v1.2.1. Language switching changes visible text only; it does not rewrite action IDs, button keys, mappings, or profiles.

Generic Mouse Mode uses separate generic side-button mapping keys internally so it can coexist with supported Logitech layouts without duplicate visible side-button entries.

## Limitations

- Windows is the only official release target for v1.2.1.
- Generic Mouse Mode is Windows-only.
- Generic Mouse Mode currently supports only Middle Button, Side Button 1, and Side Button 2.
- Generic Mouse Mode does not support left-button remapping, right-button remapping, scroll up/down remapping, or arbitrary extra mouse buttons.
- Generic Mouse Mode does not identify separate standard mice per physical device yet.
- Vendor-specific buttons that do not appear as standard Windows mouse events are not supported by Generic Mouse Mode.
- Some Logitech features depend on device firmware and exposed HID++ capabilities.
- macOS support is planned but not officially available.
- Linux support remains validation-only and is not an official public release target.
- Double Click is planned but not implemented yet.
- Long Press timeout is fixed at 300 ms and is not configurable in the UI yet.
- Macro support and sequential actions are not implemented yet.

## Troubleshooting

- If PourInput does not start, make sure the archive was extracted before running `PourInput.exe`.
- If a standard mouse button is missing, confirm that Generic Mouse Mode is enabled in Settings.
- If native middle-click or browser Back / Forward does not return, turn Generic Mouse Mode off and restart PourInput.
- If a Logitech button is missing, the device may not expose the required HID++ capability. Open a device support request with the device info JSON from the Mouse page.
- If the application language does not match your choice, open Settings, select the language again, and restart PourInput.

## Building From Source

Requirements:

- Python 3.12
- Dependencies from `requirements.txt`
- PyInstaller for packaged builds

Create an environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the app from source:

```powershell
.\.venv\Scripts\python.exe main_qml.py
```

Run the test suite:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Build the Windows app:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller PourInput.spec --noconfirm
```

Raw build output is written to `dist/PourInput/`.

## Packaging

Create a versioned Windows release package:

```powershell
.\scripts\create_release.ps1 -Version v1.2.1
```

If no version is specified, the packaging script reads the latest versioned Windows zip in `release/` and increments the patch version.

Release output:

```text
release/
    PourInput-v1.2.1-Windows.zip
    RELEASE_NOTES-v1.2.1.md
    CHANGELOG.md
```

Zip layout:

```text
PourInput-v1.2.1/
    PourInput.exe
    LICENSE
    README.md
    CHANGELOG.md
    RELEASE_NOTES.md
    all required runtime files
```

The release script removes only temporary build output before packaging. It preserves `.git`, source code, release history, settings, logs, and previous versioned releases.

## Release Platform Policy

v1.2.1 remains officially Windows-only.

The public GitHub Release should contain only:

- `PourInput-v1.2.1-Windows.zip`
- `pourinput-v1.2.1-update.json`

macOS and Linux CI/build validation may remain, but public macOS and Linux release packages are not part of the v1.2.1 official release.

## Roadmap

### Completed

- **Multi-Action click / long-press support** - one supported physical button can run different actions for click and long press.
- **Generic Mouse Mode** - standard Windows Middle Button, Side Button 1, and Side Button 2 can use PourInput actions without Logitech HID++, and turning the mode off restores native middle-click and Back / Forward behavior.
- **Application language switching** - the visible UI can switch between English and Simplified Chinese without changing saved mappings.
- **Capability-based device support foundations** - PourInput can enable or limit features according to detected device capabilities instead of relying only on a static device list.

### Planned / Future Directions

Future development is focused on Enhanced Easy-Switch, Action Layers, and more advanced multi-action workflows.

- **Enhanced Easy-Switch** - Easy-Switch is Logitech's device-switching feature that allows supported mice to move between paired computers or devices. Enhanced Easy-Switch is a planned PourInput direction intended to make switching between connected computers more convenient than relying only on the mouse's original device-switching method. It may also become a foundation for future cross-device workflows.
- **Action Layers** - Action Layers would allow the same physical mouse buttons to perform different actions in different layers, increasing the number of functions available from a limited number of buttons.
- **Advanced Multi-Action** - Advanced Multi-Action is a future direction for expanding beyond the current click and long-press model into richer button interactions and action workflows.

These are development directions, not guaranteed release commitments or fixed deadlines.

## Contributing

Contributions are welcome. Good first contributions include documentation polish, tests, device support data, and focused bug fixes.

Before opening a pull request:

1. Keep behavior changes small and well tested.
2. Run `python -m unittest discover -s tests`.
3. Include device info JSON when changing mouse support.
4. Update documentation when changing user-visible behavior.

To add another Multi-Action button in the future:

1. Add the button key to the Multi-Action button configuration.
2. Ensure the button has down and up events.
3. Add a default Long Press mapping.
4. Expose the button through the backend capability data.
5. Add focused engine, config, backend, and UI tests.

See [CONTRIBUTING.md](CONTRIBUTING.md), [CONTRIBUTING_DEVICES.md](CONTRIBUTING_DEVICES.md), and [DEVELOPMENT.md](DEVELOPMENT.md) for more detail.

## Credits

PourInput is based on the original [Mouser](https://github.com/TomBadash/Mouser) project. Many thanks to the Mouser contributors for creating the foundation that made this project possible.

PourInput continues development independently while respecting and acknowledging the original project.

Maintainer: `pour-soi`

## License

This project keeps the original Mouser license. See [LICENSE](LICENSE).
