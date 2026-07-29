# macOS compatibility audit

This audit records the platform boundaries that matter to PourInput's
experimental macOS build. It distinguishes code readiness from real-device
validation. Windows remains the supported stable release and its paths and
features must not regress.

## Storage and filesystem

| Concern | Windows | macOS | Status |
|---|---|---|---|
| Configuration | `%APPDATA%\PourInput\config.json` | `~/Library/Application Support/PourInput/config.json` | platform path boundary; automated |
| Logs | `%APPDATA%\PourInput\logs` | `~/Library/Logs/PourInput` | platform path boundary; automated |
| Update working state | `%LOCALAPPDATA%\PourInput\updates` | `~/Library/Application Support/PourInput/updates` | macOS manual-update state only; automated |
| Temporary capture files | system temp | system temp under `PourInput/` | automated path test |
| User screenshots | `Pictures\Screenshots` | `~/Pictures/Screenshots` | shared path logic; file dialogs require hardware testing |
| Installer backups | next to the writable Windows installation | none | Windows-only updater; macOS manual install |
| Local database | none | none | not applicable |
| Persistent cache | none | none | not applicable |

Paths use `pathlib`/`os.path`; no runtime code contains a hardcoded drive
letter. Windows backslash and drive-letter parsing remains intentionally
present in application catalog and secure ZIP-validation logic.

## Platform-specific dependencies

| Windows dependency or assumption | Boundary | macOS classification |
|---|---|---|
| `WH_MOUSE_LL`, Raw Input, `WM_XBUTTON*`, suppression tokens, Win32 window | `core/mouse_hook_windows.py`, selected by `core/mouse_hook.py` | replaced by Quartz `CGEventTap`; real-device validation pending |
| `SendInput`, virtual-key codes, media keys | Windows branch in `core/key_simulator.py` | replaced by Quartz/AppKit events; real-device validation pending |
| Registry application discovery and `.exe` catalog entries | guarded Windows branch in `core/app_catalog.py` | replaced by `/Applications` discovery and bundle identifiers |
| Foreground window APIs and UWP handling | guarded Windows branch in `core/app_detector.py` | replaced by `NSWorkspace` |
| HKCU Run startup registration | guarded helper in `core/startup.py` | replaced by per-user LaunchAgent; real login validation pending |
| Windows mutex/AppUserModelID | guarded functions in `main_qml.py` | QLocalServer handles single-instance activation; Win32 calls are no-ops |
| Windows toast/native tray conventions | Qt tray and platform shell setup | native AppKit status item with Qt notification fallback; visual/permission testing pending |
| Native `CF_DIB` clipboard delivery | `ui/windows_screenshot.py`, imported only on Windows | macOS shortcut/`screencapture` implementation; clipboard testing pending |
| `.exe`, `_internal`, writable onedir update replacement | `core/update_installer.py` and Windows-only backend branch | automatic install disabled; manual release-page flow |
| PowerShell/batch build and ZIP commands | Windows build/release scripts | separate zsh/PyInstaller/`ditto` workflow |
| `.ico` application icon | Windows app shell/spec | `.icns` bundle icon built from existing branding |
| Generic Mouse Mode | Windows settings and hook route | gracefully hidden/disabled; a native equivalent is deferred |
| Windows Control/Alt/Win shortcuts | platform key registry and simulator branch | Command/Option/native navigation mappings |
| Windows application file filter | backend platform branch | `.app` filter on macOS |
| Windows install and service assumptions | updater only; no Windows service exists | no installer/service; experimental ZIP is manually installed |

Windows-only modules are imported behind `sys.platform` dispatch. The macOS
import smoke test verifies that `core.mouse_hook_windows`,
`ui.windows_screenshot`, `winreg`, and `ctypes.wintypes` are absent after the
macOS startup import path.

## UX and system behavior review

| Area | Implemented or reviewed | Still requires physical Mac |
|---|---|---|
| Menu bar and tray | AppKit status item, Qt fallback, localized menu actions | notch/menu crowding, menu interaction, notification appearance |
| Window and Dock | activation-policy switching, icon refresh, hide-on-close | traffic lights, Cmd+Tab, Mission Control, Spaces, full-screen |
| Quit/session behavior | explicit quit plus logout/restart/shutdown handling | real logout/restart and unsaved-session behavior |
| Keyboard conventions | Command-aware shortcut labels and simulation | keyboard layouts, media keys, system-reserved shortcuts |
| File dialogs | `.app` application chooser and directory chooser | native dialog UX and sandbox/security prompts |
| Accessibility | fail-closed startup gate with explanatory dialog | grant, revoke, upgrade, relaunch, and multiple-bundle identity behavior |
| Screen Recording | preflight check and shortcut fallback | grant/deny/revoke, multi-display and Retina capture |
| Input Monitoring | CGEventTap design uses Accessibility | confirm whether target macOS versions prompt separately |
| Notifications | Qt notification surface remains available | permission prompt and banners while app is background-only |
| Dark mode/fonts/Retina | Qt system appearance and font policies | visual QA at 1x/2x and mixed displays |
| Clipboard | Qt/native screenshot actions | paste durability across target applications |
| Opening URLs/files | `QDesktopServices` with browser fallback | default-browser behavior |
| Background/login | `LSUIElement`, menu-bar lifecycle, LaunchAgent | login, sleep/wake, Fast User Switching |
| App sandbox | no sandbox entitlement or Mac App Store packaging | not claimed; sandboxing would require a larger redesign |

## Packaging and automation

`PourInput-mac.spec` creates `PourInput.app` with the existing `.icns`,
application version, `LSUIElement`, QML, images, and build metadata. The
experimental workflow runs tests and QML linting, checks macOS imports and
paths, builds both architectures, verifies bundle contents and Mach-O
architecture, initializes packaged QML in an offscreen smoke mode, archives
with `ditto`, and uploads versioned artifacts and logs.

The workflow does not publish, tag, push, use secrets, notarize, or invoke the
project's signing step. PyInstaller/macOS tooling may apply implementation
level ad-hoc signatures while assembling Mach-O files; no Apple identity or
Developer account is configured or claimed.

## Readiness classification

- **Fully implemented and automatically testable:** path selection, resource
  resolution, profile persistence logic, platform dispatch, bundle metadata
  verification, manual update fallback.
- **macOS-native equivalent implemented:** hooks, key simulation, foreground
  app detection, LaunchAgent startup, status item, screenshots.
- **Gracefully disabled:** Generic Mouse Mode and automatic in-place updates.
- **Deferred pending real-device testing:** all permissions, physical input,
  suppression, notifications, menus, Dock/window behavior, screenshots,
  clipboard, sleep/wake, login startup, and visual quality.
- **Larger redesign:** signed/notarized distribution, sandboxed/Mac App Store
  packaging, and a macOS equivalent of Windows Generic Mouse Mode.
