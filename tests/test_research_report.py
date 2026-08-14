import unittest
from pathlib import Path
import re


REPORT = Path(__file__).resolve().parents[1] / "docs" / "research-report.md"


class ResearchReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = REPORT.read_text(encoding="utf-8")

    def test_report_contains_required_paper_sections(self) -> None:
        for section in (
            "## Abstract",
            "## 5. Original confirmatory experiment",
            "## 6. Confirmatory robustness experiment",
            "## 8. Threats to validity",
            "## 10. Reproducibility and data availability",
            "## 11. Conclusion",
        ):
            self.assertIn(section, self.text)

    def test_report_records_frozen_sample_sizes(self) -> None:
        self.assertIn("120 condition-trials", self.text)
        self.assertRegex(self.text, re.compile(r"648\s+live decisions"))

    def test_report_does_not_overgeneralize_to_people(self) -> None:
        self.assertIn("not claims about human communities", self.text)


if __name__ == "__main__":
    unittest.main()
