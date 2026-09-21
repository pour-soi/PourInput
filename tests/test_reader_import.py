import tempfile
import unittest
from pathlib import Path
import zipfile

from core.reader_import import group_sentences, import_document, _epub_member


class ReaderImportTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_short_mixed_text_preserves_punctuation_and_decimals(self):
        text = 'Dr. Ivy paid 3.14 dollars. “Hello!” 第一句。第二句？第三句！'
        self.assertEqual(group_sentences(text), [text])

    def test_balanced_groups_preserve_all_text_with_mixed_sentence_lengths(self):
        import re
        for text in ("字" * 1500, ("短。" * 12 + "长" * 180 + "，结束。") * 8,
                     ("A short sentence. " + "another word " * 35) * 5):
            with self.subTest(text_length=len(text)):
                groups = group_sentences(text)
                lengths = [len(group) for group in groups]
                self.assertGreaterEqual(min(lengths), 90)
                self.assertLessEqual(max(lengths), 150)
                self.assertEqual(re.sub(r"\s", "", "".join(groups)), re.sub(r"\s", "", text))

    def test_nearby_punctuation_preferred_and_small_tail_balanced(self):
        self.assertEqual(group_sentences("甲" * 109 + "，" + "乙" * 130),
                         ["甲" * 109 + "，", "乙" * 130])
        self.assertEqual([len(g) for g in group_sentences("字" * 250)], [125, 125])

    def test_txt_encodings(self):
        for encoding in ("utf-8-sig", "utf-16", "gb18030"):
            with self.subTest(encoding=encoding):
                path = self.root / "book.txt"
                path.write_bytes("你好。再见！".encode(encoding))
                self.assertEqual(import_document(path), ("book", ["你好。再见！"]))

    def test_epub_uses_spine_order_and_ignores_script_and_head(self):
        path = self.root / "book.epub"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("META-INF/container.xml", '<container><rootfiles><rootfile full-path="OPS/book.opf"/></rootfiles></container>')
            archive.writestr("OPS/book.opf", '<package><manifest><item id="a" href="a.xhtml" media-type="application/xhtml+xml"/><item id="b" href="b.xhtml" media-type="application/xhtml+xml"/></manifest><spine><itemref idref="b"/><itemref idref="a"/></spine></package>')
            archive.writestr("OPS/a.xhtml", '<html xmlns="http://www.w3.org/1999/xhtml"><body><p>Last.</p></body></html>')
            archive.writestr("OPS/b.xhtml", '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>Ignore.</title></head><body><script>Ignore.</script><p>First &amp; second.</p></body></html>')
        self.assertEqual(import_document(path), ("book", ["First & second. Last."]))

    def test_nonlocal_epub_paths_rejected(self):
        for href in ("../../escape", "https://example.com/a", "/absolute", "%2e%2e/%2e%2e/escape"):
            with self.subTest(href=href), self.assertRaises(ValueError):
                _epub_member("OPS", href)

    def test_empty_and_invalid_imports_fail(self):
        path = self.root / "empty.txt"
        path.write_text("   ")
        with self.assertRaises(ValueError):
            import_document(path)
        path = self.root / "invalid.epub"
        path.write_bytes(b"not a zip")
        with self.assertRaises(zipfile.BadZipFile):
            import_document(path)

