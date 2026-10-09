"""Isolated Mouse-page contracts: no real input engine, app catalog, or user data."""
import copy
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QSG_RHI_BACKEND", "software")
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtCore import QObject, QUrl, QMetaObject, Q_ARG, Qt
from PySide6.QtQml import QQmlApplicationEngine, QQmlExpression
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from core.config import DEFAULT_CONFIG
from core.device_layouts import DEVICE_LAYOUTS, get_device_layout
from ui.backend import Backend
from ui.locale_manager import LocaleManager
from ui.reading import ReadingController
from main_qml import UiState, AppIconProvider
from tests.test_backend import _FakeEngine

APP = QApplication.instance() or QApplication([])
# The Windows offscreen plugin does not enumerate system fonts automatically.
if os.name == "nt":
    for name in ("segoeui.ttf", "segoeuib.ttf", "msyh.ttc", "msyhbd.ttc", "seguisym.ttf"):
        QFontDatabase.addApplicationFont(str(Path(os.environ["WINDIR"]) / "Fonts" / name))
    APP.setFont(QFont("Segoe UI", 10))
ROOT = Path(__file__).resolve().parents[1]

@unittest.skipUnless(sys.platform == "win32", "Windows Generic Mouse UI contract")
class MousePageUiTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="pourinput-mouse-ui-")
        self.addCleanup(self.directory.cleanup)
        for target, kwargs in [
            ("ui.backend.save_config", {}),
            ("core.config.save_config", {}),
            ("ui.backend.supports_login_startup", {"return_value": False}),
            ("ui.backend.Backend._cleanupStaleUpdatePreparation", {}),
            ("ui.backend.Backend._configureUpdateChecks", {}),
            ("ui.backend.Backend._consumeUpdateResultMarker", {}),
            ("ui.backend.app_catalog.get_app_catalog", {"return_value": []}),
        ]:
            mock = patch(target, **kwargs)
            mock.start()
            self.addCleanup(mock.stop)
        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg["settings"]["check_for_updates"] = False
        cfg["profiles"]["default"]["mappings"].update(
            middle="screenshot_region_clip", hscroll_left="screenshot_region_clip",
            hscroll_right="screenshot_region_file")
        cfg["profiles"]["editor"] = copy.deepcopy(cfg["profiles"]["default"])
        cfg["profiles"]["editor"].update(label="Example Editor", apps=[])
        self.fake = _FakeEngine(cfg=cfg)
        self.lm = LocaleManager("en")
        self.state = UiState(APP, "en")
        self.lm.languageChanged.connect(lambda: self.state.setLanguage(self.lm.language))
        self.backend = Backend(engine=self.fake, root_dir=str(ROOT), locale_manager=self.lm)
        self.reader = ReadingController(Mock(spec=["set_reading_wheel_handler"]),
                                        self.directory.name, key_down=lambda _: False, locale_manager=self.lm)
        self.qml = QQmlApplicationEngine()
        self.qml.addImageProvider("appicons", AppIconProvider(str(ROOT)))
        context = dict(backend=self.backend, reader=self.reader, uiState=self.state, lm=self.lm,
                       launchHidden=False, appName="PourInput", appVersion="1.4.3",
                       appBuildMode="Source checkout", appCommit="test", appMaintainer="test", appLaunchPath="test")
        for key, value in context.items():
            self.qml.rootContext().setContextProperty(key, value)
        self.warnings = []
        self.qml.warnings.connect(lambda warnings: self.warnings.extend(w.toString() for w in warnings))
        self.device("mx_master_3")
        self.qml.load(QUrl.fromLocalFile(str(ROOT / "ui/qml/Main.qml")))
        self.assertTrue(self.qml.rootObjects(), self.warnings)
        self.window = self.qml.rootObjects()[0]
        self.page = self.window.findChild(QObject, "mousePage")
        self.addCleanup(self.dispose)
        QTest.qWait(150)

    def dispose(self):
        self.window.close()
        self.reader.close()
        self.qml.deleteLater()
        QTest.qWait(20)

    def device(self, key):
        generic = key == "generic_mouse"
        self.backend._cfg["settings"]["generic_mouse_enabled"] = generic
        self.backend._mouse_connected = not generic
        self.backend._device_layout = get_device_layout(key)
        self.backend._effective_supported_buttons = {h["buttonKey"] for h in self.backend._device_layout["hotspots"]}
        self.backend._device_display_name = "Generic Mouse" if generic else self.backend._device_layout["label"]
        self.backend.settingsChanged.emit()
        self.backend.mouseConnectedChanged.emit()
        self.backend.deviceStatusChanged.emit()
        self.backend.deviceLayoutChanged.emit()
        self.backend.mappingsChanged.emit()

    def dots(self):
        def walk(item):
            yield item
            for child in item.childItems():
                yield from walk(child)
        return [item for item in walk(self.window.contentItem())
                if item.objectName().startswith("hotspot_")]

    def evaluate(self, expression):
        expr = QQmlExpression(self.qml.rootContext(), self.page, expression)
        value = expr.evaluate()
        self.assertFalse(expr.hasError(), expr.error().toString())
        return value

    def test_layouts_languages_and_sizes(self):
        for key, layout in DEVICE_LAYOUTS.items():
            if not layout["hotspots"] and key != "generic_mouse":
                continue
            self.device(key)
            for language in ("en", "zh_CN"):
                self.lm.setLanguage(language)
                for width, height in ((920, 620), (1280, 900)):
                    with self.subTest(device=key, language=language, size=(width, height)):
                        self.window.resize(width, height)
                        QTest.qWait(70)
                        image = self.window.findChild(QObject, "mouseMapImage")
                        self.assertGreaterEqual(image.property("y"), 0)
                        self.assertLessEqual(image.property("y") + image.property("height"), image.parentItem().height())
                        image_left = image.property("x")
                        image_right = image_left + image.property("width")
                        dots = self.dots()
                        self.assertEqual(len(dots), len(self.backend.deviceHotspots))
                        rectangles = []
                        for dot in dots:
                            x, y, w, h = (dot.property(p) for p in ("labelX", "labelY", "labelWidth", "labelHeight"))
                            self.assertTrue(x + w <= image_left or x >= image_right)
                            self.assertGreaterEqual(x, 0)
                            self.assertLessEqual(x + w, dot.property("width"))
                            self.assertLessEqual(y + h, dot.property("height"))
                            for a, b, c, d in rectangles:
                                self.assertTrue(x + w <= a or a + c <= x or y + h <= b or b + d <= y)
                            rectangles.append((x, y, w, h))
                        segments = []
                        def cross(a, b, c):
                            return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
                        for dot in dots:
                            self.assertEqual(dot.property("labelSide"), "left" if dot.property("normX") < .5 else "right")
                            points = [(dot.property("cx"), dot.property("cy")),
                                      (dot.property("lineBendX"), dot.property("cy")),
                                      (dot.property("lineEndX"), dot.property("lineEndY"))]
                            for a, b in zip(points, points[1:]):
                                for c, d in segments:
                                    self.assertFalse(cross(a,b,c)*cross(a,b,d) < -0.001
                                                     and cross(c,d,a)*cross(c,d,b) < -0.001,
                                                     "Connector paths cross")
                                segments.append((a,b))
                        for side in ("left", "right"):
                            ordered = sorted([d for d in dots if d.property("labelSide") == side], key=lambda d: d.property("cy"))
                            self.assertEqual([d.property("lineEndY") for d in ordered],
                                             sorted(d.property("lineEndY") for d in ordered))
                        output = os.environ.get("POURINPUT_UI_SCREENSHOTS")
                        if output and key in ("mx_master", "mx_master_3", "mx_master_3s", "mx_master_4", "generic_mouse"):
                            Path(output).mkdir(parents=True, exist_ok=True)
                            self.assertTrue(self.window.grabWindow().save(str(Path(output) / f"{key}-{language}-{width}.png")))
        # Existing Main.qml StandardKey shortcut warning is unrelated to this change.
        self.assertEqual([w for w in self.warnings if "Only binding to one of multiple key bindings" not in w], [])

    def test_long_english_and_chinese_labels_wrap_without_truncation(self):
        self.window.resize(920, 620)
        for language in ("en", "zh_CN"):
            self.lm.setLanguage(language)
            for index, dot in enumerate(self.dots()):
                dot.setProperty("label", "Horizontal scroll left" if index % 2 else "Horizontal scroll right")
                dot.setProperty("sublabel", "Screenshot Region → Clipboard | Screenshot Region → File")
            QTest.qWait(70)
            bottom = {"left": 0, "right": 0}
            for dot in sorted(self.dots(), key=lambda d: d.property("cy")):
                side = dot.property("labelSide")
                self.assertGreaterEqual(dot.property("labelY"), bottom[side])
                bottom[side] = dot.property("labelY") + dot.property("labelHeight")
                self.assertLessEqual(bottom[side], dot.property("height"))
                def texts(item):
                    for child in item.childItems():
                        if child.property("text") is not None:
                            yield child
                        yield from texts(child)
                for text in texts(dot):
                    self.assertFalse(text.property("truncated"))
            output = os.environ.get("POURINPUT_UI_SCREENSHOTS")
            if output:
                self.assertTrue(self.window.grabWindow().save(str(Path(output) / f"long-labels-{language}-920.png")))

    def test_profile_selection_and_automatic_switch_keep_correct_mapping(self):
        selector = self.window.findChild(QObject, "profileSelector")
        profiles = self.backend.profiles
        index = next(i for i, p in enumerate(profiles) if p["name"] == "editor")
        QMetaObject.invokeMethod(selector, "activated", Q_ARG(int, index))
        self.assertEqual(self.page.property("selectedProfile"), "editor")
        add = self.window.findChild(QObject, "addProfileButton")
        self.assertTrue(add.property("visible"))
        self.assertGreater(add.property("width"), 20)
        self.assertGreater(add.property("contentItem").width(), 10)
        QTest.mouseClick(self.window, Qt.LeftButton, pos=add.mapToScene(add.boundingRect().center()).toPoint())
        self.assertTrue(self.page.property("hasBlockingDialog"))
        QMetaObject.invokeMethod(self.window.findChild(QObject, "addAppDialog"), "close")
        QTest.qWait(350)
        self.backend._cfg["active_profile"] = "default"
        self.backend.activeProfileChanged.emit()
        self.assertEqual(self.page.property("selectedProfile"), "default")
        self.evaluate('selectButton("middle")')
        self.assertEqual(self.page.property("selectedButton"), "middle")
        self.assertTrue(self.window.findChild(QObject, "mouseMapImage").property("visible"))
        dot = next(dot for dot in self.dots() if dot.objectName() == "hotspot_middle")
        self.assertTrue(dot.property("isSelected"))
        self.backend._cfg["profiles"]["default"]["mappings"]["middle"] = "none"
        self.backend._cfg["profiles"]["default"]["mappings"]["middle_long"] = "none"
        self.backend.mappingsChanged.emit()
        self.assertFalse(dot.property("configured"))
        self.backend._cfg["profiles"]["default"]["mappings"]["middle"] = "copy"
        self.backend.mappingsChanged.emit()
        self.assertTrue(dot.property("configured"))
        output = os.environ.get("POURINPUT_UI_SCREENSHOTS")
        if output:
            self.window.resize(1280, 900)
            QTest.qWait(100)
            self.assertTrue(self.window.grabWindow().save(str(Path(output) / "selected-editor-en-1280.png")))

    def test_delete_nondefault_profile_uses_confirmation_and_preserves_default(self):
        button = self.window.findChild(QObject, "deleteProfileButton")
        self.assertFalse(button.property("visible"))
        self.evaluate('selectProfile("editor")')
        QTest.qWait(40)
        self.assertTrue(button.property("visible"))
        QTest.mouseClick(self.window, Qt.LeftButton, pos=button.mapToScene(button.boundingRect().center()).toPoint())
        self.assertTrue(self.page.property("hasBlockingDialog"))
        self.assertIn("editor", self.backend._cfg["profiles"])
        QMetaObject.invokeMethod(self.window.findChild(QObject, "deleteProfileDialog"), "accept")
        self.assertNotIn("editor", self.backend._cfg["profiles"])
        self.assertIn("default", self.backend._cfg["profiles"])

    def test_generic_visual_does_not_change_device_capabilities(self):
        original = copy.deepcopy(self.backend._device_layout)
        self.backend._cfg["settings"]["generic_mouse_enabled"] = True
        self.assertEqual(self.backend.deviceImageAsset, original["image_asset"])
        self.device("generic_mouse")
        self.assertEqual({h["buttonKey"] for h in self.backend.deviceHotspots},
                         {"middle", "generic_xbutton1", "generic_xbutton2"})
        self.assertEqual(self.backend._device_layout, get_device_layout("generic_mouse"))
        self.backend._cfg["settings"]["generic_mouse_enabled"] = False
        self.assertEqual(self.backend.deviceHotspots, [])
        self.assertFalse(self.backend.hasInteractiveDeviceLayout)

    def test_responsive_header_reflows_without_changing_assignments(self):
        self.device("mx_master_4")
        self.backend._battery_level = 45
        self.backend.batteryLevelChanged.emit()
        self.evaluate('selectButton("middle")')
        from PySide6.QtCore import QPointF
        heading = self.window.findChild(QObject, "mousePageHeading")
        profiles = self.window.findChild(QObject, "profileControls")
        tabs = self.window.findChild(QObject, "buttonTabs")
        summary = self.window.findChild(QObject, "buttonSummaryRow")
        mappings = copy.deepcopy(self.backend._cfg["profiles"])
        top = lambda item: item.mapToScene(QPointF(0, 0)).y()
        for language in ("en", "zh_CN"):
            self.lm.setLanguage(language)
            for width, height, compact in ((920, 620, True), (1280, 900, False), (1024, 768, True), (1920, 1080, False), (1280, 900, False)):
                self.window.resize(width, height)
                QTest.qWait(350)
                self.assertEqual(self.page.property("compactLayout"), compact)
                device = self.window.findChild(QObject, "mouseDeviceColumn")
                editor = self.window.findChild(QObject, "mouseEditorColumn")
                self.assertEqual(self.page.property("wideLayout"), width == 1920)
                if width == 1920:
                    self.assertAlmostEqual(top(device), top(editor))
                    self.assertGreaterEqual(editor.x(), device.width())
                    self.assertLessEqual(editor.x() + editor.width(), self.page.width())
                    self.assertGreaterEqual(top(summary), top(tabs) + tabs.height())
                else:
                    self.assertGreaterEqual(top(editor), top(device) + device.height())
                if compact:
                    self.assertGreaterEqual(top(profiles), top(heading) + heading.height())
                    self.assertGreaterEqual(top(summary), top(tabs) + tabs.height())
                else:
                    self.assertLess(abs(top(profiles) - top(heading)), 30)
                    if width != 1920:
                        self.assertLess(abs(top(summary) - top(tabs)), tabs.height())
                self.assertAlmostEqual(tabs.width(), 240)
                self.assertEqual(self.backend._cfg["profiles"], mappings)
                output = os.environ.get("POURINPUT_UI_SCREENSHOTS")
                if output and width != 1024:
                    picker = self.window.findChild(QObject, "actionPicker")
                    scroll = picker.parentItem()
                    while scroll is not None and scroll.property("contentY") is None:
                        scroll = scroll.parentItem()
                    scroll.setProperty("contentY", 0)
                    QTest.qWait(80)
                    self.window.grabWindow().save(str(Path(output) / f"responsive-top-{language}-{width}.png"))
                    y = picker.mapToItem(scroll.property("contentItem"), QPointF(0, 0)).y()
                    scroll.setProperty("contentY", min(y - 12, max(0, scroll.property("contentHeight") - scroll.height())))
                    QTest.qWait(80)
                    self.window.grabWindow().save(str(Path(output) / f"responsive-actions-{language}-{width}.png"))
        self.assertEqual([w for w in self.warnings if "Only binding to one of multiple key bindings" not in w], [])

if __name__ == "__main__":
    unittest.main()
