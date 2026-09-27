import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from PySide6.QtGui import QFont
from tests.test_reading_ui import APP
from core.reader_import import import_document
from ui.reading import ReadingController


class ChapterJumpLayoutTests(unittest.TestCase):
    def test_jump_starts_at_title_for_pages_and_auto_scroll_and_survives_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'book.txt'
            source = '雨夜\n\n' + '雨夜的正文😀。' * 30 + '天亮以后继续出发。\n\n归途\n\n第二天早晨，云层散开。' + '山间的空气格外清新。' * 80
            path.write_text(source, encoding='utf-8')
            hook = Mock(spec=['set_reading_wheel_handler'])
            reader = ReadingController(hook, Path(directory) / 'reader', key_down=lambda _: False)
            font = QFont('Microsoft YaHei')
            font.setPixelSize(27)
            try:
                reader._finish_import(import_document(path, True), '')
                reader.setEnabled(True)
                reader.setViewport(400, 230, font)
                for continuous in (False, True):
                    reader._change(continuous_scroll=continuous)
                    reader.jumpToChapter(1)
                    self.assertTrue(reader.text.startswith('归途\n第二天早晨'), repr(reader.text))
                    self.assertNotIn('天亮以后继续出发', reader.text)
                    before = reader.text
                    reader.move(1)
                    reader.move(-1)
                    self.assertEqual(reader.text, before)
                    reader.setViewport(340, 230, font)
                    self.assertTrue(reader.text.startswith('归途\n'))
                    restored = ReadingController(hook, Path(directory) / 'reader', key_down=lambda _: False)
                    try:
                        restored.setViewport(340, 230, font)
                        self.assertTrue(restored.text.startswith('归途\n'))
                    finally:
                        restored.close()
                # Layout adds only whitespace, never loses or repeats book content.
                rendered = ''.join(line[2] for line in reader._lines)
                self.assertEqual(re.sub(r'\s', '', rendered), re.sub(r'\s', '', source))
            finally:
                reader.close()
