import json
from pathlib import Path
import plistlib
import tempfile
import unittest

from core.version import APP_VERSION
from tools.verify_macos_bundle import REQUIRED_RESOURCE_SUFFIXES, verify_bundle


class MacOSBundleVerifierTests(unittest.TestCase):
    def _bundle(self, root: Path, *, version: str = APP_VERSION) -> Path:
        bundle = root / "PourInput.app"
        contents = bundle / "Contents"
        executable = contents / "MacOS" / "PourInput"
        executable.parent.mkdir(parents=True)
        executable.write_bytes(b"fake Mach-O")
        info = {
            "CFBundleExecutable": "PourInput",
            "CFBundleIdentifier": "io.github.pour_soi.pourinput",
            "CFBundleShortVersionString": version,
            "LSUIElement": True,
        }
        with (contents / "Info.plist").open("wb") as info_file:
            plistlib.dump(info, info_file)
        resources = contents / "Resources"
        for suffix in REQUIRED_RESOURCE_SUFFIXES:
            target = resources / suffix
            target.parent.mkdir(parents=True, exist_ok=True)
            if suffix == "POURINPUT_build_info.json":
                target.write_text(
                    json.dumps(
                        {"version": version, "commit": "abc123", "dirty": False}
                    ),
                    encoding="utf-8",
                )
            else:
                target.write_text("resource", encoding="utf-8")
        return bundle

    def test_accepts_complete_bundle_with_matching_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = verify_bundle(
                self._bundle(Path(tmp)),
                expected_version=APP_VERSION,
                expected_architecture="arm64",
            )

        self.assertEqual(result["version"], APP_VERSION)
        self.assertEqual(result["commit"], "abc123")
        self.assertEqual(result["architecture"], "arm64")

    def test_rejects_missing_resource(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle(Path(tmp))
            (bundle / "Contents" / "Resources" / "ui" / "qml" / "Main.qml").unlink()

            with self.assertRaisesRegex(ValueError, "ui/qml/Main.qml"):
                verify_bundle(bundle, expected_version=APP_VERSION)

    def test_rejects_mismatched_or_dirty_build_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._bundle(Path(tmp))
            build_info = (
                bundle
                / "Contents"
                / "Resources"
                / "POURINPUT_build_info.json"
            )
            build_info.write_text(
                json.dumps({"version": "9.9.9", "commit": "", "dirty": True}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "build metadata version"):
                verify_bundle(bundle, expected_version=APP_VERSION)


if __name__ == "__main__":
    unittest.main()
