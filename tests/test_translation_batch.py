import unittest

from scripts.translation_batch import prepare_batch


def inventory(count=30):
    return {
        "source_sha256": "source-v1",
        "units": [
            {"page": page, "source_text": f"Texto {page}", "source_text_sha256": f"hash-{page}"}
            for page in range(1, count + 1)
        ],
    }


class TranslationBatchTests(unittest.TestCase):
    def test_empty_edition_starts_with_first_25_translation_pages(self):
        source = inventory()
        result = prepare_batch(source, {"source_sha256": "source-v1", "language": "en", "units": []})
        self.assertEqual([unit["page"] for unit in result["translation_units"]], list(range(1, 26)))
        self.assertEqual(len(result["translation_tasks"]), 25)
        self.assertEqual(result["translation_remaining"], 30)
        self.assertEqual(result["review_backlog"], [])
        self.assertEqual(result["review_remaining"], 0)

    def test_existing_drafts_do_not_displace_missing_translation_pages(self):
        source = inventory()
        edition = {
            "source_sha256": "source-v1",
            "language": "en",
            "units": [
                {
                    "page": page,
                    "source_text_sha256": f"hash-{page}",
                    "translated_text": f"Translation {page}",
                    "author": "translator",
                    "reviews": {},
                }
                for page in (1, 2)
            ],
        }
        result = prepare_batch(source, edition)
        self.assertEqual([unit["page"] for unit in result["translation_units"]], list(range(3, 28)))
        self.assertEqual([task["page"] for task in result["review_backlog"]], [1, 2])
        self.assertEqual(result["translation_remaining"], 28)
        self.assertEqual(result["review_remaining"], 2)

    def test_rejects_duplicate_and_unknown_translation_pages(self):
        source = inventory(2)
        base = {"source_sha256": "source-v1", "language": "en"}
        duplicate = dict(base, units=[{"page": 1}, {"page": 1}])
        unknown = dict(base, units=[{"page": 3}])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            prepare_batch(source, duplicate)
        with self.assertRaisesRegex(ValueError, "absent"):
            prepare_batch(source, unknown)

    def test_rejects_non_positive_limit(self):
        with self.assertRaisesRegex(ValueError, "positive"):
            prepare_batch(inventory(), {"source_sha256": "source-v1", "language": "en", "units": []}, 0)


if __name__ == "__main__":
    unittest.main()
