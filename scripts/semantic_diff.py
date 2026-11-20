"""Conservative PDF content preservation preflight; not editorial approval."""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import fitz


def normalize(text):
    return re.findall(r"\w+", text.casefold(), flags=re.UNICODE)


def extract(pdf):
    pages = []
    with fitz.open(pdf) as doc:
        for page in doc:
            images = Counter()
            for item in page.get_images(full=True):
                xref = item[0]
                image = doc.extract_image(xref)
                if image and image.get("image"):
                    images[hashlib.sha256(image["image"]).hexdigest()] += 1
            pages.append({
                "tokens": Counter(normalize(page.get_text())),
                "images": images,
                "drawings": len(page.get_drawings()),
            })
    return pages


def compare(baseline, candidate):
    before, after = extract(baseline), extract(candidate)
    issues = []
    if len(before) != len(after):
        issues.append(f"Page count changed: {len(before)} -> {len(after)}")
    for index, original in enumerate(before):
        if index >= len(after):
            issues.append(f"Page {index + 1}: missing from candidate")
            continue
        current = after[index]
        missing_tokens = original["tokens"] - current["tokens"]
        if missing_tokens:
            issues.append(f"Page {index + 1}: {sum(missing_tokens.values())} baseline tokens missing")
        missing_images = original["images"] - current["images"]
        if missing_images:
            issues.append(f"Page {index + 1}: {sum(missing_images.values())} embedded images removed or changed")
        if current["drawings"] < original["drawings"]:
            issues.append(f"Page {index + 1}: vector drawing count decreased: {original['drawings']} -> {current['drawings']}")
    return {
        "status": "failed" if issues else "passed",
        "baseline_pages": len(before), "candidate_pages": len(after),
        "issues": issues,
        "limitations": (
            "Checks per-page token counts, embedded image bytes and vector drawing counts only. "
            "Cannot prove meaning, rasterized vector preservation, placement, visual similarity, "
            "reading order or accessibility. Human review remains mandatory."
        ),
    }


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
