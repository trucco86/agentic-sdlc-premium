import unittest
from scripts.visual_review_checklist import checklist


class VisualReviewChecklistTests(unittest.TestCase):
    def test_deduplicates_and_sorts_pages(self):
        result = checklist({"review_items": [
            {"page": 14, "reason": "low occupation"},
            {"page": 3, "reason": "visual only"},
            {"page": 14, "reason": "low occupation"},
        ]})
        self.assertIn("Pages flagged: 2", result)
        self.assertLess(result.index("| 3 |"), result.index("| 14 |"))
        self.assertIn("Pending", result)

    def test_empty_list_does_not_claim_approval(self):
        result = checklist({"review_items": []})
        self.assertIn("Pages flagged: 0", result)
        self.assertIn("PENDING HUMAN REVIEW", result)


if __name__ == "__main__":
    unittest.main()
