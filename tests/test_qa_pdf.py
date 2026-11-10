import tempfile
import unittest
from pathlib import Path
import fitz
from scripts.qa_pdf import inspect

class PdfGateTests(unittest.TestCase):
    def test_valid_minimal_pdf(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"sample.pdf"
            doc=fitz.open()
            page=doc.new_page()
            page.insert_text((72,72),"Apostila editorial")
            doc.save(path)
            doc.close()
            result=inspect(path,{"minimum_pages":1,"expected_bookmarks":0,"expected_internal_links":0})
            self.assertEqual(result["status"],"passed")
            self.assertEqual(result["pages"],1)

    def test_missing_bookmarks_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"sample.pdf"
            doc=fitz.open()
            doc.new_page().insert_text((72,72),"Apostila editorial")
            doc.save(path)
            doc.close()
            result=inspect(path,{"minimum_pages":1,"expected_bookmarks":2,"expected_internal_links":0})
            self.assertEqual(result["status"],"failed")
            self.assertTrue(any("Marcadores" in issue for issue in result["critical_issues"]))

if __name__=="__main__":
    unittest.main()
