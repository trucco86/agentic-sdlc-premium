#!/usr/bin/env python3
"""Render only pages flagged for editorial review. Output remains a private artifact."""
import argparse
import json
from pathlib import Path
import fitz

def render_review_pages(pdf, qa, outdir, limit=20, dpi=100):
    outdir=Path(outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    doc=fitz.open(pdf)
    pages=sorted({int(x["page"]) for x in qa.get("review_items",[]) if 1 <= int(x["page"]) <= len(doc)})[:limit]
    saved=[]
    for num in pages:
        dest=outdir/f"page-{num:03d}.png"
        doc[num-1].get_pixmap(dpi=dpi,alpha=False).save(dest)
        saved.append(str(dest))
    doc.close()
    return saved

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("pdf")
    p.add_argument("--qa",default="build/qa.json")
    p.add_argument("--output",default="build/review")
    p.add_argument("--limit",type=int,default=20)
    args=p.parse_args()
    qa=json.loads(Path(args.qa).read_text(encoding="utf-8"))
    print("\n".join(render_review_pages(args.pdf,qa,args.output,limit=args.limit)))
