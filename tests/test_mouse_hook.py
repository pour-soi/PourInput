import importlib
import ctypes
import queue
import sys
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, MagicMock, call, patch

import core
from core import mouse_hook
from core.mouse_hook_base import BaseMouseHook
from core.mouse_hook_types import HidRuntimeState, LifecycleInvalidation, MouseEvent


class _FakeEvdevDevice:
    def __init__(self, *, name, path, vendor, capabilities, product=0, fd=11):
        self.name = name
        self.path = path
        self.fd = fd
        self.info = SimpleNamespace(
            vendor=vendor,
            product=product,
            version=1,
            bustype=0x03,
        )
        self._capabilities = capabilities
        self.grab = Mock()
        self.ungrab = Mock()
        self.close = Mock()
        self.read = Mock(return_value=[])

    def capabilities(self, absinfo=False):
        return self._capabilities


class _CapturingListener:
    def __init__(self, on_down=None, on_up=None, on_move=None,
                 on_connect=None, on_disconnect=None, extra_diverts=None):
        self.on_down = on_down
        self.on_up = on_up
        self.on_move = on_move
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.extra_diverts = extra_diverts or {}
        self.connected_device = None
        self.started = False
        self.stopped = False

    def start(self):
        self.started = True
        return True

    def stop(self):
        self.stopped = True


class _FakeLinuxEcodes:
    EV_SYN = 0x00
    EV_REL = 0x02
    EV_KEY = 0x01
    REL_X = 0x00
    REL_Y = 0x01
    REL_WHEEL = 0x08
    REL_HWHEEL = 0x06
    BTN_LEFT = 0x110
    BTN_RIGHT = 0x111
    BTN_MIDDLE = 0x112
    BTN_SIDE = 0x113
    BTN_EXTRA = 0x114


class _FakeLinuxUInput:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.write_event = Mock()
        self.write = Mock()
        self.close = Mock()


class BaseMouseHookRuntimeStateTests(unittest.TestCase):
    def test_intentional_reconnect_retains_then_expires_device_identity(self):
        hook = BaseMouseHook()
        device = SimpleNamespace(key="mx_master_3")
        listener = SimpleNamespace(
            connected_device=device,
            preserve_device_identity_on_reconnect=False,
        )
        hook._hid_gesture = listener
        connection_changes = []
        hook.set_connection_change_callback(connection_changes.append)
        hook._on_hid_connect()

        listener.connected_device = None
        listener.preserve_device_identity_on_reconnect = True
        hook._on_hid_disconnect()

        self.assertFalse(hook.device_connected)
        self.assertIs(hook.connected_device, device)

        listener.preserve_device_identity_on_reconnect = False
        hook._on_hid_disconnect()

        self.assertIsNone(hook.connected_device)
        self.assertEqual(connection_changes, [True, False, False])

    def test_default_runtime_state_is_disconnected(self):
        hook = BaseMouseHook()

        self.assertEqual(hook.hid_runtime_state, HidRuntimeState())

    def test_runtime_state_projects_hid_identity(self):
        hook = BaseMouseHook()
        device = SimpleNamespace(name="MX Master 3S")
        hook._hid_gesture = SimpleNamespace(connected_device=device)

        hook._on_hid_connect()

        state = hook.hid_runtime_state
        self.assertTrue(state.input_ready)
        self.assertTrue(state.hid_ready)
        self.assertIs(state.connected_device, device)

    def test_status_callback_is_optional(self):
        hook = BaseMouseHook()
        hook._emit_status("ignored")
        messages = []

        hook.set_status_callback(messages.append)
        hook._emit_status("Linux evdev remapping restored.")
        self.assertEqual(messages, ["Linux evdev remapping restored."])


class LogitechHidEdgeDeduplicationTests(unittest.TestCase):
    def _hook(self):
        hook = BaseMouseHook()
        hook._connected_device = SimpleNamespace(key="mx_master_3")
        hook._dispatch = Mock()
        return hook

    def test_repeated_down_before_up_is_ignored(self):
        hook = self._hook()

        self.assertTrue(hook._on_hid_xbutton2_down())
        self.assertFalse(hook._on_hid_xbutton2_down())

        self.assertEqual(hook._dispatch.call_count, 1)
        self.assertEqual(
            hook._dispatch.call_args.args[0].event_type,
            MouseEvent.LOGI_XBUTTON2_DOWN,
        )

    def test_repeated_up_after_release_is_ignored(self):
        hook = self._hook()
        hook._on_hid_xbutton2_down()
        hook._on_hid_xbutton2_up()

        self.assertFalse(hook._on_hid_xbutton2_up())
        self.assertEqual(hook._dispatch.call_count, 2)

    def test_back_and_forward_pressed_state_are_independent(self):
        hook = self._hook()

        self.assertTrue(hook._on_hid_xbutton1_down())
        self.assertTrue(hook._on_hid_xbutton2_down())
        self.assertFalse(hook._on_hid_xbutton1_down())
        self.assertTrue(hook._on_hid_xbutton2_up())

        self.assertEqual(hook._dispatch.call_count, 3)

    def test_disconnect_clears_pressed_state(self):
        hook = self._hook()
        hook._on_hid_xbutton2_down()

        hook._set_device_connected(False)

        self.assertTrue(hook._on_hid_xbutton2_down())
        self.assertEqual(hook._dispatch.call_count, 2)

    def test_sync_hid_extra_diverts_pushes_mode_shift_to_listener(self):
        hook = BaseMouseHook()
        listener = SimpleNamespace(update_extra_diverts=Mock(return_value=True))
        hook._hid_gesture = listener
        hook.divert_mode_shift = True

        self.assertTrue(hook.sync_hid_extra_diverts())

        listener.update_extra_diverts.assert_called_once()
        extra = listener.update_extra_diverts.call_args.args[0]
        self.assertIn(0x00C4, extra)

    def test_sync_hid_extra_diverts_routes_mx_master_side_buttons(self):
        hook = BaseMouseHook()
        listener = SimpleNamespace(update_extra_diverts=Mock(return_value=True))
        hook._hid_gesture = listener
        hook.divert_logi_xbutton1 = True
        hook.divert_logi_xbutton2 = True
        hook._connected_device = SimpleNamespace(key="mx_master_3")
        hook.debug_mode = True
        debug_messages = []
        hook.set_debug_callback(debug_messages.append)

        self.assertTrue(hook.sync_hid_extra_diverts())

        extra = listener.update_extra_diverts.call_args.args[0]
        self.assertEqual(set(extra), {0x0053, 0x0056})
        seen = []
        hook.register(
            MouseEvent.LOGI_XBUTTON1_DOWN,
            lambda event: seen.append(event.event_type),
        )
        extra[0x0053]["on_down"]()
        self.assertEqual(seen, [MouseEvent.LOGI_XBUTTON1_DOWN])
        self.assertTrue(any(
            "device=mx_master_3" in message
            and "cid=0x0053" in message
            and "detected=xbutton1" in message
            for message in debug_messages
        ))



class BaseMouseHookDispatchQueueTests(unittest.TestCase):
    def test_enqueue_keeps_queue_bounded_and_drops_oldest(self):
        hook = BaseMouseHook()
        hook._init_dispatch_queue(maxsize=2)

        hook._enqueue_dispatch_event(SimpleNamespace(event_type="e1", raw_data=None))
        hook._enqueue_dispatch_event(SimpleNamespace(event_type="e2", raw_data=None))
        hook._enqueue_dispatch_event(SimpleNamespace(event_type="e3", raw_data=None))

        self.assertEqual(hook._dispatch_queue.qsize(), 2)
        first = hook._dispatch_queue.get_nowait()
        second = hook._dispatch_queue.get_nowait()
        self.assertEqual(first.event_type, "e2")
        self.assertEqual(second.event_type, "e3")

    def test_enqueue_drops_and_emits_debug_when_still_full(self):
        hook = BaseMouseHook()
        hook._init_dispatch_queue(maxsize=1)
        hook.debug_mode = True
        hook.set_debug_callback(Mock())

        hook._dispatch_queue.put_nowait(SimpleNamespace(event_type="old", raw_data=None))
        with patch.object(hook._dispatch_queue, "get_nowait", side_effect=queue.Empty):
            with patch.object(hook._dispatch_queue, "put_nowait", side_effect=[queue.Full, queue.Full]):
                hook._enqueue_dispatch_event(SimpleNamespace(event_type="new", raw_data=None))

        hook._debug_callback.assert_called_once()
        self.assertIn("Dropped event due to full dispatch queue", hook._debug_callback.call_args[0][0])


class BaseMouseHookBindingSnapshotTests(unittest.TestCase):
    def test_binding_snapshot_replacement_is_atomic_and_immutable(self):
        hook = BaseMouseHook()
        first_callback = Mock()
        first_builder = hook.new_binding_builder()
        first_builder.register(MouseEvent.XBUTTON1_DOWN, first_callback)
        first_builder.block(MouseEvent.XBUTTON1_DOWN)
        first_builder.set_route(MouseEvent.XBUTTON1_DOWN, "generic_xbutton1")
        first = hook.publish_bindings(first_builder)

        second_callback = Mock()
        second_builder = hook.new_binding_builder()
        second_builder.register(MouseEvent.XBUTTON1_DOWN, second_callback)
        second = hook.publish_bindings(second_builder)

        self.assertEqual(second.generation, first.generation + 1)
        self.assertEqual(first.callbacks[MouseEvent.XBUTTON1_DOWN], (first_callback,))
        self.assertIn(MouseEvent.XBUTTON1_DOWN, first.blocked_events)
        self.assertEqual(first.routes[MouseEvent.XBUTTON1_DOWN], "generic_xbutton1")
        self.assertEqual(second.callbacks[MouseEvent.XBUTTON1_DOWN], (second_callback,))
        self.assertNotIn(MouseEvent.XBUTTON1_DOWN, second.blocked_events)

    def test_retired_queued_event_does_not_execute_new_or_old_callback(self):
        hook = BaseMouseHook()
        old_callback = Mock()
        old_builder = hook.new_binding_builder()
        old_builder.register(MouseEvent.XBUTTON1_DOWN, old_callback)
        old_snapshot = hook.publish_bindings(old_builder)
        event = hook.bind_event(
            MouseEvent(MouseEvent.XBUTTON1_DOWN),
            old_snapshot,
        )

        new_callback = Mock()
        new_builder = hook.new_binding_builder()
        new_builder.register(MouseEvent.XBUTTON1_DOWN, new_callback)
        hook.publish_bindings(new_builder)
        hook._dispatch(event)

        old_callback.assert_not_called()
        new_callback.assert_not_called()

    def test_replacement_waits_for_admitted_callback_to_finish(self):
        hook = BaseMouseHook()
        callback = Mock()
        builder = hook.new_binding_builder()
        builder.register(MouseEvent.XBUTTON1_DOWN, callback)
        snapshot = hook.publish_bindings(builder)
        event = hook.bind_event(MouseEvent(MouseEvent.XBUTTON1_DOWN), snapshot)
        admitted = threading.Event()
        allow_callback = threading.Event()
        retirement_waiting = threading.Event()
        replacement_done = threading.Event()
        original_acquire = snapshot.dispatch_state.try_acquire
        original_wait = snapshot.dispatch_state.wait_for_drain

        def controlled_acquire():
            acquired = original_acquire()
            admitted.set()
            allow_callback.wait()
            return acquired

        def observed_wait(timeout=None):
            retirement_waiting.set()
            return original_wait(timeout)

        snapshot.dispatch_state.try_acquire = controlled_acquire
        snapshot.dispatch_state.wait_for_drain = observed_wait
        dispatch_thread = threading.Thread(target=hook._dispatch, args=(event,))
        dispatch_thread.start()
        self.assertTrue(admitted.wait(1))

        def replace():
            hook.publish_bindings(hook.new_binding_builder())
            replacement_done.set()

        replace_thread = threading.Thread(target=replace)
        replace_thread.start()
        self.assertTrue(retirement_waiting.wait(1))
        self.assertFalse(replacement_done.is_set())
        allow_callback.set()
        dispatch_thread.join(1)
        replace_thread.join(1)

        self.assertTrue(replacement_done.is_set())
        callback.assert_called_once_with(event)

    def test_reentrant_replacement_does_not_self_deadlock(self):
        hook = BaseMouseHook()
        replacement_returned = Mock()

        def callback(_event):
            hook.publish_bindings(hook.new_binding_builder())
            replacement_returned()

        builder = hook.new_binding_builder()
        builder.register(MouseEvent.XBUTTON1_DOWN, callback)
        snapshot = hook.publish_bindings(builder)
        hook._dispatch(hook.bind_event(MouseEvent(MouseEvent.XBUTTON1_DOWN), snapshot))

        replacement_returned.assert_called_once_with()

    def test_overflow_queues_lifecycle_invalidation_before_new_event(self):
        hook = BaseMouseHook()
        hook._init_dispatch_queue(maxsize=3)
        invalidator = Mock()
        builder = hook.new_binding_builder()
        builder.set_route(MouseEvent.XBUTTON1_UP, "generic_xbutton1")
        builder.set_lifecycle_invalidator(invalidator)
        snapshot = hook.publish_bindings(builder)
        up = hook.bind_event(MouseEvent(MouseEvent.XBUTTON1_UP), snapshot)
        hook._enqueue_dispatch_event(up)
        hook._enqueue_dispatch_event(MouseEvent(MouseEvent.HSCROLL_LEFT))
        hook._enqueue_dispatch_event(MouseEvent(MouseEvent.HSCROLL_RIGHT))
        new_event = MouseEvent(MouseEvent.MIDDLE_DOWN)
        hook._enqueue_dispatch_event(new_event)

        control = hook._dispatch_queue.get_nowait()
        self.assertIsInstance(control, LifecycleInvalidation)
        hook._dispatch(control)
        invalidator.assert_called_once_with(snapshot.generation, "generic_xbutton1")
        self.assertIs(hook._dispatch_queue.get_nowait(), new_event)

    def test_consecutive_overflow_preserves_pending_invalidations(self):
        hook = BaseMouseHook()
        hook._init_dispatch_queue(maxsize=2)
        invalidator = Mock()
        builder = hook.new_binding_builder()
        builder.set_route(MouseEvent.XBUTTON1_UP, "generic_xbutton1")
        builder.set_lifecycle_invalidator(invalidator)
        snapshot = hook.publish_bindings(builder)

        for _ in range(2):
            up = hook.bind_event(MouseEvent(MouseEvent.XBUTTON1_UP), snapshot)
            hook._enqueue_dispatch_event(up)
            hook._enqueue_dispatch_event(MouseEvent(MouseEvent.MIDDLE_DOWN))
            hook._enqueue_dispatch_event(MouseEvent(MouseEvent.MIDDLE_UP))

        control = hook._dispatch_queue.get_nowait()
        self.assertIsInstance(control, LifecycleInvalidation)
        hook._dispatch(control)
        self.assertGreaterEqual(invalidator.call_count, 2)


@unittest.skipUnless(sys.platform == "win32", "Windows-only low-level hook tests")
class WindowsXButtonHookTests(unittest.TestCase):
    def _windows_module(self):
        return importlib.import_module("core.mouse_hook_windows")

    def _event_pointer(self, module, *, mouse_data=0, flags=0):
        data = module.MSLLHOOKSTRUCT()
        data.mouseData = mouse_data
        data.flags = flags
        return ctypes.pointer(data)

    def _xbutton_pointer(self, module, xbutton):
        return self._event_pointer(module, mouse_data=xbutton << 16)

    def _configure_logitech_side_buttons(self, hook):
        hook._connected_device = SimpleNamespace(key="mx_master_3")
        hook.divert_logi_xbutton1 = True
        hook.divert_logi_xbutton2 = True
        builder = hook.new_binding_builder()
        for event_type, logical in (
            (MouseEvent.LOGI_XBUTTON1_DOWN, "xbutton1"),
            (MouseEvent.LOGI_XBUTTON1_UP, "xbutton1"),
            (MouseEvent.LOGI_XBUTTON2_DOWN, "xbutton2"),
            (MouseEvent.LOGI_XBUTTON2_UP, "xbutton2"),
        ):
            builder.set_route(event_type, logical)
        return hook.publish_bindings(builder)

    def _injected_xbutton_pointer(self, module, xbutton):
        return self._event_pointer(
            module,
            mouse_data=xbutton << 16,
            flags=module.INJECTED_FLAG,
        )

    def test_logitech_hid_xbutton_down_and_up_suppress_matching_native_events(self):
        module = self._windows_module()
        hook = module.MouseHook()
        self._configure_logitech_side_buttons(hook)

        with patch.object(module, "CallNextHookEx", return_value=123):
            hook._on_hid_xbutton1_down()
            down_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONDOWN,
                self._injected_xbutton_pointer(module, module.XBUTTON1),
            )
            hook._on_hid_xbutton1_up()
            up_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONUP,
                self._injected_xbutton_pointer(module, module.XBUTTON1),
            )

        self.assertEqual((down_result, up_result), (1, 1))

    def test_injected_windows_up_confirms_active_hid_hold_before_suppression(self):
        module = self._windows_module()
        hook = module.MouseHook()
        self._configure_logitech_side_buttons(hook)
        hold = (11, 4, 0x0056, 9)
        listener = SimpleNamespace(
            active_side_button_hold=Mock(return_value=hold),
            confirm_side_button_release=Mock(
                side_effect=lambda *_args, **_kwargs: hook._on_hid_xbutton2_up()
            ),
        )
        hook._hid_gesture = listener
        hook._on_hid_xbutton2_down()

        with patch.object(module, "CallNextHookEx", return_value=123):
            down_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONDOWN,
                self._injected_xbutton_pointer(module, module.XBUTTON2),
            )
            up_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONUP,
                self._injected_xbutton_pointer(module, module.XBUTTON2),
            )

        self.assertEqual((down_result, up_result), (1, 1))
        listener.confirm_side_button_release.assert_called_once_with(
            0x0056,
            hold,
            source="injected xbutton2_up",
        )

    def test_wrong_button_windows_up_cannot_release_active_forward_hold(self):
        module = self._windows_module()
        hook = module.MouseHook()
        self._configure_logitech_side_buttons(hook)
        hold = (11, 4, 0x0056, 9)
        listener = SimpleNamespace(
            active_side_button_hold=Mock(
                side_effect=lambda cid: hold if cid == 0x0056 else None
            ),
            confirm_side_button_release=Mock(),
        )
        hook._hid_gesture = listener
        hook._on_hid_xbutton2_down()

        with patch.object(module, "CallNextHookEx", return_value=123):
            hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONDOWN,
                self._injected_xbutton_pointer(module, module.XBUTTON2),
            )
            wrong_up = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONUP,
                self._injected_xbutton_pointer(module, module.XBUTTON1),
            )

        self.assertEqual(wrong_up, 123)
        listener.confirm_side_button_release.assert_not_called()

    def test_logitech_forward_suppression_is_independent_from_back(self):
        module = self._windows_module()
        hook = module.MouseHook()
        self._configure_logitech_side_buttons(hook)

        with patch.object(module, "CallNextHookEx", return_value=123):
            hook._on_hid_xbutton2_down()
            wrong_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONDOWN,
                self._injected_xbutton_pointer(module, module.XBUTTON1),
            )
            matching_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONDOWN,
                self._injected_xbutton_pointer(module, module.XBUTTON2),
            )

        self.assertEqual(wrong_result, 123)
        self.assertEqual(matching_result, 1)

    def test_stale_logitech_suppression_does_not_swallow_later_event(self):
        module = self._windows_module()
        hook = module.MouseHook()
        self._configure_logitech_side_buttons(hook)
        hook._on_hid_xbutton1_down()
        hook._logi_xbutton_suppression[MouseEvent.XBUTTON1_DOWN]["expires_at"] = 0

        with patch.object(module, "CallNextHookEx", return_value=123):
            result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONDOWN,
                self._injected_xbutton_pointer(module, module.XBUTTON1),
            )

        self.assertEqual(result, 123)

    def test_unmatched_injected_xbutton_and_other_mouse_input_pass_through(self):
        module = self._windows_module()
        hook = module.MouseHook()
        self._configure_logitech_side_buttons(hook)

        with patch.object(module, "CallNextHookEx", return_value=123):
            xbutton_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONDOWN,
                self._injected_xbutton_pointer(module, module.XBUTTON1),
            )
            left_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                0x0201,
                self._event_pointer(module, flags=module.INJECTED_FLAG),
            )

        self.assertEqual((xbutton_result, left_result), (123, 123))

    def test_binding_replacement_and_disconnect_clear_suppression(self):
        module = self._windows_module()
        hook = module.MouseHook()
        self._configure_logitech_side_buttons(hook)
        hook._on_hid_xbutton1_down()
        self.assertTrue(hook._logi_xbutton_suppression)

        hook.publish_bindings(hook.new_binding_builder())
        self.assertFalse(hook._logi_xbutton_suppression)

        self._configure_logitech_side_buttons(hook)
        hook._on_hid_xbutton2_down()
        hook._on_hid_disconnect()
        self.assertFalse(hook._logi_xbutton_suppression)

    def test_generic_route_does_not_arm_logitech_suppression(self):
        module = self._windows_module()
        hook = module.MouseHook()
        hook._connected_device = SimpleNamespace(key="mx_master_3")
        builder = hook.new_binding_builder()
        builder.set_route(MouseEvent.XBUTTON1_DOWN, "generic_xbutton1")
        builder.block(MouseEvent.XBUTTON1_DOWN)
        hook.publish_bindings(builder)

        self.assertFalse(
            hook._arm_logi_xbutton_suppression(MouseEvent.LOGI_XBUTTON1_DOWN)
        )
        with patch.object(module, "CallNextHookEx", return_value=123):
            injected_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONDOWN,
                self._injected_xbutton_pointer(module, module.XBUTTON1),
            )
            physical_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONDOWN,
                self._xbutton_pointer(module, module.XBUTTON1),
            )

        self.assertEqual(injected_result, 123)
        self.assertEqual(physical_result, 1)

    def test_xbutton1_down_up_are_enqueued_and_pass_through_by_default(self):
        module = self._windows_module()
        hook = module.MouseHook()

        with patch.object(module, "CallNextHookEx", return_value=123):
            down_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONDOWN,
                self._xbutton_pointer(module, module.XBUTTON1),
            )
            up_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONUP,
                self._xbutton_pointer(module, module.XBUTTON1),
            )

        self.assertEqual(down_result, 123)
        self.assertEqual(up_result, 123)
        down_event = hook._dispatch_queue.get_nowait()
        up_event = hook._dispatch_queue.get_nowait()
        self.assertEqual(
            [down_event.event_type, up_event.event_type],
            [
                module.MouseEvent.XBUTTON1_DOWN,
                module.MouseEvent.XBUTTON1_UP,
            ],
        )

    def test_xbutton2_down_up_are_enqueued_and_pass_through_by_default(self):
        module = self._windows_module()
        hook = module.MouseHook()

        with patch.object(module, "CallNextHookEx", return_value=123):
            down_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONDOWN,
                self._xbutton_pointer(module, module.XBUTTON2),
            )
            up_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONUP,
                self._xbutton_pointer(module, module.XBUTTON2),
            )

        self.assertEqual(down_result, 123)
        self.assertEqual(up_result, 123)
        down_event = hook._dispatch_queue.get_nowait()
        up_event = hook._dispatch_queue.get_nowait()
        self.assertEqual(
            [down_event.event_type, up_event.event_type],
            [
                module.MouseEvent.XBUTTON2_DOWN,
                module.MouseEvent.XBUTTON2_UP,
            ],
        )

    def test_blocking_xbutton_does_not_suppress_unrelated_mouse_events(self):
        module = self._windows_module()
        hook = module.MouseHook()
        hook.block(module.MouseEvent.XBUTTON1_DOWN)

        with patch.object(module, "CallNextHookEx", return_value=123):
            xbutton_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONDOWN,
                self._xbutton_pointer(module, module.XBUTTON1),
            )
            middle_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_MBUTTONDOWN,
                self._event_pointer(module),
            )
            left_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                0x0201,
                self._event_pointer(module),
            )
            wheel_result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_MOUSEWHEEL,
                self._event_pointer(module),
            )

        self.assertEqual(xbutton_result, 1)
        self.assertEqual(middle_result, 123)
        self.assertEqual(left_result, 123)
        self.assertEqual(wheel_result, 123)

    def test_existing_xbutton_blocking_still_works(self):
        module = self._windows_module()
        hook = module.MouseHook()
        hook.block(module.MouseEvent.XBUTTON2_UP)

        with patch.object(module, "CallNextHookEx", return_value=123):
            result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONUP,
                self._xbutton_pointer(module, module.XBUTTON2),
            )

        self.assertEqual(result, 1)

    def test_debug_logging_reports_xbutton_routing_and_callback_execution(self):
        module = self._windows_module()
        hook = module.MouseHook()
        callback = Mock()
        debug_messages = []
        hook.debug_mode = True
        hook.set_debug_callback(debug_messages.append)
        hook.register(module.MouseEvent.XBUTTON1_DOWN, callback)
        hook.block(module.MouseEvent.XBUTTON1_DOWN)

        with patch.object(module, "CallNextHookEx", return_value=123):
            result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONDOWN,
                self._xbutton_pointer(module, module.XBUTTON1),
            )

        self.assertEqual(result, 1)
        event = hook._dispatch_queue.get_nowait()
        hook._dispatch(event)
        callback.assert_called_once()
        joined = "\n".join(debug_messages)
        self.assertIn("WM_XBUTTONDOWN", joined)
        self.assertIn("device=unavailable(WH_MOUSE_LL)", joined)
        self.assertIn("blocked=True", joined)
        self.assertIn("callbacks=1", joined)
        self.assertIn("Callback executed for xbutton1_down", joined)

    def test_suppression_and_callback_context_use_the_receipt_generation(self):
        module = self._windows_module()
        hook = module.MouseHook()
        old_callback = Mock()
        old_builder = hook.new_binding_builder()
        old_builder.register(module.MouseEvent.XBUTTON1_DOWN, old_callback)
        old_builder.block(module.MouseEvent.XBUTTON1_DOWN)
        old_builder.set_route(module.MouseEvent.XBUTTON1_DOWN, "generic_xbutton1")
        old_snapshot = hook.publish_bindings(old_builder)

        with patch.object(module, "CallNextHookEx", return_value=123):
            result = hook._low_level_handler_inner(
                module.HC_ACTION,
                module.WM_XBUTTONDOWN,
                self._xbutton_pointer(module, module.XBUTTON1),
            )

        self.assertEqual(result, 1)
        queued = hook._dispatch_queue.get_nowait()
        self.assertEqual(queued.binding_generation, old_snapshot.generation)
        self.assertEqual(queued.binding_route, "generic_xbutton1")
        self.assertTrue(queued.binding_suppressed)
        self.assertEqual(queued.binding_callbacks, (old_callback,))

        new_callback = Mock()
        new_builder = hook.new_binding_builder()
        new_builder.register(module.MouseEvent.XBUTTON1_DOWN, new_callback)
        hook.publish_bindings(new_builder)
        hook._dispatch(queued)

        old_callback.assert_not_called()
        new_callback.assert_not_called()


@unittest.skipUnless(sys.platform == "win32", "Windows-only worker lifecycle test")
class WindowsMouseHookShutdownTests(unittest.TestCase):
    def test_stop_preserves_live_worker_reference(self):
        module = importlib.import_module("core.mouse_hook_windows")
        hook = module.MouseHook()
        worker = Mock()
        worker.is_alive.return_value = True
        hook._dispatch_worker_thread = worker

        with patch.object(module.threading, "current_thread", return_value=object()):
            stopped = hook.stop()

        self.assertFalse(stopped)
        self.assertIs(hook._dispatch_worker_thread, worker)
        worker.join.assert_called_once_with(timeout=1)


class LinuxMouseHookReconnectTests(unittest.TestCase):
    def _reload_for_linux(self):
        fake_evdev = SimpleNamespace(
            ecodes=_FakeLinuxEcodes,
            UInput=_FakeLinuxUInput,
            InputDevice=Mock(name="InputDevice"),
        )
        with (
            patch.object(sys, "platform", "linux"),
            patch.dict(sys.modules, {"evdev": fake_evdev}),
        ):
            sys.modules.pop("core.mouse_hook_linux", None)
            if hasattr(core, "mouse_hook_linux"):
                delattr(core, "mouse_hook_linux")
            mouse_hook_linux = importlib.import_module("core.mouse_hook_linux")
            importlib.reload(mouse_hook)

        def cleanup():
            sys.modules.pop("core.mouse_hook_linux", None)
            if hasattr(core, "mouse_hook_linux"):
                delattr(core, "mouse_hook_linux")
            importlib.reload(mouse_hook)

        self.addCleanup(cleanup)
        return mouse_hook

    def _fake_caps(self, module, *, include_side=True):
        ecodes = module._ecodes
        key_codes = [ecodes.BTN_LEFT, ecodes.BTN_RIGHT, ecodes.BTN_MIDDLE]
        if include_side:
            key_codes.extend([ecodes.BTN_SIDE, ecodes.BTN_EXTRA])
        return {
            ecodes.EV_REL: [ecodes.REL_X, ecodes.REL_Y],
            ecodes.EV_KEY: key_codes,
        }

    def _patch_evdev_lookup(self, module, devices_by_path):
        fake_evdev_mod = SimpleNamespace(list_devices=lambda: list(devices_by_path))

        def fake_input_device(path):
            return devices_by_path[path]

        return (
            patch.object(module, "_evdev_mod", fake_evdev_mod),
            patch.object(module, "_InputDevice", side_effect=fake_input_device),
        )

    def test_find_mouse_device_prefers_logitech_candidates(self):
        module = self._reload_for_linux()
        logi = _FakeEvdevDevice(
            name="MX Master 3S",
            path="/dev/input/event1",
            vendor=module._LOGI_VENDOR,
            capabilities=self._fake_caps(module),
        )
        generic = _FakeEvdevDevice(
            name="Generic Mouse",
            path="/dev/input/event0",
            vendor=0x1234,
            capabilities=self._fake_caps(module),
        )

        patches = self._patch_evdev_lookup(
            module,
            {
                generic.path: generic,
                logi.path: logi,
            },
        )
        with patches[0], patches[1]:
            chosen = module.MouseHook()._find_mouse_device()

        self.assertIs(chosen, logi)
        self.assertTrue(generic.close.called)
        self.assertFalse(logi.close.called)

    def test_find_mouse_device_prefers_known_supported_logitech_model(self):
        module = self._reload_for_linux()
        legacy = _FakeEvdevDevice(
            name="Logitech Performance MX",
            path="/dev/input/event11",
            vendor=module._LOGI_VENDOR,
            product=0x101A,
            capabilities=self._fake_caps(module),
        )
        modern = _FakeEvdevDevice(
            name="Logitech MX Master 3S",
            path="/dev/input/event22",
            vendor=module._LOGI_VENDOR,
            product=0xB034,
            capabilities=self._fake_caps(module),
        )

        patches = self._patch_evdev_lookup(
            module,
            {
                legacy.path: legacy,
                modern.path: modern,
            },
        )
        with patches[0], patches[1]:
            chosen = module.MouseHook()._find_mouse_device()

        self.assertIs(chosen, modern)
        self.assertTrue(legacy.close.called)
        self.assertFalse(modern.close.called)

    def test_find_mouse_device_returns_none_when_only_non_logitech_candidates_exist(self):
        module = self._reload_for_linux()
        generic_one = _FakeEvdevDevice(
            name="Generic Mouse A",
            path="/dev/input/event0",
            vendor=0x1234,
            capabilities=self._fake_caps(module),
        )
        generic_two = _FakeEvdevDevice(
            name="Generic Mouse B",
            path="/dev/input/event1",
            vendor=0x4321,
            capabilities=self._fake_caps(module),
        )

        patches = self._patch_evdev_lookup(
            module,
            {
                generic_one.path: generic_one,
                generic_two.path: generic_two,
            },
        )
        with patches[0], patches[1]:
            chosen = module.MouseHook()._find_mouse_device()

        self.assertIsNone(chosen)

    def test_find_mouse_device_logs_permission_errors_opening_evdev(self):
        module = self._reload_for_linux()
        fake_evdev_mod = SimpleNamespace(list_devices=lambda: ["/dev/input/event0"])

        with (
            patch.object(module, "_evdev_mod", fake_evdev_mod),
            patch.object(module, "_InputDevice", side_effect=PermissionError("denied")),
            patch("builtins.print") as print_mock,
        ):
            chosen = module.MouseHook()._find_mouse_device()

        self.assertIsNone(chosen)
        messages = [
            " ".join(str(arg) for arg in call.args)
            for call in print_mock.call_args_list
        ]
        self.assertTrue(
            any("Permission denied opening /dev/input/event0" in msg for msg in messages)
        )

    def test_find_mouse_device_falls_back_to_glob_when_evdev_list_is_empty(self):
        module = self._reload_for_linux()
        logi = _FakeEvdevDevice(
            name="MX Master 3S",
            path="/dev/input/event4",
            vendor=module._LOGI_VENDOR,
            capabilities=self._fake_caps(module),
        )
        fake_evdev_mod = SimpleNamespace(list_devices=lambda: [])

        with (
            patch.object(module, "_evdev_mod", fake_evdev_mod),
            patch.object(module.glob, "glob", return_value=[logi.path]),
            patch.object(module, "_InputDevice", return_value=logi),
            patch("builtins.print") as print_mock,
        ):
            module._LOG_ONCE_KEYS.clear()
            chosen = module.MouseHook()._find_mouse_device()

        self.assertIs(chosen, logi)
        messages = [
            " ".join(str(arg) for arg in call.args)
            for call in print_mock.call_args_list
        ]
        self.assertTrue(
            any("falling back to visible /dev/input/event* nodes" in msg for msg in messages)
        )

    def test_hid_reconnect_requests_rescan_for_fallback_evdev_device(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        hook._running = True
        hook._hid_gesture = SimpleNamespace(connected_device={"name": "MX Master 3S"})
        hook._evdev_device = SimpleNamespace(info=SimpleNamespace(vendor=0x1234))

        hook._on_hid_connect()

        self.assertFalse(hook.device_connected)
        self.assertTrue(hook.hid_ready)
        self.assertEqual(hook.connected_device, {"name": "MX Master 3S"})
        self.assertEqual(
            hook.hid_runtime_state,
            HidRuntimeState(
                input_ready=False,
                hid_ready=True,
                connected_device={"name": "MX Master 3S"},
            ),
        )
        self.assertTrue(hook._rescan_requested.is_set())
        self.assertTrue(hook._evdev_wakeup.is_set())

    def test_hid_connect_wakes_evdev_scan_when_no_evdev_device_is_grabbed(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        hook._running = True
        hook._hid_gesture = SimpleNamespace(connected_device={"name": "MX Master 3S"})

        hook._on_hid_connect()

        self.assertTrue(hook.hid_ready)
        self.assertTrue(hook._rescan_requested.is_set())
        self.assertTrue(hook._evdev_wakeup.is_set())

    def test_hid_reconnect_does_not_rescan_when_evdev_already_grabs_logitech(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        hook._hid_gesture = SimpleNamespace(connected_device={"name": "MX Master 3S"})
        hook._evdev_device = SimpleNamespace(
            info=SimpleNamespace(vendor=module._LOGI_VENDOR)
        )
        hook._evdev_connected_device = {"name": "MX Master 3S"}
        hook._set_evdev_ready(True)

        hook._on_hid_connect()

        self.assertTrue(hook.device_connected)
        self.assertFalse(hook._rescan_requested.is_set())
        self.assertEqual(
            hook.hid_runtime_state,
            HidRuntimeState(
                input_ready=True,
                hid_ready=True,
                connected_device={"name": "MX Master 3S"},
            ),
        )

    def test_hid_connect_does_not_mark_device_connected_when_evdev_is_missing(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        hook._hid_gesture = SimpleNamespace(connected_device={"name": "MX Master 3S"})
        hook._evdev_device = SimpleNamespace(info=SimpleNamespace(vendor=0x1234))

        hook._on_hid_connect()

        self.assertFalse(hook.device_connected)

    def test_hid_disconnect_keeps_evdev_driven_connected_state(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        hook._hid_gesture = SimpleNamespace(connected_device={"name": "MX Master 3S"})
        hook._evdev_device = SimpleNamespace(info=SimpleNamespace(vendor=module._LOGI_VENDOR))
        hook._evdev_connected_device = {"name": "MX Master 3S"}
        hook._set_evdev_ready(True)
        hook._hid_ready = True
        hook._connected_device = {"name": "MX Master 3S"}

        hook._on_hid_disconnect()

        self.assertTrue(hook.device_connected)
        self.assertEqual(hook.connected_device, {"name": "MX Master 3S"})
        self.assertEqual(
            hook.hid_runtime_state,
            HidRuntimeState(
                input_ready=True,
                hid_ready=False,
                connected_device={"name": "MX Master 3S"},
            ),
        )

    def test_setup_evdev_marks_connected_and_populates_fallback_device_info(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        logi = _FakeEvdevDevice(
            name="MX Master 3S",
            path="/dev/input/event1",
            vendor=module._LOGI_VENDOR,
            capabilities=self._fake_caps(module),
        )

        with (
            patch.object(hook, "_find_mouse_device", return_value=logi),
        ):
            self.assertTrue(hook._setup_evdev())

        self.assertTrue(hook.device_connected)
        self.assertEqual(getattr(hook.connected_device, "display_name", None), "MX Master 3S")
        self.assertEqual(getattr(hook.connected_device, "source", None), "evdev")
        self.assertEqual(hook.hid_runtime_state.input_ready, True)
        self.assertEqual(hook.hid_runtime_state.hid_ready, False)
        self.assertEqual(
            getattr(hook.hid_runtime_state.connected_device, "source", None),
            "evdev",
        )
        self.assertTrue(hook.evdev_remap_ready)

    def test_setup_evdev_in_passthrough_detects_without_uinput_or_grab(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        hook.set_ui_passthrough(True)
        logi = _FakeEvdevDevice(
            name="MX Master 3S",
            path="/dev/input/event1",
            vendor=module._LOGI_VENDOR,
            capabilities=self._fake_caps(module),
        )

        with (
            patch.object(hook, "_find_mouse_device", return_value=logi),
            patch.object(module, "_UInput", side_effect=AssertionError("no uinput")),
        ):
            self.assertTrue(hook._setup_evdev())

        self.assertTrue(hook.device_connected)
        self.assertTrue(hook.evdev_ready)
        self.assertFalse(hook.evdev_remap_ready)
        logi.grab.assert_not_called()
        self.assertIsNone(hook._uinput)

    def test_setup_evdev_uinput_failure_keeps_detection_without_remap(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        messages = []
        hook.set_status_callback(messages.append)
        logi = _FakeEvdevDevice(
            name="MX Master 3S",
            path="/dev/input/event1",
            vendor=module._LOGI_VENDOR,
            capabilities=self._fake_caps(module),
        )

        with (
            patch.object(hook, "_find_mouse_device", return_value=logi),
            patch.object(module, "_UInput", side_effect=PermissionError("denied")),
        ):
            self.assertTrue(hook._setup_evdev())

        self.assertTrue(hook.device_connected)
        self.assertTrue(hook.evdev_ready)
        self.assertFalse(hook.evdev_remap_ready)
        logi.grab.assert_not_called()
        self.assertEqual(len(messages), 1)
        self.assertIn("virtual input device could not be created", messages[0])

    def test_setup_evdev_grab_failure_keeps_detection_without_remap(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        messages = []
        hook.set_status_callback(messages.append)
        hook._dispatch = Mock()
        logi = _FakeEvdevDevice(
            name="MX Master 3S",
            path="/dev/input/event1",
            vendor=module._LOGI_VENDOR,
            capabilities=self._fake_caps(module),
        )
        logi.grab.side_effect = OSError("busy")

        with patch.object(hook, "_find_mouse_device", return_value=logi):
            self.assertTrue(hook._setup_evdev())

        self.assertTrue(hook.device_connected)
        self.assertFalse(hook.evdev_remap_ready)
        self.assertIsNone(hook._uinput)
        self.assertEqual(len(messages), 1)
        self.assertIn("mouse could not be grabbed", messages[0])

        hook._handle_button(
            SimpleNamespace(
                type=module._ecodes.EV_KEY,
                code=module._ecodes.BTN_MIDDLE,
                value=1,
            )
        )
        hook._handle_rel(
            SimpleNamespace(
                type=module._ecodes.EV_REL,
                code=module._ecodes.REL_HWHEEL,
                value=1,
            )
        )

        hook._dispatch.assert_not_called()

    def test_filtered_uinput_events_drop_hi_res_wheel_codes(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        module._ecodes.EV_FF = 0x15
        module._ecodes.REL_WHEEL_HI_RES = 0x0B
        module._ecodes.REL_HWHEEL_HI_RES = 0x0C
        dev = _FakeEvdevDevice(
            name="MX Master 3S",
            path="/dev/input/event1",
            vendor=module._LOGI_VENDOR,
            capabilities={
                module._ecodes.EV_SYN: [0, 1, 2],
                module._ecodes.EV_REL: [
                    module._ecodes.REL_X,
                    module._ecodes.REL_Y,
                    module._ecodes.REL_WHEEL,
                    module._ecodes.REL_HWHEEL,
                    module._ecodes.REL_WHEEL_HI_RES,
                    module._ecodes.REL_HWHEEL_HI_RES,
                ],
                module._ecodes.EV_KEY: [
                    module._ecodes.BTN_LEFT,
                    module._ecodes.BTN_RIGHT,
                    module._ecodes.BTN_MIDDLE,
                ],
                module._ecodes.EV_FF: [80],
            },
        )

        events = hook._filtered_uinput_events(dev)

        self.assertNotIn(module._ecodes.EV_SYN, events)
        self.assertNotIn(module._ecodes.EV_FF, events)
        self.assertEqual(
            events[module._ecodes.EV_REL],
            [
                module._ecodes.REL_X,
                module._ecodes.REL_Y,
                module._ecodes.REL_WHEEL,
                module._ecodes.REL_HWHEEL,
            ],
        )

    def test_listen_loop_exits_when_rescan_is_requested(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        hook._running = True
        hook._set_evdev_remap_ready(True)
        hook._evdev_device = SimpleNamespace(fd=11, read=Mock(return_value=[]))
        select_calls = []

        def fake_select(readable, writable, exceptional, timeout):
            select_calls.append(timeout)
            hook._rescan_requested.set()
            return ([11], [], [])

        with patch.object(module, "_select_mod", SimpleNamespace(select=fake_select)):
            hook._listen_loop()

        self.assertEqual(select_calls, [0.5])
        self.assertEqual(hook._evdev_device.read.call_count, 1)

    def test_listen_loop_waits_without_polling_when_remap_is_not_ready(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        hook._running = True
        hook._evdev_device = SimpleNamespace(fd=11, read=Mock(return_value=[]))
        select_mock = Mock()

        def stop_wait(timeout):
            hook._running = False

        with (
            patch.object(module, "_select_mod", SimpleNamespace(select=select_mock)),
            patch.object(hook, "_wait_for_evdev_wakeup", side_effect=stop_wait) as wait_mock,
        ):
            hook._listen_loop()

        wait_mock.assert_called_once_with(None)
        select_mock.assert_not_called()
        hook._evdev_device.read.assert_not_called()

    def test_evdev_loop_clears_rescan_and_retries_after_listen_returns(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        hook._running = True
        setup_calls = []
        seen_rescan_state = []
        cleanup_calls = []

        def fake_setup():
            setup_calls.append(len(setup_calls))
            if len(setup_calls) == 1:
                hook._set_evdev_remap_ready(True)
                return True
            seen_rescan_state.append(hook._rescan_requested.is_set())
            hook._running = False
            return False

        def fake_listen():
            hook._rescan_requested.set()

        def fake_cleanup():
            cleanup_calls.append(True)

        with (
            patch.object(hook, "_setup_evdev", side_effect=fake_setup),
            patch.object(hook, "_listen_loop", side_effect=fake_listen),
            patch.object(hook, "_cleanup_evdev", side_effect=fake_cleanup),
            patch.object(module.time, "sleep", return_value=None),
        ):
            hook._evdev_loop()

        self.assertEqual(len(setup_calls), 2)
        self.assertEqual(seen_rescan_state, [False])
        self.assertEqual(len(cleanup_calls), 1)

    def test_evdev_loop_detection_only_waits_without_reopening(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        hook._running = True
        setup_calls = []
        cleanup_calls = []
        wait_timeouts = []

        def fake_setup():
            setup_calls.append(True)
            hook._evdev_device = SimpleNamespace(close=Mock())
            hook._set_evdev_ready(True)
            hook._set_evdev_remap_ready(False)
            return True

        def fake_wait(timeout):
            wait_timeouts.append(timeout)
            self.assertIsNotNone(hook._evdev_device)
            hook._running = False

        def fake_cleanup():
            cleanup_calls.append(True)
            hook._evdev_device = None

        with (
            patch.object(hook, "_setup_evdev", side_effect=fake_setup),
            patch.object(hook, "_wait_for_evdev_wakeup", side_effect=fake_wait),
            patch.object(hook, "_cleanup_evdev", side_effect=fake_cleanup),
        ):
            hook._evdev_loop()

        self.assertEqual(len(setup_calls), 1)
        self.assertEqual(wait_timeouts, [None])
        self.assertEqual(len(cleanup_calls), 1)

    def test_evdev_remap_status_dedupes_by_ready_reason_tuple(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        messages = []
        hook.set_status_callback(messages.append)

        hook._set_evdev_remap_ready(False, "uinput_failed")
        hook._set_evdev_remap_ready(False, "uinput_failed")
        hook._set_evdev_remap_ready(False, "grab_failed")
        hook._set_evdev_remap_ready(True)
        hook._disable_evdev_remapping()
        hook._set_evdev_remap_ready(True)

        self.assertEqual(len(messages), 3)
        self.assertIn("virtual input device could not be created", messages[0])
        self.assertIn("mouse could not be grabbed", messages[1])
        self.assertEqual(messages[2], "Linux evdev remapping restored.")

    def test_evdev_remap_helpers_are_idempotent(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()

        self.assertFalse(hook._acquire_evdev_grab())
        hook._disable_evdev_remapping()

        dev = _FakeEvdevDevice(
            name="MX Master 3S",
            path="/dev/input/event1",
            vendor=module._LOGI_VENDOR,
            capabilities=self._fake_caps(module),
        )
        hook._evdev_device = dev

        self.assertTrue(hook._enable_evdev_remapping())
        self.assertTrue(hook._enable_evdev_remapping())

        dev.grab.assert_called_once()
        self.assertTrue(hook.evdev_remap_ready)

    def test_hid_mode_shift_dispatches_when_evdev_remap_is_unavailable(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        hook._ui_passthrough = False
        hook._set_evdev_remap_ready(False, "grab_failed")
        hook._dispatch = Mock()

        hook._on_hid_mode_shift_down()

        hook._dispatch.assert_called_once()

    def test_gesture_click_callback_fires_again_after_reconnect(self):
        module = self._reload_for_linux()
        seen = []

        with (
            patch.object(module, "HidGestureListener", _CapturingListener),
            patch.object(module, "_EVDEV_OK", False),
        ):
            hook = module.MouseHook()
            hook.register(module.MouseEvent.GESTURE_CLICK, lambda event: seen.append(event.event_type))
            hook.start()
            listener = hook._hid_gesture

            listener.on_down()
            listener.on_up()
            hook._on_hid_disconnect()
            hook._on_hid_connect()
            listener.on_down()
            listener.on_up()

        self.assertEqual(
            seen,
            [module.MouseEvent.GESTURE_CLICK, module.MouseEvent.GESTURE_CLICK],
        )

    def test_ui_passthrough_does_not_mirror_ungrabbed_events(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        forwarded = Mock()
        uinput = SimpleNamespace(write_event=forwarded, write=Mock())
        hook._uinput = uinput
        hook._dispatch = Mock()
        hook.invert_vscroll = True
        hook.set_ui_passthrough(True)

        event = SimpleNamespace(
            type=module._ecodes.EV_REL,
            code=module._ecodes.REL_WHEEL,
            value=1,
        )

        hook._handle_rel(event)

        forwarded.assert_not_called()
        uinput.write.assert_not_called()
        hook._dispatch.assert_not_called()

    def test_ui_passthrough_releases_grab_and_wakes_evdev_loop(self):
        module = self._reload_for_linux()
        hook = module.MouseHook()
        messages = []
        hook.set_status_callback(messages.append)
        dev = _FakeEvdevDevice(
            name="MX Master 3S",
            path="/dev/input/event1",
            vendor=module._LOGI_VENDOR,
            capabilities=self._fake_caps(module),
        )
        hook._evdev_device = dev
        hook._evdev_grabbed = True

        hook.set_ui_passthrough(True)
        hook.set_ui_passthrough(False)

        dev.ungrab.assert_called_once()
        dev.grab.assert_called_once()
        self.assertFalse(hook._rescan_requested.is_set())
        self.assertTrue(hook.evdev_remap_ready)
        self.assertEqual(
            messages,
            [
                "Linux input passthrough enabled; evdev remapping paused",
                "Linux input passthrough disabled; evdev remapping restored",
            ],
        )

    def test_mode_shift_callbacks_fire_again_after_reconnect(self):
        module = self._reload_for_linux()
        seen = []

        with (
            patch.object(module, "HidGestureListener", _CapturingListener),
            patch.object(module, "_EVDEV_OK", False),
        ):
            hook = module.MouseHook()
            hook.divert_mode_shift = True
            hook.register(module.MouseEvent.MODE_SHIFT_DOWN, lambda event: seen.append(event.event_type))
            hook.register(module.MouseEvent.MODE_SHIFT_UP, lambda event: seen.append(event.event_type))
            hook.start()
            listener = hook._hid_gesture

            listener.extra_diverts[0x00C4]["on_down"]()
            listener.extra_diverts[0x00C4]["on_up"]()
            hook._on_hid_disconnect()
            hook._on_hid_connect()
            listener.extra_diverts[0x00C4]["on_down"]()
            listener.extra_diverts[0x00C4]["on_up"]()

        self.assertEqual(
            seen,
            [
                module.MouseEvent.MODE_SHIFT_DOWN,
                module.MouseEvent.MODE_SHIFT_UP,
                module.MouseEvent.MODE_SHIFT_DOWN,
                module.MouseEvent.MODE_SHIFT_UP,
            ],
        )


@unittest.skipUnless(sys.platform == "darwin", "macOS-only tests")
class MacOSEventTapDisabledTests(unittest.TestCase):
    """Verify CGEventTap is re-enabled when macOS disables it."""

    def setUp(self):
        self.mock_quartz = MagicMock(name="Quartz")
        mouse_hook.Quartz = self.mock_quartz

    def tearDown(self):
        if hasattr(mouse_hook, "Quartz") and isinstance(
                mouse_hook.Quartz, MagicMock):
            del mouse_hook.Quartz

    def _make_hook(self):
        hook = mouse_hook.MouseHook()
        hook._running = True
        hook._tap = MagicMock(name="tap")
        return hook

    def test_reenable_on_timeout(self):
        hook = self._make_hook()
        dummy = MagicMock(name="cg_event")

        hook._event_tap_callback(
            None, mouse_hook._kCGEventTapDisabledByTimeout, dummy, None)

        self.mock_quartz.CGEventTapEnable.assert_called_once_with(
            hook._tap, True)

    def test_reenable_on_user_input(self):
        hook = self._make_hook()
        dummy = MagicMock(name="cg_event")

        hook._event_tap_callback(
            None, mouse_hook._kCGEventTapDisabledByUserInput, dummy, None)

        self.mock_quartz.CGEventTapEnable.assert_called_once_with(
            hook._tap, True)

    def test_normal_event_does_not_reenable(self):
        hook = self._make_hook()
        dummy = MagicMock(name="cg_event")
        self.mock_quartz.CGEventGetIntegerValueField.return_value = 0

        hook._event_tap_callback(None, 1, dummy, None)  # kCGEventLeftMouseDown

        self.mock_quartz.CGEventTapEnable.assert_not_called()


@unittest.skipUnless(sys.platform == "darwin", "macOS-only tests")
class MacOSTrackpadScrollFilterTests(unittest.TestCase):
    """Verify CGEventTap callback passes through trackpad events untouched."""

    _kCGScrollWheelEventIsContinuous = 88
    _kCGEventScrollWheel = 22  # Quartz.kCGEventScrollWheel

    def setUp(self):
        self.mock_quartz = MagicMock(name="Quartz")
        self.mock_quartz.kCGEventScrollWheel = self._kCGEventScrollWheel
        mouse_hook.Quartz = self.mock_quartz

    def tearDown(self):
        if hasattr(mouse_hook, "Quartz") and isinstance(
                mouse_hook.Quartz, MagicMock):
            del mouse_hook.Quartz

    def _make_hook(self):
        hook = mouse_hook.MouseHook()
        hook._running = True
        hook._tap = MagicMock(name="tap")
        hook.invert_vscroll = True
        hook.block(mouse_hook.MouseEvent.HSCROLL_LEFT)
        hook.block(mouse_hook.MouseEvent.HSCROLL_RIGHT)
        return hook

    def _mock_get_field(self, is_continuous, source_user_data=0):
        """side_effect: returns is_continuous for field 88, source_user_data
        for kCGEventSourceUserData, and 0 for everything else."""
        def _get(event, field):
            if field == self._kCGScrollWheelEventIsContinuous:
                return is_continuous
            if field == self.mock_quartz.kCGEventSourceUserData:
                return source_user_data
            return 0
        return _get

    def test_trackpad_scroll_passes_through_callback(self):
        """Trackpad continuous scroll should be returned as-is, not blocked."""
        hook = self._make_hook()
        cg_event = MagicMock(name="cg_event")
        self.mock_quartz.CGEventGetIntegerValueField.side_effect = \
            self._mock_get_field(is_continuous=1)

        result = hook._event_tap_callback(
            None, self._kCGEventScrollWheel, cg_event, None)

        self.assertIs(result, cg_event)
        # Verify no HSCROLL events were dispatched
        self.assertTrue(hook._dispatch_queue.empty())

    def test_trackpad_hscroll_not_blocked(self):
        """Trackpad horizontal scroll must NOT trigger hscroll action."""
        hook = self._make_hook()
        cg_event = MagicMock(name="cg_event")

        def _get(event, field):
            if field == self._kCGScrollWheelEventIsContinuous:
                return 1  # trackpad
            if field == self.mock_quartz.kCGScrollWheelEventFixedPtDeltaAxis2:
                return 5 * 65536  # non-zero horizontal delta
            if field == self.mock_quartz.kCGEventSourceUserData:
                return 0
            return 0
        self.mock_quartz.CGEventGetIntegerValueField.side_effect = _get

        result = hook._event_tap_callback(
            None, self._kCGEventScrollWheel, cg_event, None)

        self.assertIs(result, cg_event)  # passed through, not blocked
        self.assertTrue(hook._dispatch_queue.empty())

    def test_trackpad_filter_can_be_disabled(self):
        """Continuous scroll should be handled when ignore_trackpad is off."""
        hook = self._make_hook()
        hook.ignore_trackpad = False
        cg_event = MagicMock(name="cg_event")

        def _get(event, field):
            if field == self._kCGScrollWheelEventIsContinuous:
                return 1  # trackpad / Magic Mouse
            if field == self.mock_quartz.kCGScrollWheelEventFixedPtDeltaAxis2:
                return 3 * 65536  # positive = HSCROLL_RIGHT
            if field == self.mock_quartz.kCGEventSourceUserData:
                return 0
            return 0
        self.mock_quartz.CGEventGetIntegerValueField.side_effect = _get

        result = hook._event_tap_callback(
            None, self._kCGEventScrollWheel, cg_event, None)

        self.assertIsNone(result)
        self.assertFalse(hook._dispatch_queue.empty())
        event = hook._dispatch_queue.get_nowait()
        self.assertEqual(event.event_type, mouse_hook.MouseEvent.HSCROLL_RIGHT)

    def test_mouse_wheel_hscroll_dispatched_and_blocked(self):
        """Discrete mouse wheel horizontal scroll SHOULD dispatch and block."""
        hook = self._make_hook()
        cg_event = MagicMock(name="cg_event")

        def _get(event, field):
            if field == self._kCGScrollWheelEventIsContinuous:
                return 0  # mouse wheel
            if field == self.mock_quartz.kCGScrollWheelEventFixedPtDeltaAxis2:
                return 3 * 65536  # positive = HSCROLL_RIGHT
            if field == self.mock_quartz.kCGEventSourceUserData:
                return 0
            return 0
        self.mock_quartz.CGEventGetIntegerValueField.side_effect = _get

        result = hook._event_tap_callback(
            None, self._kCGEventScrollWheel, cg_event, None)

        self.assertIsNone(result)  # blocked
        self.assertFalse(hook._dispatch_queue.empty())
        event = hook._dispatch_queue.get_nowait()
        self.assertEqual(event.event_type, mouse_hook.MouseEvent.HSCROLL_RIGHT)


if __name__ == "__main__":
    unittest.main()
