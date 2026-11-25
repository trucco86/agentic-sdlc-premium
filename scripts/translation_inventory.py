"""Generate deterministic page translation units; no external translation service."""
import argparse
import hashlib
import json
from pathlib import Path
import fitz

def inventory(source, manifest):
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    policy = json.loads(manifest.read_text(encoding="utf-8"))
    if digest != policy["sha256"]:
        raise ValueError("Canonical source checksum mismatch")
    with fitz.open(source) as doc:
        if len(doc) != policy["pages"]:
            raise ValueError("Canonical page count mismatch")
        units = []
        for i, page in enumerate(doc, 1):
            text = page.get_text(sort=True)
            units.append({"page": i, "source_text": text,
                          "source_text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                          "visual_review_required": True,
                          "status": "pending"})
        return {"source_sha256": digest, "source_language": "pt-BR",
                "target_language": "en", "units": units}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=Path("source/current.pdf"))
    p.add_argument("--manifest", type=Path, default=Path("editorial/source_manifest.json"))
    p.add_argument("--output", type=Path, default=Path("build/translation/inventory.json"))
    a = p.parse_args()
    result = inventory(a.source, a.manifest)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
