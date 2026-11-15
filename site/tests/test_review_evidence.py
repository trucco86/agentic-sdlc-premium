from pathlib import Path
import importlib.util
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("review_evidence", ROOT / "scripts/review_evidence.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ReviewEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / "content/reviews/demo-verifiable-specs-001.json").read_text())
    def test_demo_pending_is_valid_but_not_approved(self):
        self.assertEqual(mod.validate_record(self.record), [])
        self.assertEqual(self.record["status"], "draft")
    def test_missing_source_is_rejected(self):
        self.record["sources"] = []
        self.assertTrue(any("source" in e for e in mod.validate_record(self.record)))
    def test_http_source_is_rejected(self):
        self.record["sources"][0]["url"] = "http://example.org"
        self.assertTrue(any("HTTPS" in e for e in mod.validate_record(self.record)))
    def test_fake_reviewed_state_is_rejected(self):
        self.record["status"] = "reviewed"
        self.assertTrue(any("independent reviews" in e for e in mod.validate_record(self.record)))
    def test_self_approval_is_rejected(self):
        self.record["reviews"]["technical_reviewer"] = {
            "verdict": "pass", "reviewer": self.record["author"],
            "evidence_url": "https://github.com/example/repo/pull/1"
        }
        self.assertTrue(any("author cannot" in e for e in mod.validate_record(self.record)))
    def test_publication_authorization_is_rejected(self):
        self.record["publication_authorized"] = True
        self.assertTrue(any("publication cannot" in e for e in mod.validate_record(self.record)))
    def test_repository_review_records(self):
        self.assertEqual(mod.validate_directory(ROOT / "content/reviews"), [])

if __name__ == "__main__":
    unittest.main()
