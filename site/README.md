# Protótipo local do Agentic SDLC Premium

Este diretório contém um **protótipo estático de navegação**, sem dependências externas e **sem publicação**.

## Testar localmente

```bash
python -m http.server 8000 --directory site
```

Abra http://localhost:8000. Para validar os requisitos básicos:

```bash
python -m unittest discover -s site/tests -v
```

## Limites explícitos

- Conteúdo de aula demonstrativo, **não** transcrição de uma aula realizada.
- Não há importação automática do PDF, nem sincronização de aulas.
- Nenhuma alteração no PDF V0.6, no documento mestre ou no GitHub Pages.
- Antes de publicação, implementar conteúdo versionado, ledger de aulas, migração auditável, revisão de licenças e segurança, busca, testes de links e acessibilidade.
- A publicação pública futura exige aprovação explícita.
