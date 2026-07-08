<p align="center">
  <img src="images/logo.png" alt="PourInput logo" width="96">
</p>

# PourInput

**One Button. Two Actions.**

[![CI](https://github.com/pour-soi/PourInput/actions/workflows/ci.yml/badge.svg)](https://github.com/pour-soi/PourInput/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/pour-soi/PourInput?sort=semver)](https://github.com/pour-soi/PourInput/releases)
[![License](https://img.shields.io/github/license/pour-soi/PourInput)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](requirements.txt)

PourInput is an open-source fork of [TomBadash/Mouser](https://github.com/TomBadash/Mouser) that adds a generic Multi-Action Button framework for Logitech HID++ mice.

Supported mouse buttons can have independent **Click Action** and **Long Press Action** mappings. For example, one button can take a screenshot when clicked and switch scroll mode when held.

Current release: `v1.0.0`

Repository: `pour-soi/PourInput`

## Why PourInput?

Logitech mice often expose useful extra controls, but not every workflow fits a single action per button. PourInput solves that by making each supported button behave like two configurable controls:

- **Click** for the fast action you use constantly.
- **Long Press** for the secondary action you still want nearby.

Compared with the original Mouser project, this fork focuses on reusable multi-action button handling instead of one-off button-specific timing logic. Compared with Logitech Options+, this project is open source, scriptable, reviewable, and easier to inspect when debugging HID++ behavior. It does not replace every Options+ feature; it is a focused tool for configurable button remapping.

## Features

- Generic **Multi-Action** framework — supported buttons can perform different actions on **Click** and **Long Press**.
- **Extended button customization** — assign independent Click and Long Press actions to supported buttons, including **Mode Shift**, **Back**, and **Forward**.
- Improved **Mode Shift** handling — more reliable event detection and HID++ synchronization.
- Application-specific profiles — automatically switch button mappings for different applications.
- Pointer, scrolling, and SmartShift controls — configure supported Logitech device features.
- Built-in screenshot actions — capture the full screen or a selected region to the clipboard or a file.
- Portable Windows release — no Python installation required.

## Screenshots

### Main Window

Configure the active device, profiles, and supported button mappings from the main mouse view.

![Main Window](assets/screenshot-main.png)

### Multi-Action Configuration

Choose the action assigned to a supported Click or Long Press slot.

![Multi-Action Configuration](assets/screenshot-actions.png)

### About

Review the PourInput version, maintainer, upstream credit, build mode, commit, and launch path.

![About](assets/screenshot-about.png)

## Installation

1. Download `PourInput-v1.0.0-Windows.zip` from the [latest release](https://github.com/pour-soi/PourInput/releases/latest).
2. Extract the zip file.
3. Run `PourInput-v1.0.0/PourInput.exe`.
4. Quit any other PourInput or PourInput build before launching this one.

The packaged Windows app includes the runtime files it needs. You do not need to install Python to use a release build.

## Usage

Open the Mouse page and select a supported button.

Each supported button can show:

- **Click Action**
- **Long Press Action**

Examples:

- Back: Click -> Browser Back, Long Press -> Copy
- Forward: Click -> Browser Forward, Long Press -> Paste
- Mode Shift: Click -> Screenshot Region -> Clipboard, Long Press -> Switch Scroll Mode

A press shorter than 300 ms runs the Click Action. A press held for at least 300 ms runs the Long Press Action when released.

If no Long Press Action is configured, the button keeps the same behavior it had before the Multi-Action framework was added.

## Supported Devices

PourInput targets Logitech HID++ mice that the app can detect and control. Support depends on what each mouse exposes through HID++ and the operating system. Some controls must be reprogrammable and divertable before PourInput can intercept them.

| Device | Support |
|--------|---------|
| MX Master 3 | ✅ Supported for cataloged Multi-Action controls |
| MX Master 3S | ✅ Supported for cataloged Multi-Action controls |
| MX Anywhere 3 | ✅ Supported for cataloged controls |
| MX Vertical | ⚠️ Partial; layout and available controls differ |
| MX Master 4 / 2S / original MX Master | Depends on available HID++ features |
| MX Anywhere 3S / 2S | Depends on available HID++ features |
| Signature M650 / M650 L | Partial; no Mode Shift or horizontal scroll controls |
| G502 family | Partial; remapped at the OS level where available |
| Others | Depends on available HID++ features |

Multi-Action support is currently focused on Mode Shift, Back, and Forward where those controls are exposed. Other buttons may still be available as standard mouse events, and device-specific capabilities such as DPI, SmartShift, battery reporting, gesture controls, and horizontal scroll vary by model.

If your mouse is detected but a button is missing, open a device support request and include the device info JSON from the Mouse page.

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
.\scripts\create_release.ps1 -Version v1.0.0
```

If no version is specified, the packaging script reads the latest versioned Windows zip in `release/` and increments the patch version.

Release output:

```text
release/
    PourInput-v1.0.0-Windows.zip
    RELEASE_NOTES-v1.0.0.md
    CHANGELOG.md
```

Zip layout:

```text
PourInput-v1.0.0/
    PourInput.exe
    LICENSE
    README.md
    CHANGELOG.md
    RELEASE_NOTES.md
    all required runtime files
```

The release script removes only temporary build output before packaging. It preserves `.git`, source code, release history, settings, logs, and previous versioned releases.

## Known Limitations

- Windows is the only official release target for v1.0.0.
- PourInput is intended for Logitech HID++ devices.
- Some features depend on device firmware and exposed HID++ capabilities.
- macOS support is planned but not officially available.
- Double Click is planned but not implemented yet.
- Long Press timeout is fixed at 300 ms and is not configurable in the UI yet.
- Macro support and sequential actions are not implemented yet.

## Roadmap

### Current (v1.0.0)

- Multi-Action framework
- Click / Long Press actions
- Mode Shift improvements
- Independent PourInput branding

### Planned

- Enhanced Easy-Switch
- More customizable button actions
- Better device detection
- Configuration import/export
- macOS experimental support
- Flow-inspired multi-device features (long-term)

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
