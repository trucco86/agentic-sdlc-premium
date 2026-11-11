# Agentic SDLC Premium | Esteira editorial privada

**Sem OpenAI API e sem publicacao automatica.**

## Como funciona

- `source/current.pdf`: documento V0.6 de 323 paginas, importado do Google Drive com hash fixado no manifesto.
- `editorial/source_manifest.json`: origem e SHA-256 verificados antes de gerar a previa.
- `editorial/policy.json`: gates minimos de integridade (paginas, marcadores, links, vazio fisico).
- `scripts/qa_pdf.py`: verifica a baseline e sinaliza paginas pouco preenchidas para revisao humana.
- `scripts/report.py`: gera `build/EDITORIAL_REPORT.md` sem LLM.
- `scripts/review_images.py`: cria PNGs de paginas sinalizadas para revisao visual.
- `.github/workflows/editorial.yml`: executa em PRs, main, manualmente e diariamente as 12:00 UTC (09:00 Brasilia).

## Onde acompanhar

- GitHub Actions: execucoes, resultados e artefatos privados (14 dias)
- `editorial/backlog.md`: prioridades e criterios para evolucao
- Automacao do ChatGPT: resumo diario as 18:00, independente do GitHub Actions

## Limitacoes reais

Esta esteira **valida e gera previas**. Ela nao escreve autonomamente novos capitulos nem aplica correcoes editoriais via IA. Para isso seria necessaria integracao adicional, que esta explicitamente descartada neste momento por custo.

GitHub Actions usa a franquia e as regras de cobranca da conta GitHub. As execucoes devem ser monitoradas para permanecer dentro do limite do plano. Nao existem secrets de API OpenAI exigidos.

## Governanca

Apostila e relatorios permanecem privados. Sem GitHub Pages, releases publicas, deploy, auto-merge ou publicação automatica. Edicoes de conteudo devem ser propostas por PR, com QA, revisao humana e aprovacao antes de qualquer publicacao.
