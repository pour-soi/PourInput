import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock

from core.reader import ReaderStore, ReaderModel
from core.reader_import import import_document
from tests.test_reading_ui import APP
from ui.reading import ReadingController


class ChapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def txt(self):
        path = self.root / 'book.txt'
        path.write_text('序言\n开头。\n第一章 初见\n' + '正文😀。' * 80 + '\n第二章 重逢\n结束。', encoding='utf-8')
        return import_document(path, with_chapters=True)

    def test_txt_anchors_preserve_titles_and_match_body_across_groups(self):
        title, groups, chapters = self.txt()
        self.assertEqual([c['title'] for c in chapters], ['序言', '第一章 初见', '第二章 重逢'])
        for entry in chapters:
            tail = groups[entry['group_index']][entry['group_offset']:] + ''.join(groups[entry['group_index'] + 1:])
            self.assertTrue(tail.startswith(entry['title'].split()[0]))
        store = ReaderStore(self.root / 'reader')
        model = ReaderModel(store)
        model.open_document(title, groups, chapters)
        self.assertEqual(ReaderModel(store).document['chapters'], chapters)

    def epub(self, ncx=False):
        path = self.root / 'book.epub'
        nav_item = '<item id="toc" href="toc.ncx" media-type="application/x-dtbncx+xml"/>' if ncx else '<item id="toc" href="nav.xhtml" properties="nav" media-type="application/xhtml+xml"/>'
        with zipfile.ZipFile(path, 'w') as z:
            z.writestr('META-INF/container.xml', '<container><rootfile full-path="OPS/book.opf"/></container>')
            z.writestr('OPS/book.opf', '<package><manifest>' + nav_item + '<item id="body" href="body.xhtml" media-type="application/xhtml+xml"/></manifest><spine><itemref idref="body"/></spine></package>')
            z.writestr('OPS/body.xhtml', '<html><body><p>Intro 😀.</p><h1 id="one">Arrival</h1><p>' + 'Text. ' * 60 + '</p><h1 id="two">Return</h1><p>End.</p></body></html>')
            if ncx:
                z.writestr('OPS/toc.ncx', '<ncx><navMap><navPoint><navLabel><text>Arrival</text></navLabel><content src="body.xhtml#one"/></navPoint><navPoint><navLabel><text>Return</text></navLabel><content src="body.xhtml#two"/></navPoint></navMap></ncx>')
            else:
                z.writestr('OPS/nav.xhtml', '<html xmlns:epub="http://www.idpf.org/2007/ops"><nav epub:type="toc"><ol><li><a href="body.xhtml#one">Arrival</a><ol><li><a href="body.xhtml#two">Return</a></li></ol></li></ol></nav></html>')
        return import_document(path, with_chapters=True)

    def test_epub3_and_epub2_fragment_targets(self):
        for ncx in (False, True):
            with self.subTest(ncx=ncx):
                _, groups, chapters = self.epub(ncx)
                self.assertEqual([c['title'] for c in chapters], ['Arrival', 'Return'])
                for entry in chapters:
                    self.assertTrue(groups[entry['group_index']][entry['group_offset']:].startswith(entry['title']))

    def test_legacy_directory_does_not_write_or_move_reader(self):
        store = ReaderStore(self.root / 'reader')
        model = ReaderModel(store)
        model.open_document('Old', ['第一章 开始。内容。 第二章 结束。'])
        model.update(group_offset=12)
        before = {p: p.read_bytes() for p in store.directory.rglob('*.json')}
        reader = ReadingController(Mock(spec=['set_reading_wheel_handler']), store.directory, key_down=lambda _: False)
        self.addCleanup(reader.close)
        self.assertTrue(reader.chaptersEstimated)
        self.assertEqual(len(reader.chapters), 2)
        self.assertEqual(reader.model.state.group_offset, 12)
        self.assertEqual(before, {p: p.read_bytes() for p in store.directory.rglob('*.json')})

    def test_jump_persists_anchor_without_changing_hide_enabled_or_wheel(self):
        reader = ReadingController(Mock(spec=['set_reading_wheel_handler']), self.root / 'reader', key_down=lambda _: False)
        self.addCleanup(reader.close)
        reader._finish_import(self.txt(), '')
        reader.setEnabled(True)
        reader.setHideKey(5)
        reader._observe_button(5, True)
        reader._observe_button(5, False)
        _, epoch, _ = reader._gate.feed(0)
        reader.jumpToChapter(2)
        entry = reader.chapters[2]
        state = reader.model.state
        self.assertEqual((state.group_index, state.group_offset), (entry['group_index'], entry['group_offset']))
        self.assertTrue(reader.enabled)
        self.assertTrue(reader.model.hidden)
        self.assertTrue(reader._gate.accepts(epoch))
        self.assertEqual(ReaderModel(reader.model.store).state, state)
        self.assertEqual(reader.currentChapter, 2)
        reader.jumpToChapter(999)
        self.assertEqual(reader.model.state, state)

    def test_invalid_saved_chapter_fails_without_overwriting_document(self):
        store = ReaderStore(self.root / 'reader')
        doc = store.save_document('Book', ['Text'])
        path = store.directory / 'documents' / (doc + '.json')
        value = json.loads(path.read_text(encoding='utf-8'))
        value['chapters'] = [{'title': 'Bad', 'group_index': 99, 'group_offset': 0}]
        path.write_text(json.dumps(value), encoding='utf-8')
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            store.load_document(doc)
        self.assertEqual(path.read_bytes(), before)

    def test_no_headings_and_english_txt_headings(self):
        path = self.root / 'english.txt'
        path.write_text('Ordinary text. No chapters.', encoding='utf-8')
        self.assertEqual(import_document(path, True)[2], [])
        path.write_text('Chapter 1 Arrival\nBody.\nChapter II Return\nEnd.', encoding='utf-8')
        self.assertEqual([e['title'] for e in import_document(path, True)[2]],
                         ['Chapter 1 Arrival', 'Chapter II Return'])

    def test_epub_without_toc_uses_heading_tags(self):
        self.epub()
        original = self.root / 'book.epub'
        fallback = self.root / 'fallback.epub'
        with zipfile.ZipFile(original) as source, zipfile.ZipFile(fallback, 'w') as target:
            for name in source.namelist():
                data = source.read(name)
                if name == 'OPS/book.opf':
                    data = data.replace(b'properties="nav"', b'')
                target.writestr(name, data)
        self.assertEqual([e['title'] for e in import_document(fallback, True)[2]], ['Arrival', 'Return'])

    def test_qml_chapter_selection_and_bilingual_labels(self):
        from PySide6.QtCore import QObject, QUrl, QMetaObject, Q_ARG
        from PySide6.QtQml import QQmlComponent, QQmlEngine
        reader = ReadingController(Mock(spec=['set_reading_wheel_handler']), self.root / 'reader', key_down=lambda _: False)
        self.addCleanup(reader.close)
        reader._finish_import(self.txt(), '')
        engine = QQmlEngine()
        component = QQmlComponent(engine, QUrl.fromLocalFile(str(Path(__file__).resolve().parents[1] / 'ui/qml/ReadingPage.qml')))
        page = component.createWithInitialProperties({'controller': reader, 'theme': {'textPrimary': '#111', 'textSecondary': '#666', 'bgCard': '#fff'}})
        self.assertIsNotNone(page, str(component.errors()))
        try:
            picker = page.findChild(QObject, 'readingChapterPicker')
            self.assertEqual(picker.property('count'), 3)
            picker.setProperty('currentIndex', 2)
            self.assertTrue(QMetaObject.invokeMethod(picker, 'activated', Q_ARG(int, 2)))
            self.assertEqual(reader.currentChapter, 2)
            self.assertFalse(reader.enabled)  # Selecting while off must not claim wheel.
            reader._locale.setLanguage('zh_CN')
            self.assertEqual(reader.strings['reading.chapters'], '章节目录')
            reader._locale.setLanguage('en')
            self.assertEqual(reader.strings['reading.chapters'], 'Chapters')
        finally:
            page.deleteLater()


if __name__ == '__main__':
    unittest.main()
