#!/usr/bin/env python3
"""Conservative structural QA. Human review is still mandatory for editorial quality."""
import argparse, json, re
from pathlib import Path
import fitz

def inspect(pdf, policy):
    doc=fitz.open(pdf)
    issues=[]; review=[]
    if len(doc)<policy.get("minimum_pages",1): issues.append("PDF sem paginas suficientes")
    toc=doc.get_toc()
    if len(toc)<policy.get("expected_bookmarks",0): issues.append("Marcadores abaixo da linha de base")
    links=0
    for i,p in enumerate(doc):
        text=p.get_text().strip()
        if not text: review.append({"page":i+1,"reason":"sem texto extraivel; verificar se e pagina visual"})
        lines=[x for x in text.splitlines() if x.strip()]
        if len(lines)<=3 and len(p.get_drawings())<8 and not p.get_images(): review.append({"page":i+1,"reason":"possivel pagina orfa"})
        for link in p.get_links():
            if link.get("kind")==fitz.LINK_GOTO:
                links+=1
                target=link.get("page",-1)
                if target<0 or target>=len(doc): issues.append(f"Link interno invalido na pagina {i+1}")
    if links<policy.get("expected_internal_links",0): issues.append("Links internos abaixo da linha de base")
    result={"pdf":str(pdf),"pages":len(doc),"bookmarks":len(toc),"internal_links":links,"critical_issues":issues,"review_items":review,"status":"failed" if issues else "passed"}
    doc.close()
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("pdf");ap.add_argument("--policy",default="editorial/policy.json");ap.add_argument("--output",default="build/qa.json")
    args=ap.parse_args()
    policy=json.loads(Path(args.policy).read_text())
    result=inspect(args.pdf,policy)
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=False))
    print(json.dumps(result,ensure_ascii=False))
    raise SystemExit(bool(result["critical_issues"]))
