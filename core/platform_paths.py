"""Platform-aware storage paths used by PourInput.

Windows locations intentionally preserve the paths used by existing releases.
macOS follows the standard Library directory layout without requiring an
additional runtime dependency.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
from typing import Mapping


APP_DIRECTORY_NAME = "PourInput"


def _platform_name(platform_name: str | None) -> str:
    return platform_name or sys.platform


def _environment(environ: Mapping[str, str] | None) -> Mapping[str, str]:
    return os.environ if environ is None else environ


def _home_path(home: str | os.PathLike[str] | None) -> Path:
    return Path(home).expanduser() if home is not None else Path.home()


def config_dir(
    *,
    platform_name: str | None = None,
    home: str | os.PathLike[str] | None = None,
    environ: Mapping[str, str] | None = None,
) -> Path:
    """Return the directory containing configuration and application state."""

    platform_name = _platform_name(platform_name)
    home_path = _home_path(home)
    env = _environment(environ)
    if platform_name == "darwin":
        return home_path / "Library" / "Application Support" / APP_DIRECTORY_NAME
    if platform_name.startswith("linux"):
        base = Path(env.get("XDG_CONFIG_HOME") or home_path / ".config").expanduser()
        return base / APP_DIRECTORY_NAME
    base = Path(env.get("APPDATA") or home_path).expanduser()
    return base / APP_DIRECTORY_NAME


def log_dir(
    *,
    platform_name: str | None = None,
    home: str | os.PathLike[str] | None = None,
    environ: Mapping[str, str] | None = None,
) -> Path:
    """Return the platform-native directory for rotating application logs."""

    platform_name = _platform_name(platform_name)
    home_path = _home_path(home)
    env = _environment(environ)
    if platform_name == "darwin":
        return home_path / "Library" / "Logs" / APP_DIRECTORY_NAME
    if platform_name.startswith("linux"):
        base = Path(
            env.get("XDG_STATE_HOME") or home_path / ".local" / "state"
        ).expanduser()
        return base / APP_DIRECTORY_NAME / "logs"
    base = Path(env.get("APPDATA") or home_path).expanduser()
    return base / APP_DIRECTORY_NAME / "logs"


def update_data_dir(
    *,
    platform_name: str | None = None,
    home: str | os.PathLike[str] | None = None,
    environ: Mapping[str, str] | None = None,
) -> Path:
    """Return update-state storage while retaining existing Windows behavior."""

    platform_name = _platform_name(platform_name)
    home_path = _home_path(home)
    env = _environment(environ)
    if platform_name.startswith("win"):
        base = Path(
            env.get("LOCALAPPDATA") or home_path / "AppData" / "Local"
        ).expanduser()
        return base / APP_DIRECTORY_NAME / "updates"
    if platform_name == "darwin":
        return config_dir(
            platform_name=platform_name,
            home=home_path,
            environ=env,
        ) / "updates"
    # Preserve the existing Linux/other-platform location.
    return home_path / f".{APP_DIRECTORY_NAME}" / "updates"


def temporary_dir(
    *,
    temp_root: str | os.PathLike[str] | None = None,
) -> Path:
    """Return an application-scoped directory beneath the system temp root."""

    root = Path(temp_root) if temp_root is not None else Path(tempfile.gettempdir())
    return root / APP_DIRECTORY_NAME


def screenshots_dir(
    *,
    home: str | os.PathLike[str] | None = None,
) -> Path:
    """Return the primary user-generated screenshot directory."""

    return _home_path(home) / "Pictures" / "Screenshots"
