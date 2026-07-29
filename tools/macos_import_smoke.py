"""macOS-only import and platform-boundary smoke checks."""

from __future__ import annotations

from pathlib import Path
import sys


def main() -> int:
    if sys.platform != "darwin":
        raise SystemExit("macos_import_smoke.py must run on macOS")

    from core.platform_paths import config_dir, log_dir
    import core.app_catalog  # noqa: F401
    import core.app_detector  # noqa: F401
    import core.key_simulator  # noqa: F401
    import core.mouse_hook  # noqa: F401
    import main_qml

    loaded = set(sys.modules)
    required = {"core.mouse_hook_macos"}
    forbidden = {
        "core.mouse_hook_windows",
        "ui.windows_screenshot",
        "winreg",
        "ctypes.wintypes",
    }
    missing = sorted(required - loaded)
    unexpected = sorted(forbidden & loaded)
    if missing:
        raise SystemExit(f"macOS platform modules not loaded: {missing}")
    if unexpected:
        raise SystemExit(f"Windows-only modules imported on macOS: {unexpected}")

    home = Path.home()
    expected_config = home / "Library" / "Application Support" / "PourInput"
    expected_logs = home / "Library" / "Logs" / "PourInput"
    if config_dir() != expected_config:
        raise SystemExit(f"unexpected macOS config path: {config_dir()}")
    if log_dir() != expected_logs:
        raise SystemExit(f"unexpected macOS log path: {log_dir()}")

    root = Path(main_qml.ROOT)
    required_resources = (
        root / "ui" / "qml" / "Main.qml",
        root / "images" / "logo_icon.png",
        root / "images" / "logo_tray_template.png",
    )
    missing_resources = [str(path) for path in required_resources if not path.is_file()]
    if missing_resources:
        raise SystemExit(f"development resources missing: {missing_resources}")

    print("macOS import and platform-boundary smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
