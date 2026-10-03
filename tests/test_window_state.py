"""Window size persistence using only temporary files and offscreen windows."""
import json
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from PySide6.QtCore import QRect
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from ui.window_state import WindowSizeState

APP = QApplication.instance() or QApplication([])


class WindowSizeTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "window-size.json"

    def window(self):
        window = QWindow()
        window.setMinimumWidth(920)
        window.setMinimumHeight(620)
        window.resize(1060, 700)
        screen = Mock()
        screen.availableGeometry.return_value = QRect(0, 0, 1600, 1000)
        with patch.object(window, "screen", return_value=screen):
            state = WindowSizeState(window, self.path)
        self.addCleanup(window.destroy)
        return window, state

    def test_relaunch_restores_both_normal_sizes_and_only_size_fields(self):
        for width, height in ((920, 620), (1280, 900)):
            with self.subTest(size=(width, height)):
                window, state = self.window()
                window.showNormal()
                window.resize(width, height)
                QTest.qWait(250)
                self.assertEqual(json.loads(self.path.read_text()),
                                 {"width": width, "height": height})
                window.close()
                restored, _ = self.window()
                self.assertEqual((restored.width(), restored.height()), (width, height))

    def test_close_flushes_pending_resize(self):
        window, state = self.window()
        window.showNormal()
        window.resize(1200, 800)
        window.close()
        self.assertEqual(json.loads(self.path.read_text()), {"width": 1200, "height": 800})

    def test_non_normal_geometry_does_not_replace_saved_size(self):
        window, state = self.window()
        window.showNormal()
        window.resize(1200, 800)
        state.save()
        for visibility in (QWindow.Visibility.Maximized, QWindow.Visibility.Minimized,
                           QWindow.Visibility.Hidden):
            window.setVisibility(visibility)
            window.resize(1500, 950)
            QTest.qWait(250)
            state.save()
            self.assertEqual(json.loads(self.path.read_text()), {"width": 1200, "height": 800})

    def test_saved_size_is_clamped_to_screen_and_minimum(self):
        self.path.write_text('{"width": 5000, "height": 10}')
        window, _ = self.window()
        self.assertEqual((window.width(), window.height()), (1600, 620))

    def test_invalid_or_missing_file_uses_default_size(self):
        for data in (None, "bad json", '{"width": true, "height": 900}',
                     '{"width": -1, "height": 900}', "[]"):
            if data is not None:
                self.path.write_text(data)
            window, _ = self.window()
            self.assertEqual((window.width(), window.height()), (1060, 700))


if __name__ == "__main__":
    unittest.main()
