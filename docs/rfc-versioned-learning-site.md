# RFC: Agentic SDLC Premium como site versionado

Status: proposta, sem autorização de publicação. Data: 2026-11-14.

## Decisão proposta

Adotar conteúdo Markdown/MDX versionado no GitHub como fonte canônica de futuras edições, com site estático de documentação e exportação PDF secundária. Manter `source/current.pdf` e manifesto V0.6 intactos até concluir migração com reconciliação editorial.

## Arquitetura inicial

- Site estático gerado com Astro + Starlight, a confirmar em PR de protótipo após avaliação de dependências.
- `content/chapters/`: capítulos consolidados e revisados.
- `content/lessons/`: aulas datadas com identificador estável, objetivos, pré-requisitos, fontes e resumo.
- `content/glossary/`: termos canônicos, links cruzados e definições.
- `content/diagrams/`: diagramas em Mermaid e ativos versionados.
- `content/lesson-ledger.json`: rastreabilidade de aula -> capítulos -> PR -> status.
- `editorial/migration-map.json`: correspondência entre 323 páginas da V0.6, seções e arquivos editáveis.

## Fluxo diário

1. Aula agendada gera rascunho separado; execução da automação não implica presença, aprendizado nem publicação.
2. Curadoria compara conceitos e exemplos com conteúdo canônico; identifica duplicações e fontes.
3. PR Draft registra mudanças, referência da aula e diff; revisão humana é obrigatória.
4. CI valida frontmatter, links internos, IDs duplicados, referências, build e ausência de publicação acidental.
5. Somente aprovação explícita permite merge e eventual deploy.

## Gates de migração

- Cobertura integral dos capítulos, exemplos, exercícios, glossário, fontes e diagramas da V0.6.
- Comparação semântica com PDF e documento mestre do Drive; discrepâncias registradas.
- QA visual responsivo e acessibilidade; índice e busca.
- Preservação dos originais privados e do histórico.
- Publicação no GitHub Pages **bloqueada** até decisão explícita sobre visibilidade: Pages pode expor conteúdo mesmo quando o repositório é privado, conforme plano/configuração.

## Estado verificado em 2026-11-14

- Automação `Estudar Agentic SDLC`: habilitada, agenda diária às 08:00 America/Sao_Paulo, última execução registrada em 14/11.
- Não há evidência suficiente de que toda aula tenha sido incorporada ao documento mestre.
- PDF V0.6 no repositório: 323 páginas; último QA confirmado: 10 testes, zero falhas críticas e 14 páginas para revisão.
- Documento mestre Google Docs editável identificado, mas equivalência à V0.6 não comprovada.
- Integração Codex não comprovada.

## Primeiro PR de implementação após esta RFC

Criar site local não publicado, 1 capítulo piloto, 1 aula com ledger, busca e navegação, testes de build e links, sem GitHub Pages habilitado. Validar no PR antes de ampliar a migração.
