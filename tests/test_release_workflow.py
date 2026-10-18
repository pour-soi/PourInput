"""Release safety contracts; these checks never dispatch a build or publish."""
from pathlib import Path
import re
import unittest


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/release.yml"


class ReleaseWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def job(self, name):
        match = re.search(
            rf"^  {re.escape(name)}:\n(.*?)(?=^  [\w-]+:\n|\Z)",
            self.workflow, re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(match, f"Missing release job: {name}")
        return match.group(1)

    def test_release_creation_requires_separate_publication_and_existing_tag(self):
        commands = re.sub(r"\\\n\s*", " ", self.workflow)
        creates = re.findall(r"^\s*gh release create (.+)$", commands, re.MULTILINE)
        self.assertEqual(len(creates), 1)
        self.assertRegex(creates[0], r"(?:^|\s)--draft(?:\s|$)")
        self.assertRegex(creates[0], r"(?:^|\s)--verify-tag(?:\s|$)")
        self.assertNotRegex(self.workflow, r"gh release (?:edit|delete|upload)\b")

    def test_existing_release_is_rejected_before_creation(self):
        release = self.job("release")
        self.assertRegex(
            release,
            r'(?s)if gh release view "\$\{\{ env.RELEASE_TAG \}\}".*?; then'
            r'.*?exit 1\s+fi\s+gh release create',
        )

    def test_builds_and_release_use_clean_immutable_tag_source(self):
        for name in ("build-windows", "build-macos", "build-linux", "release"):
            with self.subTest(job=name):
                job = self.job(name)
                self.assertIn("ref: refs/tags/${{ env.RELEASE_TAG }}", job)
                self.assertIn(
                    'test "$(git rev-parse HEAD)" = '
                    '"$(git rev-parse "refs/tags/$RELEASE_TAG^{commit}")"', job,
                )
                self.assertIn('test -z "$(git status --porcelain)"', job)

    def test_v151_builds_only_windows_for_tag_and_manual_dispatch(self):
        for name in ("build-macos", "build-linux"):
            with self.subTest(job=name):
                condition = re.search(r"^    if: (.+)$", self.job(name), re.MULTILINE).group(1)
                self.assertIn("github.ref != 'refs/tags/v1.5.1'", condition)
                self.assertIn("github.event.inputs.release_tag != 'v1.5.1'", condition)
        windows_condition = re.search(
            r"^    if: (.+)$", self.job("build-windows"), re.MULTILINE,
        ).group(1)
        self.assertNotIn("v1.5.1", windows_condition)
        self.assertIn("needs: [build-windows]", self.job("release"))


if __name__ == "__main__":
    unittest.main()
