import copy
import hashlib
import unittest

from scripts.translation_gate import validate


class TranslationGateTests(unittest.TestCase):
    def setUp(self):
        self.inventory = {
            "source_sha256": "source",
            "units": [{"page": 1, "source_text": "Olá", "source_text_sha256": "original"}],
        }
        digest = hashlib.sha256(b"Hello").hexdigest()
        self.edition = {
            "source_sha256": "source",
            "language": "en",
            "units": [{
                "page": 1,
                "source_text_sha256": "original",
                "translated_text": "Hello",
                "author": "translator",
                "reviews": {
                    role: {
                        "decision": "approved",
                        "reviewer": reviewer,
                        "translation_sha256": digest,
                        "source_sha256": "source",
                        "source_text_sha256": "original",
                    }
                    for role, reviewer in (
                        ("technical", "technical-reviewer"),
                        ("editorial", "editorial-reviewer"),
                        ("visual", "visual-reviewer"),
                    )
                },
            }],
        }

    def test_gate_accepts_complete_independent_current_reviews(self):
        self.assertEqual(validate(self.inventory, self.edition), 1)

    def test_gate_rejects_missing_stale_or_self_approved_records(self):
        mutations = ("missing", "stale_edition", "edited_translation",
                     "missing_visual_review", "author_self_review",
                     "stale_source_revision", "same_technical_and_editorial_reviewer",
                     "missing_author")
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                bad = copy.deepcopy(self.edition)
                if mutation == "missing":
                    bad["units"] = []
                elif mutation == "stale_edition":
                    bad["source_sha256"] = "old"
                elif mutation == "edited_translation":
                    bad["units"][0]["translated_text"] = "Changed"
                elif mutation == "missing_visual_review":
                    del bad["units"][0]["reviews"]["visual"]
                elif mutation == "author_self_review":
                    bad["units"][0]["reviews"]["technical"]["reviewer"] = "translator"
                elif mutation == "stale_source_revision":
                    bad["units"][0]["reviews"]["technical"]["source_text_sha256"] = "old"
                elif mutation == "same_technical_and_editorial_reviewer":
                    bad["units"][0]["reviews"]["editorial"]["reviewer"] = "technical-reviewer"
                elif mutation == "missing_author":
                    bad["units"][0]["author"] = ""
                with self.assertRaises(ValueError):
                    validate(self.inventory, bad)

    def test_gate_invalidates_approval_after_source_page_changes(self):
        changed_inventory = copy.deepcopy(self.inventory)
        changed_inventory["source_sha256"] = "source-v2"
        changed_inventory["units"][0]["source_text_sha256"] = "original-v2"
        changed_edition = copy.deepcopy(self.edition)
        changed_edition["source_sha256"] = "source-v2"
        changed_edition["units"][0]["source_text_sha256"] = "original-v2"
        with self.assertRaises(ValueError):
            validate(changed_inventory, changed_edition)


if __name__ == "__main__":
    unittest.main()
