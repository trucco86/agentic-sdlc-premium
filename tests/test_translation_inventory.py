import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import fitz
from scripts.translation_inventory import inventory

class InventoryTests(unittest.TestCase):
    def test_source_bound_units(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pdf = root / "source.pdf"
            with fitz.open() as doc:
                for text in ("Primeira", "Segunda"):
                    doc.new_page().insert_text((72,72), text)
                doc.save(pdf)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "pages": 2}))
            result = inventory(pdf, manifest)
            self.assertEqual([u["page"] for u in result["units"]], [1,2])
            self.assertIn("Segunda", result["units"][1]["source_text"])
            self.assertTrue(all(u["status"] == "pending" and u["visual_review_required"] for u in result["units"]))
            manifest.write_text(json.dumps({"sha256": "invalid", "pages": 2}))
            with self.assertRaises(ValueError):
                inventory(pdf, manifest)
