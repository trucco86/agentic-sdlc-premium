import copy
import hashlib
import unittest
from scripts.translation_gate import validate

class TranslationGateTests(unittest.TestCase):
    def test_gate(self):
        inventory = {"source_sha256":"source","units":[{"page":1,"source_text":"Olá","source_text_sha256":"original"}]}
        digest = hashlib.sha256(b"Hello").hexdigest()
        edition = {"source_sha256":"source","language":"en","units":[{"page":1,"source_text_sha256":"original","translated_text":"Hello","reviews":{r:{"decision":"approved","reviewer":r,"translation_sha256":digest} for r in ("technical","editorial","visual")}}]}
        self.assertEqual(validate(inventory, edition),1)
        for mutation in ("missing","stale","edited","review"):
            bad = copy.deepcopy(edition)
            if mutation == "missing": bad["units"] = []
            elif mutation == "stale": bad["source_sha256"] = "old"
            elif mutation == "edited": bad["units"][0]["translated_text"] = "Changed"
            else: del bad["units"][0]["reviews"]["visual"]
            with self.assertRaises(ValueError): validate(inventory,bad)
