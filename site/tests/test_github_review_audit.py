import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("github_review_audit", ROOT / "scripts/github_review_audit.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class GithubReviewAuditTests(unittest.TestCase):
    def setUp(self):
        self.pr = {"number": 3, "draft": True, "user": {"login": "owner"},
                   "head": {"sha": "abc123"}}
    def test_no_reviews_blocks(self):
        result = mod.audit(self.pr, [])
        self.assertEqual(result["independent_approvals"], 0)
        self.assertFalse(result["merge_authorized"])
        self.assertFalse(result["publish_authorized"])
    def test_author_approval_does_not_count(self):
        reviews = [{"user":{"login":"owner"},"state":"APPROVED","submitted_at":"2026-11-15T00:00:00Z"}]
        self.assertEqual(mod.audit(self.pr, reviews)["independent_approvals"], 0)
    def test_latest_change_request_supersedes_approval(self):
        reviews = [
            {"user":{"login":"reviewer"},"state":"APPROVED","submitted_at":"2026-11-15T00:00:00Z"},
            {"user":{"login":"reviewer"},"state":"CHANGES_REQUESTED","submitted_at":"2026-11-15T01:00:00Z"}
        ]
        result = mod.audit(self.pr, reviews)
        self.assertEqual(result["independent_approvals"], 0)
        self.assertEqual(result["changes_requested_by"], ["reviewer"])
    def test_approval_is_not_publication_authorization(self):
        reviews = [{"user":{"login":"reviewer"},"state":"APPROVED","submitted_at":"2026-11-15T00:00:00Z"}]
        result = mod.audit(self.pr, reviews)
        self.assertEqual(result["independent_approvals"], 1)
        self.assertFalse(result["human_release_authorized"])
        self.assertFalse(result["publish_authorized"])

if __name__ == "__main__":
    unittest.main()
