import ctypes
import sys
import unittest
from unittest.mock import Mock, patch

from core.reader_wheel import ReaderWheel


class ReaderWheelTests(unittest.TestCase):
    def test_disabled_wheel_passes_through(self):
        self.assertEqual(ReaderWheel().feed(120)[0], False)

    def test_high_resolution_threshold_and_one_step_per_burst(self):
        wheel = ReaderWheel()
        wheel.configure(True)
        self.assertEqual(wheel.feed(-30, 0)[2], 0)
        self.assertEqual(wheel.feed(-30, .02)[2], 0)
        self.assertEqual(wheel.feed(-60, .04)[2], 1)
        self.assertEqual(wheel.feed(-1200, .1)[2], 0)
        self.assertEqual(wheel.feed(-120, .3)[2], 0)
        self.assertEqual(wheel.feed(120, .6)[2], -1)

    def test_all_burst_deltas_consumed_even_after_navigation(self):
        wheel = ReaderWheel()
        wheel.configure(True)
        for i in range(100):
            self.assertTrue(wheel.feed(-120, i / 100)[0])

    def test_pending_commands_invalidated_by_disable_or_document_change(self):
        wheel = ReaderWheel()
        wheel.configure(True)
        _, epoch, _ = wheel.feed(120)
        wheel.configure(False)
        self.assertFalse(wheel.accepts(epoch))
        wheel.configure(True)
        self.assertFalse(wheel.accepts(epoch))
        _, current, _ = wheel.feed(120)
        self.assertTrue(wheel.accepts(current))


@unittest.skipUnless(sys.platform == "win32", "Windows wheel hook")
class WindowsReaderWheelTests(unittest.TestCase):
    def test_reader_claim_precedes_inversion_and_keeps_mapping_snapshot(self):
        from core import mouse_hook_windows as module
        hook = module.MouseHook()
        hook.invert_vscroll = True
        snapshot = hook.capture_binding_snapshot()
        gate = ReaderWheel()
        gate.configure(True)
        hook.set_reading_wheel_handler(lambda delta: gate.feed(delta)[0])
        data = module.MSLLHOOKSTRUCT()
        data.mouseData = (120 << 16)
        with patch.object(module, "CallNextHookEx", return_value=37) as native, patch.object(module, "PostMessageW") as post:
            self.assertEqual(hook._low_level_handler_inner(0, module.WM_MOUSEWHEEL, ctypes.pointer(data)), 1)
            native.assert_not_called()
            post.assert_not_called()
            self.assertIs(hook.capture_binding_snapshot(), snapshot)
            gate.configure(False)
            hook.invert_vscroll = False
            self.assertEqual(hook._low_level_handler_inner(0, module.WM_MOUSEWHEEL, ctypes.pointer(data)), 37)

    def test_synthetic_wheel_not_recaptured(self):
        from core import mouse_hook_windows as module
        hook = module.MouseHook()
        handler = Mock(return_value=True)
        hook.set_reading_wheel_handler(handler)
        data = module.MSLLHOOKSTRUCT()
        data.mouseData = 120 << 16
        data.flags = module.INJECTED_FLAG
        with patch.object(module, "CallNextHookEx", return_value=37):
            self.assertEqual(hook._low_level_handler_inner(0, module.WM_MOUSEWHEEL, ctypes.pointer(data)), 37)
        handler.assert_not_called()


    def test_hold_observation_does_not_change_suppressed_button_routing(self):
        from core import mouse_hook_windows as module
        from core.mouse_hook_types import MouseEvent
        hook = module.MouseHook()
        builder = hook.new_binding_builder()
        builder.block(MouseEvent.XBUTTON1_DOWN)
        hook.publish_bindings(builder)
        observer = Mock()
        hook.set_reading_button_observer(observer)
        data = module.MSLLHOOKSTRUCT()
        data.mouseData = module.XBUTTON1 << 16
        with patch.object(module, "CallNextHookEx", return_value=37):
            self.assertEqual(hook._low_level_handler_inner(0, module.WM_XBUTTONDOWN, ctypes.pointer(data)), 1)
            observer.assert_called_once_with(5, True)
            observer.side_effect = RuntimeError("observer failed")
            self.assertEqual(hook._low_level_handler_inner(0, module.WM_XBUTTONDOWN, ctypes.pointer(data)), 1)

