import hashlib
import unittest
from scripts.editorial_queue import plan

class QueueTests(unittest.TestCase):
    def test_order(self):
        inv = {"source_sha256":"s","units":[{"page":1,"source_text":"Olá","source_text_sha256":"p"}]}
        edition = {"source_sha256":"s","language":"en","units":[]}
        self.assertEqual(plan(inv,edition)[0]["agent"],"translation")
        unit = {"page":1,"source_text_sha256":"p","translated_text":"Hello","author":"translator","reviews":{}}
        edition["units"] = [unit]
        for role in ("technical","editorial","visual"):
            self.assertEqual(plan(inv,edition)[0]["agent"],role)
            unit["reviews"][role] = {"decision":"approved","reviewer":role,"translation_sha256":hashlib.sha256(b"Hello").hexdigest(),"source_sha256":"s","source_text_sha256":"p"}
        self.assertEqual(plan(inv,edition),[])
        unit["translated_text"] = "Hi"
        self.assertEqual(plan(inv,edition)[0]["agent"],"technical")
        edition["source_sha256"] = "old"
        self.assertEqual(plan(inv,edition)[0]["agent"],"translation")
