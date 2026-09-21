<p align="center">
  <img src="images/logo.png" alt="PourInput" width="180">
</p>

# PourInput

### Make your mouse more useful. Read at your own pace.

**English** · [简体中文](README_CN.md)

Customize your mouse buttons and keep a book within reach. PourInput brings application-specific shortcuts and a floating reader to your Windows desktop, with local TXT / EPUB import and smooth automatic scrolling.

[**Download for Windows · v1.4.2**](https://github.com/pour-soi/PourInput/releases/download/v1.4.2/PourInput-v1.4.2-Windows.zip)

[What's new](https://github.com/pour-soi/PourInput/releases/tag/v1.4.2) · [macOS edition](#macos-edition) · [Report a problem](https://github.com/pour-soi/PourInput/issues)

![PourInput floating reader with continuous scrolling](images/Screenshot_reading_panel_en.png)

**Mouse shortcuts · Continuous reading · Your settings, saved locally**

## A reader that stays with you

Open a local TXT or EPUB file and read in a floating panel above your other windows. Move it using the book-and-sprout handle, resize it from the lower-right corner, and choose the text size and color that suit you.

### Scroll at your own pace

Use the wheel to navigate manually, or start automatic reading and let the text move smoothly upward. Adjust the speed, pause whenever you need, and continue from the same place. The panel and font stay the same size.

Automatic reading stops at the end of the document. Your reading position is saved, and reopening PourInput restores it with automatic scrolling paused.

### Keep it discreet

Choose **Normal**, **Minimal**, or **Ghost**. The panel stays on top without taking keyboard focus. Minimal and Ghost allow clicks through the text area; the separate move and resize handles remain available. You can make the background fully transparent while keeping the text visible.

Hold your hide key to make the panel disappear. Automatic scrolling pauses while it is hidden and resumes on release, without losing your place.

![English Reading page with automatic reading and appearance controls](images/Screenshot_reading_en.png)

*Reading screenshots use the actual application interface with sample text.*

## Mouse buttons that fit what you do

Give supported buttons separate **Click** and **Long Press** actions. Use built-in shortcuts for copying, pasting, switching browser tabs, taking screenshots, and other everyday tasks. Application profiles let the same button do different things in different apps.

**Standard mouse buttons.** Generic Mouse Mode handles Windows middle and side buttons, including mice such as ZOWIE. You do not need a supported Logitech device to use this layer.

**MX Master enhancements.** Supported HID++ controls can provide gestures, Mode Shift, SmartShift, DPI, battery information, and horizontal scrolling. Available controls depend on the device and firmware.

**One clear owner for each input.** When Generic Mouse Mode is on, it owns supported standard inputs. A mapping set to “none” stays inactive; it does not fall back to an MX mapping. Non-overlapping MX controls remain available, and saved device mappings are retained when you switch modes.

## Reading and mouse controls work together

- **Reading OFF:** the wheel scrolls the active application normally.
- **Reading ON:** the vertical wheel navigates the reader instead of scrolling the page behind it, whether Generic Mouse Mode is on or off.
- **Mouse hide button:** while reading, this button only hides/restores the panel. Turn Reading Mode off to restore its usual action.
- **While hidden:** Reading Mode still owns the wheel. Hiding does not exit reading or reset the position.
- **Keyboard hide keys:** their normal keyboard action remains available; exclusive hide-button handling applies to mouse buttons.

Documents and reading position are stored separately from mouse profiles and the main mouse configuration. Changing mouse profiles does not reset the book you are reading.

## Get started on Windows

[**Download PourInput v1.4.2 for Windows**](https://github.com/pour-soi/PourInput/releases/download/v1.4.2/PourInput-v1.4.2-Windows.zip)

1. Extract the **entire ZIP** to a short path, such as `F:\Apps`. Do not run the app inside the ZIP or skip files if extraction fails.
2. Quit any older PourInput instance from its **system tray menu**. Closing the settings window only hides it.
3. Open `PourInput/PourInput.exe`. No separate Python installation is needed.
4. To customize buttons, open the mouse page and select a button.
5. To read, select the **book icon** in the left sidebar, import a TXT or EPUB, and turn on **Reading Mode**. Select **Start / resume auto-scroll** for continuous reading.

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

**Text is moving and you want it to stop?** Select **Pause auto-scroll** on the Reading page. Holding the hide key only pauses it temporarily; releasing resumes it.

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
