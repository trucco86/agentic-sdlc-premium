#!/usr/bin/env python3
"""Build a complete, page-faithful HTML edition from the versioned private PDF."""
import argparse
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
        reader_pages = []
        for number, page in enumerate(doc, 1):
            # SVG preserves diagrams, layout and page content. Text remains text when possible.
            svg = page.get_svg_image(text_as_path=False)
            svg_name = f"pagina-{number:03d}.svg"
            (output / svg_name).write_text(svg, encoding="utf-8")
            loading = "eager" if number == 1 else "lazy"
            reader_pages.append(
                f'<section class="page" id="p{number}" aria-label="Página {number}">'
                f'<img src="{svg_name}" width="{round(page.rect.width)}" height="{round(page.rect.height)}" '
                f'loading="{loading}" decoding="async" alt="Página {number} da apostila">'
                f'<footer>{number} / {len(doc)}</footer></section>'
            )
            previous = f"pagina-{number-1:03d}.html" if number > 1 else "index.html"
            following = f"pagina-{number+1:03d}.html" if number < len(doc) else "index.html"
            body = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agentic SDLC Premium | Página {number}</title>
<style>body{{margin:0;background:#101827;color:white;font:16px system-ui}}
nav{{display:flex;justify-content:space-between;gap:12px;padding:14px;flex-wrap:wrap}}
a{{color:#a8d5ff}}main{{max-width:1000px;margin:auto;padding:12px}}
svg{{width:100%;height:auto;background:white;display:block}}</style></head>
<body><nav><a href="index.html">Índice</a><span>Página {number} de {len(doc)}</span>
<a href="{previous}">Anterior</a><a href="{following}">Próxima</a></nav>
<main>{svg}</main></body></html>"""
            (output / f"pagina-{number:03d}.html").write_text(body, encoding="utf-8")
        pages = "\n".join(reader_pages)
        index = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agentic SDLC Premium | Apostila completa</title>
<style>
*{{box-sizing:border-box}}html{{scroll-padding-top:100px}}
body{{margin:0;background:#e5e7eb;color:#182233;font:16px system-ui}}
header{{position:sticky;top:0;z-index:2;background:#101827;color:white;padding:12px 16px;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}}
header h1{{font-size:16px;margin:0}}form{{display:flex;align-items:center;gap:8px}}input{{width:70px}}button,input{{font:inherit;padding:6px}}
main{{max-width:1000px;margin:auto;padding:12px}}.page{{margin:0 auto 16px;background:white;box-shadow:0 2px 8px #0002}}
.page img{{display:block;width:100%;height:auto}}footer{{text-align:center;padding:6px;color:#475569;font-size:12px}}
@media(max-width:600px){{main{{padding:4px}}.page{{margin-bottom:8px}}}}
@media print{{header,footer{{display:none}}main{{padding:0;max-width:none}}.page{{break-after:page;box-shadow:none;margin:0}}}}
</style></head>
<body><header><h1>Agentic SDLC Premium · V0.6 · {len(doc)} páginas</h1>
<form id="jump"><label for="page">Ir à página</label><input id="page" type="number" min="1" max="{len(doc)}" value="1" required><button>Ir</button></form></header>
<main>{pages}</main>
<script>document.getElementById('jump').addEventListener('submit',function(e){{e.preventDefault();const n=document.getElementById('page').value;const p=document.getElementById('p'+n);if(p){{p.scrollIntoView();history.replaceState(null,'','#p'+n);}}}});</script>
</body></html>"""
        (output / "index.html").write_text(index, encoding="utf-8")
        count = len(list(output.glob("pagina-*.html")))
        if count != len(doc):
            raise ValueError(f"Incomplete HTML output: {count}/{len(doc)}")
        (output / "build-manifest.json").write_text(json.dumps({"source_sha256":policy["sha256"],"pages":count},indent=2),encoding="utf-8")
        print(f"Generated {count} complete HTML pages in {output}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=Path("source/current.pdf"))
    p.add_argument("--manifest", type=Path, default=Path("editorial/source_manifest.json"))
    p.add_argument("--output", type=Path, default=Path("build/full-html"))
    a = p.parse_args()
    build(a.source,a.manifest,a.output)
