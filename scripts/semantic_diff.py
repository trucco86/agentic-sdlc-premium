"""Fail-closed semantic preservation check for PDF revisions.

Compares normalized per-page text and reports removed content. This is a
conservative preflight, not a replacement for human visual review.
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

import fitz


def normalize(text):
    return re.findall(r"\w+", text.casefold(), flags=re.UNICODE)


def extract(pdf):
    with fitz.open(pdf) as doc:
        return [normalize(page.get_text()) for page in doc]


def compare(baseline, candidate):
    before = extract(baseline)
    after = extract(candidate)
    issues = []
    if len(before) != len(after):
        issues.append(f"Page count changed: {len(before)} -> {len(after)}")
    for index, original in enumerate(before):
        if index >= len(after):
            issues.append(f"Page {index + 1}: missing from candidate")
            continue
        removed = Counter(original) - Counter(after[index])
        if removed:
            issues.append(f"Page {index + 1}: {sum(removed.values())} baseline tokens missing")
    return {"status": "failed" if issues else "passed", "baseline_pages": len(before),
            "candidate_pages": len(after), "issues": issues,
            "limitations": "Per-page token preservation only; visual layout, diagrams, reading order and moved text require human review."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline")
    parser.add_argument("candidate")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = compare(args.baseline, args.candidate)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    print(payload)
    return 1 if result["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
