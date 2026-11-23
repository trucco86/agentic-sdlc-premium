import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release_decision", ROOT / "scripts/release_decision.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ReleaseDecisionTests(unittest.TestCase):
    def test_no_github_audit_blocks(self):
        result = mod.combine({"schema_checks":"pass","editorial_decision":"ready_for_human_approval"}, None)
        self.assertIn("github_review_audit_unavailable", result["blocking_reasons"])
        self.assertFalse(result["publication_authorized"])
    def test_even_approved_pr_does_not_publish(self):
        github = {"draft":True,"independent_approvals":2,"changes_requested_by":[]}
        result = mod.combine({"schema_checks":"pass","editorial_decision":"ready_for_human_approval"}, github)
        self.assertEqual(result["decision"], "blocked")
        self.assertFalse(result["merge_authorized"])
        self.assertIn("separate_publication_approval_missing", result["blocking_reasons"])
    def test_requested_changes_block(self):
        github = {"draft":True,"independent_approvals":1,"changes_requested_by":["reviewer"]}
        result = mod.combine({"schema_checks":"pass","editorial_decision":"ready_for_human_approval"}, github)
        self.assertIn("changes_requested", result["blocking_reasons"])
    def test_schema_failure_blocks(self):
        result = mod.combine({"schema_checks":"fail","editorial_decision":"blocked"}, {})
        self.assertIn("editorial_schema_failed", result["blocking_reasons"])

if __name__ == "__main__":
    unittest.main()
