#!/usr/bin/env python3
"""Read-only editorial gate report. A passing schema is never a publication approval."""
import argparse
import json
from pathlib import Path
from validate_content import validate as validate_content
from review_evidence import validate_directory

def build_report(content_root: Path):
    ledger_path = content_root / "lesson-ledger.json"
    errors = validate_content(content_root)
    errors += validate_directory(content_root / "reviews")
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        entries = ledger.get("entries", [])
    except (OSError, ValueError):
        entries = []
    records = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        lesson_id = item.get("lesson_id")
        review_path = content_root / "reviews" / (str(lesson_id) + ".json")
        if not review_path.exists():
            errors.append(f"{lesson_id}: missing review evidence record")
            review_status = "missing"
        else:
            try:
                review_status = json.loads(review_path.read_text(encoding="utf-8")).get("status", "unknown")
            except (OSError, ValueError):
                review_status = "invalid"
                errors.append(f"{lesson_id}: unreadable review evidence record")
        records.append({"lesson_id": lesson_id, "content_state": item.get("status"),
                        "review_state": review_status, "incorporated": item.get("incorporated") is True})
    return {"schema_checks": "fail" if errors else "pass",
            "editorial_decision": "blocked_pending_human_review",
            "publication_decision": "not_authorized",
            "lesson_count": len(records), "lessons": records, "errors": errors,
            "pending_actions": ["Independent source and technical review",
                                "Verified GitHub review identities and PR approvals",
                                "Explicit owner approval for merge",
                                "Separate explicit owner approval for public deployment"]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1] / "content")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report(args.root)
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output)
    return 1 if report["schema_checks"] == "fail" else 0

if __name__ == "__main__":
    raise SystemExit(main())
