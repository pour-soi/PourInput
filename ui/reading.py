"""Qt bridge for the independent reader; hook callbacks only enqueue navigation."""
import ctypes
import math
from bisect import bisect_right
import re
import sys
import threading
import time
from dataclasses import replace

from PySide6.QtCore import QObject, Property, Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import QFileDialog, QColorDialog
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QTextLayout, QTextOption

from ui.locale_manager import LocaleManager
from core.reader import ReaderModel, ReaderStore
from core.reader_import import import_document
from core.reader_wheel import ReaderWheel


class ReadingController(QObject):
    changed = Signal()
    scrollChanged = Signal()
    _navigation = Signal(int, int)
    _imported = Signal(object, str)
    _buttonEdge = Signal(int, bool)

    def __init__(self, hook, directory, parent=None, key_down=None, locale_manager=None):
        super().__init__(parent)
        self._locale = locale_manager or LocaleManager("en", self)
        self._locale.languageChanged.connect(self.changed.emit)
        self._hook = hook
        self._gate = ReaderWheel()
        self._closed = False
        if key_down is None and sys.platform == "win32":
            query = ctypes.WinDLL("user32", use_last_error=True).GetAsyncKeyState
            query.argtypes = [ctypes.c_int]
            query.restype = ctypes.c_short
            key_down = lambda key: bool(query(key) & 0x8000)
        self._key_down = key_down or (lambda key: False)
        self._mouse_down = {}
        self._buttonEdge.connect(self._observe_button, Qt.QueuedConnection)
        self._hold_timer = QTimer(self)
        self._hold_timer.setTimerType(Qt.PreciseTimer)
        self._hold_timer.setInterval(16)
        self._hold_timer.timeout.connect(self._poll_hold)
        self._busy = False
        self._error = ""
        self._viewport = None
        self._page_key = None
        self._pages = []
        self._line_height = 28
        self._lines = []
        self._auto_running = False
        self._scroll_dirty = False
        self._scroll_last = time.monotonic()
        self._scroll_saved = self._scroll_last
        self._scroll_timer = QTimer(self)
        self._scroll_timer.setTimerType(Qt.PreciseTimer)
        self._scroll_timer.setInterval(16)
        self._scroll_timer.timeout.connect(self._scroll_tick)
        self.model = None
        try:
            self.model = ReaderModel(ReaderStore(directory))
        except Exception as exc:
            self._error = "Reader store could not be opened; files were preserved: " + str(exc)
        self._supported = hasattr(hook, "set_reading_wheel_handler")
        self._navigation.connect(self._navigate, Qt.QueuedConnection)
        self._imported.connect(self._finish_import, Qt.QueuedConnection)
        if self._supported:
            hook.set_reading_wheel_handler(self.handle_wheel)
        if hasattr(hook, "set_reading_button_observer"):
            hook.set_reading_button_observer(self._buttonEdge.emit)
        self._sync_gate()
        self._sync_hold()

    def _sync_gate(self):
        self._gate.configure(self._supported and self.enabled and not self._closed)

    def handle_wheel(self, delta):
        claimed, epoch, step = self._gate.feed(delta)
        if step:
            self._navigation.emit(epoch, step)
        return claimed

    @Slot(int, int)
    def _navigate(self, epoch, step):
        if self._gate.accepts(epoch):
            self.move(step)

    def _change(self, **changes):
        if self.model is None or self._closed:
            return
        try:
            self.model.update(**changes)
            self._error = ""
            if "reading_enabled" in changes:
                self._sync_gate()
            self._sync_hold()
        except Exception as exc:
            self._error = str(exc)
        self.changed.emit()

    enabled = Property(bool, lambda self: bool(self.model and self.model.state.reading_enabled), notify=changed)
    panelVisible = Property(bool, lambda self: bool(self.model and self.model.visible and self._supported and not self._closed), notify=changed)
    def _ensure_pages(self):
        if not self.model or not self.model.groups or self._viewport is None:
            return False
        width, height, font = self._viewport
        key = (self.model.state.document_id, width, height, font.toString())
        if key == self._page_key:
            return True
        pages = []
        lines_per_page = max(1, int(height // self._line_height))
        # Group boundaries are storage anchors, not page breaks.
        group_starts, length = [], 0
        for group in self.model.groups:
            group_starts.append(length)
            length += len(group) + 1
        text = " ".join(self.model.groups)
        layout = QTextLayout(text, font)
        option = QTextOption()
        option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        layout.setTextOption(option)
        layout.beginLayout()
        starts = []
        while True:
            line = layout.createLine()
            if not line.isValid():
                break
            line.setLineWidth(width)
            starts.append(line.textStart())
        layout.endLayout()
        # Qt indexes UTF-16; persisted offsets use Python character indexes.
        encoded = text.encode("utf-16-le")
        offsets, previous, position = [], 0, 0
        for offset in starts:
            position += len(encoded[previous * 2:offset * 2].decode("utf-16-le"))
            offsets.append(position)
            previous = offset
        self._lines = []
        for index, start in enumerate(offsets):
            group = bisect_right(group_starts, start) - 1
            end = offsets[index + 1] if index + 1 < len(offsets) else len(text)
            self._lines.append((group, start - group_starts[group], text[start:end]))
        for first in range(0, len(offsets), lines_per_page):
            start = offsets[first]
            end = offsets[first + lines_per_page] if first + lines_per_page < len(offsets) else len(text)
            group = bisect_right(group_starts, start) - 1
            pages.append((group, start - group_starts[group], text[start:end]))
        self._line_anchors = [(g, o) for g, o, text in self._lines]
        self._pages, self._page_key = pages, key
        return bool(pages)

    def _page_index(self):
        state = self.model.state
        return max(0, bisect_right([(group, start) for group, start, text in self._pages],
                                   (state.group_index, state.group_offset)) - 1)

    def _page_text(self):
        if self._ensure_pages():
            if self.continuousScroll:
                first = self._line_index()
                count = math.ceil(self._viewport[1] / self._line_height) + 2
                return "".join(line[2] for line in self._lines[first:first + count])
            return self._pages[self._page_index()][2]
        return self.model.text if self.model else ""

    continuousScroll = Property(bool, lambda self: bool(self.model and self.model.state.continuous_scroll), notify=changed)
    autoRunning = Property(bool, lambda self: self._auto_running, notify=changed)
    scrollSpeed = Property(int, lambda self: self.model.state.scroll_speed if self.model else 24, notify=changed)
    scrollOffset = Property(float, lambda self: self.model.state.scroll_fraction * self._line_height if self.model and self.continuousScroll else 0, notify=scrollChanged)

    def _line_index(self):
        state = self.model.state
        return max(0, bisect_right(self._line_anchors,
                                   (state.group_index, state.group_offset)) - 1)

    def _flush_scroll(self):
        if not self._scroll_dirty or self.model is None:
            return
        try:
            self.model.store.save_state(self.model.state)
            self._scroll_dirty = False
            self._scroll_saved = time.monotonic()
        except Exception as exc:
            self._error = str(exc)
            self._auto_running = False
            self._scroll_timer.stop()
            self.changed.emit()

    @Slot(int)
    def setScrollSpeed(self, speed):
        self._change(scroll_speed=max(5, min(100, speed)))

    @Slot(bool)
    def setAutoRunning(self, running):
        if running and (not self.enabled or self._closed or not self._ensure_pages()):
            return
        if running:
            self._change(continuous_scroll=True)
            if not self.continuousScroll:
                return
        self._auto_running = bool(running)
        self._scroll_last = time.monotonic()
        if running:
            self._scroll_timer.start()
        else:
            self._scroll_timer.stop()
            self._flush_scroll()
        self.changed.emit()
        self.scrollChanged.emit()

    def _scroll_tick(self):
        now = time.monotonic()
        elapsed = min(0.1, max(0, now - self._scroll_last))
        self._scroll_last = now
        self._advance_scroll(elapsed)
        if not self.model.hidden and now - self._scroll_saved >= 2:
            self._flush_scroll()

    def _advance_scroll(self, elapsed):
        if not self._auto_running or not self.panelVisible or not self._ensure_pages():
            return
        first = self._line_index()
        limit = max(0, len(self._lines) - self._viewport[1] / self._line_height)
        position = min(limit, first + self.model.state.scroll_fraction
                       + max(0, elapsed) * self.scrollSpeed / self._line_height)
        index = int(position)
        group, offset, text = self._lines[index]
        self.model.state = replace(self.model.state, group_index=group,
                                   group_offset=offset, scroll_fraction=position - index)
        self._scroll_dirty = True
        if index != first:
            self.changed.emit()
        self.scrollChanged.emit()
        if position >= limit:
            self.setAutoRunning(False)

    @Slot(float, float, QFont)
    def setViewport(self, width, height, font):
        if width <= 0 or height <= 0:
            return
        viewport = (float(width), float(height), QFont(font))
        if self._viewport == viewport:
            return
        self._viewport = viewport
        self._line_height = math.ceil(QFontMetricsF(font).height() * 1.25)
        self.changed.emit()
        self.scrollChanged.emit()

    readerLineHeight = Property(int, lambda self: self._line_height, notify=changed)
    text = Property(str, _page_text, notify=changed)
    title = Property(str, lambda self: self.model.document["title"] if self.model and self.model.document else self._locale.tr("reading.no_document"), notify=changed)
    position = Property(int, lambda self: self._page_index() + 1 if self._ensure_pages() else (self.model.state.group_index + 1 if self.model and self.model.groups else 0), notify=changed)
    groupCount = Property(int, lambda self: len(self._pages) if self._ensure_pages() else (len(self.model.groups) if self.model else 0), notify=changed)
    displayMode = Property(str, lambda self: self.model.state.display_mode if self.model else "Normal", notify=changed)
    panelOpacity = Property(float, lambda self: self.model.state.opacity if self.model else 0.9, notify=changed)
    strings = Property("QVariantMap", lambda self: self._locale.strings, notify=changed)

    def _localized_error(self):
        if not self._error or self._locale.language == "en":
            return self._error
        if self.model is None:
            return self._locale.tr("reading.store_error")
        key = "reading.import_error" if "Import" in self._error else "reading.error"
        return self._locale.tr(key)

    error = Property(str, _localized_error, notify=changed)
    busy = Property(bool, lambda self: self._busy, notify=changed)
    supported = Property(bool, lambda self: self._supported, constant=True)

    hideKey = Property(int, lambda self: self.model.state.hide_key if self.model else 0, notify=changed)
    hideChoices = Property("QVariantList", lambda self: [
        {"label": self._locale.tr("reading.none"), "key": 0},
        {"label": self._locale.tr("reading.middle"), "key": 4},
        {"label": self._locale.tr("reading.back"), "key": 5},
        {"label": self._locale.tr("reading.forward"), "key": 6},
        {"label": self._locale.tr("reading.left"), "key": 1},
        {"label": self._locale.tr("reading.right"), "key": 2},
        {"label": "Shift", "key": 16},
        {"label": "Ctrl", "key": 17},
        {"label": "Alt", "key": 18},
        {"label": self._locale.tr("reading.space"), "key": 32},
        {"label": self._locale.tr("reading.tab"), "key": 9},
        {"label": self._locale.tr("reading.escape"), "key": 27},
        *[{"label": "F" + str(i + 1), "key": 112 + i} for i in range(24)],
        *[{"label": chr(i), "key": i} for i in range(65, 91)],
        *[{"label": chr(i), "key": i} for i in range(48, 58)],
    ], constant=True)

    @Slot(int)
    def setHideKey(self, key):
        if key in {choice["key"] for choice in self.hideChoices}:
            self._change(hide_key=key)

    def _sync_hold(self):
        active = self._supported and self.enabled and self.hideKey != 0 and not self._closed
        if hasattr(self._hook, "set_reading_hide_key"):
            self._hook.set_reading_hide_key(self.hideKey if active else 0)
        if active:
            self._hold_timer.start()
        else:
            self._hold_timer.stop()
        self._poll_hold()

    @Slot()
    def _poll_hold(self):
        if self.model is None:
            return
        down = self._mouse_down.get(self.hideKey)
        if down is None:
            down = self._key_down(self.hideKey) if self.hideKey else False
        hidden = bool(self._hold_timer.isActive() and down)
        if self.model.hidden != hidden:
            # Visibility only: no model.update(), gate reset, or persistence.
            self.model.set_hidden(hidden)
            self._scroll_last = time.monotonic()
            self.changed.emit()

    @Slot(int, bool)
    def _observe_button(self, key, down):
        if self._closed:
            return
        if key == 0:
            self._mouse_down.clear()
        else:
            self._mouse_down[key] = down
        self._poll_hold()

    @Slot(bool)
    def setEnabled(self, enabled):
        if not enabled:
            self.setAutoRunning(False)
        if enabled and not self._supported:
            return
        self._change(reading_enabled=bool(enabled))

    @Slot(str)
    def setDisplayMode(self, mode):
        if mode in ("Normal", "Minimal", "Ghost"):
            self._change(display_mode=mode)

    panelWidth = Property(int, lambda self: self.model.state.panel_width if self.model else 640, notify=changed)
    panelHeight = Property(int, lambda self: self.model.state.panel_height if self.model else 0, notify=changed)

    @Slot(int)
    def setPanelWidth(self, width):
        self._change(panel_width=max(240, min(1920, width)))

    @Slot(int)
    def setPanelHeight(self, height):
        self._change(panel_height=0 if height == 0 else max(80, min(1080, height)))

    @Slot(int, int)
    def setPanelSize(self, width, height):
        self._change(panel_width=max(240, min(1920, width)),
                     panel_height=max(80, min(1080, height)))

    transparentBackground = Property(bool, lambda self: bool(self.model and self.model.state.transparent_background), notify=changed)
    fontColor = Property(str, lambda self: self.model.state.font_color if self.model else "#f3f5f7", notify=changed)
    fontSize = Property(int, lambda self: self.model.state.font_size if self.model else 0, notify=changed)

    @Slot(bool)
    def setTransparentBackground(self, enabled):
        self._change(transparent_background=bool(enabled))

    @Slot(int)
    def setFontSize(self, size):
        self._change(font_size=max(12, min(72, size)))

    @Slot(str)
    def setFontColor(self, color):
        if re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            self._change(font_color=color.lower())

    @Slot()
    def chooseFontColor(self):
        color = QColorDialog.getColor(QColor(self.fontColor), None, self._locale.tr("reading.color_title"))
        if color.isValid():
            self.setFontColor(color.name())

    @Slot(float)
    def setOpacity(self, opacity):
        self._change(opacity=max(0.2, min(1.0, opacity)))

    @Slot(int)
    def move(self, direction):
        if self.model is None or self._closed:
            return
        try:
            if self.enabled and self._ensure_pages():
                index = max(0, min(len(self._pages) - 1, self._page_index() + (1 if direction > 0 else -1)))
                group, start, text = self._pages[index]
                self.model.update(group_index=group, group_offset=start, scroll_fraction=0.0)
                self._scroll_last = time.monotonic()
                self.scrollChanged.emit()
            else:
                self.model.navigate(1 if direction > 0 else -1)
            self._error = ""
        except Exception as exc:
            self._error = str(exc)
        self.changed.emit()

    @Slot()
    def chooseDocument(self):
        if self._busy or self.model is None:
            return
        path, _ = QFileDialog.getOpenFileName(None, self._locale.tr("reading.dialog_import"), "", self._locale.tr("reading.file_filter"))
        if path:
            self.importPath(path)

    @Slot(str)
    def importPath(self, path):
        if self._busy or self.model is None or self._closed:
            return
        self._busy = True
        self._error = ""
        self.changed.emit()

        def work():
            try:
                result, error = import_document(path), ""
            except Exception as exc:
                result, error = None, "Import failed: " + str(exc)
            if not self._closed:
                self._imported.emit(result, error)

        threading.Thread(target=work, daemon=True, name="ReaderImport").start()

    @Slot(object, str)
    def _finish_import(self, result, error):
        if self._closed:
            return
        self._busy = False
        try:
            if error:
                raise ValueError(error)
            self.setAutoRunning(False)
            self.model.open_document(*result)
            self.scrollChanged.emit()
            self._sync_gate()
            self._error = ""
        except Exception as exc:
            self._error = str(exc)
        self.changed.emit()

    @Slot()
    def close(self):
        self.setAutoRunning(False)
        self._closed = True
        if hasattr(self._hook, "set_reading_hide_key"):
            self._hook.set_reading_hide_key(0)
        self._hold_timer.stop()
        self._gate.configure(False)
        if self._supported:
            self._hook.set_reading_wheel_handler(None)
        if hasattr(self._hook, "set_reading_button_observer"):
            self._hook.set_reading_button_observer(None)
        self.changed.emit()

