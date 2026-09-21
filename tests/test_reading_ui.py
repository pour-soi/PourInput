import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock

from PySide6.QtCore import Qt, QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine
from PySide6.QtWidgets import QApplication
from ui.reading import ReadingController

APP = QApplication.instance() or QApplication([])
ROOT = Path(__file__).resolve().parents[1]


class ReadingUiTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.hook = Mock(spec=["set_reading_wheel_handler"])
        self.reader = ReadingController(self.hook, self.temporary.name, key_down=lambda key: False)
        self.addCleanup(self.reader.close)

    def document(self):
        self.reader._finish_import(("Book", ["First sentence.", "Second sentence."]), "")
        self.reader.setEnabled(True)

    def test_navigation_queued_and_disable_invalidates_pending_command(self):
        self.document()
        self.assertTrue(self.reader.handle_wheel(-120))
        self.assertEqual(self.reader.position, 1)
        self.reader.setEnabled(False)
        APP.processEvents()
        self.assertEqual(self.reader.position, 1)
        self.reader.setEnabled(True)
        self.reader.handle_wheel(-120)
        APP.processEvents()
        self.assertEqual(self.reader.position, 2)

    @unittest.skipUnless(os.name == "nt", "Windows HID reader bridge")
    def test_hid_reports_hide_without_side_action_mappings(self):
        from unittest.mock import patch
        from PySide6.QtCore import QEvent
        from core.mouse_hook_windows import MouseHook
        from core.hid_gesture import HidGestureListener
        hook = MouseHook()
        with patch.object(HidGestureListener, "start", return_value=True):
            listener = hook._start_hid_listener()
        reader = ReadingController(hook, self.temporary.name, key_down=lambda key: False)
        self.addCleanup(reader.close)
        reader._finish_import(("Book", ["One.", "Two."]), "")
        reader.setEnabled(True)
        listener._feat_idx = 9
        action = Mock()
        hook._dispatch = action
        for key, cid in ((5, 0x0053), (6, 0x0056)):
            self.assertNotIn(cid, listener._extra_diverts)
            reader.setHideKey(key)
            before = reader.model.state
            down = [0x11, 0xFF, 9, 0, 0, cid, 0, 0]
            listener._on_report(down)
            listener._on_report(down)
            APP.sendPostedEvents(reader, QEvent.MetaCall)
            APP.processEvents()
            self.assertFalse(reader.panelVisible)
            self.assertEqual(reader.model.state, before)
            self.assertTrue(reader.handle_wheel(1))
            listener._on_report([0x11, 0xFF, 9, 0, 0, 0])
            APP.sendPostedEvents(reader, QEvent.MetaCall)
            APP.processEvents()
            self.assertTrue(reader.panelVisible)
            self.assertEqual(reader.model.state, before)
            listener._on_report(down)
            APP.sendPostedEvents(reader, QEvent.MetaCall)
            APP.processEvents()
            listener._clear_extra_divert_holds("disconnect")
            APP.sendPostedEvents(reader, QEvent.MetaCall)
            APP.processEvents()
            self.assertTrue(reader.panelVisible)
            self.assertEqual(reader.model.state, before)
        action.assert_not_called()

    def test_background_import_completes_locally(self):
        path = Path(self.temporary.name) / "book.txt"
        path.write_text("First. Second.", encoding="utf-8")
        self.reader.importPath(str(path))
        deadline = time.monotonic() + 3
        while self.reader.busy and time.monotonic() < deadline:
            APP.processEvents()
            time.sleep(.005)
        self.assertFalse(self.reader.busy)
        self.assertEqual(self.reader.error, "")
        self.assertEqual(self.reader.text, "First. Second.")

    def test_failed_import_preserves_document_position_and_ownership(self):
        self.document()
        self.reader.move(1)
        before = self.reader.model.state
        self.reader._finish_import(None, "Invalid EPUB")
        self.assertEqual(self.reader.model.state, before)
        self.assertTrue(self.reader.handle_wheel(10))
        self.assertIn("Invalid EPUB", self.reader.error)

    def test_panel_loads_and_modes_have_no_focus_and_clickthrough_flags(self):
        self.document()
        engine = QQmlEngine()
        component = QQmlComponent(engine, QUrl.fromLocalFile(str(ROOT / "ui/qml/ReadingPanel.qml")))
        panel = component.createWithInitialProperties({"controller": self.reader})
        self.assertIsNotNone(panel, str(component.errors()))
        try:
            APP.processEvents()
            self.assertIsNone(panel.transientParent())
            self.assertTrue(panel.flags() & Qt.WindowDoesNotAcceptFocus)
            self.assertTrue(panel.flags() & Qt.WindowStaysOnTopHint)
            self.assertTrue(panel.flags() & Qt.FramelessWindowHint)
            self.assertFalse(panel.flags() & Qt.WindowTransparentForInput)
            self.reader.setDisplayMode("Ghost")
            APP.processEvents()
            self.assertTrue(panel.flags() & Qt.WindowTransparentForInput)
            self.assertTrue(panel.isVisible())
            self.reader._finish_import(("Long passage", ["字" * 600]), "")
            self.reader.setDisplayMode("Normal")
            APP.processEvents()
            self.assertLessEqual(panel.height(), panel.screen().geometry().height() - 80)
            self.assertGreaterEqual(panel.y(), panel.screen().geometry().y())
        finally:
            panel.close()

    def test_custom_panel_dimensions_preserve_modes_and_reading_state(self):
        self.document()
        before = self.reader.model.state
        engine = QQmlEngine()
        component = QQmlComponent(engine, QUrl.fromLocalFile(str(ROOT / "ui/qml/ReadingPanel.qml")))
        panel = component.createWithInitialProperties({"controller": self.reader})
        self.assertIsNotNone(panel, str(component.errors()))
        try:
            self.reader.setPanelWidth(480)
            self.reader.setPanelHeight(180)
            for mode in ("Normal", "Minimal", "Ghost"):
                self.reader.setDisplayMode(mode)
                APP.processEvents()
                self.assertEqual(panel.width(), min(480, panel.screen().geometry().width() - 40))
                self.assertEqual(panel.height(), min(180, panel.screen().geometry().height() - 140))
                self.assertTrue(panel.flags() & Qt.WindowDoesNotAcceptFocus)
                self.assertEqual(bool(panel.flags() & Qt.WindowTransparentForInput), mode != "Normal")
            self.assertEqual(self.reader.model.state.document_id, before.document_id)
            self.assertEqual(self.reader.model.state.group_index, before.group_index)
            self.assertEqual(self.reader.enabled, before.reading_enabled)
            self.assertTrue(self.reader.handle_wheel(1))
            self.reader.setPanelWidth(9999)
            self.reader.setPanelHeight(-1)
            self.assertEqual(self.reader.panelWidth, 1920)
            self.assertEqual(self.reader.panelHeight, 80)
            self.reader.setPanelHeight(0)
            APP.processEvents()
            self.assertGreater(panel.height(), 0)
        finally:
            panel.close()

    def test_fixed_font_pages_fit_and_preserve_text_and_restart_position(self):
        from PySide6.QtCore import QObject
        from PySide6.QtGui import QFontDatabase, QFont
        if os.name == "nt":
            previous_font = APP.font()
            QFontDatabase.addApplicationFont("C:/Windows/Fonts/msyh.ttc")
            QFontDatabase.addApplicationFont("C:/Windows/Fonts/seguiemj.ttf")
            APP.setFont(QFont("Microsoft YaHei"))
            self.addCleanup(APP.setFont, previous_font)
        self.document()
        original = "字" * 180 + "😀阅读。" * 20 + " English words " * 20
        groups = [original[i:i + 120] for i in range(0, len(original), 120)]
        original = " ".join(groups)
        self.reader._finish_import(("Book", groups), "")
        engine = QQmlEngine()
        component = QQmlComponent(engine, QUrl.fromLocalFile(str(ROOT / "ui/qml/ReadingPanel.qml")))
        panel = component.createWithInitialProperties({"controller": self.reader})
        self.assertIsNotNone(panel, str(component.errors()))
        try:
            self.reader.setPanelSize(400, 160)
            self.reader.setFontSize(23)
            body = panel.findChild(QObject, "readingBody")
            for mode in ("Normal", "Minimal", "Ghost"):
                self.reader.setDisplayMode(mode)
                self.reader.model.update(group_index=0, group_offset=0)
                for _ in range(5): APP.processEvents()
                chunks = []
                for page in range(self.reader.groupCount):
                    for _ in range(3): APP.processEvents()
                    chunks.append(self.reader.text)
                    self.assertEqual(body.property("font").pixelSize(), 23)
                    self.assertEqual(panel.height(), 160)
                    if page < self.reader.groupCount - 1:
                        self.assertEqual(body.property("lineCount"),
                                         int(body.property("height") // self.reader.readerLineHeight))
                    self.assertLessEqual(body.property("contentHeight"), body.property("height") + 1)
                    self.reader.move(1)
                self.assertEqual("".join(chunks), original)
                for expected in reversed(chunks[:-1]):
                    self.reader.move(-1)
                    self.assertEqual(self.reader.text, expected)
            self.reader.move(1)
            anchor = self.reader.model.state
            self.reader.setPanelSize(320, 160)
            for _ in range(5): APP.processEvents()
            self.assertEqual(self.reader.model.state.group_offset, anchor.group_offset)
            restored = ReadingController(self.hook, self.temporary.name, key_down=lambda key: False)
            self.addCleanup(restored.close)
            restored.setViewport(body.property("width"), body.property("height"), body.property("font"))
            self.assertEqual(restored.text, self.reader.text)
            self.assertEqual(restored.model.state.group_offset, anchor.group_offset)
        finally:
            panel.close()

    def test_transparent_background_and_custom_font_keep_text_and_input_rules(self):
        from PySide6.QtCore import QObject
        self.document()
        before = self.reader.model.state
        engine = QQmlEngine()
        component = QQmlComponent(engine, QUrl.fromLocalFile(str(ROOT / "ui/qml/ReadingPanel.qml")))
        panel = component.createWithInitialProperties({"controller": self.reader})
        self.assertIsNotNone(panel, str(component.errors()))
        try:
            self.reader.setTransparentBackground(True)
            self.reader.setFontColor("#12ABEF")
            self.reader.setFontSize(32)
            for mode in ("Normal", "Minimal", "Ghost"):
                self.reader.setDisplayMode(mode)
                for _ in range(5): APP.processEvents()
                background = panel.findChild(QObject, "readingBackground")
                body = panel.findChild(QObject, "readingBody")
                self.assertEqual(background.property("color").alpha(), 0)
                self.assertEqual(body.property("color").name(), "#12abef")
                self.assertEqual(body.property("font").pixelSize(), 32)
                self.assertEqual(body.property("text"), "First sentence. Second sentence.")
                self.assertTrue(panel.isVisible())
                self.assertTrue(panel.flags() & Qt.WindowDoesNotAcceptFocus)
                self.assertEqual(bool(panel.flags() & Qt.WindowTransparentForInput), mode != "Normal")
            self.assertEqual(self.reader.model.state.document_id, before.document_id)
            self.assertEqual(self.reader.model.state.group_index, before.group_index)
            self.assertTrue(self.reader.enabled)
            self.assertTrue(self.reader.handle_wheel(1))
            self.reader.setFontColor("invalid")
            self.assertEqual(self.reader.fontColor, "#12abef")
            self.reader.setTransparentBackground(False)
            APP.processEvents()
            self.assertGreater(background.property("color").alpha(), 0)
        finally:
            panel.close()

    def test_font_color_dialog_cancel_preserves_settings(self):
        from unittest.mock import patch
        from PySide6.QtGui import QColor
        before = self.reader.model.state
        with patch("ui.reading.QColorDialog.getColor", return_value=QColor()):
            self.reader.chooseFontColor()
        self.assertEqual(self.reader.model.state, before)

    def test_reader_language_switch_keeps_book_and_settings(self):
        from ui.locale_manager import LocaleManager
        locale = LocaleManager("zh_CN")
        reader = ReadingController(self.hook, self.temporary.name, locale_manager=locale)
        self.addCleanup(reader.close)
        self.assertEqual(reader.title, "尚未导入文件")
        self.assertEqual(reader.strings["reading.normal"], "标准")
        self.assertEqual(reader.hideChoices[2]["label"], "后退键")
        reader._finish_import(("Book", ["One.", "Two."]), "")
        reader.setEnabled(True)
        reader.move(1)
        before = reader.model.state
        saved = (Path(self.temporary.name) / "state.json").read_bytes()
        chinese_keys = {key for key in reader.strings if key.startswith("reading.")}
        reader._finish_import(None, "Import failed: broken file")
        self.assertNotIn("Import", reader.error)
        locale.setLanguage("en")
        self.assertEqual(reader.strings["reading.normal"], "Normal")
        self.assertEqual(reader.hideChoices[2]["label"], "Back button")
        self.assertEqual(chinese_keys, {key for key in reader.strings if key.startswith("reading.")})
        self.assertEqual(reader.model.state, before)
        self.assertEqual((Path(self.temporary.name) / "state.json").read_bytes(), saved)

    def test_drag_handle_stays_interactive_while_text_is_click_through(self):
        from PySide6.QtGui import QWindow
        self.document()
        engine = QQmlEngine()
        component = QQmlComponent(engine, QUrl.fromLocalFile(str(ROOT / "ui/qml/ReadingPanel.qml")))
        panel = component.createWithInitialProperties({"controller": self.reader})
        self.assertIsNotNone(panel, str(component.errors()))
        try:
            grip = panel.findChild(QWindow, "readingDragHandle")
            self.assertIsNotNone(grip)
            for mode in ("Normal", "Minimal", "Ghost"):
                self.reader.setDisplayMode(mode)
                APP.processEvents()
                self.assertTrue(grip.isVisible())
                self.assertFalse(grip.flags() & Qt.WindowTransparentForInput)
                self.assertTrue(grip.flags() & Qt.WindowDoesNotAcceptFocus)
                self.assertEqual(bool(panel.flags() & Qt.WindowTransparentForInput), mode != "Normal")
                panel.setX(100)
                panel.setY(120)
                APP.processEvents()
                self.assertEqual(grip.x(), panel.x() + panel.width() - grip.width())
                self.assertEqual(grip.y() + grip.height(), panel.y() - 8)
                self.assertEqual((grip.width(), grip.height()), (40, 40))
            self.reader.setHideKey(16)
            self.reader._key_down = lambda key: key == 16
            self.reader._poll_hold()
            APP.processEvents()
            self.assertFalse(panel.isVisible())
            self.assertFalse(grip.isVisible())
        finally:
            panel.close()

    def test_resize_handle_saves_dimensions_without_changing_reading_state(self):
        from PySide6.QtCore import QObject, QMetaObject
        from PySide6.QtGui import QWindow
        self.document()
        engine = QQmlEngine()
        component = QQmlComponent(engine, QUrl.fromLocalFile(str(ROOT / "ui/qml/ReadingPanel.qml")))
        panel = component.createWithInitialProperties({"controller": self.reader})
        self.assertIsNotNone(panel, str(component.errors()))
        try:
            handle = panel.findChild(QWindow, "readingResizeHandle")
            grip = panel.findChild(QObject, "readingResizeGrip")
            before = self.reader.model.state
            for mode in ("Normal", "Minimal", "Ghost"):
                self.reader.setDisplayMode(mode)
                APP.processEvents()
                self.assertTrue(handle.isVisible())
                self.assertFalse(handle.flags() & Qt.WindowTransparentForInput)
                self.assertTrue(handle.flags() & Qt.WindowDoesNotAcceptFocus)
                panel.setWidth(420)
                panel.setHeight(200)
                self.assertTrue(QMetaObject.invokeMethod(grip, "saveSize"))
                APP.processEvents()
                self.assertEqual((self.reader.panelWidth, self.reader.panelHeight), (420, 200))
                self.assertEqual(handle.x(), panel.x() + panel.width() - 24)
                self.assertEqual(handle.y(), panel.y() + panel.height() - 24)
                self.assertEqual(self.reader.model.state.document_id, before.document_id)
                self.assertEqual(self.reader.model.state.group_index, before.group_index)
                self.assertTrue(self.reader.enabled)
            import json
            saved = json.loads((Path(self.temporary.name) / "state.json").read_text())
            self.assertEqual((saved["panel_width"], saved["panel_height"]), (420, 200))
            self.reader.setHideKey(16)
            self.reader._key_down = lambda key: True
            self.reader._poll_hold()
            APP.processEvents()
            self.assertFalse(handle.isVisible())
            self.assertTrue(self.reader.handle_wheel(1))
        finally:
            panel.close()

    def test_page_loads(self):
        engine = QQmlEngine()
        component = QQmlComponent(engine, QUrl.fromLocalFile(str(ROOT / "ui/qml/ReadingPage.qml")))
        page = component.createWithInitialProperties({
            "controller": self.reader,
            "theme": {"textPrimary": "#fff", "textSecondary": "#aaa", "bgCard": "#222"},
        })
        self.assertIsNotNone(page, str(component.errors()))
        page.deleteLater()


    def test_hold_hides_only_and_keeps_wheel_ownership_and_saved_state(self):
        self.document()
        self.reader.setHideKey(119)
        self.reader._key_down = Mock(return_value=True)
        before = self.reader.model.state
        saved = (Path(self.temporary.name) / "state.json").read_bytes()
        _, epoch, _ = self.reader._gate.feed(0)
        self.reader._poll_hold()
        self.assertFalse(self.reader.panelVisible)
        self.assertEqual(self.reader.model.state, before)
        self.assertEqual((Path(self.temporary.name) / "state.json").read_bytes(), saved)
        self.assertTrue(self.reader._gate.accepts(epoch))
        self.assertTrue(self.reader.handle_wheel(10))
        self.reader._key_down.return_value = False
        self.reader._poll_hold()
        self.assertTrue(self.reader.panelVisible)
        self.assertEqual(self.reader.model.state, before)

    def test_observed_suppressed_mouse_button_hides_and_release_restores(self):
        self.document()
        self.reader.setHideKey(5)
        self.reader._key_down = Mock(return_value=False)
        before = self.reader.model.state
        self.reader._observe_button(5, True)
        self.assertFalse(self.reader.panelVisible)
        self.reader._observe_button(5, False)
        self.assertTrue(self.reader.panelVisible)
        self.assertEqual(self.reader.model.state, before)

    def test_hidden_panel_still_navigates_and_close_detaches(self):
        self.document()
        self.reader.setHideKey(5)
        self.reader._observe_button(5, True)
        self.reader.handle_wheel(-120)
        APP.processEvents()
        self.assertEqual(self.reader.position, 2)
        self.assertFalse(self.reader.panelVisible)
        self.reader.close()
        self.assertFalse(self.reader.handle_wheel(120))
        self.assertFalse(self.reader._hold_timer.isActive())
        self.hook.set_reading_wheel_handler.assert_called_with(None)


    def test_mouse_profiles_and_generic_toggles_preserve_reader_and_saved_mappings(self):
        import copy
        from unittest.mock import patch
        from core.config import DEFAULT_CONFIG
        from core.engine import Engine
        from test_engine import _FakeMouseHook, _FakeAppDetector
        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg["profiles"]["other"] = copy.deepcopy(cfg["profiles"]["default"])
        cfg["profiles"]["default"]["mappings"]["xbutton1"] = "browser_back"
        cfg["profiles"]["default"]["mappings"]["generic_xbutton1"] = "none"
        original = copy.deepcopy(cfg["profiles"])
        with patch("core.engine.MouseHook", _FakeMouseHook), patch("core.engine.AppDetector", _FakeAppDetector):
            engine = Engine(initial_config=cfg)
        # Bind this reader to the same hook that receives profile generations.
        engine.hook.set_reading_wheel_handler = Mock()
        with tempfile.TemporaryDirectory() as directory:
            reader = ReadingController(engine.hook, directory)
            try:
                reader._finish_import(("Book", ["One.", "Two."]), "")
                reader.setEnabled(True)
                reader.move(1)
                state = reader.model.state
                saved = (Path(directory) / "state.json").read_bytes()
                for generic in (True, False, True):
                    for profile in ("other", "default"):
                        cfg["settings"]["generic_mouse_enabled"] = generic
                        cfg["active_profile"] = profile
                        engine._replace_bindings("reader integration")
                        self.assertEqual(reader.model.state, state)
                        self.assertTrue(reader.handle_wheel(10))
                        self.assertEqual((Path(directory) / "state.json").read_bytes(), saved)
                self.assertEqual(cfg["profiles"], original)
            finally:
                reader.close()

