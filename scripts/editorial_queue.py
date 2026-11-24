"""Deterministic editorial task planner. Does not execute LLM calls."""
import hashlib
import json
import argparse
from pathlib import Path

def plan(inventory, edition):
    current = edition.get("source_sha256") == inventory["source_sha256"] and edition.get("language") == "en"
    records = {u["page"]: u for u in edition.get("units", [])} if current else {}
    tasks = []
    for source in inventory["units"]:
        page = source["page"]
        target = records.get(page, {})
        content = target.get("translated_text")
        if not target.get("author") or target.get("source_text_sha256") != source["source_text_sha256"] or not isinstance(content, str) or (source["source_text"].strip() and not content.strip()):
            tasks.append({"page":page,"agent":"translation","source_text_sha256":source["source_text_sha256"]})
            continue
        digest = hashlib.sha256(content.encode()).hexdigest()
        reviews = target.get("reviews", {})
        for role in ("technical","editorial","visual"):
            review = reviews.get(role, {})
            independent = role != "editorial" or review.get("reviewer") != reviews.get("technical", {}).get("reviewer")
            if review.get("decision") != "approved" or not review.get("reviewer") or review.get("translation_sha256") != digest or not independent or review.get("reviewer") == target["author"] or review.get("source_sha256") != inventory["source_sha256"] or review.get("source_text_sha256") != source["source_text_sha256"]:
                tasks.append({"page":page,"agent":role,"translation_sha256":digest})
                break
    return tasks

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("inventory", type=Path)
    p.add_argument("edition", type=Path)
    p.add_argument("--limit", type=int, default=10)
    a = p.parse_args()
    if a.limit < 1:
        p.error("limit must be positive")
    tasks = plan(json.loads(a.inventory.read_text()), json.loads(a.edition.read_text()))
    print(json.dumps({"remaining":len(tasks),"tasks":tasks[:a.limit]},indent=2))
