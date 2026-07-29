import os
from pathlib import Path
import tempfile
import unittest

from core.platform_paths import (
    config_dir,
    log_dir,
    screenshots_dir,
    temporary_dir,
    update_data_dir,
)


class PlatformPathTests(unittest.TestCase):
    def test_macos_paths_use_library_and_pictures_locations(self):
        home = Path("/Users/tester")

        self.assertEqual(
            config_dir(platform_name="darwin", home=home, environ={}),
            home / "Library" / "Application Support" / "PourInput",
        )
        self.assertEqual(
            log_dir(platform_name="darwin", home=home, environ={}),
            home / "Library" / "Logs" / "PourInput",
        )
        self.assertEqual(
            update_data_dir(platform_name="darwin", home=home, environ={}),
            home / "Library" / "Application Support" / "PourInput" / "updates",
        )
        self.assertEqual(
            screenshots_dir(home=home),
            home / "Pictures" / "Screenshots",
        )

    def test_windows_config_log_and_update_paths_remain_compatible(self):
        home = Path("C:/Users/tester")
        env = {
            "APPDATA": "C:/Users/tester/AppData/Roaming",
            "LOCALAPPDATA": "C:/Users/tester/AppData/Local",
        }

        self.assertEqual(
            config_dir(platform_name="win32", home=home, environ=env),
            Path(env["APPDATA"]) / "PourInput",
        )
        self.assertEqual(
            log_dir(platform_name="win32", home=home, environ=env),
            Path(env["APPDATA"]) / "PourInput" / "logs",
        )
        self.assertEqual(
            update_data_dir(platform_name="win32", home=home, environ=env),
            Path(env["LOCALAPPDATA"]) / "PourInput" / "updates",
        )

    def test_linux_paths_preserve_xdg_behavior(self):
        home = Path("/home/tester")
        env = {
            "XDG_CONFIG_HOME": "/custom/config",
            "XDG_STATE_HOME": "/custom/state",
        }

        self.assertEqual(
            config_dir(platform_name="linux", home=home, environ=env),
            Path("/custom/config/PourInput"),
        )
        self.assertEqual(
            log_dir(platform_name="linux", home=home, environ=env),
            Path("/custom/state/PourInput/logs"),
        )
        self.assertEqual(
            update_data_dir(platform_name="linux", home=home, environ=env),
            home / ".PourInput" / "updates",
        )

    def test_temporary_files_stay_beneath_system_temp_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                temporary_dir(temp_root=tmp),
                Path(tmp) / "PourInput",
            )


if __name__ == "__main__":
    unittest.main()
