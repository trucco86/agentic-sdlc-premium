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
        for number, page in enumerate(doc, 1):
            # SVG preserves diagrams, layout and page content. Text remains text when possible.
            svg = page.get_svg_image(text_as_path=False)
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
        links = "\n".join(f'<li><a href="pagina-{n:03d}.html">Página {n}</a></li>' for n in range(1, len(doc)+1))
        index = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agentic SDLC Premium | Apostila completa</title>
<style>body{{font:17px system-ui;margin:auto;max-width:900px;padding:24px;line-height:1.6}}
ol{{columns:3}}@media(max-width:600px){{ol{{columns:2}}}}li{{break-inside:avoid}}</style></head>
<body><h1>Agentic SDLC Premium</h1><p>Edição HTML integral do PDF V0.6, com {len(doc)} páginas.
A diagramação é preservada em SVG; esta edição ainda requer revisão de acessibilidade e navegação semântica.</p>
<a href="pagina-001.html">Começar leitura</a><h2>Índice de páginas</h2><ol>{links}</ol></body></html>"""
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
