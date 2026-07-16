"""
Shared mouse hook behavior used by platform implementations.
"""

import queue
import threading
import time
from types import MappingProxyType

try:
    from core.hid_gesture import HidGestureListener
except Exception:
    HidGestureListener = None

from core.mouse_hook_types import (
    BindingBuilder,
    BindingSnapshot,
    DispatchGenerationState,
    HidRuntimeState,
    MouseEvent,
    LifecycleInvalidation,
    format_debug_details,
)


class BaseMouseHook:
    def __init__(self):
        self._binding_lock = threading.Lock()
        self._binding_snapshot = BindingSnapshot.empty()
        self._debug_callback = None
        self._gesture_callback = None
        self._status_callback = None
        self.debug_mode = False
        self.invert_vscroll = False
        self.invert_hscroll = False
        self._gesture_active = False
        self._hid_gesture = None
        self._device_connected = False
        self._connection_change_cb = None
        self.divert_mode_shift = False
        self.divert_dpi_switch = False
        self._gesture_direction_enabled = False
        self._gesture_threshold = 50.0
        self._gesture_deadzone = 40.0
        self._gesture_timeout_ms = 3000
        self._gesture_cooldown_ms = 500
        self._gesture_tracking = False
        self._gesture_triggered = False
        self._gesture_started_at = 0.0
        self._gesture_last_move_at = 0.0
        self._gesture_delta_x = 0.0
        self._gesture_delta_y = 0.0
        self._gesture_cooldown_until = 0.0
        self._gesture_input_source = None
        self._connected_device = None
        self._dispatch_queue = None

    def _init_dispatch_queue(self, maxsize=0):
        """Initialize dispatch queue storage for subclasses with event threads."""
        self._dispatch_queue = queue.Queue(maxsize=max(0, int(maxsize)))

    def _enqueue_dispatch_event(self, event):
        """Best-effort enqueue that bounds memory when queue has a max size."""
        q = self._dispatch_queue
        if q is None:
            return
        if q.maxsize <= 0:
            q.put(event)
            return
        try:
            q.put_nowait(event)
            return
        except queue.Full:
            pass
        evicted = []
        try:
            evicted.append(q.get_nowait())
        except queue.Empty:
            pass
        contexts = []
        for item in evicted:
            if isinstance(item, LifecycleInvalidation):
                contexts.extend(item.contexts)
                continue
            context = self._lifecycle_context(item)
            if context is not None:
                contexts.append(context)
        if contexts and q.maxsize == 1:
            context = self._lifecycle_context(event)
            if context is not None:
                contexts.append(context)
            event = None
        elif contexts:
            # Put the invalidation ahead of every surviving data event.  Once a
            # lifecycle edge is lost, retaining later queued edges could let
            # them observe stale press state before the worker invalidates it.
            while True:
                try:
                    item = q.get_nowait()
                except queue.Empty:
                    break
                if isinstance(item, LifecycleInvalidation):
                    contexts.extend(item.contexts)
                else:
                    context = self._lifecycle_context(item)
                    if context is not None:
                        contexts.append(context)
        try:
            if contexts:
                q.put_nowait(LifecycleInvalidation(tuple(contexts)))
            if event is not None:
                q.put_nowait(event)
        except queue.Full:
            self._emit_debug("Dropped event due to full dispatch queue")

    @staticmethod
    def _lifecycle_context(event):
        event_type = getattr(event, "event_type", "")
        route = getattr(event, "binding_route", None)
        invalidator = getattr(event, "binding_lifecycle_invalidator", None)
        generation = getattr(event, "binding_generation", None)
        if (
            route
            and invalidator
            and generation is not None
            and (event_type.endswith("_down") or event_type.endswith("_up"))
        ):
            return generation, route, invalidator
        return None

    def register(self, event_type, callback):
        builder = BindingBuilder(self.capture_binding_snapshot())
        builder.register(event_type, callback)
        self.publish_bindings(builder)

    def block(self, event_type):
        builder = BindingBuilder(self.capture_binding_snapshot())
        builder.block(event_type)
        self.publish_bindings(builder)

    def unblock(self, event_type):
        builder = BindingBuilder(self.capture_binding_snapshot())
        builder.unblock(event_type)
        self.publish_bindings(builder)

    def reset_bindings(self, wait_timeout=None):
        return self.publish_bindings(BindingBuilder(), wait_timeout=wait_timeout)

    @property
    def _callbacks(self):
        return self._binding_snapshot.callbacks

    @property
    def _blocked_events(self):
        return self._binding_snapshot.blocked_events

    def new_binding_builder(self):
        return BindingBuilder()

    def capture_binding_snapshot(self):
        with self._binding_lock:
            return self._binding_snapshot

    def publish_bindings(self, builder, wait_timeout=None):
        """Publish atomically, then wait without the binding lock for old leases.

        Lock order is binding lock -> generation-state lock.  Callback bodies
        hold only a generation lease, never either structural lock.
        """
        callbacks = MappingProxyType(
            {
                event_type: tuple(callbacks)
                for event_type, callbacks in builder.callbacks.items()
            }
        )
        with self._binding_lock:
            previous = self._binding_snapshot
            previous.dispatch_state.retire()
            snapshot = BindingSnapshot(
                generation=self._binding_snapshot.generation + 1,
                callbacks=callbacks,
                blocked_events=frozenset(builder.blocked_events),
                routes=MappingProxyType(dict(builder.routes)),
                dispatch_state=DispatchGenerationState(),
                lifecycle_invalidator=builder.lifecycle_invalidator,
            )
            self._binding_snapshot = snapshot
        self._last_retirement_complete = previous.dispatch_state.wait_for_drain(
            timeout=wait_timeout
        )
        return snapshot

    def bind_event(self, event, snapshot=None):
        """Attach the exact binding generation used when the event was received."""
        snapshot = snapshot or self.capture_binding_snapshot()
        event.binding_generation = snapshot.generation
        event.binding_route = snapshot.routes.get(event.event_type)
        event.binding_callbacks = snapshot.callbacks.get(event.event_type, ())
        event.binding_suppressed = event.event_type in snapshot.blocked_events
        event.binding_dispatch_state = snapshot.dispatch_state
        event.binding_lifecycle_invalidator = snapshot.lifecycle_invalidator
        return event

    def configure_gestures(
        self,
        enabled=False,
        threshold=50,
        deadzone=40,
        timeout_ms=3000,
        cooldown_ms=500,
    ):
        self._gesture_direction_enabled = bool(enabled)
        self._gesture_threshold = float(max(5, threshold))
        self._gesture_deadzone = float(max(0, deadzone))
        self._gesture_timeout_ms = max(250, int(timeout_ms))
        self._gesture_cooldown_ms = max(0, int(cooldown_ms))
        if not self._gesture_direction_enabled:
            self._gesture_tracking = False
            self._gesture_triggered = False
            self._gesture_input_source = None

    def set_connection_change_callback(self, cb):
        self._connection_change_cb = cb

    @property
    def device_connected(self):
        return self._device_connected

    @property
    def connected_device(self):
        return self._connected_device

    @property
    def hid_runtime_state(self):
        hg = getattr(self, "_hid_gesture", None)
        hid_device = getattr(hg, "connected_device", None) if hg else None
        return HidRuntimeState(
            input_ready=bool(self._device_connected),
            hid_ready=hid_device is not None,
            connected_device=self._connected_device,
        )

    def dump_device_info(self):
        hg = getattr(self, "_hid_gesture", None)
        if hg and hasattr(hg, "dump_device_info"):
            return hg.dump_device_info()
        return None

    def _set_device_connected(self, connected):
        if connected == self._device_connected:
            return
        self._device_connected = connected
        state = "Connected" if connected else "Disconnected"
        print(f"[MouseHook] Device {state}")
        if self._connection_change_cb:
            try:
                self._connection_change_cb(connected)
            except Exception:
                pass

    def set_debug_callback(self, callback):
        self._debug_callback = callback

    def set_gesture_callback(self, callback):
        self._gesture_callback = callback

    def set_status_callback(self, callback):
        self._status_callback = callback

    def _emit_debug(self, message):
        if self.debug_mode and self._debug_callback:
            try:
                self._debug_callback(message)
            except Exception:
                pass

    def _emit_status(self, message):
        if self._status_callback:
            try:
                self._status_callback(message)
            except Exception:
                pass

    def _emit_gesture_event(self, event):
        if self.debug_mode and self._gesture_callback:
            try:
                self._gesture_callback(event)
            except Exception:
                pass

    def _dispatch(self, event):
        if isinstance(event, LifecycleInvalidation):
            for generation, route, invalidator in event.contexts:
                invalidator(generation, route)
            return
        if getattr(event, "binding_generation", None) is None:
            self.bind_event(event)
        dispatch_state = event.binding_dispatch_state
        if not dispatch_state.try_acquire():
            self._emit_debug(
                f"Dropped retired event {event.event_type} "
                f"generation={event.binding_generation}"
            )
            return
        try:
            callbacks = event.binding_callbacks
            self._emit_debug(
                f"Dispatch {event.event_type}"
                f"{format_debug_details(event.raw_data)} callbacks={len(callbacks)}"
            )
            if event.event_type.startswith("gesture_"):
                self._emit_gesture_event(
                    {
                        "type": "dispatch",
                        "event_name": event.event_type,
                        "callbacks": len(callbacks),
                    }
                )
            if not callbacks:
                self._emit_debug(f"No mapped action for {event.event_type}")
                if event.event_type.startswith("gesture_"):
                    self._emit_gesture_event(
                        {
                            "type": "unmapped",
                            "event_name": event.event_type,
                        }
                    )
            for callback in callbacks:
                try:
                    callback(event)
                    self._emit_debug(f"Callback executed for {event.event_type}")
                except Exception as exc:
                    print(f"[MouseHook] callback error: {exc}")
        finally:
            dispatch_state.release()

    def _hid_gesture_available(self):
        return self._hid_gesture is not None and self._device_connected

    def _gesture_cooldown_active(self):
        return time.monotonic() < self._gesture_cooldown_until

    def _start_gesture_tracking(self):
        self._gesture_tracking = self._gesture_direction_enabled
        self._gesture_started_at = time.monotonic()
        self._gesture_last_move_at = self._gesture_started_at
        self._gesture_delta_x = 0.0
        self._gesture_delta_y = 0.0
        self._gesture_input_source = None

    def _finish_gesture_tracking(self):
        self._gesture_tracking = False
        self._gesture_started_at = 0.0
        self._gesture_last_move_at = 0.0
        self._gesture_delta_x = 0.0
        self._gesture_delta_y = 0.0
        self._gesture_input_source = None

    def _detect_gesture_event(self):
        delta_x = self._gesture_delta_x
        delta_y = self._gesture_delta_y

        abs_x = abs(delta_x)
        abs_y = abs(delta_y)
        dominant = max(abs_x, abs_y)
        if dominant < self._gesture_threshold:
            return None

        cross_limit = max(self._gesture_deadzone, dominant * 0.35)

        if abs_x > abs_y:
            if abs_y > cross_limit:
                return None
            if delta_x > 0:
                return MouseEvent.GESTURE_SWIPE_RIGHT
            return MouseEvent.GESTURE_SWIPE_LEFT

        if abs_x > cross_limit:
            return None
        if delta_y > 0:
            return MouseEvent.GESTURE_SWIPE_DOWN
        return MouseEvent.GESTURE_SWIPE_UP

    def _build_extra_diverts(self):
        extra = {}
        if self.divert_mode_shift:
            extra[0x00C4] = {
                "on_down": self._on_hid_mode_shift_down,
                "on_up": self._on_hid_mode_shift_up,
            }
        if self.divert_dpi_switch:
            extra[0x00FD] = {
                "on_down": self._on_hid_dpi_switch_down,
                "on_up": self._on_hid_dpi_switch_up,
            }
        return extra

    def sync_hid_extra_diverts(self):
        """Push the current extra-divert set into the running HID listener."""
        listener = self._hid_gesture
        if listener is None or not hasattr(listener, "update_extra_diverts"):
            return False
        return listener.update_extra_diverts(self._build_extra_diverts())

    def _start_hid_listener(self):
        platform_module = getattr(self.__class__, "_platform_module", None)
        listener_cls = getattr(platform_module, "HidGestureListener", HidGestureListener)
        if listener_cls is None:
            return None
        listener = listener_cls(
            on_down=self._on_hid_gesture_down,
            on_up=self._on_hid_gesture_up,
            on_move=self._on_hid_gesture_move,
            on_connect=self._on_hid_connect,
            on_disconnect=self._on_hid_disconnect,
            extra_diverts=self._build_extra_diverts(),
        )
        self._hid_gesture = listener
        if not listener.start():
            self._hid_gesture = None
        return self._hid_gesture

    def _stop_hid_listener(self):
        if self._hid_gesture:
            self._hid_gesture.stop()
            self._hid_gesture = None

    def _on_hid_connect(self):
        self._connected_device = (
            self._hid_gesture.connected_device if self._hid_gesture else None
        )
        self._set_device_connected(True)

    def _on_hid_disconnect(self):
        self._connected_device = None
        self._set_device_connected(False)

    def _on_hid_gesture_down(self):
        self._dispatch(MouseEvent(MouseEvent.GESTURE_DOWN))

    def _on_hid_gesture_up(self):
        self._dispatch(MouseEvent(MouseEvent.GESTURE_UP))

    def _on_hid_gesture_move(self, dx, dy):
        self._accumulate_gesture_delta(dx, dy, "hid_rawxy")

    def _on_hid_mode_shift_down(self):
        self._dispatch(MouseEvent(MouseEvent.MODE_SHIFT_DOWN))

    def _on_hid_mode_shift_up(self):
        self._dispatch(MouseEvent(MouseEvent.MODE_SHIFT_UP))

    def _on_hid_dpi_switch_down(self):
        self._dispatch(MouseEvent(MouseEvent.DPI_SWITCH_DOWN))

    def _on_hid_dpi_switch_up(self):
        self._dispatch(MouseEvent(MouseEvent.DPI_SWITCH_UP))
