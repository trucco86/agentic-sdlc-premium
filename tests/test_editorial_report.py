import unittest

from scripts.report import build_report


class EditorialReportTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {"source_filename": "current.pdf", "drive_file_id": "private"}

    def test_critical_issue_is_reported_as_blocked(self):
        qa = {"pages": 323, "bookmarks": 54, "internal_links": 28,
              "critical_issues": ["Link interno invalido"], "review_items": []}
        report = build_report(qa, self.manifest)
        self.assertIn("**BLOQUEADO**", report)
        self.assertIn("Link interno invalido", report)
        self.assertIn("Falhas criticas: **1**", report)

    def test_structural_pass_does_not_claim_editorial_approval(self):
        qa = {"pages": 323, "bookmarks": 54, "internal_links": 28,
              "critical_issues": [], "review_items": [
                  {"page": 42, "reason": "baixa ocupacao vertical do texto"}]}
        report = build_report(qa, self.manifest)
        self.assertIn("QA estrutural aprovado", report)
        self.assertIn("Pagina 42", report)
        self.assertIn("nao substitui leitura ou aprovacao editorial", report)
        self.assertNotIn("**BLOQUEADO**", report)


if __name__ == "__main__":
    unittest.main()
