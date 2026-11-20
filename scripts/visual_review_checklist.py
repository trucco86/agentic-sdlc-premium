"""Produce a private, auditable checklist for human PDF page review."""
import argparse
import json
from pathlib import Path


def checklist(qa):
    grouped = {}
    for item in qa.get("review_items", []):
        page = int(item["page"])
        grouped.setdefault(page, []).append(item.get("reason", "review required"))
    lines = [
        "# Private PDF visual review checklist", "",
        "Status: PENDING HUMAN REVIEW. This document is not an approval.", "",
        f"Pages flagged: {len(grouped)}", "",
        "| Page | Automated finding | Human review |",
        "| --- | --- | --- |",
    ]
    for page in sorted(grouped):
        reasons = "; ".join(sorted(set(grouped[page]))).replace("|", "/")
        lines.append(f"| {page} | {reasons} | Pending |")
    lines.extend(["", "Review each flagged page for clipping, overlap, readability, diagrams and page breaks.",
                  "Approval must be recorded by a human reviewer in the PR."])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--qa", default="build/qa.json")
    parser.add_argument("--output", default="build/VISUAL_REVIEW_CHECKLIST.md")
    args = parser.parse_args()
    qa = json.loads(Path(args.qa).read_text(encoding="utf-8"))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(checklist(qa), encoding="utf-8")


if __name__ == "__main__":
    main()
