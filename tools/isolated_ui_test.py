"""Explicit Windows-only, disposable real-device test entry point.
Run from a fresh interpreter; never imported by production startup.
"""
import copy
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
TITLE = "PourInput UI Refinement Test"


def prepare():
    if any(name in sys.modules for name in ("core.config", "main_qml", "ui.backend")):
        raise RuntimeError("Isolation must be established before application imports")
    root = Path(tempfile.mkdtemp(prefix="pourinput-ui-test-"))
    for variable, folder in (("APPDATA", "roaming"), ("LOCALAPPDATA", "local"),
                             ("USERPROFILE", "profile"), ("HOME", "profile"),
                             ("TEMP", "temp"), ("TMP", "temp")):
        path = root / folder
        path.mkdir(exist_ok=True)
        os.environ[variable] = str(path)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT))
    from core import config
    # Also make newly created profiles and missing-key fallback neutral.
    for profile in config.DEFAULT_CONFIG["profiles"].values():
        profile["mappings"] = dict.fromkeys(profile["mappings"], "none")
    cfg = copy.deepcopy(config.DEFAULT_CONFIG)
    cfg["settings"].update(start_at_login=False, start_minimized=False,
                           check_for_updates=False, screenshot_directory=str(root / "screenshots"))
    (root / "screenshots").mkdir()
    config.save_config(cfg)
    return root


def test_backend(base):
    from PySide6.QtCore import Slot

    class IsolatedBackend(base):
        def _configureUpdateChecks(self):
            pass

        def _consumeUpdateResultMarker(self):
            pass

        def _cleanupStaleUpdatePreparation(self):
            pass

        def _startUpdateCheck(self, manual=False):
            pass

        def blocked(self):
            print("[Isolated test] Startup integration and updates are disabled.")

        @Slot(bool)
        def setStartAtLogin(self, value):
            self.blocked()

        @Slot(bool)
        def setCheckForUpdates(self, value):
            self.blocked()

        @Slot()
        def prepareLatestUpdate(self):
            self.blocked()

        @Slot()
        def installPreparedUpdate(self):
            self.blocked()

    return IsolatedBackend


def test_engine(base):
    from core.engine import MouseHook

    class IsolatedEngine(base):
        def __init__(self, *args, **kwargs):
            # Do not write default DPI before the user configures the test instance.
            with patch.object(MouseHook, "set_dpi", return_value=None, create=True):
                super().__init__(*args, **kwargs)

        def _request_saved_settings_replay(self, *, startup_fallback=False):
            # No automatic DPI/SmartShift writes on connection or reconnection.
            # Explicit Settings actions still use the normal engine methods.
            pass

    return IsolatedEngine


def run():
    if sys.platform != "win32" or len(sys.argv) != 1:
        raise SystemExit("Use this entry point on Windows without extra arguments.")
    root = prepare()
    # Scoped, test-process-only substitution; production modules on disk are untouched.
    with patch("core.startup.supports_login_startup", return_value=False):
        import main_qml
        main_qml.APP_NAME = TITLE
        main_qml.Backend = test_backend(main_qml.Backend)
        main_qml.Engine = test_engine(main_qml.Engine)
        original_acquire = main_qml._acquire_windows_single_instance_mutex

        def acquire():
            acquired = original_acquire()
            if not acquired:
                print("Exit the existing PourInput instance from its tray menu, then retry.")
            return acquired

        main_qml._acquire_windows_single_instance_mutex = acquire
        print(f"{TITLE}\nIsolated state: {root}\nAll initial mappings: Do Nothing / Pass-through.")
        print("Do not enable auto-start or updates. Configure test mappings manually.")
        return main_qml.main()


if __name__ == "__main__":
    raise SystemExit(run())
