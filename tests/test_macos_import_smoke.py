from pathlib import Path
import sys
import unittest

from tools import macos_import_smoke


class MacOSImportSmokeTests(unittest.TestCase):
    def test_script_bootstraps_repository_root_for_direct_execution(self):
        expected_root = Path(__file__).resolve().parents[1]

        self.assertEqual(macos_import_smoke.ROOT, expected_root)
        self.assertIn(str(expected_root), sys.path)


if __name__ == "__main__":
    unittest.main()
