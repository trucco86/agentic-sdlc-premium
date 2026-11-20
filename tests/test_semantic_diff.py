import tempfile
import unittest
from pathlib import Path

import fitz
from scripts.semantic_diff import compare, normalize


def make_pdf(path, pages):
    with fitz.open() as doc:
        for text in pages:
            doc.new_page().insert_text((72, 72), text)
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


if __name__ == "__main__":
    unittest.main()
