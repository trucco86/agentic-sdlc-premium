#!/usr/bin/env python3
"""PDF preflight: machine-checkable integrity plus non-blocking layout triage."""
import argparse
import json
from pathlib import Path
import fitz

def inspect(pdf, policy):
    doc = fitz.open(pdf)
    critical = []
    review = []
    page_count = len(doc)
    if page_count < policy.get("minimum_pages", 1):
        critical.append("PDF sem paginas suficientes")
    expected = policy.get("expected_page_count")
    if expected is not None and page_count != expected:
        critical.append(f"Contagem divergente: {page_count} vs {expected}")
    toc = doc.get_toc()
    if len(toc) < policy.get("expected_bookmarks", 0):
        critical.append("Marcadores abaixo da linha de base")
    internal_links = 0
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        drawings = len(page.get_drawings())
        images = len(page.get_images())
        if not text and drawings == 0 and images == 0:
            critical.append(f"Pagina fisicamente vazia: {i+1}")
        elif not text:
            review.append({"page": i+1, "reason": "conteudo apenas visual; conferir manualmente"})
        blocks = [b for b in page.get_text("blocks") if b[4].strip() and len(b[4].strip()) > 15]
        if i+1 not in policy.get("layout_exempt_pages", []) and blocks and len(text) >= 250:
            occupied = (max(b[3] for b in blocks) - min(b[1] for b in blocks)) / page.rect.height
            if occupied < policy.get("min_text_occupation_ratio", 0.4):
                review.append({"page": i+1, "reason": "baixa ocupacao vertical do texto", "ratio": round(occupied, 3)})
        for link in page.get_links():
            if link.get("kind") == fitz.LINK_GOTO:
                internal_links += 1
                dest = link.get("page", -1)
                if not isinstance(dest, int) or not 0 <= dest < page_count:
                    critical.append(f"Link interno invalido na pagina {i+1}")
    if internal_links < policy.get("expected_internal_links", 0):
        critical.append("Links internos abaixo da linha de base")
    result = {"pdf": str(pdf), "pages": page_count, "bookmarks": len(toc),
              "internal_links": internal_links, "critical_issues": critical,
              "review_items": review, "status": "failed" if critical else "passed"}
    doc.close()
    return result

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--policy", default="editorial/policy.json")
    ap.add_argument("--output", default="build/qa.json")
    args = ap.parse_args()
    result = inspect(args.pdf, json.loads(Path(args.policy).read_text()))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(bool(result["critical_issues"]))
