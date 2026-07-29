"""Validate the structure and metadata of a packaged PourInput macOS app."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import plistlib


REQUIRED_RESOURCE_SUFFIXES = (
    "ui/qml/Main.qml",
    "ui/qml/MousePage.qml",
    "images/logo_icon.png",
    "images/logo_tray_template.png",
    "POURINPUT_build_info.json",
)


def _find_resource(bundle: Path, suffix: str) -> Path | None:
    normalized_suffix = suffix.replace("\\", "/")
    for candidate in bundle.rglob(Path(suffix).name):
        if candidate.as_posix().endswith(normalized_suffix):
            return candidate
    return None


def verify_bundle(
    bundle_path: str | Path,
    *,
    expected_version: str,
    expected_architecture: str | None = None,
) -> dict[str, str]:
    bundle = Path(bundle_path)
    errors: list[str] = []
    if bundle.suffix != ".app" or not bundle.is_dir():
        raise ValueError(f"macOS app bundle not found: {bundle}")

    info_path = bundle / "Contents" / "Info.plist"
    executable_path = bundle / "Contents" / "MacOS" / "PourInput"
    if not info_path.is_file():
        errors.append("missing Contents/Info.plist")
        info = {}
    else:
        with info_path.open("rb") as info_file:
            info = plistlib.load(info_file)

    if not executable_path.is_file():
        errors.append("missing Contents/MacOS/PourInput")
    if info.get("CFBundleExecutable") != "PourInput":
        errors.append("CFBundleExecutable must be PourInput")
    if info.get("CFBundleIdentifier") != "io.github.pour_soi.pourinput":
        errors.append("unexpected CFBundleIdentifier")
    if info.get("CFBundleShortVersionString") != expected_version:
        errors.append("CFBundleShortVersionString does not match application version")
    if info.get("LSUIElement") is not True:
        errors.append("LSUIElement must be enabled for menu-bar operation")

    found_resources: dict[str, Path] = {}
    for suffix in REQUIRED_RESOURCE_SUFFIXES:
        candidate = _find_resource(bundle, suffix)
        if candidate is None:
            errors.append(f"missing bundled resource: {suffix}")
        else:
            found_resources[suffix] = candidate

    build_info_path = found_resources.get("POURINPUT_build_info.json")
    build_info: dict[str, object] = {}
    if build_info_path is not None:
        try:
            build_info = json.loads(build_info_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid build metadata: {exc}")
        else:
            if build_info.get("version") != expected_version:
                errors.append("build metadata version does not match application version")
            if build_info.get("dirty") is not False:
                errors.append("build metadata must identify a clean source tree")

    if expected_architecture and executable_path.is_file():
        # Architecture is asserted by the runner/toolchain and recorded here.
        # The workflow separately checks the Mach-O header with `file`.
        expected_architecture = expected_architecture.strip()
        if expected_architecture not in {"arm64", "x86_64"}:
            errors.append(f"unsupported expected architecture: {expected_architecture}")

    if errors:
        raise ValueError("; ".join(errors))

    return {
        "bundle": str(bundle),
        "version": str(info["CFBundleShortVersionString"]),
        "identifier": str(info["CFBundleIdentifier"]),
        "executable": str(executable_path),
        "commit": str(build_info.get("commit") or ""),
        "architecture": expected_architecture or "",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle")
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--expected-architecture", choices=("arm64", "x86_64"))
    args = parser.parse_args(argv)

    result = verify_bundle(
        args.bundle,
        expected_version=args.expected_version,
        expected_architecture=args.expected_architecture,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
