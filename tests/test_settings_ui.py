"""Settings renders with isolated configuration; no startup or update actions run."""
import os
import unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QObject
from PySide6.QtTest import QTest
from PySide6.QtGui import QFont, QTextLayout
from tests.test_mouse_page_ui import MousePageUiTests, APP
from ui.font_policy import apply_application_font

class SettingsUiTests(unittest.TestCase):
    setUp = MousePageUiTests.setUp
    dispose = MousePageUiTests.dispose
    device = MousePageUiTests.device

    def test_languages_sizes_and_font_fallback(self):
        with patch('ui.backend.supports_login_startup', return_value=True):
            self.fake.smart_shift_supported = True
            self.backend._hid_features_ready = True
            self.window.setProperty('currentPage', 1)
            QTest.qWait(150)
            page = self.window.findChild(QObject, 'settingsPage')
            scroll = page.findChild(QObject, 'settingsScroll')
            flick = scroll.property('contentItem')
            output = os.environ.get('POURINPUT_SETTINGS_SCREENSHOTS')
            for language in ('en', 'zh_CN'):
                self.lm.setLanguage(language)
                for width, height in ((1280,900),(920,620)):
                    self.window.resize(width,height)
                    QTest.qWait(150)
                    for key in ('top','languageContent','startupContent','screenshotContent'):
                        target = page.findChild(QObject,key) if key != 'top' else None
                        y = target.mapToItem(flick.property('contentItem'),target.boundingRect().topLeft()).y()-24 if target else 0
                        flick.setProperty('contentY',min(y,max(0,flick.property('contentHeight')-flick.height())))
                        QTest.qWait(180)
                        if output:
                            Path(output).mkdir(parents=True,exist_ok=True)
                            self.assertTrue(self.window.grabWindow().save(str(Path(output)/f'{key}-{language}-{width}.png')))
            self.assertEqual([w for w in self.warnings if 'Only binding to one of multiple key bindings' not in w],[])
        apply_application_font(APP, 'en', QFont('Segoe UI',10))
        for bold in (False,True):
            font=QFont('Segoe UI',10); font.setBold(bold)
            layout=QTextLayout('English / 简体中文',font)
            layout.beginLayout(); layout.createLine(); layout.endLayout()
            families={run.rawFont().familyName() for run in layout.glyphRuns()}
            self.assertIn('Segoe UI',families)
            self.assertIn('Microsoft YaHei UI',families)
            self.assertNotIn('SimSun',families)
