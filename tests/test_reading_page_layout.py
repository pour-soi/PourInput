"""Reading layout checks using temporary books and the isolated app fixture."""
import os
import unittest
from pathlib import Path
from PySide6.QtCore import QObject, QMetaObject, QPointF, Qt
from PySide6.QtTest import QTest
from PySide6.QtQml import QQmlEngine, QQmlProperty
from tests.test_mouse_page_ui import MousePageUiTests

class ReadingPageLayoutTests(unittest.TestCase):
    setUp = MousePageUiTests.setUp
    dispose = MousePageUiTests.dispose
    device = MousePageUiTests.device

    def test_sections_help_preview_and_bilingual_sizes(self):
        from core.reader_import import import_document
        sample = Path(self.directory.name) / "A Quiet Morning — Sample Book.txt"
        sample.write_text("Chapter 1 Morning\nThe morning light reached the window. A quiet street stretched toward the river.\n\nChapter 2 The River\nA second sample page.", encoding="utf-8")
        self.reader._finish_import(import_document(sample, with_chapters=True), "")
        self.window.setProperty("currentPage", 2)
        page = self.window.findChild(QObject, "readingPage")
        flick = page.property("contentItem")
        sections = [page.findChild(QObject, "section_" + k) for k in ("book", "reading", "appearance", "controls")]
        output = os.environ.get("POURINPUT_READING_SCREENSHOTS")
        def capture(name, y=0):
            flick.setProperty("contentY", min(y, max(0, flick.property("contentHeight") - flick.height())))
            QTest.qWait(100)
            if output:
                Path(output).mkdir(parents=True, exist_ok=True)
                self.assertTrue(self.window.grabWindow().save(str(Path(output) / (name + ".png"))))
        initial = self.reader.model.state
        for language in ("en", "zh_CN"):
            self.lm.setLanguage(language)
            for width, height in ((1280, 900), (920, 620), (1600, 900)):
                self.window.resize(width, height)
                QTest.qWait(150)
                self.assertEqual([s.y() for s in sections], sorted(s.y() for s in sections))
                self.assertTrue(all(s.isVisible() for s in sections))
                self.assertGreater(page.findChild(QObject, "readingPreview").height(), 32)
                # Resizing must rearrange controls without changing their height or stored settings.
                for key in ("readingPanelWidth", "readingPanelHeight", "readingFontSize"):
                    control = page.findChild(QObject, key)
                    self.assertEqual(control.height(), 42)
                    self.assertLessEqual(control.width(), 240)
                self.assertFalse(page.findChild(QObject, "readingPanelHeight").isEnabled())
                for key in ("appearanceModeGroup", "appearanceSizeGroup", "appearanceTextGroup"):
                    group = page.findChild(QObject, key)
                    self.assertLessEqual(group.x() + group.width(), page.width())
                self.assertEqual(self.reader.model.state, initial)
                capture(f"reading-{language}-{width}")
                capture(f"appearance-{language}-{width}", sections[2].y()-12)
                capture(f"controls-{language}-{width}", sections[3].y()-12)
            before = self.reader.model.state
            for key in ("reading", "appearance", "controls"):
                button = page.findChild(QObject, key + "Help")
                detail = page.findChild(QObject, key + "HelpText")
                self.assertFalse(detail.isVisible())
                button.setProperty("checked", True)
                QTest.qWait(30)
                self.assertTrue(detail.isVisible())
                self.assertEqual(self.reader.model.state, before)
            capture(f"help-{language}", sections[3].y()-12)
            for key in ("reading", "appearance", "controls"):
                page.findChild(QObject, key + "Help").setProperty("checked", False)
        self.assertEqual([w for w in self.warnings if "Only binding to one of multiple key bindings" not in w], [])

    def test_appearance_pairs_share_columns_without_changing_saved_state(self):
        self.window.setProperty("currentPage", 2)
        page = self.window.findChild(QObject, "readingPage")
        container = page.findChild(QObject, "appearanceContainer")
        groups = [page.findChild(QObject, "appearance" + name + "Group") for name in ("Mode", "Size", "Text")]
        cells = [page.findChild(QObject, "appearance_" + name) for name in ("mode", "opacity", "width", "height", "font_size", "font_color")]
        self.reader.setPanelWidth(660)
        state_file = Path(self.directory.name) / "state.json"
        saved = state_file.read_bytes()
        initial = self.reader.model.state
        def point(item):
            return item.mapToItem(container, QPointF())
        for language in ("en", "zh_CN"):
            self.lm.setLanguage(language)
            for width, height in ((920, 620), (1280, 900), (1600, 900)):
                self.window.resize(width, height)
                QTest.qWait(100)
                self.assertLessEqual(container.width(), 704)
                self.assertEqual([g.property("columns") for g in groups], [2, 2, 2])
                for left, right in zip(cells[::2], cells[1::2]):
                    self.assertAlmostEqual(point(left).y(), point(right).y())
                    self.assertAlmostEqual(left.width(), right.width(), delta=1)
                    self.assertAlmostEqual(point(left).x(), point(cells[0]).x())
                    self.assertAlmostEqual(point(right).x(), point(cells[1]).x())
                default = page.findChild(QObject, "readingDefaultHeight")
                panel_height = page.findChild(QObject, "readingPanelHeight")
                self.assertAlmostEqual(point(default).x(), point(panel_height).x())
                self.assertGreaterEqual(point(default).y(), point(panel_height).y() + panel_height.height())
                transparent = page.findChild(QObject, "readingTransparentBackground")
                self.assertAlmostEqual(transparent.width(), container.width())
                self.assertGreaterEqual(point(transparent).y(), groups[2].y() + groups[2].height())
                self.assertLessEqual(page.findChild(QObject, "readingOpacity").width(), 320)
                self.assertEqual(self.reader.model.state, initial)
                self.assertEqual(state_file.read_bytes(), saved)
        # Simulate less usable content width without changing the supported window minimum.
        for usable_width, columns in ((579, 1), (580, 2), (420, 1)):
            self.assertTrue(QQmlProperty(container, "Layout.maximumWidth", QQmlEngine.contextForObject(container)).write(usable_width))
            QTest.qWait(100)
            self.assertAlmostEqual(container.width(), usable_width)
            self.assertEqual([g.property("columns") for g in groups], [columns] * 3)
            if columns == 1:
                for left, right in zip(cells[::2], cells[1::2]):
                    self.assertGreater(point(right).y(), point(left).y())
            for key in ("readingDisplayMode", "readingPanelWidth", "readingPanelHeight", "readingFontSize", "readingTextColor"):
                control = page.findChild(QObject, key)
                self.assertEqual(control.height(), 42)
                self.assertEqual(control.property("font").pixelSize(), 16)
            self.assertEqual(state_file.read_bytes(), saved)

    def test_numeric_adjustments_preserve_existing_values_and_disabled_height(self):
        self.window.setProperty("currentPage", 2)
        self.window.resize(1280, 900)
        QTest.qWait(100)
        page = self.window.findChild(QObject, "readingPage")
        flick = page.property("contentItem")
        width = page.findChild(QObject, "readingPanelWidth")
        height = page.findChild(QObject, "readingPanelHeight")
        flick.setProperty("contentY", max(0, width.mapToItem(flick.property("contentItem"), QPointF()).y() - 100))
        QTest.qWait(100)
        before = self.reader.panelWidth
        point = width.mapToScene(QPointF(width.width() - 19, width.height() / 2)).toPoint()
        QTest.mouseClick(self.window, Qt.LeftButton, Qt.NoModifier, point)
        self.assertEqual(self.reader.panelWidth, before + 20)
        self.assertEqual(width.property("value"), self.reader.panelWidth)
        self.assertFalse(height.isEnabled())
        self.assertEqual(self.reader.panelHeight, 0)

    def test_hide_key_labels_follow_language_without_changing_stored_values(self):
        self.window.setProperty("currentPage", 2)
        QTest.qWait(100)
        picker = self.window.findChild(QObject, "readingHideKeyPicker")
        keys = [choice["key"] for choice in self.reader.hideChoices]
        for key, labels in ((0, ("None", "不设置", "None")),
                            (5, ("Back button", "后退键", "Back button"))):
            self.reader.setHideKey(key)
            before = self.reader.model.state
            state_file = Path(self.directory.name) / "state.json"
            saved = state_file.read_bytes()
            for language, label in zip(("en", "zh_CN", "en"), labels):
                self.lm.setLanguage(language)
                QTest.qWait(50)
                self.assertEqual(picker.property("displayText"), label)
                self.assertEqual(picker.property("currentValue"), key)
                self.assertEqual([choice["key"] for choice in self.reader.hideChoices], keys)
                self.assertEqual(self.reader.model.state, before)
                self.assertEqual(state_file.read_bytes(), saved)
