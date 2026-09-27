import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from core.reader_chapters import inferred_headings
from core.reader_import import import_document
from core.reader import ReaderModel
from tests.test_reading_ui import APP
from ui.reading import ReadingController


class InferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def book(self):
        return '初见\n\n' + '这是正文中的一个完整句子。' * 15 + '\n\n归途\n\n' + '这是另一段较长的正文。' * 15

    def test_detects_isolated_titles_and_keeps_anchors_and_flags(self):
        path = self.root / 'book.txt'
        path.write_text(self.book(), encoding='utf-8')
        _, groups, entries = import_document(path, True)
        self.assertEqual([e['title'] for e in entries], ['初见', '归途'])
        for entry in entries:
            self.assertTrue(entry['inferred'])
            self.assertTrue(groups[entry['group_index']][entry['group_offset']:].startswith(entry['title']))

    def test_does_not_guess_poetry_lists_sentences_or_flattened_legacy_text(self):
        for text in ('初见\n\n一句诗\n\n归途\n\n另一句诗',
                     self.book().replace('初见', '发生了什么？').replace('归途', '后来呢？'),
                     self.book().replace('\n', ' '),
                     self.book().replace('初见', '01').replace('归途', '02')):
            with self.subTest(text=text[:30]):
                self.assertEqual(inferred_headings(text), [])

    def test_explicit_headings_take_priority(self):
        path = self.root / 'book.txt'
        path.write_text('第一章 明确标题\n正文。\n\n' + self.book(), encoding='utf-8')
        entries = import_document(path, True)[2]
        self.assertEqual(len(entries), 1)
        self.assertFalse(entries[0].get('inferred', False))

    def test_confirmation_cancel_and_jump_with_qml_and_reload(self):
        from PySide6.QtCore import QObject, QUrl, QMetaObject, Q_ARG
        from PySide6.QtQuick import QQuickView
        path = self.root / 'book.txt'
        path.write_text(self.book(), encoding='utf-8')
        reader = ReadingController(Mock(spec=['set_reading_wheel_handler']), self.root / 'reader', key_down=lambda _: False)
        self.addCleanup(reader.close)
        reader._finish_import(import_document(path, True), '')
        view = QQuickView()
        view.setInitialProperties({'controller': reader, 'theme': {'textPrimary': '#111', 'textSecondary': '#666', 'bgCard': '#fff'}})
        view.setSource(QUrl.fromLocalFile(str(Path(__file__).resolve().parents[1] / 'ui/qml/ReadingPage.qml')))
        view.resize(900, 800)
        view.show()
        try:
            APP.processEvents()
            page = view.rootObject()
            self.assertIsNotNone(page, str(view.errors()))
            picker = page.findChild(QObject, 'readingChapterPicker')
            dialog = page.findChild(QObject, 'chapterConfirmation')
            before = reader.model.state
            for action in ('reject', 'accept'):
                picker.setProperty('currentIndex', 1)
                self.assertTrue(QMetaObject.invokeMethod(picker, 'activated', Q_ARG(int, 1)))
                self.assertTrue(dialog.property('visible'))
                self.assertEqual(reader.model.state, before)
                self.assertTrue(QMetaObject.invokeMethod(dialog, action))
                if action == 'reject':
                    self.assertEqual(reader.model.state, before)
                else:
                    self.assertEqual(reader.currentChapter, 1)
            restored = ReaderModel(reader.model.store)
            self.assertEqual(restored.state, reader.model.state)
            self.assertTrue(restored.document['chapters'][1]['inferred'])
            reader._locale.setLanguage('zh_CN')
            self.assertTrue(reader.chapterLabels[1]['label'].endswith('（推测）'))
        finally:
            view.close()
