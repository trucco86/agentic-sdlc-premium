import tempfile
import unittest
from pathlib import Path

import fitz

from scripts.review_images import render_review_pages


class ReviewImagesTests(unittest.TestCase):
    def test_renders_only_unique_valid_flagged_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf = root / "sample.pdf"
            doc = fitz.open()
            for _ in range(3):
                doc.new_page()
            doc.save(pdf)
            doc.close()

            qa = {"review_items": [
                {"page": 3, "reason": "layout"},
                {"page": 1, "reason": "layout"},
                {"page": 3, "reason": "duplicate"},
                {"page": 0, "reason": "invalid"},
                {"page": 4, "reason": "out of range"},
            ]}
            images = render_review_pages(pdf, qa, root / "review", limit=2, dpi=72)
            self.assertEqual([Path(item).name for item in images],
                             ["page-001.png", "page-003.png"])
            self.assertTrue(all(Path(item).is_file() for item in images))

    def test_no_review_items_produces_no_images(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf = root / "sample.pdf"
            doc = fitz.open()
            doc.new_page()
            doc.save(pdf)
            doc.close()
            self.assertEqual(render_review_pages(pdf, {"review_items": []},
                                                  root / "review"), [])


if __name__ == "__main__":
    unittest.main()
