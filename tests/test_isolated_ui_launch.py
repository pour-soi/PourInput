"""Isolation contracts; never starts an engine or opens the real application."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch
from PySide6.QtCore import QObject, QMetaObject, Q_ARG
from tools.isolated_ui_test import TITLE, WINDOW_STATE_FILE, run, test_backend, test_engine


class IsolatedLaunchTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "win32", "Windows-only isolated launcher data paths")
    def test_fresh_process_uses_only_disposable_state_and_neutral_defaults(self):
        script = '''
import json
from tools.isolated_ui_test import prepare, WINDOW_STATE_FILE
root = prepare()
from core import config
cfg = config.load_config(strict=True)
assert all(v == 'none' for p in cfg['profiles'].values() for v in p['mappings'].values())
assert all(v == 'none' for p in config.DEFAULT_CONFIG['profiles'].values() for v in p['mappings'].values())
assert str(config.CONFIG_FILE).startswith(str(root))
assert str(config.CONFIG_DIR).startswith(str(root))
assert not (root / 'roaming/PourInput/reader').exists()
assert not cfg['settings']['check_for_updates']
assert not cfg['settings']['start_at_login']
assert not str(WINDOW_STATE_FILE).startswith(str(root))
assert WINDOW_STATE_FILE.name == 'pourinput-ui-refinement-window-size.json'
print('ISOLATION_OK')
'''
        result = subprocess.run([sys.executable, '-B', '-c', script], cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('ISOLATION_OK', result.stdout)

    def test_unsupported_platform_rejects_launch_before_preparing_data(self):
        for platform in ('linux', 'darwin'):
            with self.subTest(platform=platform), patch.object(sys, 'platform', platform), patch('tools.isolated_ui_test.prepare') as prepare:
                with self.assertRaisesRegex(SystemExit, 'Use this entry point on Windows'):
                    run()
                prepare.assert_not_called()

    def test_entry_identity_mutex_and_production_restoration(self):
        import core.startup as startup
        original = startup.supports_login_startup
        main = Mock()
        main._acquire_windows_single_instance_mutex.return_value = False
        main.Backend = QObject
        main.Engine = object
        def fake_main():
            self.assertEqual(main.APP_NAME, TITLE)
            self.assertEqual(main.WINDOW_STATE_FILE, WINDOW_STATE_FILE)
            self.assertFalse(startup.supports_login_startup())
            self.assertFalse(main._acquire_windows_single_instance_mutex())
            return 0
        main.main.side_effect = fake_main
        with patch('tools.isolated_ui_test.prepare', return_value=Path('isolated')), patch.dict(sys.modules, {'main_qml': main}), patch.object(sys, 'argv', ['isolated_ui_test.py']), patch.object(sys, 'platform', 'win32'):
            self.assertEqual(run(), 0)
        self.assertIs(startup.supports_login_startup, original)

    def test_qt_slots_cannot_enable_startup_or_install_updates(self):
        from tests.test_mouse_page_ui import MousePageUiTests
        from ui.backend import Backend
        isolated = test_backend(Backend)
        fixture = MousePageUiTests()
        try:
            with patch('tests.test_mouse_page_ui.Backend', isolated), patch('ui.backend.sync_login_startup_from_config') as sync, patch('ui.backend.apply_login_startup') as apply:
                fixture.setUp()
                backend = fixture.backend
                for name in ('prepareLatestUpdate', 'installPreparedUpdate', 'manualCheckForUpdates'):
                    self.assertTrue(QMetaObject.invokeMethod(backend, name))
                for name in ('setStartAtLogin', 'setCheckForUpdates'):
                    self.assertTrue(QMetaObject.invokeMethod(backend, name, Q_ARG(bool, True)))
                sync.assert_not_called()
                apply.assert_not_called()
                self.assertFalse(backend.checkForUpdates)
                self.assertFalse(backend.startAtLogin)
                self.assertFalse(backend.updateInstallInProgress)
        finally:
            fixture.doCleanups()

    def test_no_automatic_device_settings_writes(self):
        from core.engine import MouseHook
        class Base:
            def __init__(self):
                MouseHook.set_dpi(None, 1000)
            def _request_saved_settings_replay(self, **kwargs):
                raise AssertionError("must not replay test defaults")
        with patch.object(MouseHook, "set_dpi", create=True) as setter:
            engine = test_engine(Base)()
            engine._request_saved_settings_replay(startup_fallback=True)
            setter.assert_not_called()
            self.assertIs(MouseHook.set_dpi, setter)
