import tempfile
import unittest
from pathlib import Path

import fitz
from scripts.semantic_diff import compare, normalize


def make_pdf(path, pages, with_drawing=False):
    with fitz.open() as doc:
        for text in pages:
            page = doc.new_page()
            page.insert_text((72, 72), text)
            if with_drawing:
                page.draw_rect(fitz.Rect(100, 100, 150, 150))
        doc.save(path)


class SemanticPreservationTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(normalize("Hello, WORLD!"), ["hello", "world"])

    def test_unchanged_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.pdf", Path(tmp) / "b.pdf"
            make_pdf(a, ["One two three"])
            make_pdf(b, ["One two three"])
            self.assertEqual(compare(a, b)["status"], "passed")

    def test_removed_words_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.pdf", Path(tmp) / "b.pdf"
            make_pdf(a, ["One two three"])
            make_pdf(b, ["One two"])
            self.assertEqual(compare(a, b)["status"], "failed")

    def test_missing_page_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.pdf", Path(tmp) / "b.pdf"
            make_pdf(a, ["First", "Second"])
            make_pdf(b, ["First"])
            self.assertEqual(compare(a, b)["status"], "failed")

    def test_removed_vector_drawing_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.pdf", Path(tmp) / "b.pdf"
            make_pdf(a, ["Diagram"], with_drawing=True)
            make_pdf(b, ["Diagram"])
            result = compare(a, b)
            self.assertEqual(result["status"], "failed")
            self.assertTrue(any("vector drawing" in issue for issue in result["issues"]))

    def test_unchanged_vector_drawing_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.pdf", Path(tmp) / "b.pdf"
            make_pdf(a, ["Diagram"], with_drawing=True)
            make_pdf(b, ["Diagram"], with_drawing=True)
            self.assertEqual(compare(a, b)["status"], "passed")


if __name__ == "__main__":
    unittest.main()
