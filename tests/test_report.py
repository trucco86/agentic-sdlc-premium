import unittest
from scripts.report import build_report

class ReportTests(unittest.TestCase):
    def test_report_pass_and_human_review(self):
        r=build_report({"pages":323,"bookmarks":54,"internal_links":28,
                        "critical_issues":[],"review_items":[{"page":27,"reason":"baixo preenchimento"}]},
                       {"source_filename":"test.pdf","drive_file_id":"sample"})
        self.assertIn("QA estrutural aprovado",r)
        self.assertIn("Pagina 27",r)
        self.assertIn("Nenhum arquivo e publicado automaticamente",r)

    def test_report_failure_does_not_claim_success(self):
        r=build_report({"pages":322,"bookmarks":54,"internal_links":28,
                        "critical_issues":["Pagina faltando"],"review_items":[]},{})
        self.assertIn("BLOQUEADO",r)
        self.assertIn("Pagina faltando",r)
        self.assertNotIn("Estado: **QA estrutural aprovado**",r)

if __name__=="__main__":
    unittest.main()
