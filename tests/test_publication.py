import unittest
from pathlib import Path

from scripts.reproduce_publication import (
    PACKAGE,
    reproduce_phase6,
    reproduce_phase12,
    verify_checksums,
)


class PublicationPackageTests(unittest.TestCase):
    def test_licenses_and_citation_are_present(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "LICENSE").is_file())
        self.assertTrue((root / "CITATION.cff").is_file())
        self.assertTrue((PACKAGE / "LICENSE-DATA.md").is_file())

    def test_publication_checksums(self) -> None:
        verify_checksums()

    def test_checksums_are_independent_of_platform_line_endings(self) -> None:
        source = (PACKAGE / "data" / "phase6_confirmatory_analysis.json").read_text(
            encoding="utf-8"
        )
        self.assertEqual(
            source.replace("\r\n", "\n"),
            source.replace("\n", "\r\n").replace("\r\r\n", "\r\n").replace("\r\n", "\n"),
        )

    def test_phase6_analysis_is_reproducible(self) -> None:
        result = reproduce_phase6()
        self.assertEqual(result["design"]["condition_trials"], 120)

    def test_phase12_analysis_is_reproducible(self) -> None:
        result = reproduce_phase12()
        self.assertEqual(result.records, 648)
        self.assertEqual(result.cells, 12)


if __name__ == "__main__":
    unittest.main()
