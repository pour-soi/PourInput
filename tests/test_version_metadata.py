import unittest

from core import version


class VersionMetadataTests(unittest.TestCase):
    def test_about_dialog_maintainer_metadata_uses_current_owner(self):
        self.assertEqual(version.APP_NAME, "PourInput")
        self.assertEqual(version.ORIGINAL_PROJECT, "TomBadash/Mouser")
        self.assertEqual(version.CUSTOMIZED_BY, "pour-soi")


if __name__ == "__main__":
    unittest.main()
