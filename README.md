<p align="center">
  <img src="images/logo.png" alt="PourInput logo" width="420">
</p>

# PourInput

**One Button. Two Actions.**

**English** | [简体中文](README_CN.md)

PourInput is an independent Windows input customization application that lets users configure flexible mouse button behaviors, including short-press and long-press actions. It provides clear, local, and device-aware control without depending on proprietary device software.

<p>
  <a href="https://github.com/pour-soi/PourInput/releases/download/v1.3.0/PourInput-v1.3.0-Windows.zip">
    <img src="https://img.shields.io/badge/Download_for_Windows-v1.3.0-0078D4?style=for-the-badge&logo=windows11&logoColor=white" alt="Download for Windows">
  </a>
  <a href="https://github.com/pour-soi/PourInput/releases/tag/v1.3.0">
    <img src="https://img.shields.io/badge/Release_Notes-v1.3.0-555555?style=for-the-badge" alt="Release Notes">
  </a>
</p>

Latest: `v1.3.0` · Windows

[![CI](https://github.com/pour-soi/PourInput/actions/workflows/ci.yml/badge.svg)](https://github.com/pour-soi/PourInput/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/pour-soi/PourInput?sort=semver)](https://github.com/pour-soi/PourInput/releases)
[![License](https://img.shields.io/github/license/pour-soi/PourInput)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](requirements.txt)

## Why PourInput?

Many mice expose useful extra controls, but not every workflow fits one fixed action per button. PourInput lets supported mouse buttons do different things depending on how they are used.

Multi-Action currently supports separate Click Action and Long Press Action mappings. For example, one side button can copy text when clicked and run Browser Forward when held.

Generic Mouse Mode lets standard Windows middle and side-button events use PourInput actions without requiring Logitech HID++ support or a connected supported Logitech mouse.

PourInput does not replace every Logitech Options+ feature. It is a focused, open-source tool for configurable button remapping and advanced button actions.

## Features

- **Multi-Action click / long-press support** - supported buttons can run one action when clicked and another action when held.
- **Generic Mouse Mode** - Middle Button, Side Button 1, and Side Button 2 can be mapped through standard Windows mouse events without Logitech HID++.
- **Runtime Generic Mouse Mode switching** - the mode is disabled by default, can be enabled in Settings, and returns supported buttons to native behavior when disabled.
- **Logitech controls remain available** - supported Logitech controls continue to work, and Generic Mouse Mode does not create duplicate middle-button or side-button entries.
- **English / Simplified Chinese UI switching** - users can change the visible application language from Settings.
- **Saved language preference** - English is the default when no preference exists; the selected language is saved and restored on the next launch.
- **Compatible mappings and profiles** - language switching changes visible labels only and does not rewrite action IDs, button keys, mappings, or profile data.
- **Capability-based device support foundations** - PourInput enables features according to what a device exposes instead of relying only on a static brand list.
- **Logitech HID++ advanced features where supported** - supported Logitech devices may expose Mode Shift, SmartShift, adjustable DPI, battery reporting, gesture controls, and horizontal scroll.
- **Application-specific profiles** - automatically switch button mappings for different applications.
- **Built-in screenshot actions** - capture the full screen or a selected region to the clipboard or a file.
- **Portable Windows release** - packaged builds do not require a separate Python installation.

## Screenshots

| Mouse & Profiles | General Settings |
|---|---|
| ![PourInput Mouse and Profiles page in English light mode](images/Screenshot_mouse.png) | ![PourInput General Settings page in Simplified Chinese light mode](images/Screenshot_settings.png) |

![PourInput Generic Mouse Mode page in Simplified Chinese light mode](images/Screenshot.png)

## How It Works

Open the Mouse page and choose a supported button. Each supported Multi-Action button can show:

- **Click Action**
- **Long Press Action**

Examples:

- Middle Button: Click -> Copy, Long Press -> Paste
- Side Button 1: Click -> Copy, Long Press -> Browser Forward
- Side Button 2: Click -> Paste, Long Press -> Browser Back
- Mode Shift on a supported Logitech device: Click -> Screenshot Region -> Clipboard, Long Press -> Switch Scroll Mode

A press shorter than 300 ms runs the Click Action. A press held for at least 300 ms runs the Long Press Action when released.

If no Long Press Action is configured, the button keeps the same behavior it had before the Multi-Action framework was added.

## Generic Mouse Mode

Generic Mouse Mode supports these standard Windows mouse buttons:

| Button | Supported slots |
|--------|-----------------|
| Middle Button | Click Action, Long Press Action |
| Side Button 1 | Click Action, Long Press Action |
| Side Button 2 | Click Action, Long Press Action |

Generic Mouse Mode is Windows-only. It is disabled by default and must be enabled manually in Settings.

The mode works without a connected supported Logitech mouse. It listens for standard Windows middle-button and side-button events, then dispatches the configured PourInput Click Action or Long Press Action.

Existing Logitech-specific controls remain available. When Generic Mouse Mode is enabled while a supported Logitech mouse is connected, PourInput avoids duplicate middle-button or side-button entries.

Multiple standard mice cannot currently have separate generic mappings because standard Windows mouse events are not distinguished by physical source device.

Generic Mouse Mode does not support left-button remapping, right-button remapping, scroll up/down remapping, arbitrary extra mouse buttons, or vendor-specific buttons that do not appear as standard Windows mouse events.

## Download & Installation

Current version: `v1.3.0`

Windows users should download:

```text
PourInput-v1.3.0-Windows.zip
```

Direct download:
[PourInput-v1.3.0-Windows.zip](https://github.com/pour-soi/PourInput/releases/download/v1.3.0/PourInput-v1.3.0-Windows.zip)

Release notes:
[v1.3.0 — PourInput Visual System](https://github.com/pour-soi/PourInput/releases/tag/v1.3.0)

Installation:

1. Download `PourInput-v1.3.0-Windows.zip`.
2. Extract the zip file.
3. Run `PourInput-v1.3.0/PourInput.exe`.
4. Quit any other PourInput or PourInput build before launching this one.

The packaged Windows app includes the runtime files it needs. You do not need to install Python to use a release build.

On first launch, PourInput creates its configuration automatically. English is used by default unless a saved language preference already exists.

## Platform Support

Windows is the only official public release target for v1.3.0.

The public GitHub Release should contain only:

- `PourInput-v1.3.0-Windows.zip`
- `PourInput-v1.3.0-Windows.zip.sha256`
- `pourinput-v1.3.0-update.json`

macOS support is planned but not officially available. Linux support remains validation-only and is not an official public release target.

## Device Support

PourInput uses capability-based device support. It enables features according to what a device can actually do rather than treating support as a simple brand-based yes/no list.

A mouse with standard Windows middle and side buttons can use Generic Mouse Mode. A supported Logitech device may expose additional HID++ features.

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

## Limitations

- Generic Mouse Mode currently supports only Middle Button, Side Button 1, and Side Button 2.
- Generic Mouse Mode does not identify separate standard mice per physical device yet.
- Some Logitech features depend on device firmware and exposed HID++ capabilities.
- Double Click is planned but not implemented yet.
- Long Press timeout is fixed at 300 ms and is not configurable in the UI yet.
- Macro support and sequential actions are not implemented yet.

## Troubleshooting

- If PourInput does not start, make sure the archive was extracted before running `PourInput.exe`.
- If a standard mouse button is missing, confirm that Generic Mouse Mode is enabled in Settings.
- If native middle-click or browser Back / Forward does not return, turn Generic Mouse Mode off and restart PourInput.
- If a Logitech button is missing, the device may not expose the required HID++ capability. Open a device support request with the device info JSON from the Mouse page.
- If the application language does not match your choice, open Settings, select the language again, and restart PourInput.

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

## Development

Start with the [architecture overview](docs/ARCHITECTURE.md) for runtime structure and the [Pour product-family design system](docs/POUR_DESIGN_SYSTEM.md) for design and visual-release guidance.

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

Create a versioned Windows release package:

```powershell
.\scripts\create_release.ps1 -Version v1.3.0
```

The release script writes versioned output under `release/` and preserves `.git`, source code, release history, settings, logs, and previous versioned releases.

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

Historical acknowledgement: early PourInput development incorporated work from the [Mouser](https://github.com/TomBadash/Mouser) project. PourInput is now independently designed, maintained, configured, and released; Mouser is not required to run it.

Maintainer: `pour-soi`

## License

PourInput is licensed under the MIT License. Copyright and attribution notices are preserved in [LICENSE](LICENSE).
