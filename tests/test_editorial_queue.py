import copy
import hashlib
import unittest

from scripts.editorial_queue import plan


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.inventory = {
            "source_sha256": "s",
            "units": [{"page": 1, "source_text": "Olá", "source_text_sha256": "p"}],
        }
        digest = hashlib.sha256(b"Hello").hexdigest()
        self.unit = {
            "page": 1,
            "source_text_sha256": "p",
            "translated_text": "Hello",
            "author": "translator",
            "reviews": {
                role: {
                    "decision": "approved",
                    "reviewer": reviewer,
                    "translation_sha256": digest,
                    "source_sha256": "s",
                    "source_text_sha256": "p",
                }
                for role, reviewer in (
                    ("technical", "technical-reviewer"),
                    ("editorial", "editorial-reviewer"),
                    ("visual", "visual-reviewer"),
                )
            },
        }
        self.edition = {"source_sha256": "s", "language": "en", "units": [self.unit]}

    def test_translation_and_review_order(self):
        edition = {"source_sha256": "s", "language": "en", "units": []}
        self.assertEqual(plan(self.inventory, edition)[0]["agent"], "translation")
        unit = copy.deepcopy(self.unit)
        edition["units"] = [unit]
        self.assertEqual(plan(self.inventory, edition), [])
        unit["translated_text"] = "Hi"
        self.assertEqual(plan(self.inventory, edition)[0]["agent"], "technical")

    def test_queue_reopens_author_self_review(self):
        edition = copy.deepcopy(self.edition)
        edition["units"][0]["reviews"]["technical"]["reviewer"] = "translator"
        self.assertEqual(plan(self.inventory, edition)[0]["agent"], "technical")

    def test_queue_reopens_approval_after_source_revision_changes(self):
        inventory = copy.deepcopy(self.inventory)
        inventory["source_sha256"] = "s-v2"
        inventory["units"][0]["source_text_sha256"] = "p-v2"
        edition = copy.deepcopy(self.edition)
        edition["source_sha256"] = "s-v2"
        edition["units"][0]["source_text_sha256"] = "p-v2"
        self.assertEqual(plan(inventory, edition)[0]["agent"], "technical")

    def test_stale_edition_restarts_translation(self):
        edition = copy.deepcopy(self.edition)
        edition["source_sha256"] = "old"
        self.assertEqual(plan(self.inventory, edition)[0]["agent"], "translation")


if __name__ == "__main__":
    unittest.main()
