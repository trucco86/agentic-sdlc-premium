from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1] / "content"

class ContentIntegrityTests(unittest.TestCase):
    def test_ledger_references_exist_and_are_not_approved(self):
        ledger = json.loads((ROOT / "lesson-ledger.json").read_text(encoding="utf-8"))
        self.assertEqual(ledger["migration_status"], "not_started")
        ids = set()
        for entry in ledger["entries"]:
            lesson_id = entry["lesson_id"]
            self.assertNotIn(lesson_id, ids)
            ids.add(lesson_id)
            lesson = json.loads((ROOT / "lessons" / (lesson_id + ".json")).read_text(encoding="utf-8"))
            self.assertEqual(lesson["id"], lesson_id)
            self.assertFalse(entry["approved"])
            self.assertFalse(entry["incorporated"])
            self.assertFalse(lesson["attendance_verified"])
            for chapter_id in entry["chapter_ids"]:
                chapter = json.loads((ROOT / "chapters" / (chapter_id + ".json")).read_text(encoding="utf-8"))
                self.assertEqual(chapter["id"], chapter_id)
                self.assertIn(lesson_id, chapter["lessons"])
    def test_no_demo_content_masquerades_as_canonical(self):
        for path in (ROOT / "lessons").glob("*.json"):
            lesson = json.loads(path.read_text(encoding="utf-8"))
            if lesson["status"] == "demo":
                self.assertFalse(lesson["canonical"])
                self.assertFalse(lesson["approved"])
                self.assertEqual(lesson["source_kind"], "synthetic_demo")

if __name__ == "__main__":
    unittest.main()
