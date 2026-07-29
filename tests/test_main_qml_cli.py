import unittest
from unittest.mock import patch

try:
    import main_qml
except Exception:  # pragma: no cover - env without PySide6 / project deps
    main_qml = None


@unittest.skipIf(main_qml is None, "main_qml / PySide6 not available")
class MainQmlCliTests(unittest.TestCase):
    def test_parse_known_cli_flags_and_forwards_qt_args(self):
        parsed = main_qml._parse_cli_args([
            "main_qml.py",
            "--start-hidden",
            "--hid-backend=auto",
            "--qt-flag",
        ])

        self.assertEqual(
            parsed,
            (
                ["main_qml.py", "--qt-flag"],
                "auto",
                True,
                False,
            ),
        )

    def test_startup_smoke_mode_is_explicitly_opt_in(self):
        with patch.dict(
            main_qml.os.environ,
            {"POURINPUT_STARTUP_SMOKE_TEST": "true"},
            clear=False,
        ):
            self.assertTrue(main_qml._smoke_test_requested())

        with patch.dict(main_qml.os.environ, {}, clear=True):
            self.assertFalse(main_qml._smoke_test_requested())


if __name__ == "__main__":
    unittest.main()
