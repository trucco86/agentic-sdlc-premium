#!/usr/bin/env python3
"""Produce a human-readable private PR review summary from audit JSON."""
import argparse
import json
from pathlib import Path

def render(editorial, github, release):
    lines = [
        "# Agentic SDLC Premium: parecer editorial privado",
        "",
        "Este documento é diagnóstico, não uma autorização de merge ou publicação.",
        "",
        "## Estado da entrega",
        f"- Integridade editorial: {editorial.get('schema_checks', 'unknown')}",
        f"- Aulas registradas: {editorial.get('lesson_count', 0)}",
        f"- Auditoria GitHub disponível: {'sim' if github else 'não'}",
        f"- Decisão: {release.get('decision', 'blocked')}",
        "- Merge autorizado: não",
        "- Publicação autorizada: não",
        "",
        "## Revisões reais no GitHub",
    ]
    if github:
        lines.extend([
            f"- PR: #{github.get('pr_number', '?')}",
            f"- Commit auditado: {github.get('head_sha') or 'não informado'}",
            f"- Revisores independentes aprovando: {github.get('independent_approvals', 0)}",
            f"- Solicitações de alteração: {', '.join(github.get('changes_requested_by', [])) or 'nenhuma registrada'}",
        ])
    else:
        lines.append("- Sem dados verificados de revisão; liberação bloqueada")
    lines.extend(["", "## Bloqueios"])
    lines.extend(f"- {reason}" for reason in release.get("blocking_reasons", []))
    lines.extend(["", "## Conteúdo rastreado"])
    for lesson in editorial.get("lessons", []):
        lines.append(f"- {lesson.get('lesson_id')}: conteúdo={lesson.get('content_state')}; revisão={lesson.get('review_state')}")
    lines.extend(["", "## Pendências de decisão humana",
                  "- Revisão independente de conteúdo e fontes",
                  "- Aprovação explícita para merge",
                  "- Aprovação separada para publicar o site", ""])
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--editorial", type=Path, required=True)
    parser.add_argument("--github", type=Path)
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    editorial = json.loads(args.editorial.read_text(encoding="utf-8"))
    github = json.loads(args.github.read_text(encoding="utf-8")) if args.github and args.github.exists() else None
    release = json.loads(args.release.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(editorial, github, release), encoding="utf-8")
    print("Private editorial review summary generated")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
