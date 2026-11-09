# Agentic SDLC Premium | Esteira editorial privada

Projeto editorial versionado. **Nao publicar automaticamente.**

## Estado da implantacao
- GitHub Actions: agendamento diario 12:00 UTC (09:00 America/Sao_Paulo), PR e execucao manual.
- QA: integridade de marcadores, links internos e revisao de paginas orfas.
- Preview: artefato privado de GitHub Actions, nunca GitHub Pages.
- Bloqueio intencional: a fonte `source/current.pdf` precisa ser incorporada.
- Codex: **nao conectado ainda**. Agendamento nao equivale a edicao autonoma.
- Nenhum deploy publico, auto-merge ou permissao de escrita em workflows.

## Proximas etapas
1. Importar PDF V0.6 de 323 paginas, verificar checksum e manter fonte editavel em `content/`.
2. Portar o gate de aproveitamento de pagina e testes visuais.
3. Configurar executor Codex com credenciais seguras e PRs draft.
4. Revisar PR e liberar somente por aprovacao humana.

## Governanca
A publicacao e uma etapa separada, sem acionamento automatico. Nao salvar tokens no repositorio.
