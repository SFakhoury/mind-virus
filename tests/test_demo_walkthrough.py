import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WALKTHROUGH = ROOT / "docs" / "demo-walkthrough.md"


class DemoWalkthroughTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WALKTHROUGH.read_text(encoding="utf-8")

    def test_walkthrough_contains_complete_scene_sequence(self) -> None:
        for scene in range(1, 8):
            self.assertIn(f"### Scene {scene}", self.text)

    def test_walkthrough_protects_secrets_and_costs(self) -> None:
        self.assertIn("makes no OpenAI API calls", self.text)
        self.assertIn("No API key", self.text)
        self.assertIn("Do not add `--live`", self.text)

    def test_walkthrough_has_publication_acceptance_checklist(self) -> None:
        self.assertIn("## Recording acceptance checklist", self.text)
        self.assertIn("Video URL", self.text)
        self.assertIn("Demo commit", self.text)


if __name__ == "__main__":
    unittest.main()
