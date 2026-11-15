from pathlib import Path
import importlib.util
import json
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validate_content", ROOT / "scripts" / "validate_content.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class EditorialGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "lessons").mkdir()
        (self.root / "chapters").mkdir()
        self.entry = {"lesson_id":"demo-001","chapter_ids":["foundations"],"status":"demo",
                      "approved":False,"incorporated":False,"source_run_id":None}
        self.lesson = {"id":"demo-001","chapter_ids":["foundations"],"status":"demo",
                       "canonical":False,"approved":False,"source_kind":"synthetic_demo"}
        self.chapter = {"id":"foundations","lessons":["demo-001"]}
        self.save()
    def save(self):
        (self.root / "lesson-ledger.json").write_text(json.dumps({"entries":[self.entry]}))
        (self.root / "lessons/demo-001.json").write_text(json.dumps(self.lesson))
        (self.root / "chapters/foundations.json").write_text(json.dumps(self.chapter))
    def test_valid_demo(self):
        self.assertEqual(module.validate(self.root), [])
    def test_blocks_unreviewed_promotion(self):
        self.entry["approved"] = True
        self.entry["incorporated"] = True
        self.save()
        self.assertTrue(any("promotion requires" in e for e in module.validate(self.root)))
    def test_blocks_missing_chapter(self):
        (self.root / "chapters/foundations.json").unlink()
        self.assertTrue(any("chapter unavailable" in e for e in module.validate(self.root)))
    def test_blocks_duplicate_id(self):
        (self.root / "lesson-ledger.json").write_text(json.dumps({"entries":[self.entry,self.entry]}))
        self.assertTrue(any("duplicate lesson_id" in e for e in module.validate(self.root)))
    def test_blocks_ledger_state_mismatch(self):
        self.entry["status"] = "drafted"
        self.save()
        self.assertTrue(any("state mismatch" in e for e in module.validate(self.root)))
    def test_current_repository_content(self):
        self.assertEqual(module.validate(ROOT / "content"), [])

if __name__ == "__main__":
    unittest.main()
