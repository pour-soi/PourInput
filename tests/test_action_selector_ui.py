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

    def assert_category(self, selector, selected):
        self.assertEqual(selector.property("activeCategory"), selected)
        visible_actions = set()
        for category in self.backend.actionCategories:
            active = category["category"] == selected
            self.assertEqual(self.find(selector, "category_" + category["category"]).property("checked"), active)
            for action in category["actions"]:
                chip = self.find(selector, "action_" + action["id"])
                self.assertIsNotNone(chip)
                self.assertEqual(chip.isVisible(), active, action["id"])
                self.assertEqual(chip.parentItem().parentItem().isVisible(), active, category["category"])
                if chip.isVisible():
                    visible_actions.add(action["id"])
        self.assertTrue(visible_actions)

    def test_single_category_navigation_selected_action_and_languages(self):
        self.backend.setProfileMapping("default", "middle_long", "copy")
        QTest.qWait(2200)  # Let the existing saved toast expire before captures.
        self.evaluate('selectButton("middle")')
        QTest.qWait(320)
        selector = self.window.findChild(QObject, "buttonActionSelector")
        mappings = self.backend._cfg["profiles"]["default"]["mappings"]
        original = copy.deepcopy(mappings)
        self.assert_category(selector, "Screenshot")
        self.assertTrue(self.find(selector, "action_screenshot_region_clip").property("isCurrent"))
        self.screenshot("category-before-click")
        header = self.find(selector, "category_Browser")
        point = header.mapToScene(header.boundingRect().center()).toPoint()
        QTest.mouseClick(self.window, Qt.LeftButton, Qt.NoModifier, point)
        QTest.qWait(50)
        self.assert_category(selector, "Browser")
        QTest.mouseClick(self.window, Qt.LeftButton, Qt.NoModifier, point)
        QTest.qWait(50)
        self.assert_category(selector, "Browser")
        self.assertEqual(mappings, original)
        self.assertEqual(selector.property("currentAction"), "screenshot_region_clip")
        header.setProperty("focus", False)  # Keep navigation focus out of review captures.

        # Reopening the editor restores the assigned category, not the last browsed one.
        self.evaluate('selectButton("middle")')
        QTest.qWait(320)
        self.evaluate('selectButton("middle")')
        QTest.qWait(320)
        self.assert_category(selector, "Screenshot")
        tabs = self.window.findChild(QObject, "buttonTabs")
        for language in ("en", "zh_CN"):
            self.lm.setLanguage(language)
            if language == "zh_CN":
                self.assertEqual(self.lm.trCategory("Mouse"), "鼠标")
            for width, height in ((920, 620), (1280, 900)):
                self.window.resize(width, height)
                for category in ("Screenshot", "Media", "Navigation"):
                    self.call(self.find(selector, "category_" + category), "clicked")
                    self.assert_category(selector, category)
                    self.assertEqual(mappings, original)
                    self.screenshot(f"category-{category.lower()}-{language}-{width}")
                    for entry in self.backend.actionCategories:
                        button = self.find(selector, "category_" + entry["category"])
                        self.assertLessEqual(button.width(), selector.width())
                tabs.setProperty("currentIndex", 1)
                QTest.qWait(50)
                self.assertEqual(mappings, original)
                self.assertEqual(selector.property("currentAction"), mappings.get("middle_long", "none"))
                self.assert_category(selector, "Editing")
                self.assertTrue(self.find(selector, "action_copy").property("isCurrent"))
                self.screenshot(f"long-press-{language}-{width}")
                tabs.setProperty("currentIndex", 0)
                QTest.qWait(50)
                self.assert_category(selector, "Screenshot")
                self.assertTrue(self.find(selector, "action_screenshot_region_clip").property("isCurrent"))
        from core.key_simulator import ACTIONS
        for action in ACTIONS.values():
            self.assertNotEqual(self.lm.trAction(action["label"]), action["label"])
        self.assertEqual([w for w in self.warnings if "Only binding to one of multiple key bindings" not in w], [])

    def test_gesture_grid_preserves_independent_actions_and_threshold(self):
        self.backend._effective_supported_buttons.update(
            {"gesture_left", "gesture_right", "gesture_up", "gesture_down"})
        self.backend.mappingsChanged.emit()
        self.evaluate('selectButton("gesture")')
        QTest.qWait(350)
        mappings = self.backend._cfg["profiles"]["default"]["mappings"]
        threshold = self.backend.gestureThreshold
        actions = list(self.backend.allActions)
        for direction, aid in (("Tap", "copy"), ("Left", "paste"), ("Right", "cut"), ("Up", "undo"), ("Down", "select_all")):
            combo = self.window.findChild(QObject, "gesture" + direction + "Selector")
            before = copy.deepcopy(mappings)
            index = next(i for i, action in enumerate(actions) if action["id"] == aid)
            self.assertTrue(QMetaObject.invokeMethod(combo, "activated", Q_ARG(int, index)))
            key = "gesture" if direction == "Tap" else "gesture_" + direction.lower()
            self.assertEqual(mappings[key], aid)
            self.assertEqual({k: v for k, v in mappings.items() if k != key},
                             {k: v for k, v in before.items() if k != key})
        original = copy.deepcopy(mappings)
        QTest.qWait(2200)  # Capture after the existing saved toast has expired.
        for language in ("en", "zh_CN"):
            self.lm.setLanguage(language)
            for width, height in ((920, 620), (1280, 900), (1600, 900)):
                self.window.resize(width, height)
                QTest.qWait(350)
                grid = self.window.findChild(QObject, "gestureSwipeGrid")
                self.assertEqual(grid.property("columns"), 2)
                self.assertEqual(self.backend.gestureThreshold, threshold)
                self.assertEqual(mappings, original)
                for direction in ("Tap", "Left", "Right", "Up", "Down"):
                    combo = self.window.findChild(QObject, "gesture" + direction + "Selector")
                    self.assertEqual(combo.height(), 42)
                    self.assertGreaterEqual(combo.width(), 280)
                    self.assertLessEqual(combo.width(), self.window.findChild(QObject, "gestureEditor").width())
                    key = "gesture" if direction == "Tap" else "gesture_" + direction.lower()
                    self.assertEqual(actions[combo.property("currentIndex")]["id"], mappings[key])
                self.screenshot(f"gesture-{language}-{width}")
        combo = self.window.findChild(QObject, "gestureLeftSelector")
        index = next(i for i, action in enumerate(actions) if action["id"] == "__custom__")
        self.assertTrue(QMetaObject.invokeMethod(combo, "activated", Q_ARG(int, index)))
        dialog = self.window.findChild(QObject, "keyCaptureDialog")
        self.assertEqual(dialog.property("targetButton"), "gesture_left")
        self.call(dialog, "captured", "ctrl+shift+k")
        self.call(dialog, "close")
        self.assertEqual(mappings["gesture_left"], "custom:ctrl+shift+k")
        self.assertEqual(mappings["gesture_right"], original["gesture_right"])

    def test_gesture_grid_reflows_only_when_two_controls_cannot_fit(self):
        self.window.resize(1600, 900)
        self.evaluate('selectButton("gesture")')
        editor = self.window.findChild(QObject, "gestureEditor")
        grid = self.window.findChild(QObject, "gestureSwipeGrid")
        mappings = copy.deepcopy(self.backend._cfg["profiles"])
        threshold = self.backend.gestureThreshold
        for language in ("en", "zh_CN"):
            self.lm.setLanguage(language)
            for available, columns in ((560, 1), (579, 1), (580, 2), (637, 2)):
                editor.setProperty("width", available)
                QTest.qWait(350)
                self.assertEqual(grid.width(), available)
                self.assertEqual(grid.property("columns"), columns)
                left = self.window.findChild(QObject, "gestureLeftSelector")
                right = self.window.findChild(QObject, "gestureRightSelector")
                left_pos = left.mapToScene(left.boundingRect().topLeft())
                right_pos = right.mapToScene(right.boundingRect().topLeft())
                if columns == 2:
                    self.assertAlmostEqual(left_pos.y(), right_pos.y())
                    self.assertGreaterEqual(right_pos.x() - left_pos.x(), left.width() + 20)
                else:
                    self.assertGreater(right_pos.y(), left_pos.y())
                for direction in ("Left", "Right", "Up", "Down"):
                    control = self.window.findChild(QObject, "gesture" + direction + "Selector")
                    self.assertGreaterEqual(control.width(), 280)
                    self.assertEqual(control.height(), 42)
                self.assertEqual(self.backend._cfg["profiles"], mappings)
                self.assertEqual(self.backend.gestureThreshold, threshold)

    def test_horizontal_polish_languages_and_sizes(self):
        self.evaluate('selectHScroll()')
        tabs = self.window.findChild(QObject, "scrollTabs")
        mappings = copy.deepcopy(self.backend._cfg["profiles"])
        for language in ("en", "zh_CN"):
            self.lm.setLanguage(language)
            for width, height in ((920, 620), (1280, 900)):
                self.window.resize(width, height)
                for side in (0, 1):
                    tabs.setProperty("currentIndex", side)
                    self.screenshot(f"horizontal-{'left' if side == 0 else 'right'}-{language}-{width}")
                    self.assertEqual(self.backend._cfg["profiles"], mappings)

    def test_horizontal_tabs_independent_and_custom_targets(self):
        self.evaluate("selectHScroll()")
        QTest.qWait(320)
        tabs = self.window.findChild(QObject, "scrollTabs")
        selector = self.window.findChild(QObject, "horizontalActionSelector")
        mappings = self.backend._cfg["profiles"]["default"]["mappings"]
        original = copy.deepcopy(mappings)
        tabs.setProperty("currentIndex", 1)
        self.assertEqual(mappings, original)
        QTest.qWait(50)
        self.assertEqual(selector.property("currentAction"), "screenshot_region_file")
        self.assert_category(selector, "Screenshot")
        self.call(self.find(selector, "category_Media"), "clicked")
        self.assert_category(selector, "Media")
        self.assertEqual(mappings, original)
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
            self.assert_category(selector, "Custom")
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
                    QTest.qWait(50)
                    self.assert_category(selector, "Screenshot" if side == 0 else "Editing")
                    self.assertEqual(selector.property("currentAction"), "screenshot_region_clip" if side == 0 else "copy")
                    self.screenshot(f"scroll-{'left' if side == 0 else 'right'}-{language}-{width}")

    def test_click_long_press_independence_and_custom_targets(self):
        self.evaluate('selectButton("middle")')
        QTest.qWait(320)
        tabs = self.window.findChild(QObject, "buttonTabs")
        selector = self.window.findChild(QObject, "buttonActionSelector")
        summary = self.window.findChild(QObject, "buttonCurrentActionSummary")
        self.assertIsNotNone(summary)
        self.assertFalse(selector.property("showCurrentAction"))
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
            self.assertEqual(summary.property("text"), self.lm.trAction(
                self.backend.actionLabelFor(mappings.get(target, "none"))))
            self.call(self.find(selector, "category_Navigation"), "clicked")
            self.assert_category(selector, "Navigation")
            self.assertEqual(mappings, before)
            self.call(selector, "picked", "copy")
            self.assert_category(selector, "Editing")
            self.assertEqual(mappings[target], "copy")
            self.assertEqual(mappings.get(other), before.get(other))
            self.call(selector, "picked", "__custom__")
            dialog = self.window.findChild(QObject, "keyCaptureDialog")
            self.assertEqual(dialog.property("targetButton"), target)
            self.call(dialog, "captured", "ctrl+shift+k")
            self.call(dialog, "close")
            self.assertEqual(mappings[target], "custom:ctrl+shift+k")
            self.assertEqual(summary.property("text"), self.lm.trAction(
                self.backend.actionLabelFor(mappings[target])))
            self.assertEqual(mappings.get(other), before.get(other))
            self.assert_category(selector, "Custom")
