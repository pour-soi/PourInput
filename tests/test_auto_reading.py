import json
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from PySide6.QtCore import QObject, QUrl
from PySide6.QtGui import QFont
from PySide6.QtQml import QQmlComponent, QQmlEngine
from PySide6.QtWidgets import QApplication
from core.reader import ReaderStore
from ui.reading import ReadingController

APP = QApplication.instance() or QApplication([])
ROOT = Path(__file__).resolve().parents[1]


class AutoReadingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.hook = Mock(spec=['set_reading_wheel_handler'])
        self.reader = ReadingController(self.hook, self.temp.name, key_down=lambda key: False)
        self.addCleanup(self.reader.close)
        self.reader._finish_import(('Demo', ['连续阅读，保持文字平稳移动。 English words 😀 ' * 50]), '')
        self.reader.setEnabled(True)
        font = QFont('Microsoft YaHei')
        font.setPixelSize(22)
        self.reader.setViewport(320, 120, font)

    def start(self):
        self.reader.setAutoRunning(True)
        self.reader._scroll_timer.stop()  # Advance elapsed time deterministically.

    def test_live_timer_advances_and_manual_navigation_keeps_auto_reading(self):
        from PySide6.QtTest import QTest
        r = self.reader
        r.setAutoRunning(True)
        QTest.qWait(160)
        self.assertGreater(r.scrollOffset, 0)
        r.move(1)
        self.assertEqual(r.scrollOffset, 0)
        self.assertTrue(r.autoRunning)
        self.assertTrue(r.handle_wheel(1))
        anchor = r.model.state
        r.setViewport(400, 120, r._viewport[2])
        self.assertEqual(r.model.state, anchor)
        r.setAutoRunning(False)

    def test_smooth_motion_speed_and_no_per_frame_disk_writes(self):
        r = self.reader
        self.start()
        r.setScrollSpeed(20)
        initial = r.text
        with patch.object(r.model.store, 'save_state') as save:
            r._advance_scroll(.1)
            self.assertAlmostEqual(r.scrollOffset, 2)
            self.assertEqual(r.text, initial)
            r._advance_scroll(.1)
            self.assertAlmostEqual(r.scrollOffset, 4)
            save.assert_not_called()
        r.setAutoRunning(False)
        before = r.model.state
        r._advance_scroll(10)
        self.assertEqual(r.model.state, before)
        r.setScrollSpeed(40)
        self.start()
        r._advance_scroll(.1)
        self.assertAlmostEqual(r.scrollOffset, 8)

    def test_hidden_freezes_state_and_retains_wheel_then_resumes(self):
        r = self.reader
        r.setHideKey(5)
        self.start()
        r._advance_scroll(.2)
        before = r.model.state
        r._observe_button(5, True)
        with patch.object(r.model.store, 'save_state') as save:
            r._advance_scroll(5)
            r._scroll_tick()
            self.assertEqual(r.model.state, before)
            self.assertTrue(r.autoRunning)
            self.assertFalse(r.panelVisible)
            self.assertTrue(r.handle_wheel(1))
            save.assert_not_called()
        r._observe_button(5, False)
        r._advance_scroll(.1)
        self.assertTrue(r.panelVisible)
        self.assertGreater(r.scrollOffset, before.scroll_fraction * r.readerLineHeight)

    def test_end_and_disable_stop_while_restart_restores_position_paused(self):
        r = self.reader
        self.start()
        r._advance_scroll(3)
        r.setAutoRunning(False)
        state = r.model.state
        restored = ReadingController(self.hook, self.temp.name, key_down=lambda key: False)
        self.addCleanup(restored.close)
        self.assertEqual(restored.model.state, state)
        self.assertFalse(restored.autoRunning)
        self.start()
        r.setEnabled(False)
        before = r.model.state
        r._advance_scroll(100)
        self.assertEqual(r.model.state, before)
        self.assertFalse(r.autoRunning)
        self.assertFalse(r.handle_wheel(-120))
        r.setEnabled(True)
        self.start()
        r._advance_scroll(100000)
        self.assertFalse(r.autoRunning)
        self.assertTrue(r.enabled)
        self.assertTrue(r.text.rstrip().endswith('😀'))

    def test_existing_store_defaults_and_invalid_speed_preserve_file(self):
        path = Path(self.temp.name) / 'state.json'
        state = json.loads(path.read_text())
        for key in ('scroll_speed', 'scroll_fraction', 'continuous_scroll'):
            state.pop(key)
        path.write_text(json.dumps(state))
        loaded = ReaderStore(self.temp.name).load_state()
        self.assertEqual(loaded.scroll_speed, 24)
        self.assertFalse(loaded.continuous_scroll)
        state['scroll_speed'] = -5
        path.write_text(json.dumps(state))
        before = path.read_bytes()
        with self.assertRaises(ValueError): ReaderStore(self.temp.name).load_state()
        self.assertEqual(path.read_bytes(), before)

    def test_rendered_text_moves_without_resizing_or_losing_wrapped_lines(self):
        r = self.reader
        r.setPanelSize(400, 200)
        r.setFontSize(22)
        engine = QQmlEngine()
        component = QQmlComponent(engine, QUrl.fromLocalFile(str(ROOT/'ui/qml/ReadingPanel.qml')))
        panel = component.createWithInitialProperties({'controller': r})
        self.assertIsNotNone(panel, str(component.errors()))
        try:
            for _ in range(5): APP.processEvents()
            body = panel.findChild(QObject, 'readingBody')
            for mode in ('Normal', 'Minimal', 'Ghost'):
                r.setDisplayMode(mode)
                for _ in range(5): APP.processEvents()
                self.start()
                r._advance_scroll(.1)
                APP.processEvents()
                self.assertAlmostEqual(body.property('y'), -r.scrollOffset)
                self.assertEqual(panel.height(), 200)
                self.assertEqual(body.property('font').pixelSize(), 22)
                self.assertTrue(body.parent().property('clip'))
                before = r._line_index() * r.readerLineHeight + r.scrollOffset
                r._advance_scroll(r.readerLineHeight / r.scrollSpeed)
                APP.processEvents()
                after = r._line_index() * r.readerLineHeight + r.scrollOffset
                self.assertAlmostEqual(after - before, r.readerLineHeight)
                self.assertEqual(body.property('text'), r.text)
            self.assertEqual(''.join(line[2] for line in r._lines), ' '.join(r.model.groups))
        finally:
            panel.close()
