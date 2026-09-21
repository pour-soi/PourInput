"""Fast wheel ownership gate; no disk, parsing, or UI work on the hook thread."""
import threading
import time


class ReaderWheel:
    def __init__(self, threshold=120, quiet_seconds=0.25):
        self.threshold = threshold
        self.quiet_seconds = quiet_seconds
        self._lock = threading.Lock()
        self._enabled = False
        self._epoch = 0
        self._last = float("-inf")
        self._total = 0
        self._fired = False

    def configure(self, enabled):
        with self._lock:
            self._enabled = bool(enabled)
            self._epoch += 1
            self._last = float("-inf")
            self._total = 0
            self._fired = False

    def accepts(self, epoch):
        with self._lock:
            return self._enabled and epoch == self._epoch

    def feed(self, delta, now=None):
        """Return (claimed, epoch, step); positive wheel = previous group.

        One step per burst, rearmed only after 250 ms without wheel input.
        Even small deltas and the remainder of a burst stay consumed.
        """
        now = time.monotonic() if now is None else now
        with self._lock:
            if not self._enabled:
                return False, self._epoch, 0
            if now - self._last >= self.quiet_seconds:
                self._total, self._fired = 0, False
            self._last = now
            self._total += delta
            step = 0
            if not self._fired and abs(self._total) >= self.threshold:
                step = -1 if self._total > 0 else 1
                self._fired = True
            return True, self._epoch, step

