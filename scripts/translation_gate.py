"""Validate translation coverage and explicit review records before publication."""
import hashlib
import json
import argparse
from pathlib import Path

def validate(inventory, edition):
    if edition.get("source_sha256") != inventory["source_sha256"]:
        raise ValueError("Stale translation source")
    if edition.get("language") != "en":
        raise ValueError("Expected English edition")
    units = inventory["units"]
    translated = edition.get("units", [])
    if [u.get("page") for u in translated] != [u["page"] for u in units]:
        raise ValueError("Incomplete or unordered translation coverage")
    for source, target in zip(units, translated):
        if target.get("source_text_sha256") != source["source_text_sha256"]:
            raise ValueError(f"Stale page {source['page']}")
        content = target.get("translated_text", "")
        if not isinstance(content, str) or (source["source_text"].strip() and not content.strip()):
            raise ValueError(f"Missing translation on page {source['page']}")
        author = target.get("author")
        if not author:
            raise ValueError("Translation author required")
        digest = hashlib.sha256(content.encode()).hexdigest()
        for role in ("technical", "editorial", "visual"):
            review = target.get("reviews", {}).get(role, {})
            if review.get("decision") != "approved" or not review.get("reviewer") or review.get("translation_sha256") != digest or review.get("source_sha256") != inventory["source_sha256"] or review.get("source_text_sha256") != source["source_text_sha256"] or review.get("reviewer") == author:
                raise ValueError(f"Missing current {role} review on page {source['page']}")
        if target["reviews"]["technical"]["reviewer"] == target["reviews"]["editorial"]["reviewer"]:
            raise ValueError("Independent review required")
    return len(units)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("inventory", type=Path)
    parser.add_argument("edition", type=Path)
    args = parser.parse_args()
    print("Approved page records:", validate(json.loads(args.inventory.read_text()), json.loads(args.edition.read_text())))
