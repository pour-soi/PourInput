"""Phase 2 presentation contracts, using the existing isolated UI fixture."""
import copy
import os
import sys
import unittest
from pathlib import Path
from PySide6.QtCore import QObject, QMetaObject, Q_ARG, Qt
from PySide6.QtTest import QTest
from tests.test_mouse_page_ui import MousePageUiTests

@unittest.skipUnless(sys.platform == "win32", "Windows UI fixture")
class ActionSelectorUiTests(unittest.TestCase):
    setUp = MousePageUiTests.setUp
    dispose = MousePageUiTests.dispose
    evaluate = MousePageUiTests.evaluate

    def device(self, key):
        MousePageUiTests.device(self, key)
        if "hscroll_left" in self.backend._effective_supported_buttons:
            self.backend._effective_supported_buttons.add("hscroll_right")
        self.backend.mappingsChanged.emit()

    def find(self, item, name):
        if item.objectName() == name:
            return item
        for child in item.childItems():
            result = self.find(child, name)
            if result is not None:
                return result
        return None

    def call(self, item, signal, text=None):
        args = () if text is None else (Q_ARG(str, text),)
        self.assertTrue(QMetaObject.invokeMethod(item, signal, *args))
        QTest.qWait(30)

    def screenshot(self, name, target=None):
        QTest.qWait(320)
        picker = self.window.findChild(QObject, "actionPicker")
        target = target or picker
        item = picker.parentItem()
        while item is not None and item.property("contentY") is None:
            item = item.parentItem()
        self.assertIsNotNone(item)
        y = target.mapToItem(item.property("contentItem"), target.boundingRect().topLeft()).y()
        item.setProperty("contentY", min(y - 12, max(0, item.property("contentHeight") - item.height())))
        QTest.qWait(80)
        output = os.environ.get("POURINPUT_UI_SCREENSHOTS")
        if output:
            Path(output).mkdir(parents=True, exist_ok=True)
            self.assertTrue(self.window.grabWindow().save(str(Path(output) / (name + ".png"))))

    def test_categories_selected_action_and_languages(self):
        self.evaluate('selectButton("middle")')
        QTest.qWait(320)
        selector = self.window.findChild(QObject, "buttonActionSelector")
        expected = {a["id"] for c in self.backend.actionCategories for a in c["actions"]}
        for action in expected:
            self.assertIsNotNone(self.find(selector, "action_" + action))
        self.assertTrue(self.find(selector, "category_Screenshot").property("checked"))
        self.assertFalse(self.find(selector, "category_Browser").property("checked"))
        self.screenshot("category-before-click")
        header = self.find(selector, "category_Browser")
        point = header.mapToScene(header.boundingRect().center()).toPoint()
        QTest.mouseClick(self.window, Qt.LeftButton, Qt.NoModifier, point)
        QTest.qWait(50)
        self.assertTrue(self.find(selector, "category_Browser").property("checked"))
        self.assertTrue(self.find(selector, "action_browser_back").isVisible())
        self.call(self.find(selector, "category_Browser"), "clicked")
        QTest.qWait(2200)  # Let the existing saved toast expire before captures.
        for language in ("en", "zh_CN"):
            self.lm.setLanguage(language)
            if language == "zh_CN":
                self.assertEqual(self.lm.trCategory("Mouse"), "\u9f20\u6807")
            for width, height in ((920, 620), (1280, 900)):
                self.window.resize(width, height)
                self.screenshot(f"normal-{language}-{width}")
                for category in self.backend.actionCategories:
                    button = self.find(selector, "category_" + category["category"])
                    self.assertLessEqual(button.width(), selector.width())
            tabs = self.window.findChild(QObject, "buttonTabs")
            tabs.setProperty("currentIndex", 1)
            self.screenshot(f"long-press-{language}")
            tabs.setProperty("currentIndex", 0)
            QTest.qWait(50)
        self.call(self.find(selector, "category_Screenshot"), "clicked")
        self.assertFalse(self.find(selector, "action_screenshot_region_clip").isVisible())
        self.screenshot("collapsed-categories")
        self.evaluate('selectButton("middle")')
        QTest.qWait(320)
        self.evaluate('selectButton("middle")')
        QTest.qWait(320)
        self.assertTrue(self.find(selector, "category_Screenshot").property("checked"))
        self.assertEqual([w for w in self.warnings if "Only binding to one of multiple key bindings" not in w], [])

    def test_horizontal_tabs_independent_and_custom_targets(self):
        self.evaluate("selectHScroll()")
        tabs = self.window.findChild(QObject, "scrollTabs")
        selector = self.window.findChild(QObject, "horizontalActionSelector")
        mappings = self.backend._cfg["profiles"]["default"]["mappings"]
        original = copy.deepcopy(mappings)
        tabs.setProperty("currentIndex", 1)
        self.assertEqual(mappings, original)
        self.assertEqual(selector.property("currentAction"), "screenshot_region_file")
        self.call(selector, "picked", "copy")
        self.assertEqual(mappings["hscroll_right"], "copy")
        self.assertEqual(mappings["hscroll_left"], original["hscroll_left"])
        for side in (0, 1):
            tabs.setProperty("currentIndex", side)
            self.call(selector, "picked", "__custom__")
            dialog = self.window.findChild(QObject, "keyCaptureDialog")
            target = "hscroll_left" if side == 0 else "hscroll_right"
            other = "hscroll_right" if side == 0 else "hscroll_left"
            before = mappings[other]
            self.assertEqual(dialog.property("targetButton"), target)
            self.call(dialog, "captured", "ctrl+shift+k")
            self.call(dialog, "close")
            self.assertEqual(mappings[target], "custom:ctrl+shift+k")
            self.assertEqual(mappings[other], before)
            self.assertTrue(self.find(selector, "category_Custom").property("checked"))
        self.call(selector, "picked", "copy")
        tabs.setProperty("currentIndex", 0)
        self.call(selector, "picked", "screenshot_region_clip")
        self.assertEqual({a["id"] for c in self.backend.actionCategories for a in c["actions"]},
                         {a["id"] for a in self.backend.allActions})
        QTest.qWait(2200)  # Let the existing saved toast expire before captures.
        for language in ("en", "zh_CN"):
            self.lm.setLanguage(language)
            if language == "zh_CN":
                self.assertEqual(self.lm.trCategory("Mouse"), "\u9f20\u6807")
            for width, height in ((920, 620), (1280, 900)):
                self.window.resize(width, height)
                for side in (0, 1):
                    tabs.setProperty("currentIndex", side)
                    self.screenshot(f"scroll-{'left' if side == 0 else 'right'}-{language}-{width}")

    def test_click_long_press_independence_and_custom_targets(self):
        self.evaluate('selectButton("middle")')
        QTest.qWait(320)
        tabs = self.window.findChild(QObject, "buttonTabs")
        selector = self.window.findChild(QObject, "buttonActionSelector")
        mappings = self.backend._cfg["profiles"]["default"]["mappings"]
        for device in ("mx_master_3", "generic_mouse"):
            self.device(device)
            self.assertEqual({a["id"] for c in self.backend.actionCategories for a in c["actions"]},
                             {a["id"] for a in self.backend.allActions})
        for side, target, other in ((1, "middle_long", "middle"), (0, "middle", "middle_long")):
            before = copy.deepcopy(mappings)
            tabs.setProperty("currentIndex", side)
            QTest.qWait(50)
            self.assertEqual(mappings, before)
            self.call(selector, "picked", "copy")
            self.assertEqual(mappings[target], "copy")
            self.assertEqual(mappings.get(other), before.get(other))
            self.call(selector, "picked", "__custom__")
            dialog = self.window.findChild(QObject, "keyCaptureDialog")
            self.assertEqual(dialog.property("targetButton"), target)
            self.call(dialog, "captured", "ctrl+shift+k")
            self.call(dialog, "close")
            self.assertEqual(mappings[target], "custom:ctrl+shift+k")
            self.assertEqual(mappings.get(other), before.get(other))
            self.assertTrue(self.find(selector, "category_Custom").property("checked"))
