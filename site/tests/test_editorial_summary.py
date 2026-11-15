import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("editorial_summary", ROOT / "scripts/editorial_summary.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class EditorialSummaryTests(unittest.TestCase):
    def test_summary_does_not_imply_approval(self):
        editorial = {"schema_checks":"pass","lesson_count":1,"lessons":[{"lesson_id":"demo-1","content_state":"demo","review_state":"draft"}]}
        github = {"pr_number":3,"head_sha":"abc","independent_approvals":2,"changes_requested_by":[]}
        release = {"decision":"blocked","blocking_reasons":["explicit_merge_approval_missing"]}
        result = mod.render(editorial, github, release)
        self.assertIn("Merge autorizado: não", result)
        self.assertIn("Publicação autorizada: não", result)
        self.assertIn("demo-1", result)
        self.assertIn("explicit_merge_approval_missing", result)
    def test_missing_github_audit_is_visible(self):
        result = mod.render({"schema_checks":"pass","lesson_count":0}, None, {"decision":"blocked","blocking_reasons":[]})
        self.assertIn("Sem dados verificados", result)

if __name__ == "__main__":
    unittest.main()
