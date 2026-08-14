import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicationDocumentationTests(unittest.TestCase):
    def test_architecture_has_system_and_experiment_diagrams(self) -> None:
        text = (ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count("```mermaid"), 3)
        self.assertIn("## Trust boundaries", text)

    def test_provenance_links_frozen_evidence(self) -> None:
        text = (ROOT / "docs" / "experiment-provenance.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("phase5_confirmatory_experiment.jsonl", text)
        self.assertIn("phase12_confirmatory_robustness.json", text)
        self.assertIn("scripts.reproduce_publication", text)

    def test_readme_links_publication_documents(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/architecture.md", text)
        self.assertIn("docs/experiment-provenance.md", text)


if __name__ == "__main__":
    unittest.main()
