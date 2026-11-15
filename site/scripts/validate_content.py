#!/usr/bin/env python3
"""Offline editorial integrity gate. Never publishes or modifies content."""
import argparse
import json
from pathlib import Path

STATES = {"demo", "proposed", "researched", "drafted", "technical_review",
          "editorial_review", "ready_for_human_approval", "approved",
          "incorporated", "published", "blocked"}

def validate(root: Path):
    errors = []
    ledger_path = root / "lesson-ledger.json"
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"ledger: {exc}"]
    entries = ledger.get("entries")
    if not isinstance(entries, list):
        return ["ledger.entries must be an array"]
    seen = set()
    for n, item in enumerate(entries):
        prefix = f"entries[{n}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        lesson_id = item.get("lesson_id")
        if not isinstance(lesson_id, str) or not lesson_id or not all(
            c.islower() or c.isdigit() or c == "-" for c in lesson_id
        ):
            errors.append(f"{prefix}: invalid lesson_id")
            continue
        if lesson_id in seen:
            errors.append(f"{prefix}: duplicate lesson_id {lesson_id}")
        seen.add(lesson_id)
        lesson_path = root / "lessons" / (lesson_id + ".json")
        try:
            lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(f"{prefix}: lesson unavailable: {exc}")
            continue
        if lesson.get("id") != lesson_id:
            errors.append(f"{prefix}: lesson id mismatch")
        status = item.get("status")
        if status not in STATES or lesson.get("status") not in STATES:
            errors.append(f"{prefix}: invalid state")
        if lesson.get("status") != status:
            errors.append(f"{prefix}: ledger/lesson state mismatch")
        chapters = item.get("chapter_ids")
        if not isinstance(chapters, list) or not chapters:
            errors.append(f"{prefix}: chapter_ids required")
            continue
        if lesson.get("chapter_ids") != chapters:
            errors.append(f"{prefix}: chapter references mismatch")
        for chapter_id in chapters:
            if not isinstance(chapter_id, str) or not chapter_id or "/" in chapter_id or ".." in chapter_id:
                errors.append(f"{prefix}: invalid chapter_id")
                continue
            try:
                chapter = json.loads((root / "chapters" / (chapter_id + ".json")).read_text(encoding="utf-8"))
                if chapter.get("id") != chapter_id or lesson_id not in chapter.get("lessons", []):
                    errors.append(f"{prefix}: chapter backlink missing: {chapter_id}")
            except (OSError, ValueError) as exc:
                errors.append(f"{prefix}: chapter unavailable: {exc}")
        approved = item.get("approved")
        incorporated = item.get("incorporated")
        if type(approved) is not bool or type(incorporated) is not bool:
            errors.append(f"{prefix}: approved/incorporated must be booleans")
        if status == "demo":
            if approved or incorporated or lesson.get("canonical") or lesson.get("approved"):
                errors.append(f"{prefix}: demo content cannot be approved or canonical")
            if lesson.get("source_kind") != "synthetic_demo":
                errors.append(f"{prefix}: demo must identify synthetic origin")
        if approved or incorporated or status in {"approved", "incorporated", "published"}:
            errors.append(f"{prefix}: promotion requires independent human evidence gate (not enabled)")
        if item.get("source_run_id") is not None and not isinstance(item["source_run_id"], str):
            errors.append(f"{prefix}: source_run_id must be string or null")
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1] / "content")
    args = parser.parse_args()
    errors = validate(args.root)
    print(json.dumps({"status": "blocked" if errors else "pass",
                      "errors": errors, "checks": "editorial_integrity_v1"},
                     ensure_ascii=False, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
