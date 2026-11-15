import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("editorial_report", ROOT / "scripts/editorial_report.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class EditorialReportTests(unittest.TestCase):
    def test_repository_report_blocks_publication(self):
        report = module.build_report(ROOT / "content")
        self.assertEqual(report["schema_checks"], "pass")
        self.assertEqual(report["publication_decision"], "not_authorized")
        self.assertEqual(report["editorial_decision"], "blocked_pending_human_review")
        self.assertGreater(report["lesson_count"], 0)
        self.assertFalse(any(lesson["incorporated"] for lesson in report["lessons"]))
    def test_missing_review_record_blocks_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "lessons").mkdir()
            (root / "chapters").mkdir()
            (root / "reviews").mkdir()
            (root / "lesson-ledger.json").write_text(json.dumps({"entries":[{
                "lesson_id":"demo-001","chapter_ids":["chapter-001"],"status":"demo",
                "approved":False,"incorporated":False,"source_run_id":None
            }]}))
            (root / "lessons/demo-001.json").write_text(json.dumps({
                "id":"demo-001","chapter_ids":["chapter-001"],"status":"demo",
                "canonical":False,"approved":False,"source_kind":"synthetic_demo"
            }))
            (root / "chapters/chapter-001.json").write_text(json.dumps({
                "id":"chapter-001","lessons":["demo-001"]
            }))
            report = module.build_report(root)
            self.assertEqual(report["schema_checks"], "fail")
            self.assertTrue(any("missing review evidence" in error for error in report["errors"]))
            self.assertEqual(report["publication_decision"], "not_authorized")

if __name__ == "__main__":
    unittest.main()
