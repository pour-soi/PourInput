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
import json, os
from pathlib import Path
from tools.isolated_ui_test import prepare, WINDOW_STATE_FILE
root = prepare()
desktop = root / 'profile' / 'Desktop'
assert desktop.is_dir(), 'isolated Desktop must exist for native Windows file dialogs'
assert not any(desktop.iterdir()), 'real Desktop contents must not be copied'
assert str(desktop.parent) == os.environ['USERPROFILE']
from core import config
cfg = config.load_config(strict=True)
assert all(v == 'none' for p in cfg['profiles'].values() for v in p['mappings'].values())
assert all(v == 'none' for p in config.DEFAULT_CONFIG['profiles'].values() for v in p['mappings'].values())
assert str(config.CONFIG_FILE).startswith(str(root))
assert str(config.CONFIG_DIR).startswith(str(root))
assert not (root / 'roaming/PourInput/reader').exists()
assert not cfg['settings']['check_for_updates']
assert not cfg['settings']['start_at_login']
from core.reader import ReaderModel, ReaderStore
store = ReaderStore(Path(config.CONFIG_DIR) / 'reader')
reader = ReaderModel(store)
reader.open_document('Isolated sample', ['First sample page.', 'Second sample page.'])
reader.update(reading_enabled=True)
reader.navigate(1)
assert store.directory.is_relative_to(root)
assert (store.directory / 'state.json').is_file()
assert ReaderModel(ReaderStore(store.directory)).text == 'Second sample page.'
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

    def test_uncertain_mutex_ownership_never_enters_application(self):
        import core.startup as startup
        original = startup.supports_login_startup
        missing = object()
        cases = [(False, 101, 1), (None, 101, 1), (1, 101, 1),
                 (True, None, 1), (True, 0, 1), (True, True, 1),
                 (True, '101', 1), (True, -1, 1), (True, object(), 1),
                 (True, missing, 1), (RuntimeError('acquisition failed'), 101, 1),
                 (True, 101, 0), (True, 101, OSError('native query failed'))]
        for acquired, handle, native in cases:
            with self.subTest(acquired=acquired, handle=handle, native=native):
                main = Mock()
                main.Backend = QObject
                main.Engine = object
                main._WINDOWS_SINGLE_INSTANCE_MUTEX_HANDLE = handle
                if handle is missing:
                    del main._WINDOWS_SINGLE_INSTANCE_MUTEX_HANDLE
                acquire = main._acquire_windows_single_instance_mutex
                if isinstance(acquired, Exception):
                    acquire.side_effect = acquired
                else:
                    acquire.return_value = acquired
                query = Mock(side_effect=native) if isinstance(native, Exception) else Mock(return_value=native)
                with patch('tools.isolated_ui_test.prepare', return_value=Path('isolated')), patch.dict(sys.modules, {'main_qml': main}), patch.object(sys, 'argv', ['isolated_ui_test.py']), patch.object(sys, 'platform', 'win32'), patch('tools.isolated_ui_test.ctypes.windll', Mock(kernel32=Mock(GetHandleInformation=query)), create=True):
                    self.assertEqual(run(), 1)
                main.main.assert_not_called()
                acquire.assert_called_once_with()
                self.assertIs(startup.supports_login_startup, original)

    def test_confirmed_mutex_is_retained_until_original_process_exit_cleanup(self):
        import ctypes
        import main_qml as main
        import core.startup as startup
        original_startup = startup.supports_login_startup
        kernel = Mock()
        kernel.CreateMutexW.return_value = 101
        kernel.GetLastError.return_value = 0
        kernel.GetHandleInformation.return_value = 1
        native_acquire = main._acquire_windows_single_instance_mutex
        def fake_main():
            self.assertEqual(main.APP_NAME, TITLE)
            self.assertEqual(main.WINDOW_STATE_FILE, WINDOW_STATE_FILE)
            self.assertFalse(startup.supports_login_startup())
            self.assertTrue(main._acquire_windows_single_instance_mutex())
            self.assertEqual(main._WINDOWS_SINGLE_INSTANCE_MUTEX_HANDLE, 101)
            kernel.CloseHandle.assert_not_called()
            return 7
        with patch('tools.isolated_ui_test.prepare', return_value=Path('isolated')), patch.object(sys, 'argv', ['isolated_ui_test.py']), patch.object(sys, 'platform', 'win32'), patch.object(ctypes, 'windll', Mock(kernel32=kernel), create=True), patch.object(main.atexit, 'register') as register, patch.multiple(main, APP_NAME=main.APP_NAME, WINDOW_STATE_FILE=main.WINDOW_STATE_FILE, Backend=main.Backend, Engine=main.Engine, _acquire_windows_single_instance_mutex=native_acquire, _WINDOWS_SINGLE_INSTANCE_MUTEX_HANDLE=None), patch.object(main, 'main', side_effect=fake_main):
            self.assertEqual(run(), 7)
            kernel.CreateMutexW.assert_called_once_with(None, False, main._windows_single_instance_mutex_name())
            self.assertEqual(kernel.GetHandleInformation.call_count, 2)
            self.assertEqual(main._WINDOWS_SINGLE_INSTANCE_MUTEX_HANDLE, 101)
            kernel.CloseHandle.assert_not_called()
            register.assert_called_once_with(main._release_windows_single_instance_mutex)
            cleanup = register.call_args.args[0]
            cleanup()
            kernel.CloseHandle.assert_called_once_with(101)
            self.assertIsNone(main._WINDOWS_SINGLE_INSTANCE_MUTEX_HANDLE)
            cleanup()
            kernel.CloseHandle.assert_called_once_with(101)
        self.assertIs(startup.supports_login_startup, original_startup)

    def test_production_fail_open_mutex_result_is_rejected_by_test_launcher(self):
        import ctypes
        import main_qml as main
        native_acquire = main._acquire_windows_single_instance_mutex
        for creation in (0, OSError('mutex API unavailable')):
            with self.subTest(creation=creation):
                kernel = Mock()
                if isinstance(creation, Exception):
                    kernel.CreateMutexW.side_effect = creation
                else:
                    kernel.CreateMutexW.return_value = creation
                with patch('tools.isolated_ui_test.prepare', return_value=Path('isolated')), patch.object(sys, 'argv', ['isolated_ui_test.py']), patch.object(sys, 'platform', 'win32'), patch.object(ctypes, 'windll', Mock(kernel32=kernel), create=True), patch.object(main.atexit, 'register') as register, patch.multiple(main, APP_NAME=main.APP_NAME, WINDOW_STATE_FILE=main.WINDOW_STATE_FILE, Backend=main.Backend, Engine=main.Engine, _acquire_windows_single_instance_mutex=native_acquire, _WINDOWS_SINGLE_INSTANCE_MUTEX_HANDLE=None), patch.object(main, 'main') as app:
                    self.assertEqual(run(), 1)
                    app.assert_not_called()
                    kernel.GetHandleInformation.assert_not_called()
                    kernel.CloseHandle.assert_not_called()
                    register.assert_not_called()

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
