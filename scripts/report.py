#!/usr/bin/env python3
"""Produce a reproducible Markdown report from the PDF QA result, without any LLM."""
import argparse
import json
from pathlib import Path

def build_report(qa, manifest):
    issues=qa.get("critical_issues", [])
    reviews=qa.get("review_items", [])
    lines=[
        "# Agentic SDLC Premium | Relatorio editorial",
        "",
        f"- Estado: **{'BLOQUEADO' if issues else 'QA estrutural aprovado'}**",
        f"- Paginas: **{qa.get('pages', '?')}**",
        f"- Marcadores: **{qa.get('bookmarks', '?')}**",
        f"- Links internos: **{qa.get('internal_links', '?')}**",
        f"- Falhas criticas: **{len(issues)}**",
        f"- Sinalizacoes para revisao humana: **{len(reviews)}**",
        f"- Origem: `{manifest.get('source_filename', 'desconhecida')}`",
        f"- ID do Drive: `{manifest.get('drive_file_id', 'desconhecido')}`",
        "",
        "## Falhas criticas",
    ]
    lines += [f"- {issue}" for issue in issues] or ["Nenhuma falha critica detectada."]
    lines += ["", "## Paginas para revisao visual"]
    lines += [f"- Pagina {item.get('page', '?')}: {item.get('reason', 'revisar')}" for item in reviews] or ["Nenhuma pagina sinalizada pelo filtro atual."]
    lines += ["", "## Proximas prioridades",
              "1. Corrigir falhas criticas antes de aprovar o PR, quando houver.",
              "2. Revisar visualmente paginas sinalizadas; nao aplicar mudancas automaticas em conteudo.",
              "3. Separar teste estrutural da aprovacao editorial e da publicacao.",
              "",
              "> Este relatorio nao substitui leitura ou aprovacao editorial. Nenhum arquivo e publicado automaticamente."]
    return "\n".join(lines)+"\n"

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--qa",default="build/qa.json")
    p.add_argument("--manifest",default="editorial/source_manifest.json")
    p.add_argument("--output",default="build/EDITORIAL_REPORT.md")
    args=p.parse_args()
    data=json.loads(Path(args.qa).read_text(encoding="utf-8"))
    manifest=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    dest=Path(args.output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(build_report(data,manifest),encoding="utf-8")
    print(dest)
