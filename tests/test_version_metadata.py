import unittest

from core import version


class VersionMetadataTests(unittest.TestCase):
    def test_about_dialog_maintainer_metadata_uses_current_owner(self):
        self.assertEqual(version.APP_NAME, "PourInput")
        self.assertEqual(version.MAINTAINER, "pour-soi")
        self.assertFalse(hasattr(version, "ORIGINAL_PROJECT"))


if __name__ == "__main__":
    unittest.main()
