#!/usr/bin/env python3
"""Validate editorial review evidence; no state transitions or publication."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

REQUIRED_ROLES = ("knowledge_curator", "technical_reviewer", "editorial_qa")
REVIEW_STATES = {"draft", "reviewed", "changes_requested"}
SOURCE_TYPES = {"official_docs", "standard", "research", "repository", "other"}

def nonempty(value):
    return isinstance(value, str) and bool(value.strip())

def https_url(value):
    if not nonempty(value):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username and not parsed.password

def validate_record(record):
    errors = []
    if not isinstance(record, dict):
        return ["record must be object"]
    lesson_id = record.get("lesson_id")
    if not nonempty(lesson_id):
        errors.append("lesson_id required")
    if record.get("status") not in REVIEW_STATES:
        errors.append("invalid review status")
    sources = record.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("at least one attributable source required")
    else:
        seen = set()
        for i, source in enumerate(sources):
            if not isinstance(source, dict):
                errors.append(f"sources[{i}] must be object")
                continue
            url = source.get("url")
            if not https_url(url):
                errors.append(f"sources[{i}] requires HTTPS URL")
            if url in seen:
                errors.append(f"sources[{i}] duplicate URL")
            seen.add(url)
            if source.get("type") not in SOURCE_TYPES:
                errors.append(f"sources[{i}] invalid type")
            for field in ("title", "claim", "accessed_at", "license_status"):
                if not nonempty(source.get(field)):
                    errors.append(f"sources[{i}] missing {field}")
            if source.get("license_status") not in {"cleared", "pending", "restricted"}:
                errors.append(f"sources[{i}] invalid license_status")
    reviews = record.get("reviews")
    if not isinstance(reviews, dict):
        errors.append("reviews must be object")
    else:
        reviewers = []
        for role in REQUIRED_ROLES:
            review = reviews.get(role)
            if not isinstance(review, dict):
                errors.append(f"missing {role} review")
                continue
            if review.get("verdict") not in {"pass", "changes_requested", "pending"}:
                errors.append(f"{role} invalid verdict")
            if review.get("verdict") == "pass":
                if not nonempty(review.get("reviewer")) or not https_url(review.get("evidence_url")):
                    errors.append(f"{role} pass requires reviewer and evidence URL")
                else:
                    reviewers.append(review["reviewer"].strip().lower())
        if len(reviewers) != len(set(reviewers)):
            errors.append("independent reviews must use different reviewers")
        author = record.get("author")
        if nonempty(author) and author.strip().lower() in reviewers:
            errors.append("author cannot approve own review")
    if record.get("status") == "reviewed":
        if not isinstance(reviews, dict) or any(
            not isinstance(reviews.get(role), dict) or reviews[role].get("verdict") != "pass"
            for role in REQUIRED_ROLES
        ):
            errors.append("reviewed status requires all independent reviews passing")
        if not isinstance(sources, list) or not sources or any(
            not isinstance(s, dict) or s.get("license_status") != "cleared" for s in sources
        ):
            errors.append("reviewed status requires all source licenses cleared")
    if record.get("publication_authorized") is True:
        errors.append("publication cannot be authorized by content evidence file")
    return errors

def validate_directory(path):
    errors = []
    for file in sorted(path.glob("*.json")):
        try:
            record = json.loads(file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(f"{file.name}: {exc}")
            continue
        errors.extend(f"{file.name}: {error}" for error in validate_record(record))
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1] / "content" / "reviews")
    args = parser.parse_args()
    errors = validate_directory(args.root)
    print(json.dumps({"status": "blocked" if errors else "pass", "errors": errors,
                      "checks": "review_evidence_v1"}, ensure_ascii=False, indent=2))
    return bool(errors)

if __name__ == "__main__":
    raise SystemExit(main())
