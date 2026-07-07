# Mouser Multi-Action

**One Button. Two Actions.**

[![CI](https://github.com/pour-soi/Mouser-Multi-Action/actions/workflows/ci.yml/badge.svg)](https://github.com/pour-soi/Mouser-Multi-Action/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/pour-soi/Mouser-Multi-Action?sort=semver)](https://github.com/pour-soi/Mouser-Multi-Action/releases)
[![License](https://img.shields.io/github/license/pour-soi/Mouser-Multi-Action)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](requirements.txt)

Mouser Multi-Action is an open-source fork of [TomBadash/Mouser](https://github.com/TomBadash/Mouser) that adds a generic Multi-Action Button framework for Logitech HID++ mice.

Supported mouse buttons can have independent **Click Action** and **Long Press Action** mappings. For example, one button can take a screenshot when clicked and switch scroll mode when held.

Current release: `v0.1.0`

Repository: `pour-soi/Mouser-Multi-Action`

## Why Mouser Multi-Action?

Logitech mice often expose useful extra controls, but not every workflow fits a single action per button. Mouser Multi-Action solves that by making each supported button behave like two configurable controls:

- **Click** for the fast action you use constantly.
- **Long Press** for the secondary action you still want nearby.

Compared with the original Mouser project, this fork focuses on reusable multi-action button handling instead of one-off button-specific timing logic. Compared with Logitech Options+, this project is open source, scriptable, reviewable, and easier to inspect when debugging HID++ behavior. It does not replace every Options+ feature; it is a focused tool for configurable button remapping.

## Features

- Generic Multi-Action Button framework.
- One reusable dispatcher for supported buttons.
- Independent Click and Long Press mappings.
- Default Long Press threshold of 300 ms.
- Back, Forward, and Mode Shift support in the first release.
- Configuration migration for existing profiles.
- UI fields for Click Action and Long Press Action.
- HID++ diversion synchronization for Mode Shift remapping.
- Windows release packaging with versioned release artifacts.

## Screenshots

Screenshots will be added in a future release.

Suggested screenshots:

- Mouse page with a supported button selected.
- Click Action and Long Press Action fields.
- Mode Shift configured with screenshot on Click and scroll mode on Long Press.
- About dialog showing version and commit metadata.

## Installation

1. Download `Mouser-Multi-Action-v0.1.0-Windows.zip` from the [latest release](https://github.com/pour-soi/Mouser-Multi-Action/releases/latest).
2. Extract the zip file.
3. Run `Mouser-Multi-Action-v0.1.0/Mouser.exe`.
4. Quit any other Mouser or Mouser Multi-Action build before launching this one.

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

Mouser Multi-Action targets Logitech HID++ mice that the app can detect and control.

Multi-Action support is currently enabled for:

- Mode Shift
- Back Button
- Forward Button

Device support depends on what the mouse exposes through HID++. Some controls must be reprogrammable and divertable before Mouser Multi-Action can intercept them. If your mouse is detected but a button is missing, open a device support request and include the device info JSON from the Mouse page.

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
.\.venv\Scripts\python.exe -m PyInstaller Mouser.spec --noconfirm
```

Raw build output is written to `dist/Mouser/`.

## Packaging

Create a versioned Windows release package:

```powershell
.\scripts\create_release.ps1 -Version v0.1.0
```

If no version is specified, the packaging script reads the latest versioned Windows zip in `release/` and increments the patch version.

Release output:

```text
release/
    Mouser-Multi-Action-v0.1.0-Windows.zip
    RELEASE_NOTES-v0.1.0.md
    CHANGELOG.md
```

Zip layout:

```text
Mouser-Multi-Action-v0.1.0/
    Mouser.exe
    LICENSE
    README.md
    CHANGELOG.md
    RELEASE_NOTES.md
    all required runtime files
```

The release script removes only temporary build output before packaging. It preserves `.git`, source code, release history, settings, logs, and previous versioned releases.

## Roadmap

### v0.2.0

- Double Click support.
- Custom Long Press timeout.

### v0.3.0

- Per-button timeout.
- Export and import configuration.

### v0.4.0

- Macro support.
- Sequential actions.

### v1.0.0

- Stable release.

## Known Issues

- Double Click is planned but not implemented yet.
- Long Press timeout is fixed at 300 ms and is not configurable in the UI yet.
- Timeout is global, not per button.
- Macro support and sequential actions are not implemented yet.
- Logitech Options+ can conflict with Mouser Multi-Action because both tools may need HID++ access.
- Device support depends on each mouse exposing compatible HID++ controls.

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

## Acknowledgements

Mouser Multi-Action is based on [TomBadash/Mouser](https://github.com/TomBadash/Mouser). The original project made the foundation for this fork possible.

Maintainer: `pour-soi`

## License

This project keeps the original Mouser license. See [LICENSE](LICENSE).
