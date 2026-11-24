#!/usr/bin/env python3
"""Build a complete, page-faithful HTML edition from the versioned private PDF."""
import argparse
import base64
import hashlib
import html
import json
from pathlib import Path

import fitz


def build(source: Path, manifest: Path, output: Path):
    policy = json.loads(manifest.read_text(encoding="utf-8"))
    if not source.is_file():
        raise ValueError("Source PDF missing")
    if hashlib.sha256(source.read_bytes()).hexdigest() != policy["sha256"]:
        raise ValueError("PDF checksum does not match approved source manifest")
    output.mkdir(parents=True, exist_ok=True)
    with fitz.open(source) as doc:
        if len(doc) != policy["pages"]:
            raise ValueError("PDF page count differs from manifest")
        bookmarks = [(level, title, page) for level, title, page in doc.get_toc()
                     if 1 <= page <= len(doc)]
        toc = "".join(
            f'<li style="--depth:{min(max(level-1,0),5)}"><a href="#p{page}">'
            f'<span>{html.escape(title)}</span><span>{page}</span></a></li>'
            for level, title, page in bookmarks
        )
        if not toc:
            toc = "".join(f'<li><a href="#p{n}">Página {n}</a></li>'
                          for n in range(1, len(doc)+1))
        reader_pages = []
        for number, page in enumerate(doc, 1):
            # SVG preserves diagrams, layout and page content. Text remains text when possible.
            svg = page.get_svg_image(text_as_path=False)
            # Embed each page as a self-contained SVG data URI to isolate SVG IDs.
            encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
            reader_pages.append(
                f'<section class="page" id="p{number}" aria-label="Página {number}">'
                f'<img src="data:image/svg+xml;base64,{encoded}" width="{round(page.rect.width)}" height="{round(page.rect.height)}" '
                f'loading="lazy" decoding="async" alt="Página {number} da apostila">'
                f'<div class="page-text">{html.escape(page.get_text(sort=True))}</div></section>'
            )
        pages = "\n".join(reader_pages)
        index = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agentic SDLC Premium | Apostila completa</title>
<style>
*{{box-sizing:border-box}}html{{scroll-padding-top:100px}}
body{{margin:0;background:#e5e7eb;color:#182233;font:16px system-ui}}
header{{position:sticky;top:0;z-index:2;background:#101827;color:white;padding:12px 16px;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}}
header h1{{font-size:16px;margin:0}}form{{display:flex;align-items:center;gap:8px}}input{{width:70px}}button,input{{font:inherit;padding:6px}}
header a{{color:white}}#sumario{{background:white;padding:16px;margin-bottom:12px}}#sumario ol{{list-style:none;padding:0}}#sumario li{{padding-left:calc(var(--depth,0)*12px)}}#sumario a{{display:flex;justify-content:space-between;gap:12px;padding:8px;color:#17467a;border-bottom:1px solid #ddd}}main{{max-width:1000px;margin:auto;padding:12px}}.page{{margin:0 auto;background:white;position:relative}}
.page-text{{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:pre-wrap}}body.text-mode .page-text{{position:static;width:auto;height:auto;clip-path:none;padding:16px;overflow:visible}}body.text-mode .page img{{display:none}}.page img{{display:block;width:100%;height:auto}}footer{{text-align:center;padding:6px;color:#475569;font-size:12px}}
@media(max-width:600px){{main{{padding:4px}}.page{{margin-bottom:0}}}}
@media print{{body.text-mode .page img{{display:block}}header,footer,.page-text,#sumario{{display:none}}main{{padding:0;max-width:none}}.page{{break-after:page;box-shadow:none;margin:0}}}}
</style></head>
<body><header><h1>Agentic SDLC Premium · V0.6 · {len(doc)} páginas</h1>
<a href="#sumario">Sumário</a><button type="button" id="mode" aria-pressed="false">Modo texto</button><form id="jump"><label for="page">Ir à página</label><input id="page" type="number" min="1" max="{len(doc)}" value="1" required><button>Ir</button></form></header>
<main><nav id="sumario" aria-label="Sumário"><h2>Sumário</h2><ol>{toc}</ol></nav>{pages}</main>
<script>document.getElementById("mode").addEventListener("click",function(){{const active=document.body.classList.toggle("text-mode");this.setAttribute("aria-pressed",String(active));this.textContent=active?"Modo visual":"Modo texto";}});document.getElementById('jump').addEventListener('submit',function(e){{e.preventDefault();const n=document.getElementById('page').value;const p=document.getElementById('p'+n);if(p){{p.scrollIntoView();history.replaceState(null,'','#p'+n);}}}});</script>
</body></html>"""
        (output / "index.html").write_text(index, encoding="utf-8")
        count = len(reader_pages)
        if count != len(doc):
            raise ValueError(f"Incomplete HTML output: {count}/{len(doc)}")
        (output / "build-manifest.json").write_text(json.dumps({"source_sha256":policy["sha256"],"pages":count},indent=2),encoding="utf-8")
        print(f"Generated one HTML document with {count} pages in {output}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=Path("source/current.pdf"))
    p.add_argument("--manifest", type=Path, default=Path("editorial/source_manifest.json"))
    p.add_argument("--output", type=Path, default=Path("build/full-html"))
    a = p.parse_args()
    build(a.source,a.manifest,a.output)
