"""Reading layout checks using temporary books and the isolated app fixture."""
import os
import unittest
from pathlib import Path
from PySide6.QtCore import QObject, QMetaObject
from PySide6.QtTest import QTest
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
        for language in ("en", "zh_CN"):
            self.lm.setLanguage(language)
            for width, height in ((1280, 900), (920, 620)):
                self.window.resize(width, height)
                QTest.qWait(150)
                self.assertEqual([s.y() for s in sections], sorted(s.y() for s in sections))
                self.assertTrue(all(s.isVisible() for s in sections))
                self.assertGreater(page.findChild(QObject, "readingPreview").height(), 32)
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
