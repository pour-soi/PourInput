"""
Shared mouse hook types and helpers.
"""

from dataclasses import dataclass, field
import threading
import time
from types import MappingProxyType
from typing import Any


@dataclass(frozen=True)
class HidRuntimeState:
    """Read-only snapshot of hook input and HID++ readiness."""

    input_ready: bool = False
    hid_ready: bool = False
    connected_device: Any = None


class DispatchGenerationState:
    """Lease state for one immutable binding generation."""

    def __init__(self):
        self._condition = threading.Condition()
        self._retired = False
        self._active_by_thread = {}

    def try_acquire(self):
        thread_id = threading.get_ident()
        with self._condition:
            if self._retired:
                return False
            self._active_by_thread[thread_id] = (
                self._active_by_thread.get(thread_id, 0) + 1
            )
            return True

    def release(self):
        thread_id = threading.get_ident()
        with self._condition:
            remaining = self._active_by_thread[thread_id] - 1
            if remaining:
                self._active_by_thread[thread_id] = remaining
            else:
                del self._active_by_thread[thread_id]
            self._condition.notify_all()

    def retire(self):
        with self._condition:
            self._retired = True
            self._condition.notify_all()

    def wait_for_drain(self, timeout=None):
        """Wait for other threads; the caller's own lease is reentrant-safe."""
        caller = threading.get_ident()
        with self._condition:
            return self._condition.wait_for(
                lambda: not any(
                    count
                    for thread_id, count in self._active_by_thread.items()
                    if thread_id != caller
                ),
                timeout=timeout,
            )


@dataclass(frozen=True)
class LifecycleInvalidation:
    """Worker-queue control record for evicted press lifecycle events."""

    contexts: tuple


@dataclass(frozen=True)
class BindingSnapshot:
    """Immutable callbacks and suppression policy for one hook generation."""

    generation: int
    callbacks: Any
    blocked_events: frozenset[str]
    routes: Any
    dispatch_state: DispatchGenerationState = field(
        default_factory=DispatchGenerationState
    )
    lifecycle_invalidator: Any = None

    @classmethod
    def empty(cls, generation=0):
        return cls(
            generation=generation,
            callbacks=MappingProxyType({}),
            blocked_events=frozenset(),
            routes=MappingProxyType({}),
            dispatch_state=DispatchGenerationState(),
        )


class BindingBuilder:
    """Mutable off-thread builder published as one immutable snapshot."""

    def __init__(self, snapshot=None):
        self.callbacks = {
            event_type: list(callbacks)
            for event_type, callbacks in getattr(snapshot, "callbacks", {}).items()
        }
        self.blocked_events = set(
            getattr(snapshot, "blocked_events", frozenset())
        )
        self.routes = dict(getattr(snapshot, "routes", {}))
        self.lifecycle_invalidator = getattr(snapshot, "lifecycle_invalidator", None)

    def register(self, event_type, callback):
        self.callbacks.setdefault(event_type, []).append(callback)

    def block(self, event_type):
        self.blocked_events.add(event_type)

    def unblock(self, event_type):
        self.blocked_events.discard(event_type)

    def set_route(self, event_type, route):
        self.routes[event_type] = route

    def set_lifecycle_invalidator(self, callback):
        self.lifecycle_invalidator = callback


class MouseEvent:
    """Represents a captured mouse event."""

    XBUTTON1_DOWN = "xbutton1_down"
    XBUTTON1_UP = "xbutton1_up"
    XBUTTON2_DOWN = "xbutton2_down"
    XBUTTON2_UP = "xbutton2_up"
    MIDDLE_DOWN = "middle_down"
    MIDDLE_UP = "middle_up"
    GESTURE_DOWN = "gesture_down"
    GESTURE_UP = "gesture_up"
    GESTURE_CLICK = "gesture_click"
    GESTURE_SWIPE_LEFT = "gesture_swipe_left"
    GESTURE_SWIPE_RIGHT = "gesture_swipe_right"
    GESTURE_SWIPE_UP = "gesture_swipe_up"
    GESTURE_SWIPE_DOWN = "gesture_swipe_down"
    HSCROLL_LEFT = "hscroll_left"
    HSCROLL_RIGHT = "hscroll_right"
    MODE_SHIFT_DOWN = "mode_shift_down"
    MODE_SHIFT_UP = "mode_shift_up"
    DPI_SWITCH_DOWN = "dpi_switch_down"
    DPI_SWITCH_UP = "dpi_switch_up"

    def __init__(self, event_type, raw_data=None):
        self.event_type = event_type
        self.raw_data = raw_data
        self.timestamp = time.time()
        self.binding_generation = None
        self.binding_route = None
        self.binding_callbacks = ()
        self.binding_suppressed = False
        self.binding_dispatch_state = None
        self.binding_lifecycle_invalidator = None


def format_debug_details(raw_data):
    if raw_data is None:
        return ""
    if isinstance(raw_data, dict):
        parts = [f"{key}={value}" for key, value in raw_data.items()]
        return " " + " ".join(parts)
    return f" value={raw_data}"
