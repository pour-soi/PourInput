import sys
import threading
import unittest
import ctypes
import struct
from unittest.mock import Mock, patch

from PIL import Image
from PySide6.QtCore import QEventLoop, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from ui.windows_screenshot import (
    IntRect,
    MonitorMap,
    VirtualCapture,
    WindowsScreenshotController,
    build_monitor_maps,
    capture_virtual_desktop,
    crop_logical_region,
    image_to_cf_dib,
    write_cf_dib_to_windows_clipboard,
)
from ui.screenshot_common import SCREENSHOT_FULL_CLIP, SCREENSHOT_FULL_FILE


class FakeClipboard:
    def __init__(self, *, fail_write=None, delayed=False):
        self.fail_write = fail_write
        self.delayed = delayed
        self.written = None
        self.available = not delayed

    def setImage(self, image):
        if self.fail_write is not None:
            raise self.fail_write
        self.written = image

    def image(self):
        if self.written is None or not self.available:
            return QImage()
        return self.written


class FakeNativeClipboardApi:
    def __init__(self, *, open_results=(True,), empty=True, set_data=True, available=True):
        self.open_results = list(open_results)
        self.empty = empty
        self.set_data = set_data
        self.available = available
        self.buffer = None
        self.freed = []
        self.closed = 0
        self.last_handle = None
        self.sequence = 10
        self.user32 = self.User32(self)
        self.kernel32 = self.Kernel32(self)

    def last_error(self):
        return 5

    class User32:
        def __init__(self, owner):
            self.owner = owner

        def OpenClipboard(self, _window):
            return self.owner.open_results.pop(0) if self.owner.open_results else False

        def EmptyClipboard(self):
            return self.owner.empty

        def SetClipboardData(self, _format, handle):
            self.owner.last_handle = handle
            self.owner.sequence += 1
            return handle if self.owner.set_data else 0

        def CloseClipboard(self):
            self.owner.closed += 1
            return True

        def IsClipboardFormatAvailable(self, _format):
            return self.owner.available

        def GetClipboardSequenceNumber(self):
            return self.owner.sequence

        def GetClipboardOwner(self):
            return 0

        def GetWindowThreadProcessId(self, _owner, _pid):
            return 0

        def GetWindowTextW(self, _owner, _title, _count):
            return 0

    class Kernel32:
        def __init__(self, owner):
            self.owner = owner

        def GlobalAlloc(self, _flags, size):
            self.owner.buffer = ctypes.create_string_buffer(size)
            return 1

        def GlobalLock(self, _handle):
            return ctypes.addressof(self.owner.buffer)

        def GlobalUnlock(self, _handle):
            return True

        def GlobalFree(self, handle):
            self.owner.freed.append(handle)
            return 0


class WindowsScreenshotGeometryTests(unittest.TestCase):
    def test_build_monitor_maps_pairs_rectangles_spatially(self):
        logical = [IntRect(100, 0, 200, 100), IntRect(-100, 0, 0, 100)]
        physical = [IntRect(0, 0, 200, 200), IntRect(-200, 0, 0, 200)]

        maps = build_monitor_maps(logical, physical)

        self.assertEqual(maps[0], MonitorMap(IntRect(-100, 0, 0, 100), IntRect(-200, 0, 0, 200)))
        self.assertEqual(maps[1], MonitorMap(IntRect(100, 0, 200, 100), IntRect(0, 0, 200, 200)))

    def test_crop_logical_region_scales_single_monitor_selection(self):
        image = Image.new("RGB", (200, 100), (10, 20, 30))
        capture = VirtualCapture(
            image=image,
            physical_rect=IntRect(0, 0, 200, 100),
            monitor_maps=(MonitorMap(IntRect(0, 0, 100, 50), IntRect(0, 0, 200, 100)),),
        )

        cropped = crop_logical_region(capture, IntRect(10, 5, 20, 15))

        self.assertEqual(cropped.size, (20, 20))

    def test_crop_logical_region_handles_negative_monitor_origin(self):
        image = Image.new("RGB", (100, 100), (50, 60, 70))
        capture = VirtualCapture(
            image=image,
            physical_rect=IntRect(-100, 0, 0, 100),
            monitor_maps=(MonitorMap(IntRect(-50, 0, 0, 50), IntRect(-100, 0, 0, 100)),),
        )

        cropped = crop_logical_region(capture, IntRect(-25, 10, 0, 20))

        self.assertEqual(cropped.size, (50, 20))

    def test_capture_virtual_desktop_composes_per_monitor_images(self):
        maps = (
            MonitorMap(IntRect(-100, 0, 0, 50), IntRect(-100, 0, 0, 50)),
            MonitorMap(IntRect(0, 0, 100, 50), IntRect(0, 0, 100, 50)),
        )

        def fake_grab(*, bbox, **_kwargs):
            color = (255, 0, 0) if bbox[0] < 0 else (0, 0, 255)
            return Image.new("RGB", (bbox[2] - bbox[0], bbox[3] - bbox[1]), color)

        capture = capture_virtual_desktop(maps, grab=fake_grab)

        self.assertEqual(capture.image.size, (200, 50))
        self.assertEqual(capture.image.getpixel((25, 10)), (255, 0, 0))
        self.assertEqual(capture.image.getpixel((175, 10)), (0, 0, 255))

    def test_file_delivery_uses_injected_path_factory(self):
        statuses = []
        target = "/tmp/custom-windows-shot.png"
        controller = WindowsScreenshotController(
            status_callback=statuses.append,
            path_factory=lambda: target,
        )

        from unittest.mock import patch

        with patch("ui.windows_screenshot.save_image_to_file", return_value=target) as save_image:
            image = Image.new("RGBA", (2, 2))
            controller._deliver_image(image, SCREENSHOT_FULL_FILE)

        save_image.assert_called_once_with(image, target)
        self.assertEqual(statuses, [f"Screenshot saved to {target}"])


class WindowsNativeClipboardTests(unittest.TestCase):
    def test_dib_payload_is_a_24_bit_bottom_up_bitmap(self):
        payload = image_to_cf_dib(Image.new("RGBA", (3, 2), (10, 20, 30, 40)))

        header = struct.unpack("<IiiHHIIIIII", payload[:40])
        self.assertEqual(header[0], 40)
        self.assertEqual(header[1:3], (3, 2))
        self.assertEqual(header[3:5], (1, 24))
        self.assertGreater(len(payload), 40)

    def test_native_clipboard_retries_contention_and_transfers_ownership(self):
        api = FakeNativeClipboardApi(open_results=(False, False, True))
        sleeps = []

        size = write_cf_dib_to_windows_clipboard(
            Image.new("RGB", (4, 3)),
            api=api,
            retry_delays=(0, 0.01, 0.02),
            sleep=sleeps.append,
        )

        self.assertEqual(size[:2], (4, 3))
        self.assertEqual(sleeps, [0.01, 0.02])
        self.assertEqual(api.last_handle, 1)
        self.assertEqual(api.freed, [])
        self.assertEqual(api.closed, 1)

    def test_failed_set_clipboard_data_frees_memory_and_logs_winerror(self):
        api = FakeNativeClipboardApi(set_data=False)

        with self.assertRaisesRegex(RuntimeError, "SetClipboardData failed.*WinError 5"):
            write_cf_dib_to_windows_clipboard(Image.new("RGB", (2, 2)), api=api)

        self.assertEqual(api.freed, [1])
        self.assertEqual(api.closed, 1)

    def test_open_failure_is_bounded_and_reports_exact_winerror(self):
        api = FakeNativeClipboardApi(open_results=(False, False))

        with self.assertRaisesRegex(RuntimeError, "OpenClipboard failed.*WinError 5"):
            write_cf_dib_to_windows_clipboard(
                Image.new("RGB", (2, 2)),
                api=api,
                retry_delays=(0, 0),
            )

        self.assertEqual(api.closed, 0)

    def test_external_format_verification_is_required(self):
        api = FakeNativeClipboardApi(available=False)

        with self.assertRaisesRegex(RuntimeError, "CF_DIB verification failed"):
            write_cf_dib_to_windows_clipboard(Image.new("RGB", (2, 2)), api=api)


class WindowsScreenshotControllerTests(unittest.TestCase):
    _MAPS = (MonitorMap(IntRect(0, 0, 20, 10), IntRect(0, 0, 20, 10)),)

    @staticmethod
    def _capture(width=20, height=10):
        return VirtualCapture(
            Image.new("RGB", (width, height), (10, 20, 30)),
            IntRect(0, 0, width, height),
            (MonitorMap(IntRect(0, 0, width, height), IntRect(0, 0, width, height)),),
        )

    def test_full_clip_request_captures_and_confirms_clipboard_image(self):
        statuses = []
        clipboard = FakeClipboard()
        controller = WindowsScreenshotController(status_callback=statuses.append)

        with (
            patch("ui.windows_screenshot.sys.platform", "linux"),
            patch("ui.windows_screenshot._system_monitor_maps", return_value=self._MAPS),
            patch("ui.windows_screenshot.capture_virtual_desktop", return_value=self._capture()) as capture,
            patch("ui.windows_screenshot.QGuiApplication.clipboard", return_value=clipboard),
            patch("builtins.print") as print_mock,
        ):
            controller._handle_request(SCREENSHOT_FULL_CLIP)

        capture.assert_called_once_with(self._MAPS)
        self.assertIsNotNone(clipboard.written)
        self.assertEqual((clipboard.written.width(), clipboard.written.height()), (20, 10))
        self.assertEqual(statuses, ["Screenshot copied to clipboard"])
        messages = [str(call.args[0]) for call in print_mock.call_args_list]
        for expected in (
            "GUI screenshot handler entered",
            "target screen selected",
            "screen capture completed",
            "image dimensions and format",
            "clipboard write requested",
            "clipboard image confirmed",
        ):
            self.assertTrue(any(expected in message for message in messages), expected)

    def test_completion_is_logged_only_after_event_driven_clipboard_confirmation(self):
        statuses = []
        scheduled = []
        clipboard = FakeClipboard(delayed=True)
        controller = WindowsScreenshotController(status_callback=statuses.append)

        with (
            patch("ui.windows_screenshot.sys.platform", "linux"),
            patch("ui.windows_screenshot.QGuiApplication.clipboard", return_value=clipboard),
            patch("ui.windows_screenshot.QTimer.singleShot", side_effect=lambda _delay, callback: scheduled.append(callback)),
            patch("builtins.print") as print_mock,
        ):
            controller._deliver_image(Image.new("RGB", (4, 3)), SCREENSHOT_FULL_CLIP)
            messages = [str(call.args[0]) for call in print_mock.call_args_list]
            self.assertFalse(any("clipboard image confirmed" in message for message in messages))
            self.assertEqual(statuses, [])

            clipboard.available = True
            scheduled.pop(0)()

        messages = [str(call.args[0]) for call in print_mock.call_args_list]
        self.assertTrue(any("clipboard image confirmed" in message for message in messages))
        self.assertEqual(statuses, ["Screenshot copied to clipboard"])

    def test_capture_failure_logs_concrete_error_and_traceback(self):
        statuses = []
        controller = WindowsScreenshotController(status_callback=statuses.append)

        with (
            patch("ui.windows_screenshot._system_monitor_maps", side_effect=RuntimeError("monitor query failed")),
            patch("builtins.print") as print_mock,
            patch("ui.windows_screenshot.traceback.print_exc") as traceback_mock,
        ):
            controller._handle_request(SCREENSHOT_FULL_CLIP)

        messages = [str(call.args[0]) for call in print_mock.call_args_list]
        self.assertTrue(any("stage=capture error=monitor query failed" in m for m in messages))
        traceback_mock.assert_called_once()
        self.assertEqual(statuses, ["Screenshot failed: monitor query failed"])

    def test_clipboard_failure_logs_concrete_error_and_traceback(self):
        statuses = []
        clipboard = FakeClipboard(fail_write=RuntimeError("clipboard busy"))
        controller = WindowsScreenshotController(status_callback=statuses.append)

        with (
            patch("ui.windows_screenshot.sys.platform", "linux"),
            patch("ui.windows_screenshot.QGuiApplication.clipboard", return_value=clipboard),
            patch("builtins.print") as print_mock,
            patch("ui.windows_screenshot.traceback.print_exc") as traceback_mock,
        ):
            controller._deliver_image(Image.new("RGB", (4, 3)), SCREENSHOT_FULL_CLIP)

        messages = [str(call.args[0]) for call in print_mock.call_args_list]
        self.assertTrue(any("stage=clipboard delivery error=clipboard busy" in m for m in messages))
        traceback_mock.assert_called_once()
        self.assertEqual(statuses, ["Screenshot failed: clipboard busy"])

    def test_repeated_clipboard_requests_keep_latest_image_alive(self):
        clipboard = FakeClipboard()
        controller = WindowsScreenshotController()

        with (
            patch("ui.windows_screenshot.sys.platform", "linux"),
            patch("ui.windows_screenshot.QGuiApplication.clipboard", return_value=clipboard),
        ):
            controller._deliver_image(Image.new("RGB", (4, 3)), SCREENSHOT_FULL_CLIP)
            first = controller._clipboard_image
            controller._deliver_image(Image.new("RGB", (8, 6)), SCREENSHOT_FULL_CLIP)

        self.assertIsNot(first, controller._clipboard_image)
        self.assertIs(controller._clipboard_image, clipboard.written)
        self.assertEqual((clipboard.image().width(), clipboard.image().height()), (8, 6))
        self.assertEqual(controller._clipboard_delivery_token, 2)

    @unittest.skipUnless(sys.platform == "win32", "Windows queued signal behavior")
    def test_worker_request_reaches_controller_on_gui_thread(self):
        app = QApplication.instance() or QApplication([])
        received = []

        class ProbeController(WindowsScreenshotController):
            handled = Signal()

            @Slot(str, int)
            def _handle_request(self, action_id, request_id=0):
                received.append((action_id, request_id, QThread.currentThread() is self.thread()))
                self._finish_request(request_id, True)
                self.handled.emit()

        controller = ProbeController(parent=app)
        loop = QEventLoop()
        controller.handled.connect(loop.quit)
        worker = threading.Thread(
            target=controller.request_action,
            args=(SCREENSHOT_FULL_CLIP,),
        )
        worker.start()
        QTimer.singleShot(1000, loop.quit)
        loop.exec()
        worker.join()

        self.assertEqual(received, [(SCREENSHOT_FULL_CLIP, 1, True)])

    def test_active_request_rejects_overlap_and_separate_request_is_allowed(self):
        controller = WindowsScreenshotController()
        emitted = []
        controller._requestAction.connect(lambda action, request_id: emitted.append((action, request_id)))

        self.assertTrue(controller.request_action(SCREENSHOT_FULL_CLIP))
        self.assertFalse(controller.request_action(SCREENSHOT_FULL_CLIP))
        controller._finish_request(1, True)
        self.assertTrue(controller.request_action(SCREENSHOT_FULL_CLIP))

        self.assertEqual(
            emitted,
            [(SCREENSHOT_FULL_CLIP, 1), (SCREENSHOT_FULL_CLIP, 2)],
        )
        controller._finish_request(2, True)

    def test_stale_completion_cannot_release_newer_request(self):
        controller = WindowsScreenshotController()
        controller._request_in_progress = True
        controller._active_request_id = 4

        controller._finish_request(3, True)

        self.assertTrue(controller._request_in_progress)
        self.assertEqual(controller._active_request_id, 4)

    def test_windows_controller_uses_native_delivery_not_qt_readback(self):
        statuses = []
        controller = WindowsScreenshotController(status_callback=statuses.append)

        with (
            patch("ui.windows_screenshot.sys.platform", "win32"),
            patch(
                "ui.windows_screenshot.write_cf_dib_to_windows_clipboard",
                return_value=(4, 3, 10, 11),
            ) as native,
            patch("ui.windows_screenshot.QTimer.singleShot") as timer,
            patch("ui.windows_screenshot.QGuiApplication.clipboard") as qt_clipboard,
        ):
            controller._deliver_image(Image.new("RGB", (4, 3)), SCREENSHOT_FULL_CLIP, 7)

        native.assert_called_once()
        qt_clipboard.assert_not_called()
        self.assertEqual(timer.call_count, 3)
        self.assertEqual(statuses, ["Screenshot copied to clipboard"])


if __name__ == "__main__":
    unittest.main()
