"""Central application font selection for Qt widgets and QML controls."""

import sys

from PySide6.QtGui import QFont, QFontDatabase


WINDOWS_CHINESE_FONT_STACK = (
    "Microsoft YaHei UI",
    "Microsoft YaHei",
)
GENERIC_FONT_FAMILIES = frozenset(("Sans Serif", "sans-serif", "system-ui"))


def is_simplified_chinese(language):
    normalized = str(language or "").replace("-", "_").lower()
    return normalized in {"zh", "zh_cn", "zh_hans"}


def resolve_font_families(
    language,
    *,
    platform_name,
    available_families,
    system_families,
):
    """Return an ordered, installed font stack for the active language."""
    available = set(available_families)
    system = [
        family
        for family in system_families
        if family and family not in GENERIC_FONT_FAMILIES
    ]
    preferred = []
    if platform_name == "win32" and is_simplified_chinese(language):
        preferred = [
            family for family in WINDOWS_CHINESE_FONT_STACK if family in available
        ]
    windows_cjk_fallbacks = []
    if platform_name == "win32":
        windows_cjk_fallbacks = [
            family for family in WINDOWS_CHINESE_FONT_STACK if family in available
        ]
    resolved = []
    for family in (*preferred, *system, *windows_cjk_fallbacks):
        if family and family not in resolved:
            resolved.append(family)
    if resolved:
        return resolved
    if platform_name == "win32":
        return ["Segoe UI"]
    if platform_name == "darwin":
        return [".AppleSystemUIFont"]
    return ["Noto Sans"]


def resolve_monospace_font_family(
    language,
    *,
    platform_name,
    available_families,
    primary_family,
):
    """Keep technical text legible without inconsistent CJK fallback."""
    if is_simplified_chinese(language):
        return primary_family
    platform_monospace = {
        "win32": "Consolas",
        "darwin": "Menlo",
    }.get(platform_name, "monospace")
    if platform_monospace == "monospace" or platform_monospace in available_families:
        return platform_monospace
    return primary_family


def apply_application_font(app, language, base_font):
    """Apply the locale-aware font before constructing or refreshing UI."""
    font = QFont(base_font)
    base_families = list(font.families()) or [font.family()]
    families = resolve_font_families(
        language,
        platform_name=sys.platform,
        available_families=QFontDatabase.families(),
        system_families=base_families,
    )
    font.setFamilies(families)
    app.setFont(font)
    return families[0]
