import hashlib
import html
import json
import tempfile
import unittest
from pathlib import Path

import fitz

from scripts.build_full_html import build


class FullHtmlTests(unittest.TestCase):
    def test_all_pages_and_navigation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pdf = root / "source.pdf"
            doc = fitz.open()
            for text in ("Primeira página", "Segunda página"):
                page = doc.new_page()
                page.insert_text((72, 72), text)
            doc.save(pdf)
            doc.close()
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "pages": 2}))
            build(pdf, manifest, root / "site")
            self.assertTrue((root / "site/index.html").exists())
            self.assertTrue((root / "site/pagina-002.html").exists())
            self.assertIn("Segunda página", html.unescape((root / "site/pagina-002.html").read_text()))
            self.assertIn("pagina-002.html", (root / "site/index.html").read_text())

    def test_rejects_modified_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pdf = root / "source.pdf"
            doc = fitz.open()
            doc.new_page()
            doc.save(pdf)
            doc.close()
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"sha256": "bad", "pages": 1}))
            with self.assertRaisesRegex(ValueError, "checksum"):
                build(pdf, manifest, root / "site")


if __name__ == "__main__":
    unittest.main()
