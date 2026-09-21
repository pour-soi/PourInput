"""Reading mouse holds own input without mutating saved bindings."""
import ctypes
import os
import tempfile
import unittest
from unittest.mock import Mock, patch


@unittest.skipUnless(os.name == 'nt', 'Windows input ownership')
class ReadingButtonOwnershipTests(unittest.TestCase):
    def setUp(self):
        from core import mouse_hook_windows as win
        self.win = win
        self.hook = win.MouseHook()
        self.observer = Mock()
        self.hook.set_reading_button_observer(self.observer)

    def edge(self, down, key=5, injected=False):
        w = self.win
        data = w.MSLLHOOKSTRUCT()
        data.mouseData = (key - 4) << 16
        data.flags = w.INJECTED_FLAG if injected else 0
        with patch.object(w, 'CallNextHookEx', return_value=123):
            return self.hook._low_level_handler_inner(
                w.HC_ACTION, w.WM_XBUTTONDOWN if down else w.WM_XBUTTONUP,
                ctypes.pointer(data))

    def test_native_and_generic_mapping_are_exclusive_only_while_reading(self):
        from core.mouse_hook_types import MouseEvent
        for mapped in (False, True):
            with self.subTest(mapped=mapped):
                hook = self.hook
                builder = hook.new_binding_builder()
                if mapped:
                    builder.set_route(MouseEvent.XBUTTON1_DOWN, 'generic_xbutton1')
                    builder.block(MouseEvent.XBUTTON1_DOWN)
                hook.publish_bindings(builder)
                before = hook.capture_binding_snapshot()
                hook.set_reading_hide_key(5)
                self.assertEqual(self.edge(True), 1)
                self.assertEqual(self.edge(False), 1)
                self.assertTrue(hook._dispatch_queue.empty())
                self.observer.assert_any_call(5, True)
                self.observer.assert_any_call(5, False)
                self.assertIs(hook.capture_binding_snapshot(), before)
                hook.set_reading_hide_key(0)
                self.assertEqual(self.edge(True), 1 if mapped else 123)
                self.assertEqual(self.edge(False), 123)
                self.assertEqual(hook._dispatch_queue.get_nowait().event_type, MouseEvent.XBUTTON1_DOWN)
                self.assertEqual(hook._dispatch_queue.get_nowait().event_type, MouseEvent.XBUTTON1_UP)

    def test_hid_actions_and_driver_duplicates_are_suppressed_then_restored(self):
        hook = self.hook
        hook._dispatch = Mock()
        hook.set_reading_hide_key(5)
        hook._on_hid_xbutton1_down()
        self.assertEqual(self.edge(True, injected=True), 1)
        hook._on_hid_xbutton1_up()
        self.assertEqual(self.edge(False, injected=True), 1)
        hook._dispatch.assert_not_called()
        hook._on_hid_xbutton2_down()
        hook._on_hid_xbutton2_up()
        self.assertEqual(hook._dispatch.call_count, 2)
        hook._dispatch.reset_mock()
        hook.set_reading_hide_key(0)
        hook._on_hid_xbutton1_down()
        hook._on_hid_xbutton1_up()
        self.assertEqual(hook._dispatch.call_count, 2)

    def test_other_mouse_hide_choices_consume_both_edges(self):
        w = self.win
        for key, down, up in ((1, 0x0201, 0x0202), (2, 0x0204, 0x0205), (4, w.WM_MBUTTONDOWN, w.WM_MBUTTONUP)):
            self.hook.set_reading_hide_key(key)
            for message in (down, up):
                data = w.MSLLHOOKSTRUCT()
                with patch.object(w, 'CallNextHookEx', return_value=123):
                    self.assertEqual(self.hook._low_level_handler_inner(w.HC_ACTION, message, ctypes.pointer(data)), 1)
            self.assertTrue(self.hook._dispatch_queue.empty())

    def test_disconnect_clears_hid_hold_ownership(self):
        self.hook.set_reading_hide_key(5)
        self.hook._dispatch = Mock()
        self.hook._on_hid_xbutton1_down()
        self.hook._on_hid_disconnect()
        self.hook.set_reading_hide_key(0)
        self.hook._on_hid_xbutton1_down()
        self.hook._on_hid_xbutton1_up()
        self.assertEqual(self.hook._dispatch.call_count, 2)

    def test_disable_mid_hold_consumes_release_but_restores_next_press(self):
        self.hook.set_reading_hide_key(5)
        self.assertEqual(self.edge(True), 1)
        self.hook.set_reading_hide_key(0)
        self.assertEqual(self.edge(False), 1)
        self.assertEqual(self.edge(True), 123)
        self.assertEqual(self.edge(False), 123)

    def test_controller_publishes_ownership_and_hide_preserves_reader_state(self):
        from PySide6.QtCore import QEvent
        from PySide6.QtWidgets import QApplication
        from ui.reading import ReadingController
        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as directory:
            reader = ReadingController(self.hook, directory, key_down=lambda key: False)
            try:
                reader._finish_import(('Book', ['First.', 'Second.']), '')
                reader.setHideKey(5)
                reader.setEnabled(True)
                before = reader.model.state
                self.assertEqual(self.edge(True), 1)
                app.sendPostedEvents(reader, QEvent.MetaCall)
                self.assertFalse(reader.panelVisible)
                self.assertEqual(reader.model.state, before)
                self.assertTrue(reader.handle_wheel(1))
                self.assertEqual(self.edge(False), 1)
                app.sendPostedEvents(reader, QEvent.MetaCall)
                self.assertTrue(reader.panelVisible)
                self.assertEqual(reader.model.state, before)
                reader.setEnabled(False)
                self.assertEqual(self.edge(True), 123)
                self.assertEqual(self.edge(False), 123)
            finally:
                reader.close()
