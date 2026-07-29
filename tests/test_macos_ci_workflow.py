from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "macos-experimental.yml"


class MacOSExperimentalWorkflowTests(unittest.TestCase):
    def test_workflow_is_manual_and_pr_capable_without_write_permissions(self):
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("workflow_dispatch:", text)
        self.assertIn("pull_request:", text)
        self.assertIn("permissions:\n  contents: read", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("gh release", text)
        self.assertNotIn("git push", text)

    def test_workflow_tests_builds_verifies_and_uploads_both_architectures(self):
        text = WORKFLOW.read_text(encoding="utf-8")

        for expected in (
            "macos-latest",
            "macos-15-intel",
            'branches: ["main", "feature/macos-experimental"]',
            "target_arch: arm64",
            "target_arch: x86_64",
            "python -m venv .venv",
            "unittest discover",
            "tools/macos_import_smoke.py",
            "tools/verify_macos_bundle.py",
            "POURINPUT_STARTUP_SMOKE_TEST",
            "ditto -c -k --sequesterRsrc --keepParent",
            "actions/upload-artifact@v7",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_workflow_explicitly_skips_project_codesign_step(self):
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn('POURINPUT_SKIP_CODESIGN: "true"', text)
        self.assertNotIn("POURINPUT_SIGN_IDENTITY", text)
        self.assertNotIn("notary", text.lower())


if __name__ == "__main__":
    unittest.main()
