# Experimental macOS support

PourInput has an experimental macOS implementation and an automated `.app`
bundle build. Windows remains the only official stable release target.

The macOS bundle is not code-signed with an Apple Developer ID, is not
notarized, and has not yet completed validation on physical macOS hardware.
A successful GitHub Actions build proves that the code imports, tests, starts
in a non-interactive smoke mode, and can be packaged. It does not prove that
mouse interception, permissions, notifications, menu-bar behavior, or every
GUI interaction works correctly on a real Mac.

## Automated build

The `macOS Experimental Build` workflow builds separate Apple Silicon and
Intel artifacts:

- `PourInput-<version>-macOS-arm64.zip`
- `PourInput-<version>-macOS-x86_64.zip`

To run it after the workflow file is committed to GitHub:

1. Open the repository's **Actions** tab.
2. Select **macOS Experimental Build**.
3. Choose **Run workflow** and the branch to test.
4. Wait for both architecture jobs to finish.
5. Open the completed run and download the application artifact for the
   target architecture. Diagnostic logs are uploaded separately.

The workflow installs dependencies in a fresh virtual environment, runs the
full automated test suite and QML linter, checks platform imports and data
paths, builds `PourInput.app`, verifies bundle metadata and required
resources, initializes the packaged QML window in smoke mode, archives the
bundle with `ditto`, and uploads the ZIP. It has read-only repository
permissions and does not publish a GitHub Release, push code, create tags,
sign with an Apple identity, or notarize the app.

## Trying an artifact

1. Download the ZIP that matches the Mac:
   - Apple Silicon (M1 or later): `arm64`
   - Intel: `x86_64`
2. Extract the ZIP in Finder.
3. Move `PourInput.app` to `/Applications` if desired.
4. Right-click `PourInput.app` and choose **Open**.
5. Confirm the Gatekeeper prompt. An unsigned, unnotarized experimental build
   may produce a warning or be blocked by local security policy.
6. Grant Accessibility permission when prompted:
   **System Settings → Privacy & Security → Accessibility**.
7. If custom screenshot-file delivery is tested, also grant Screen Recording
   permission.

Do not remove quarantine attributes or weaken system security settings as a
routine installation step. If local policy prevents opening the artifact,
report the exact Gatekeeper message.

## Data locations

| Data | macOS location |
|---|---|
| Configuration and persisted application state | `~/Library/Application Support/PourInput/` |
| Logs | `~/Library/Logs/PourInput/` |
| Update-check working state | `~/Library/Application Support/PourInput/updates/` |
| Temporary screenshot composition files | the system temporary directory under `PourInput/` |
| User-created screenshots | `~/Pictures/Screenshots/` or the folder selected in Settings |
| Login item | `~/Library/LaunchAgents/io.github.pour_soi.pourinput.plist` |

PourInput currently has no local database or persistent application cache.
Automatic in-place update installation and installation backups are
Windows-only; macOS update checks direct the user to manual installation.

## Implemented platform equivalents

| Capability | macOS behavior | Validation level |
|---|---|---|
| Mouse interception | Quartz `CGEventTap` | automated logic tests; real input still required |
| Keyboard actions | Quartz/AppKit events with Command-aware shortcuts | automated logic tests; real input still required |
| Foreground app detection | `NSWorkspace.frontmostApplication` | automated/static checks |
| Device-specific Logitech HID++ | non-exclusive hidapi/I/O Kit access | automated logic tests; real device required |
| Start at login | per-user LaunchAgent | automated unit tests; real login session required |
| Menu-bar operation | native AppKit status item with Qt fallback | automated unit tests; visual testing required |
| Screenshots | native shortcuts and `/usr/sbin/screencapture` for custom folders | automated tests; permission and clipboard testing required |
| App profiles | macOS bundle identifiers and executable identities | automated tests |
| Configuration and logs | native `~/Library` locations | automated tests |
| Packaging | PyInstaller `.app` with `.icns` branding | GitHub Actions build validation |

## Windows-only or deliberately unavailable features

- **Generic Mouse Mode** is Windows-only and remains hidden on macOS. Adding a
  macOS equivalent requires separate input-routing and hardware validation.
- **Windows Registry startup**, Win32 hooks, Raw Input, XBUTTON suppression,
  `SendInput`, native `CF_DIB`, Windows AppUserModelID, and `.exe` update
  replacement are never executed on macOS.
- **Automatic update installation** is disabled on macOS. Update checking and
  opening the release page remain available.
- Windows PowerShell and batch build commands are not used by the macOS
  workflow.

## Source development on a Mac

Requirements:

- macOS 12 or newer
- Python 3.12 recommended
- `arm64` Python for Apple Silicon or `x86_64` Python for Intel

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests
.venv/bin/python main_qml.py
```

Build locally on macOS only:

```bash
POURINPUT_PYTHON="$PWD/.venv/bin/python" ./build_macos_app.sh
```

The script uses `images/AppIcon.icns`, falling back to generating an `.icns`
from the existing logo source when necessary. By default it applies an ad-hoc
signature for local development. Set `POURINPUT_SKIP_CODESIGN=true` for the
same unsigned path used by experimental CI. `POURINPUT_SIGN_IDENTITY` remains
an optional local developer path and is not used by the experimental
workflow.

## Real-Mac validation still required

Before official macOS support or a public macOS release is claimed, test:

1. First launch, Gatekeeper behavior, and Accessibility permission recovery.
2. Apple Silicon and Intel startup from Finder and `/Applications`.
3. Logitech HID++ discovery, reconnect, every mapped control, suppression,
   rapid clicks, and long holds using physical devices.
4. Command-based custom shortcuts and media/system actions in several apps.
5. Per-app profile switching using Safari, Chrome, Finder, and another app.
6. Menu-bar icon visibility, menus, notifications, Dock activation, Cmd+Tab,
   Cmd+W, explicit Quit, logout, restart, and login startup.
7. Full-screen and region screenshots, clipboard paste, custom folders,
   multiple displays, Retina scaling, and Screen Recording denial/recovery.
8. Native file dialogs, opening URLs, clipboard ownership, dark mode, fonts,
   full-screen windows, and multiple displays.
9. Sleep/wake, device disconnect/reconnect, and long-running memory use.
10. Update notifications and manual-install messaging.

Report problems with the macOS version and architecture, macOS version,
connection type, device model, exact steps, visible result, and the relevant
log excerpt from `~/Library/Logs/PourInput/PourInput.log`. Do not include
private configuration contents or unrelated system information.
