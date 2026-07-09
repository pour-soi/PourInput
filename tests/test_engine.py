import copy
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from core.config import DEFAULT_CONFIG
from core.mouse_hook import MouseEvent
from core.mouse_hook_types import HidRuntimeState


class _FakeMouseHook:
    def __init__(self):
        self.invert_vscroll = False
        self.invert_hscroll = False
        self.debug_mode = False
        self.connected_device = None
        self.device_connected = False
        self._hid_gesture = None
        self.start_called = False
        self.stop_called = False
        self.sync_hid_extra_diverts_calls = 0
        self.blocked_events = []
        self.registered_events = []
        self.callbacks = {}

    def set_debug_callback(self, cb):
        self._debug_callback = cb

    def set_gesture_callback(self, cb):
        self._gesture_callback = cb

    def set_status_callback(self, cb):
        self._status_callback = cb

    def set_connection_change_callback(self, cb):
        self._connection_change_callback = cb

    def configure_gestures(self, **kwargs):
        self._gesture_config = kwargs

    def block(self, event_type):
        self.blocked_events.append(event_type)

    def register(self, event_type, callback):
        self.registered_events.append(event_type)
        self.callbacks.setdefault(event_type, []).append(callback)

    def reset_bindings(self):
        self.blocked_events = []
        self.registered_events = []
        self.callbacks = {}

    def sync_hid_extra_diverts(self):
        self.sync_hid_extra_diverts_calls += 1
        return True

    def start(self):
        self.start_called = True

    def stop(self):
        self.stop_called = True


class _FakeAppDetector:
    def __init__(self, callback):
        self.callback = callback
        self.start_called = False
        self.stop_called = False

    def start(self):
        self.start_called = True

    def stop(self):
        self.stop_called = True


class _ImmediateThread:
    def __init__(self, target=None, args=(), kwargs=None, **_):
        self._target = target
        self._args = args
        self._kwargs = kwargs or {}

    def start(self):
        if self._target:
            self._target(*self._args, **self._kwargs)


class _RecordedThread:
    def __init__(self, target=None, args=(), kwargs=None, name=None, **_):
        self._target = target
        self._args = args
        self._kwargs = kwargs or {}
        self.name = name
        self.start_called = False
        self.join = Mock()

    def start(self):
        self.start_called = True

    def run_target(self):
        if self._target:
            return self._target(*self._args, **self._kwargs)
        return None


class EngineHorizontalScrollTests(unittest.TestCase):
    def _make_engine(self):
        from core.engine import Engine

        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg["settings"]["hscroll_threshold"] = 1

        with (
            patch("core.engine.MouseHook", _FakeMouseHook),
            patch("core.engine.AppDetector", _FakeAppDetector),
            patch("core.engine.load_config", return_value=cfg),
        ):
            return Engine()

    def test_hscroll_desktop_action_uses_cooldown(self):
        engine = self._make_engine()
        handler = engine._make_hscroll_handler("space_left")

        with patch("core.engine.execute_action") as execute_action_mock:
            handler(SimpleNamespace(
                event_type=MouseEvent.HSCROLL_LEFT,
                raw_data=1,
                timestamp=1.00,
            ))
            handler(SimpleNamespace(
                event_type=MouseEvent.HSCROLL_LEFT,
                raw_data=1,
                timestamp=1.05,
            ))
            handler(SimpleNamespace(
                event_type=MouseEvent.HSCROLL_LEFT,
                raw_data=1,
                timestamp=1.45,
            ))

        self.assertEqual(execute_action_mock.call_count, 2)

    def test_hscroll_accumulates_fractional_mac_deltas(self):
        engine = self._make_engine()
        handler = engine._make_hscroll_handler("space_right")

        with patch("core.engine.execute_action") as execute_action_mock:
            handler(SimpleNamespace(
                event_type=MouseEvent.HSCROLL_RIGHT,
                raw_data=0.35,
                timestamp=2.00,
            ))
            handler(SimpleNamespace(
                event_type=MouseEvent.HSCROLL_RIGHT,
                raw_data=0.40,
                timestamp=2.02,
            ))
            handler(SimpleNamespace(
                event_type=MouseEvent.HSCROLL_RIGHT,
                raw_data=0.30,
                timestamp=2.04,
            ))

        self.assertEqual(execute_action_mock.call_count, 1)

    def test_connection_callback_receives_current_state_immediately(self):
        engine = self._make_engine()
        engine.hook.device_connected = True

        seen = []
        engine.set_connection_change_callback(seen.append)

        self.assertEqual(seen, [True])

    def test_connection_callback_prefers_device_connected_flag_over_stale_identity(self):
        engine = self._make_engine()
        engine.hook.device_connected = False
        engine.hook.connected_device = SimpleNamespace(name="MX Master 3S")

        seen = []
        engine.set_connection_change_callback(seen.append)

        self.assertEqual(seen, [False])

    def test_hid_features_ready_requires_hid_identity(self):
        engine = self._make_engine()

        self.assertFalse(engine.hid_features_ready)

        engine.hook._hid_gesture = SimpleNamespace(connected_device=None)
        self.assertFalse(engine.hid_features_ready)

        engine.hook._hid_gesture = SimpleNamespace(
            connected_device=SimpleNamespace(name="MX Master 3S")
        )
        self.assertTrue(engine.hid_features_ready)

    def test_gesture_mapping_enabled_when_capability_reports_gesture_button(self):
        engine = self._make_engine()
        engine.cfg["profiles"]["default"]["mappings"]["gesture_left"] = "alt_tab"
        engine.hook.connected_device = SimpleNamespace(
            capabilities=SimpleNamespace(gesture_button=True),
            capability_inventory=SimpleNamespace(has_reprog_controls=True),
        )

        with (
            patch("core.engine.load_config", return_value=engine.cfg),
            patch("core.engine.sys.platform", "linux"),
        ):
            engine.reload_mappings()

        self.assertTrue(engine.hook._gesture_config["enabled"])
        self.assertIn("gesture_swipe_left", engine.hook.registered_events)

    def test_gesture_mapping_skips_when_capability_reports_no_gesture_button(self):
        engine = self._make_engine()
        engine.cfg["profiles"]["default"]["mappings"]["gesture_left"] = "alt_tab"
        engine.hook.connected_device = SimpleNamespace(
            capabilities=SimpleNamespace(gesture_button=False),
            capability_inventory=SimpleNamespace(has_reprog_controls=True),
        )

        with (
            patch("core.engine.load_config", return_value=engine.cfg),
            patch("core.engine.sys.platform", "linux"),
        ):
            engine.reload_mappings()

        self.assertFalse(engine.hook._gesture_config["enabled"])
        self.assertNotIn("gesture_swipe_left", engine.hook.registered_events)
        self.assertNotIn("gesture_swipe_left", engine.hook.blocked_events)

    def test_gesture_mapping_preserves_fallback_when_capability_is_unknown(self):
        engine = self._make_engine()
        engine.cfg["profiles"]["default"]["mappings"]["gesture_left"] = "alt_tab"
        engine.hook.connected_device = SimpleNamespace(
            capabilities=SimpleNamespace(gesture_button=False),
        )

        with patch("core.engine.load_config", return_value=engine.cfg):
            engine.reload_mappings()

        self.assertTrue(engine.hook._gesture_config["enabled"])
        self.assertIn("gesture_swipe_left", engine.hook.registered_events)

    def test_button_capabilities_drive_multi_action_registration(self):
        engine = self._make_engine()
        engine.cfg["profiles"]["default"]["mappings"]["xbutton1_long"] = "copy"
        engine.hook.device_connected = True
        engine.hook.connected_device = SimpleNamespace(
            supported_buttons=("middle",),
            capabilities=SimpleNamespace(
                reprogrammable_buttons=("middle", "mode_shift", "xbutton1"),
            ),
            capability_inventory=SimpleNamespace(has_reprog_controls=True),
        )

        with patch("core.engine.load_config", return_value=engine.cfg):
            engine.reload_mappings()

        self.assertTrue(engine.hook.divert_mode_shift)
        self.assertIn(MouseEvent.MODE_SHIFT_DOWN, engine.hook.registered_events)
        self.assertIn(MouseEvent.MODE_SHIFT_UP, engine.hook.registered_events)

    def test_generic_mouse_disable_runtime_clears_standard_button_management(self):
        from core.engine import Engine

        cfg_enabled = copy.deepcopy(DEFAULT_CONFIG)
        cfg_enabled["settings"]["generic_mouse_enabled"] = True
        cfg_enabled["profiles"]["default"]["mappings"]["middle"] = "mouse_middle_click"
        cfg_enabled["profiles"]["default"]["mappings"]["middle_long"] = "copy"
        cfg_enabled["profiles"]["default"]["mappings"]["generic_xbutton1"] = "browser_back"
        cfg_enabled["profiles"]["default"]["mappings"]["generic_xbutton1_long"] = "copy"

        cfg_disabled = copy.deepcopy(cfg_enabled)
        cfg_disabled["settings"]["generic_mouse_enabled"] = False

        with (
            patch("core.engine.MouseHook", _FakeMouseHook),
            patch("core.engine.AppDetector", _FakeAppDetector),
            patch("core.engine.load_config", return_value=cfg_enabled),
            patch("core.engine.sys.platform", "win32"),
        ):
            engine = Engine()

        self.assertEqual(
            engine.hook.registered_events.count(MouseEvent.MIDDLE_DOWN),
            1,
        )
        self.assertEqual(
            engine.hook.registered_events.count(MouseEvent.MIDDLE_UP),
            1,
        )
        self.assertEqual(
            engine.hook.registered_events.count(MouseEvent.XBUTTON1_DOWN),
            1,
        )
        self.assertEqual(
            engine.hook.registered_events.count(MouseEvent.XBUTTON1_UP),
            1,
        )
        self.assertIn(MouseEvent.MIDDLE_DOWN, engine.hook.blocked_events)
        self.assertIn(MouseEvent.MIDDLE_UP, engine.hook.blocked_events)
        self.assertIn(MouseEvent.XBUTTON1_DOWN, engine.hook.blocked_events)
        self.assertIn(MouseEvent.XBUTTON1_UP, engine.hook.blocked_events)

        with (
            patch("core.engine.load_config", return_value=cfg_disabled),
            patch("core.engine.sys.platform", "win32"),
        ):
            engine.reload_mappings()

        self.assertNotIn(MouseEvent.MIDDLE_DOWN, engine.hook.registered_events)
        self.assertNotIn(MouseEvent.MIDDLE_UP, engine.hook.registered_events)
        self.assertNotIn(MouseEvent.XBUTTON1_DOWN, engine.hook.registered_events)
        self.assertNotIn(MouseEvent.XBUTTON1_UP, engine.hook.registered_events)
        self.assertNotIn(MouseEvent.MIDDLE_DOWN, engine.hook.blocked_events)
        self.assertNotIn(MouseEvent.MIDDLE_UP, engine.hook.blocked_events)
        self.assertNotIn(MouseEvent.XBUTTON1_DOWN, engine.hook.blocked_events)
        self.assertNotIn(MouseEvent.XBUTTON1_UP, engine.hook.blocked_events)
        self.assertNotIn(MouseEvent.MIDDLE_DOWN, engine.hook.callbacks)
        self.assertNotIn(MouseEvent.MIDDLE_UP, engine.hook.callbacks)
        self.assertNotIn(MouseEvent.XBUTTON1_DOWN, engine.hook.callbacks)
        self.assertNotIn(MouseEvent.XBUTTON1_UP, engine.hook.callbacks)

        with (
            patch("core.engine.load_config", return_value=cfg_enabled),
            patch("core.engine.sys.platform", "win32"),
        ):
            engine.reload_mappings()

        self.assertEqual(
            engine.hook.registered_events.count(MouseEvent.MIDDLE_DOWN),
            1,
        )
        self.assertEqual(
            engine.hook.registered_events.count(MouseEvent.MIDDLE_UP),
            1,
        )
        self.assertEqual(
            engine.hook.registered_events.count(MouseEvent.XBUTTON1_DOWN),
            1,
        )
        self.assertEqual(
            engine.hook.registered_events.count(MouseEvent.XBUTTON1_UP),
            1,
        )
        self.assertIn(MouseEvent.MIDDLE_DOWN, engine.hook.blocked_events)
        self.assertIn(MouseEvent.MIDDLE_UP, engine.hook.blocked_events)
        self.assertIn(MouseEvent.XBUTTON1_DOWN, engine.hook.blocked_events)
        self.assertIn(MouseEvent.XBUTTON1_UP, engine.hook.blocked_events)
        self.assertEqual(len(engine.hook.callbacks[MouseEvent.MIDDLE_DOWN]), 1)
        self.assertEqual(len(engine.hook.callbacks[MouseEvent.MIDDLE_UP]), 1)
        self.assertEqual(len(engine.hook.callbacks[MouseEvent.XBUTTON1_DOWN]), 1)
        self.assertEqual(len(engine.hook.callbacks[MouseEvent.XBUTTON1_UP]), 1)

    def test_physical_xbutton_mapping_is_not_bound_on_windows_without_device_identity(self):
        engine = self._make_engine()
        engine.hook.device_connected = True
        engine.hook.connected_device = SimpleNamespace(
            supported_buttons=("middle", "xbutton1", "xbutton2"),
            capabilities=SimpleNamespace(
                reprogrammable_buttons=("middle", "xbutton1", "xbutton2"),
            ),
            capability_inventory=SimpleNamespace(has_reprog_controls=True),
        )

        with (
            patch("core.engine.load_config", return_value=engine.cfg),
            patch("core.engine.sys.platform", "win32"),
        ):
            engine.reload_mappings()

        self.assertNotIn(MouseEvent.XBUTTON1_DOWN, engine.hook.registered_events)
        self.assertNotIn(MouseEvent.XBUTTON2_DOWN, engine.hook.registered_events)
        self.assertNotIn(MouseEvent.XBUTTON1_DOWN, engine.hook.blocked_events)
        self.assertNotIn(MouseEvent.XBUTTON2_DOWN, engine.hook.blocked_events)

    def test_generic_mouse_mode_uses_generic_side_button_mappings_only(self):
        from core.engine import Engine

        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg["settings"]["generic_mouse_enabled"] = True
        cfg["profiles"]["default"]["mappings"]["generic_xbutton1"] = "browser_back"
        cfg["profiles"]["default"]["mappings"]["generic_xbutton1_long"] = "copy"

        with (
            patch("core.engine.MouseHook", _FakeMouseHook),
            patch("core.engine.AppDetector", _FakeAppDetector),
            patch("core.engine.load_config", return_value=cfg),
            patch("core.engine.sys.platform", "win32"),
        ):
            engine = Engine()

        self.assertEqual(
            engine.hook.registered_events.count(MouseEvent.XBUTTON1_DOWN),
            1,
        )
        self.assertEqual(
            engine.hook.registered_events.count(MouseEvent.XBUTTON1_UP),
            1,
        )
        self.assertNotIn(MouseEvent.XBUTTON2_DOWN, engine.hook.registered_events)
        self.assertNotIn(MouseEvent.XBUTTON2_UP, engine.hook.registered_events)
        self.assertIn(MouseEvent.XBUTTON1_DOWN, engine.hook.blocked_events)
        self.assertIn(MouseEvent.XBUTTON1_UP, engine.hook.blocked_events)
        self.assertNotIn(MouseEvent.XBUTTON2_DOWN, engine.hook.blocked_events)

    def test_generic_mouse_mode_passes_through_unmanaged_side_buttons(self):
        from core.engine import Engine

        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg["settings"]["generic_mouse_enabled"] = True

        with (
            patch("core.engine.MouseHook", _FakeMouseHook),
            patch("core.engine.AppDetector", _FakeAppDetector),
            patch("core.engine.load_config", return_value=cfg),
            patch("core.engine.sys.platform", "win32"),
        ):
            engine = Engine()

        self.assertNotIn(MouseEvent.XBUTTON1_DOWN, engine.hook.registered_events)
        self.assertNotIn(MouseEvent.XBUTTON1_UP, engine.hook.registered_events)
        self.assertNotIn(MouseEvent.XBUTTON2_DOWN, engine.hook.registered_events)
        self.assertNotIn(MouseEvent.XBUTTON2_UP, engine.hook.registered_events)
        self.assertNotIn(MouseEvent.XBUTTON1_DOWN, engine.hook.blocked_events)
        self.assertNotIn(MouseEvent.XBUTTON2_DOWN, engine.hook.blocked_events)

    def test_middle_mapping_passes_through_without_generic_mode_or_logitech_identity(self):
        from core.engine import Engine

        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg["settings"]["generic_mouse_enabled"] = False
        cfg["profiles"]["default"]["mappings"]["middle"] = "copy"
        cfg["profiles"]["default"]["mappings"]["middle_long"] = "paste"

        with (
            patch("core.engine.MouseHook", _FakeMouseHook),
            patch("core.engine.AppDetector", _FakeAppDetector),
            patch("core.engine.load_config", return_value=cfg),
            patch("core.engine.sys.platform", "win32"),
        ):
            engine = Engine()

        self.assertNotIn(MouseEvent.MIDDLE_DOWN, engine.hook.registered_events)
        self.assertNotIn(MouseEvent.MIDDLE_UP, engine.hook.registered_events)
        self.assertNotIn(MouseEvent.MIDDLE_DOWN, engine.hook.blocked_events)
        self.assertNotIn(MouseEvent.MIDDLE_UP, engine.hook.blocked_events)

    def test_generic_mouse_click_dispatches_existing_action_handler(self):
        from core.engine import Engine

        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg["settings"]["generic_mouse_enabled"] = True
        cfg["profiles"]["default"]["mappings"]["generic_xbutton2"] = "browser_forward"

        with (
            patch("core.engine.MouseHook", _FakeMouseHook),
            patch("core.engine.AppDetector", _FakeAppDetector),
            patch("core.engine.load_config", return_value=cfg),
            patch("core.engine.sys.platform", "win32"),
        ):
            engine = Engine()

        handler = engine.hook.callbacks[MouseEvent.XBUTTON2_DOWN][0]
        with patch("core.engine.execute_action") as execute_action_mock:
            handler(SimpleNamespace(event_type=MouseEvent.XBUTTON2_DOWN))

        execute_action_mock.assert_called_once_with("browser_forward")

    def test_generic_mouse_middle_click_dispatches_existing_action_handler(self):
        from core.engine import Engine

        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg["settings"]["generic_mouse_enabled"] = True
        cfg["profiles"]["default"]["mappings"]["middle"] = "copy"

        with (
            patch("core.engine.MouseHook", _FakeMouseHook),
            patch("core.engine.AppDetector", _FakeAppDetector),
            patch("core.engine.load_config", return_value=cfg),
            patch("core.engine.sys.platform", "win32"),
        ):
            engine = Engine()

        handler = engine.hook.callbacks[MouseEvent.MIDDLE_DOWN][0]
        with patch("core.engine.execute_action") as execute_action_mock:
            handler(SimpleNamespace(event_type=MouseEvent.MIDDLE_DOWN))

        execute_action_mock.assert_called_once_with("copy")

    def test_generic_mouse_long_press_reuses_multi_action_timing(self):
        from core.engine import Engine

        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg["settings"]["generic_mouse_enabled"] = True
        cfg["profiles"]["default"]["mappings"]["generic_xbutton1"] = "browser_back"
        cfg["profiles"]["default"]["mappings"]["generic_xbutton1_long"] = "copy"

        with (
            patch("core.engine.MouseHook", _FakeMouseHook),
            patch("core.engine.AppDetector", _FakeAppDetector),
            patch("core.engine.load_config", return_value=cfg),
            patch("core.engine.sys.platform", "win32"),
        ):
            engine = Engine()

        down = engine.hook.callbacks[MouseEvent.XBUTTON1_DOWN][0]
        up = engine.hook.callbacks[MouseEvent.XBUTTON1_UP][0]
        with (
            patch("core.engine.time.monotonic", side_effect=[10.000, 10.300]),
            patch("core.engine.execute_action") as execute_action_mock,
        ):
            down(SimpleNamespace(event_type=MouseEvent.XBUTTON1_DOWN))
            up(SimpleNamespace(event_type=MouseEvent.XBUTTON1_UP))

        execute_action_mock.assert_called_once_with("copy")

    def test_generic_mouse_middle_long_press_reuses_multi_action_timing(self):
        from core.engine import Engine

        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg["settings"]["generic_mouse_enabled"] = True
        cfg["profiles"]["default"]["mappings"]["middle"] = "mouse_middle_click"
        cfg["profiles"]["default"]["mappings"]["middle_long"] = "copy"

        with (
            patch("core.engine.MouseHook", _FakeMouseHook),
            patch("core.engine.AppDetector", _FakeAppDetector),
            patch("core.engine.load_config", return_value=cfg),
            patch("core.engine.sys.platform", "win32"),
        ):
            engine = Engine()

        down = engine.hook.callbacks[MouseEvent.MIDDLE_DOWN][0]
        up = engine.hook.callbacks[MouseEvent.MIDDLE_UP][0]
        with (
            patch("core.engine.time.monotonic", side_effect=[10.000, 10.300]),
            patch("core.engine.execute_action") as execute_action_mock,
        ):
            down(SimpleNamespace(event_type=MouseEvent.MIDDLE_DOWN))
            up(SimpleNamespace(event_type=MouseEvent.MIDDLE_UP))

        execute_action_mock.assert_called_once_with("copy")

    def test_reload_mappings_syncs_live_hid_extra_diverts(self):
        engine = self._make_engine()
        initial_calls = engine.hook.sync_hid_extra_diverts_calls

        with patch("core.engine.load_config", return_value=engine.cfg):
            engine.reload_mappings()

        self.assertEqual(
            engine.hook.sync_hid_extra_diverts_calls,
            initial_calls + 1,
        )

    def test_mode_shift_short_click_dispatches_configured_action(self):
        engine = self._make_engine()
        down = engine._make_multi_action_down_handler(
            "mode_shift",
            "screenshot_region_clip",
            "switch_scroll_mode",
        )
        up = engine._make_multi_action_up_handler(
            "mode_shift",
            "screenshot_region_clip",
            "switch_scroll_mode",
        )

        with (
            patch("core.engine.time.monotonic", side_effect=[10.000, 10.299]),
            patch("core.engine.execute_action") as execute_action_mock,
            patch.object(engine, "_switch_scroll_mode") as switch_mock,
        ):
            down(SimpleNamespace(event_type=MouseEvent.MODE_SHIFT_DOWN))
            up(SimpleNamespace(event_type=MouseEvent.MODE_SHIFT_UP))

        execute_action_mock.assert_called_once_with("screenshot_region_clip")
        switch_mock.assert_not_called()

    def test_mode_shift_long_press_switches_scroll_mode(self):
        engine = self._make_engine()
        down = engine._make_multi_action_down_handler(
            "mode_shift",
            "screenshot_region_clip",
            "switch_scroll_mode",
        )
        up = engine._make_multi_action_up_handler(
            "mode_shift",
            "screenshot_region_clip",
            "switch_scroll_mode",
        )

        with (
            patch("core.engine.time.monotonic", side_effect=[10.000, 10.300]),
            patch("core.engine.execute_action") as execute_action_mock,
            patch.object(engine, "_switch_scroll_mode") as switch_mock,
        ):
            down(SimpleNamespace(event_type=MouseEvent.MODE_SHIFT_DOWN))
            up(SimpleNamespace(event_type=MouseEvent.MODE_SHIFT_UP))

        execute_action_mock.assert_not_called()
        switch_mock.assert_called_once_with()

    def test_back_long_press_dispatches_configured_long_action(self):
        engine = self._make_engine()
        down = engine._make_multi_action_down_handler("xbutton1", "browser_back", "copy")
        up = engine._make_multi_action_up_handler("xbutton1", "browser_back", "copy")

        with (
            patch("core.engine.time.monotonic", side_effect=[10.000, 10.300]),
            patch("core.engine.execute_action") as execute_action_mock,
        ):
            down(SimpleNamespace(event_type=MouseEvent.XBUTTON1_DOWN))
            up(SimpleNamespace(event_type=MouseEvent.XBUTTON1_UP))

        execute_action_mock.assert_called_once_with("copy")

    def test_forward_click_dispatches_configured_click_action(self):
        engine = self._make_engine()
        down = engine._make_multi_action_down_handler("xbutton2", "browser_forward", "paste")
        up = engine._make_multi_action_up_handler("xbutton2", "browser_forward", "paste")

        with (
            patch("core.engine.time.monotonic", side_effect=[10.000, 10.100]),
            patch("core.engine.execute_action") as execute_action_mock,
        ):
            down(SimpleNamespace(event_type=MouseEvent.XBUTTON2_DOWN))
            up(SimpleNamespace(event_type=MouseEvent.XBUTTON2_UP))

        execute_action_mock.assert_called_once_with("browser_forward")

    def test_engine_projection_prefers_hid_runtime_state(self):
        engine = self._make_engine()
        device = SimpleNamespace(name="MX Master 3S")
        engine.hook.device_connected = False
        engine.hook.connected_device = SimpleNamespace(name="stale fallback")
        engine.hook._hid_gesture = None
        engine.hook.hid_runtime_state = HidRuntimeState(
            input_ready=True,
            hid_ready=True,
            connected_device=device,
        )

        seen = []
        engine.set_connection_change_callback(seen.append)

        self.assertTrue(engine.device_connected)
        self.assertIs(engine.connected_device, device)
        self.assertTrue(engine.hid_features_ready)
        self.assertEqual(seen, [True])

    def test_duplicate_connected_refresh_does_not_restart_battery_poller(self):
        engine = self._make_engine()
        seen = []
        engine.set_connection_change_callback(seen.append)
        engine.hook._hid_gesture = SimpleNamespace(connected_device=None)
        thread_instances = []

        def fake_thread(*args, **kwargs):
            thread = _RecordedThread(*args, **kwargs)
            thread_instances.append(thread)
            return thread

        with patch("core.engine.threading.Thread", side_effect=fake_thread):
            engine._on_connection_change(True)
            battery_threads = [
                thread for thread in thread_instances if thread.name == "BatteryPoll"
            ]
            self.assertEqual(len(battery_threads), 1)
            first_thread = battery_threads[0]

            engine.hook._hid_gesture = SimpleNamespace(
                connected_device=SimpleNamespace(name="MX Master 3S")
            )
            engine._on_connection_change(True)

        self.assertEqual(seen, [False, True, True])
        battery_threads = [
            thread for thread in thread_instances if thread.name == "BatteryPoll"
        ]
        self.assertEqual(len(battery_threads), 1)
        first_thread.join.assert_not_called()
        self.assertIs(engine._battery_poll_thread, first_thread)

    def test_start_applies_saved_dpi_without_reading_device_dpi(self):
        engine = self._make_engine()
        engine.hook._hid_gesture = SimpleNamespace(
            connected_device=SimpleNamespace(name="MX Master 3S"),
            set_dpi=Mock(return_value=True),
            read_dpi=Mock(),
            smart_shift_supported=False,
        )
        seen = []
        engine.set_dpi_read_callback(seen.append)

        with (
            patch("core.engine.threading.Thread", _ImmediateThread),
            patch("time.sleep", return_value=None),
        ):
            engine.start()

        expected = engine.cfg["settings"]["dpi"]
        engine.hook._hid_gesture.set_dpi.assert_called_once_with(expected)
        engine.hook._hid_gesture.read_dpi.assert_not_called()
        self.assertEqual(seen, [expected])
        self.assertTrue(engine.hook.start_called)
        self.assertTrue(engine._app_detector.start_called)


class EngineReplayPhaseOneTests(unittest.TestCase):
    def _make_engine(self):
        from core.engine import Engine

        cfg = copy.deepcopy(DEFAULT_CONFIG)

        with (
            patch("core.engine.MouseHook", _FakeMouseHook),
            patch("core.engine.AppDetector", _FakeAppDetector),
            patch("core.engine.load_config", return_value=cfg),
        ):
            return Engine()

    @staticmethod
    def _thread_factory(instances):
        def factory(*args, **kwargs):
            thread = _RecordedThread(*args, **kwargs)
            instances.append(thread)
            return thread

        return factory

    @staticmethod
    def _non_battery_threads(instances):
        return [thread for thread in instances if thread.name != "BatteryPoll"]

    def _make_hid(self, *, connected_device=None, dpi_result=True, smart_shift_result=True):
        return SimpleNamespace(
            connected_device=connected_device,
            read_battery=Mock(return_value=None),
            set_dpi=Mock(return_value=dpi_result),
            set_smart_shift=Mock(return_value=smart_shift_result),
            smart_shift_supported=True,
        )

    def test_hid_ready_transition_requests_replay_worker(self):
        engine = self._make_engine()
        engine.hook._hid_gesture = self._make_hid(connected_device=None)
        threads = []

        with patch("core.engine.threading.Thread", side_effect=self._thread_factory(threads)):
            engine._on_connection_change(True)
            self.assertEqual(len(threads), 1)
            self.assertEqual(self._non_battery_threads(threads), [])
            engine.hook._hid_gesture.set_dpi.assert_not_called()
            engine.hook._hid_gesture.set_smart_shift.assert_not_called()

            engine.hook._hid_gesture.connected_device = SimpleNamespace(name="MX Master 3S")
            engine._on_connection_change(True)

        expected_dpi = engine.cfg["settings"]["dpi"]
        expected_ss_mode = engine.cfg["settings"]["smart_shift_mode"]
        expected_ss_enabled = engine.cfg["settings"]["smart_shift_enabled"]
        expected_ss_threshold = engine.cfg["settings"]["smart_shift_threshold"]
        replay_threads = self._non_battery_threads(threads)
        self.assertEqual(len(replay_threads), 1)
        replay_threads[0].run_target()
        engine.hook._hid_gesture.set_dpi.assert_called_once_with(expected_dpi)
        self.assertEqual(engine.hook._hid_gesture.set_smart_shift.call_count, 2)
        engine.hook._hid_gesture.set_smart_shift.assert_called_with(
            expected_ss_mode, expected_ss_enabled, expected_ss_threshold
        )

    def test_live_reconnect_replay_restores_saved_values_through_worker(self):
        engine = self._make_engine()
        engine.hook._hid_gesture = self._make_hid(connected_device=None)
        threads = []
        seen_dpi = []
        seen_smart_shift = []
        engine.set_dpi_read_callback(seen_dpi.append)
        engine.set_smart_shift_read_callback(seen_smart_shift.append)

        with patch("core.engine.threading.Thread", side_effect=self._thread_factory(threads)):
            engine._on_connection_change(True)
            engine.hook._hid_gesture.connected_device = SimpleNamespace(name="MX Master 3S")
            engine._on_connection_change(True)

        replay_threads = self._non_battery_threads(threads)
        self.assertEqual(len(replay_threads), 1)
        replay_threads[0].run_target()

        self.assertEqual(seen_dpi, [engine.cfg["settings"]["dpi"]])
        self.assertGreaterEqual(len(seen_smart_shift), 2)
        self.assertEqual(
            seen_smart_shift[-1],
            {
                "mode": engine.cfg["settings"]["smart_shift_mode"],
                "enabled": engine.cfg["settings"]["smart_shift_enabled"],
                "threshold": engine.cfg["settings"]["smart_shift_threshold"],
            },
        )

    def test_evdev_only_connected_true_does_not_request_replay_worker(self):
        engine = self._make_engine()
        engine.hook.connected_device = SimpleNamespace(name="MX Master 3S", source="evdev")
        engine.hook._hid_gesture = self._make_hid(connected_device=None)
        threads = []

        with patch("core.engine.threading.Thread", side_effect=self._thread_factory(threads)):
            engine._on_connection_change(True)
            engine._on_connection_change(True)

        self.assertEqual(len(threads), 1)
        self.assertEqual(self._non_battery_threads(threads), [])
        engine.hook._hid_gesture.set_dpi.assert_not_called()
        engine.hook._hid_gesture.set_smart_shift.assert_not_called()

    def test_duplicate_same_value_refresh_does_not_create_duplicate_replay_workers(self):
        engine = self._make_engine()
        engine.hook._hid_gesture = self._make_hid(connected_device=None)
        threads = []

        with patch("core.engine.threading.Thread", side_effect=self._thread_factory(threads)):
            engine._on_connection_change(True)

            engine.hook._hid_gesture.connected_device = SimpleNamespace(name="MX Master 3S")
            engine._on_connection_change(True)
            first_replay_threads = list(self._non_battery_threads(threads))

            engine._on_connection_change(True)

        self.assertEqual(len(first_replay_threads), 1)
        self.assertEqual(self._non_battery_threads(threads), first_replay_threads)

    def test_hid_disconnect_while_evdev_connected_allows_next_hid_replay(self):
        engine = self._make_engine()
        engine.hook.connected_device = SimpleNamespace(name="MX Master 3S", source="evdev")
        engine.hook._hid_gesture = self._make_hid(
            connected_device=SimpleNamespace(name="MX Master 3S")
        )
        threads = []

        with patch("core.engine.threading.Thread", side_effect=self._thread_factory(threads)):
            engine._on_connection_change(True)
            self.assertEqual(len(self._non_battery_threads(threads)), 1)
            self._non_battery_threads(threads)[0].run_target()

            engine.hook._hid_gesture.connected_device = None
            engine._on_connection_change(True)
            self.assertEqual(len(self._non_battery_threads(threads)), 1)

            engine.hook._hid_gesture.connected_device = SimpleNamespace(name="MX Master 3S")
            engine._on_connection_change(True)

        self.assertEqual(len(self._non_battery_threads(threads)), 2)

    def test_hid_disconnect_updates_last_hid_ready_without_connection_edge(self):
        engine = self._make_engine()
        engine.hook.connected_device = SimpleNamespace(name="MX Master 3S", source="evdev")
        engine.hook._hid_gesture = self._make_hid(
            connected_device=SimpleNamespace(name="MX Master 3S")
        )

        with patch("core.engine.threading.Thread", side_effect=self._thread_factory([])):
            engine._on_connection_change(True)
        self.assertTrue(engine._last_hid_features_ready)

        engine.hook._hid_gesture.connected_device = None
        engine._on_connection_change(True)

        self.assertFalse(engine._last_hid_features_ready)

    def test_startup_fallback_does_not_queue_replay_after_hid_ready_replay_requested(self):
        engine = self._make_engine()
        engine.hook._hid_gesture = self._make_hid(connected_device=None)
        threads = []

        with (
            patch("core.engine.threading.Thread", side_effect=self._thread_factory(threads)),
            patch("core.engine.time.sleep", return_value=None),
        ):
            engine.start()
            startup_threads = list(self._non_battery_threads(threads))
            self.assertEqual(len(startup_threads), 1)

            engine._on_connection_change(True)
            engine.hook._hid_gesture.connected_device = SimpleNamespace(name="MX Master 3S")
            engine._on_connection_change(True)

        non_battery_before_fallback = list(self._non_battery_threads(threads))
        self.assertEqual(len(non_battery_before_fallback), 2)
        replay_threads = [
            thread for thread in non_battery_before_fallback
            if thread not in startup_threads
        ]
        self.assertEqual(len(replay_threads), 1)
        replay_threads[0].run_target()

        self.assertEqual(engine.hook._hid_gesture.set_dpi.call_count, 1)
        self.assertEqual(engine.hook._hid_gesture.set_smart_shift.call_count, 2)

        startup_threads[0].run_target()

        expected_dpi = engine.cfg["settings"]["dpi"]
        expected_ss_mode = engine.cfg["settings"]["smart_shift_mode"]
        expected_ss_enabled = engine.cfg["settings"]["smart_shift_enabled"]
        expected_ss_threshold = engine.cfg["settings"]["smart_shift_threshold"]
        engine.hook._hid_gesture.set_dpi.assert_called_once_with(expected_dpi)
        self.assertEqual(engine.hook._hid_gesture.set_smart_shift.call_count, 2)
        engine.hook._hid_gesture.set_smart_shift.assert_called_with(
            expected_ss_mode, expected_ss_enabled, expected_ss_threshold
        )

    def test_replay_failure_emits_engine_status_callback(self):
        engine = self._make_engine()
        status_messages = []
        engine.set_status_callback(status_messages.append)
        engine.hook._hid_gesture = self._make_hid(
            connected_device=None,
            dpi_result=False,
            smart_shift_result=True,
        )
        threads = []

        with patch("core.engine.threading.Thread", side_effect=self._thread_factory(threads)):
            engine._on_connection_change(True)
            engine.hook._hid_gesture.connected_device = SimpleNamespace(name="MX Master 3S")
            engine._on_connection_change(True)

        replay_threads = self._non_battery_threads(threads)
        self.assertEqual(len(replay_threads), 1)
        replay_threads[0].run_target()

        self.assertTrue(status_messages)
        self.assertTrue(
            any(
                "could not be restored" in message.lower()
                for message in status_messages
            ),
            status_messages,
        )

    def test_set_dpi_writes_when_capability_reports_adjustable_dpi(self):
        engine = self._make_engine()
        engine.hook._hid_gesture = self._make_hid(
            connected_device=SimpleNamespace(
                name="MX Master 3S",
                capabilities=SimpleNamespace(adjustable_dpi=True),
            )
        )

        with patch("core.engine.save_config"):
            result = engine.set_dpi(1600)

        self.assertTrue(result)
        engine.hook._hid_gesture.set_dpi.assert_called_once_with(1600)

    def test_set_dpi_skips_when_capability_reports_no_adjustable_dpi(self):
        engine = self._make_engine()
        engine.hook._hid_gesture = self._make_hid(
            connected_device=SimpleNamespace(
                name="Mystery Logitech Mouse",
                capabilities=SimpleNamespace(adjustable_dpi=False),
                capability_inventory=SimpleNamespace(
                    raw_features=("REPROG_CONTROLS_V4",),
                ),
            )
        )

        with patch("core.engine.save_config"):
            result = engine.set_dpi(1600)

        self.assertFalse(result)
        engine.hook._hid_gesture.set_dpi.assert_not_called()

    def test_set_dpi_preserves_fallback_when_capability_is_unknown(self):
        engine = self._make_engine()
        engine.hook._hid_gesture = self._make_hid(
            connected_device=SimpleNamespace(
                name="Sparse Runtime Device",
                capabilities=SimpleNamespace(adjustable_dpi=False),
            )
        )

        with patch("core.engine.save_config"):
            result = engine.set_dpi(1600)

        self.assertTrue(result)
        engine.hook._hid_gesture.set_dpi.assert_called_once_with(1600)

    def test_battery_poll_skips_smart_shift_reads_while_replay_is_inflight(self):
        engine = self._make_engine()
        stop_event = Mock()
        stop_event.is_set.return_value = False
        stop_event.wait.return_value = True
        engine._replay_inflight = True
        engine.hook._hid_gesture = SimpleNamespace(
            connected_device=SimpleNamespace(name="MX Master 3S"),
            smart_shift_supported=True,
            read_battery=Mock(return_value=None),
            read_smart_shift=Mock(return_value={"mode": "ratchet", "enabled": False, "threshold": 25}),
        )

        engine._battery_poll_loop(stop_event)

        engine.hook._hid_gesture.read_battery.assert_called_once_with()
        engine.hook._hid_gesture.read_smart_shift.assert_not_called()

    def test_battery_poll_reads_when_capability_reports_battery(self):
        engine = self._make_engine()
        stop_event = Mock()
        stop_event.is_set.return_value = False
        stop_event.wait.return_value = True
        engine.hook._hid_gesture = SimpleNamespace(
            connected_device=SimpleNamespace(
                name="MX Master 3S",
                capabilities=SimpleNamespace(battery_status=True),
            ),
            smart_shift_supported=False,
            read_battery=Mock(return_value=88),
            read_smart_shift=Mock(),
        )
        battery_levels = []
        engine.set_battery_callback(battery_levels.append)

        engine._battery_poll_loop(stop_event)

        engine.hook._hid_gesture.read_battery.assert_called_once_with()
        self.assertEqual(battery_levels, [88])

    def test_battery_poll_skips_when_capability_reports_no_battery(self):
        engine = self._make_engine()
        stop_event = Mock()
        stop_event.is_set.return_value = False
        stop_event.wait.return_value = True
        engine.hook._hid_gesture = SimpleNamespace(
            connected_device=SimpleNamespace(
                name="Mystery Logitech Mouse",
                capabilities=SimpleNamespace(battery_status=False),
                capability_inventory=SimpleNamespace(
                    raw_features=("REPROG_CONTROLS_V4",),
                    has_reprog_controls=True,
                ),
            ),
            smart_shift_supported=False,
            read_battery=Mock(return_value=None),
            read_smart_shift=Mock(),
        )

        engine._battery_poll_loop(stop_event)

        engine.hook._hid_gesture.read_battery.assert_not_called()

    def test_battery_poll_preserves_fallback_when_capability_is_unknown(self):
        engine = self._make_engine()
        stop_event = Mock()
        stop_event.is_set.return_value = False
        stop_event.wait.return_value = True
        engine.hook._hid_gesture = SimpleNamespace(
            connected_device=SimpleNamespace(
                name="Sparse Runtime Device",
                capabilities=SimpleNamespace(battery_status=False),
            ),
            smart_shift_supported=False,
            read_battery=Mock(return_value=None),
            read_smart_shift=Mock(),
        )

        engine._battery_poll_loop(stop_event)

        engine.hook._hid_gesture.read_battery.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
