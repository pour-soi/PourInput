"""Remember only the normal main-window size, separately from user settings."""
import json
import os
from pathlib import Path

from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtGui import QWindow


class WindowSizeState(QObject):
    def __init__(self, window, path):
        super().__init__(window)
        self.window = window
        self.path = Path(path)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.save)
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            width, height = data["width"], data["height"]
            if type(width) is not int or type(height) is not int or min(width, height) <= 0:
                raise ValueError("invalid window size")
        except (OSError, ValueError, KeyError, TypeError):
            width, height = window.width(), window.height()
        available = window.screen().availableGeometry()
        window.resize(max(window.minimumWidth(), min(width, available.width())),
                      max(window.minimumHeight(), min(height, available.height())))
        window.widthChanged.connect(lambda _: self.timer.start())
        window.heightChanged.connect(lambda _: self.timer.start())
        window.installEventFilter(self)

    def save(self):
        self.timer.stop()
        if self.window.visibility() != QWindow.Visibility.Windowed:
            return
        data = {"width": self.window.width(), "height": self.window.height()}
        temporary = self.path.with_suffix(".tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary.write_text(json.dumps(data), encoding="utf-8")
            os.replace(temporary, self.path)
        except OSError as exc:
            print(f"[Window] Could not save window size: {exc}")

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.Close:
            self.save()
        return super().eventFilter(watched, event)
