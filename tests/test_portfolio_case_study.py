import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE_STUDY = ROOT / "docs" / "portfolio-case-study.md"


class PortfolioCaseStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = CASE_STUDY.read_text(encoding="utf-8")

    def test_case_study_covers_problem_decisions_and_failures(self) -> None:
        for section in (
            "## The problem",
            "## The hardest decisions",
            "## Failures that improved the project",
            "## Research results",
            "## Engineering evidence",
            "## Skills demonstrated",
        ):
            self.assertIn(section, self.text)

    def test_case_study_links_live_demo_and_research(self) -> None:
        self.assertIn("https://mind-virus-staging.onrender.com", self.text)
        self.assertIn("research-report.md", self.text)
        self.assertIn("../publication/README.md", self.text)

    def test_case_study_preserves_research_boundary(self) -> None:
        self.assertIn("does not claim to model human belief directly", self.text)


if __name__ == "__main__":
    unittest.main()
