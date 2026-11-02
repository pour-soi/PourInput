"""Brand visibility must preserve page identity and the existing usable viewport."""
import copy
import unittest

from PySide6.QtCore import QObject, QPointF
from PySide6.QtTest import QTest
from tests import test_mouse_page_ui as fixture


class BrandIdentityUiTests(unittest.TestCase):
    setUp = fixture.MousePageUiTests.setUp
    dispose = fixture.MousePageUiTests.dispose
    device = fixture.MousePageUiTests.device

    def items(self):
        def walk(item):
            yield item
            for child in item.childItems():
                yield from walk(child)
        return list(walk(self.window.contentItem()))

    def test_brand_and_localized_page_identity_fit_without_taking_content_height(self):
        config = copy.deepcopy(self.backend._cfg)
        reading_state = copy.deepcopy(self.reader.model.state)
        for mode in ("light", "dark"):
            self.state.appearanceMode = mode
            for language in ("en", "zh_CN"):
                self.lm.setLanguage(language)
                for width, height in ((920, 620), (1280, 900), (1600, 900)):
                    self.window.resize(width, height)
                    for number, name in ((0, "mousePage"), (2, "readingPage"), (1, "settingsScroll")):
                        with self.subTest(mode=mode, language=language, width=width, page=name):
                            self.window.setProperty("currentPage", number)
                            QTest.qWait(40)
                            items = self.items()
                            brands = [item for item in items if item.isVisible() and item.property("text") == "PourInput"]
                            self.assertEqual(len(brands), 1)
                            brand = brands[0]
                            title = self.lm.trCategory("Mouse") if number == 0 else self.lm.strings[
                                "reading.title" if number == 2 else "scroll.title"]
                            labels = [item for item in brand.childItems() if str(item.property("text") or "").strip().endswith(title)]
                            self.assertEqual(len(labels), 1)
                            label = labels[0]
                            self.assertGreaterEqual(label.x(), brand.implicitWidth())
                            self.assertLessEqual(label.mapToScene(QPointF(label.width(), 0)).x(), width - 28)
                            self.assertLessEqual(label.height(), brand.height())
                            palette = self.window.property("theme").toVariant()
                            self.assertEqual(brand.property("color").name(), palette["textPrimary"])
                            self.assertEqual(label.property("color").name(), palette["textSecondary"])
                            # A separate brand row would reduce the page's usable height.
                            page = self.window.findChild(QObject, name)
                            self.assertEqual(page.mapToScene(QPointF()).y(), 0)
                            self.assertEqual(page.height(), height)
        self.assertEqual(self.backend._cfg, config)
        self.assertEqual(self.reader.model.state, reading_state)

    def test_enlarged_rail_logo_preserves_navigation_and_control_sizes(self):
        reference_sizes = None
        for language in ("en", "zh_CN"):
            self.lm.setLanguage(language)
            for width, height in ((920, 620), (1280, 900), (1600, 900)):
                self.window.resize(width, height)
                QTest.qWait(40)
                items = self.items()
                logos = [item for item in items if "logo_icon.png" in str(item.property("source") or "")]
                self.assertEqual(len(logos), 1)
                logo = logos[0]
                self.assertEqual((logo.width(), logo.height()), (56, 56))
                nav = [item for item in items if item.property("name") == "mouse-simple" and item.width() == 20][0]
                # Existing navigation target remains at the same desktop position.
                self.assertEqual(nav.mapToScene(QPointF()).y(), 110)
                sizes = [(self.window.findChild(QObject, key).width(), self.window.findChild(QObject, key).height())
                         for key in ("profileSelector", "addProfileButton", "deviceSelector")]
                if reference_sizes is None:
                    reference_sizes = sizes
                self.assertEqual(sizes, reference_sizes)
                self.assertTrue(all(h == 42 for _, h in sizes))
