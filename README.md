<p align="center">
  <img src="images/logo.png" alt="PourInput" width="180">
</p>

# PourInput

### Your mouse. Your controls.

**English** · [简体中文](README_CN.md)

PourInput is a mouse customization app. Assign actions to supported buttons, give clicks and long presses different roles, and switch mappings automatically for each application. Keep control of your mouse with settings saved locally.

[**Download for Windows · v1.4.2**](https://github.com/pour-soi/PourInput/releases/download/v1.4.2/PourInput-v1.4.2-Windows.zip)

[What's new](https://github.com/pour-soi/PourInput/releases/tag/v1.4.2) · [macOS edition](#macos-edition) · [Report a problem](https://github.com/pour-soi/PourInput/issues)

![PourInput mouse button and application profile configuration](images/Screenshot_mouse_en.png)

**Button mapping · Click and Long Press · Application profiles · MX Master controls**

## Put your everyday actions on your mouse

Map supported buttons to copying, pasting, browser navigation, tab switching, screenshots, and other built-in actions. Choose the behavior for each button from the mouse page and keep your most-used commands within reach.

### One button, two actions

Assign separate **Click** and **Long Press** actions to the same supported button. A quick press can copy; a long press can paste. Choose the combination that fits your workflow.

### Different apps, different mappings

Create application profiles so the same button can perform different actions in your browser, editor, or other software. PourInput selects the appropriate profile as you switch applications. Keep a default profile for everything else.

### Standard mice, too

**Generic Mouse Mode** handles standard Windows middle and side buttons, including mice such as ZOWIE. It does not require a supported Logitech device.

![Generic Mouse Mode button configuration](images/Screenshot_generic_en.png)

### Keep your MX Master enhancements

Supported HID++ controls can provide gestures, Mode Shift, SmartShift, DPI adjustment, battery information, and horizontal scrolling. Available controls depend on the device and firmware.

Generic Mouse Mode and MX enhancements work together. Generic owns the standard inputs it supports while enabled; non-overlapping MX controls remain available. A Generic mapping set to “none” stays inactive instead of falling back to an MX action. Turning Generic off restores device-specific routing, with saved mappings retained.

## Set it up your way

1. Open the mouse page and select a supported button.
2. Choose its Click Action and, if needed, a Long Press Action.
3. Add an application profile for software that needs different mappings.
4. For standard middle and side buttons, enable Generic Mouse Mode as needed.

Switch the interface between English and Simplified Chinese without changing saved mappings. Settings stay on your computer.

## Also included: Reading Mode on Windows

Reading Mode is an optional feature alongside mouse customization. Import a local TXT or EPUB into a floating panel, navigate with the wheel, or enable smooth automatic scrolling with speed and pause controls. Customize the panel's size, text, and transparency.

Reading OFF restores ordinary scrolling. Reading ON temporarily uses the vertical wheel for the reader without changing saved mouse mappings. Hold-to-hide pauses automatic movement and resumes it on release; the configured mouse hide button returns to its usual action when reading is off.

<details>
<summary>Reading screenshot and usage details</summary>

![Reading overlay with sample text](images/Screenshot_reading_panel_en.png)

Open the book icon in the left sidebar, import a document, then enable Reading Mode. Use **Start / resume auto-scroll** or **Pause auto-scroll** on the Reading page. Playback stops at the end and restarts paused at the saved position when the app is reopened.

Normal, Minimal, and Ghost display modes are available. The panel stays on top without taking focus; Minimal and Ghost allow clicks through the text area. While temporarily hidden, Reading Mode still owns the wheel. Mouse hide buttons are exclusive while reading; keyboard hide keys retain their normal keyboard action.

Documents and reading position are stored separately from mouse profiles. The screenshot uses the actual interface with sample text. See the [Reading Mode guide](docs/READING_MODE.md) for more details.

</details>

## Get started on Windows

[**Download PourInput v1.4.2 for Windows**](https://github.com/pour-soi/PourInput/releases/download/v1.4.2/PourInput-v1.4.2-Windows.zip)

1. Extract the **entire ZIP** to a short path, such as `F:\Apps`. Do not run the app inside the ZIP or skip files if extraction fails.
2. Quit any older PourInput instance from its **system tray menu**. Closing the settings window only hides it.
3. Open `PourInput/PourInput.exe`. No separate Python installation is needed.
4. To customize buttons, open the mouse page and select a button.
5. Add application profiles and enable Generic Mouse Mode if you want to customize standard middle and side buttons.

The Windows executable is unsigned. Downloads include a SHA-256 checksum and an update manifest on the [release page](https://github.com/pour-soi/PourInput/releases/tag/v1.4.2).

## Device and platform notes

**Windows hardware validation:** MX Master 4 and a ZOWIE mouse were used to validate reading, wheel ownership, and hold-to-hide workflows. Earlier testing also covered MX Master 3 controls. This does not mean every feature is available on every model or firmware.

Generic Mouse Mode currently maps the middle button and two side buttons. It cannot distinguish multiple standard mice by physical device, and it does not offer general left/right-button or vertical-wheel remapping. Reading's wheel override is a separate feature.

Other Logitech models may work when they expose the required HID++ controls. If a device is detected but a control is missing, include the device information exported from the mouse page in a [device support request](https://github.com/pour-soi/PourInput/issues).

### macOS edition

The separate macOS release is **v1.3.4-macos.1**. The Windows reading and automatic scrolling features shown above are not included in that release.

[Apple Silicon download](https://github.com/pour-soi/PourInput/releases/download/v1.3.4-macos.1/PourInput-1.3.4-macOS-arm64.zip) · [Intel download](https://github.com/pour-soi/PourInput/releases/download/v1.3.4-macos.1/PourInput-1.3.4-macOS-x86_64.zip) · [macOS release notes](https://github.com/pour-soi/PourInput/releases/tag/v1.3.4-macos.1)

Extract the matching package, open `PourInput.app`, and grant Accessibility permission when prompted. This build is unsigned and unnotarized. Intel hardware testing used a MacBook Air and MX Master 3; Apple Silicon has build validation only. Generic Mouse Mode is Windows-only. Linux remains validation-only.

## Quick help

**A button performs an unexpected action?** Check the active application profile, Generic Mouse Mode, and whether that button is selected as the reader's hide button.

**Extraction reports “path too long”?** Cancel and extract to a shorter path. Do not skip the failed files.

**The app seems not to open?** Check the system tray for an already running copy. Quit it before opening another version.

## Development and contribution

Start with the [development guide](DEVELOPMENT.md), [architecture overview](docs/ARCHITECTURE.md), and [Reading Mode notes](docs/READING_MODE.md). For contributions, see [CONTRIBUTING.md](CONTRIBUTING.md) and [device support guidance](CONTRIBUTING_DEVICES.md).

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main_qml.py
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Maintained by **pour-soi**. Early development used work from [Mouser](https://github.com/TomBadash/Mouser); PourInput is independently maintained and does not require Mouser to run.

[MIT license](LICENSE) · [Changelog](CHANGELOG.md) · [Issues](https://github.com/pour-soi/PourInput/issues)
