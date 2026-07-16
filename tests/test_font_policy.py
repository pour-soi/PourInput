import unittest

from ui.font_policy import resolve_font_families, resolve_monospace_font_family


class FontPolicyTests(unittest.TestCase):
    def test_simplified_chinese_prefers_windows_ui_font_stack(self):
        self.assertEqual(
            resolve_font_families(
                "zh_CN",
                platform_name="win32",
                available_families={
                    "Segoe UI",
                    "Microsoft YaHei",
                    "Microsoft YaHei UI",
                },
                system_families=["Segoe UI"],
            ),
            ["Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI"],
        )

    def test_simplified_chinese_falls_back_to_installed_yahei(self):
        self.assertEqual(
            resolve_font_families(
                "zh-CN",
                platform_name="win32",
                available_families={"Microsoft YaHei", "Segoe UI"},
                system_families=["Segoe UI"],
            ),
            ["Microsoft YaHei", "Segoe UI"],
        )

    def test_english_preserves_existing_system_font(self):
        self.assertEqual(
            resolve_font_families(
                "en",
                platform_name="win32",
                available_families={"Microsoft YaHei UI", "Segoe UI"},
                system_families=["Segoe UI"],
            ),
            ["Segoe UI", "Microsoft YaHei UI"],
        )

    def test_chinese_uses_system_font_when_yahei_is_unavailable(self):
        self.assertEqual(
            resolve_font_families(
                "zh_CN",
                platform_name="win32",
                available_families={"Segoe UI"},
                system_families=["Segoe UI"],
            ),
            ["Segoe UI"],
        )

    def test_generic_macos_family_does_not_override_platform_fallback(self):
        self.assertEqual(
            resolve_font_families(
                "en",
                platform_name="darwin",
                available_families=set(),
                system_families=["Sans Serif"],
            ),
            [".AppleSystemUIFont"],
        )

    def test_generic_linux_family_does_not_override_platform_fallback(self):
        self.assertEqual(
            resolve_font_families(
                "en",
                platform_name="linux",
                available_families=set(),
                system_families=["Sans Serif"],
            ),
            ["Noto Sans"],
        )

    def test_chinese_technical_text_uses_the_same_primary_typeface(self):
        self.assertEqual(
            resolve_monospace_font_family(
                "zh_CN",
                platform_name="win32",
                available_families={"Consolas", "Microsoft YaHei UI"},
                primary_family="Microsoft YaHei UI",
            ),
            "Microsoft YaHei UI",
        )

    def test_english_technical_text_preserves_the_design_monospace_role(self):
        self.assertEqual(
            resolve_monospace_font_family(
                "en",
                platform_name="win32",
                available_families={"Consolas", "Microsoft YaHei UI"},
                primary_family="Segoe UI",
            ),
            "Consolas",
        )
