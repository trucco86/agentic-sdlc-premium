#!/usr/bin/env python3
"""Consolidate offline editorial and live GitHub audit; never authorize release."""
import argparse
import json
from pathlib import Path

def combine(editorial, github):
    reasons = []
    if editorial.get("schema_checks") != "pass":
        reasons.append("editorial_schema_failed")
    if github is None:
        reasons.append("github_review_audit_unavailable")
    else:
        if github.get("draft") is not True:
            reasons.append("draft_status_changed_requires_owner_decision")
        if github.get("changes_requested_by"):
            reasons.append("changes_requested")
        if github.get("independent_approvals", 0) < 1:
            reasons.append("independent_github_approval_missing")
    if editorial.get("editorial_decision") != "ready_for_human_approval":
        reasons.append("editorial_human_review_pending")
    reasons.extend(["explicit_merge_approval_missing", "separate_publication_approval_missing"])
    return {
        "decision": "blocked",
        "merge_authorized": False,
        "publication_authorized": False,
        "editorial_schema_checks": editorial.get("schema_checks", "unknown"),
        "github_audit_available": github is not None,
        "blocking_reasons": reasons,
        "note": "Audit only. Human approvals cannot be inferred from files or PR review events."
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--editorial", type=Path, required=True)
    parser.add_argument("--github", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    editorial = json.loads(args.editorial.read_text(encoding="utf-8"))
    github = json.loads(args.github.read_text(encoding="utf-8")) if args.github and args.github.exists() else None
    report = combine(editorial, github)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
