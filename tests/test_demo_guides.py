import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DemoGuideTests(unittest.TestCase):
    def test_rehearsal_guide_lists_every_required_page(self) -> None:
        text = (ROOT / "docs" / "demo-rehearsal-guide.md").read_text(
            encoding="utf-8"
        )
        for required in (
            "mind-virus-staging.onrender.com",
            "architecture.md",
            "portfolio-case-study.md",
            "research-report.md",
            "publication/README.md",
            "/actions",
        ):
            self.assertIn(required, text)

    def test_live_guide_preserves_paid_call_boundary(self) -> None:
        text = (ROOT / "docs" / "live-ai-acceptance-test.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("hard-capped at four paid model calls", text)
        self.assertIn("Type RUN to continue", text)
        self.assertIn("$env:OPENAI_API_KEY = $null", text)
        self.assertNotIn("sk-", text)

    def test_conclusion_contains_broader_research_message(self) -> None:
        text = (ROOT / "docs" / "demo-walkthrough.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("broader lesson goes beyond this one project", text)
        self.assertIn("build the system, test the assumptions", text)


if __name__ == "__main__":
    unittest.main()
