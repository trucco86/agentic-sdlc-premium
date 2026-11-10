import json
import unittest
from pathlib import Path

class ManifestTests(unittest.TestCase):
    def test_source_manifest_has_required_provenance(self):
        root = Path(__file__).resolve().parents[1]
        m = json.loads((root/"editorial/source_manifest.json").read_text())
        self.assertEqual(m["pages"],323)
        self.assertEqual(len(m["sha256"]),64)
        self.assertTrue(m["drive_file_id"])
        self.assertEqual(m["source_status"],"private_preview_not_published")

    def test_public_release_is_disabled(self):
        root = Path(__file__).resolve().parents[1]
        p = json.loads((root/"editorial/policy.json").read_text())
        self.assertTrue(p["public_release_requires_explicit_approval"])

if __name__=="__main__":
    unittest.main()
