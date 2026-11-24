import base64
import re
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
            doc.set_toc([[1, "Capítulo inicial", 1], [2, "Seção seguinte", 2]])
            doc.save(pdf)
            doc.close()
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "pages": 2}))
            build(pdf, manifest, root / "site")
            self.assertTrue((root / "site/index.html").exists())
            reader = (root / "site/index.html").read_text()
            self.assertEqual(reader.count('<section class="page"'), 2)
            self.assertLess(reader.index('id="p1"'), reader.index('id="p2"'))
            self.assertEqual(list((root / "site").glob("*.html")), [root / "site/index.html"])
            self.assertFalse(list((root / "site").glob("*.svg")))
            images = re.findall(r'src="data:image/svg\+xml;base64,([^"]+)"', reader)
            self.assertEqual(len(images), 2)
            self.assertIn("Segunda página", html.unescape(base64.b64decode(images[1]).decode()))
            self.assertIn('href="#p1"><span>Capítulo inicial', reader)
            self.assertIn('href="#p2"><span>Seção seguinte', reader)
            self.assertIn('href="#sumario"', reader)
            self.assertIn('id="back-toc" href="#sumario" hidden', reader)
            self.assertIn('id="sumario" aria-label="Sumário" tabindex="-1"', reader)
            self.assertIn('Voltar ao sumário', reader)
            self.assertIn('position:fixed', reader)
            self.assertIn('env(safe-area-inset-bottom)', reader)
            self.assertIn('toc.focus({preventScroll:true})', reader)
            self.assertIn('header,footer,.page-text,#sumario,#back-toc{display:none}', reader)
            self.assertIn("Primeira página", html.unescape(reader))
            self.assertIn("Segunda página", html.unescape(reader))
            self.assertNotIn('href="pagina-', reader)
            self.assertIn("@media print{body.text-mode .page img{display:block}", reader)

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
