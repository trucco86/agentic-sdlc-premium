---
name: agentic-editorial-curation
description: Curadoria e publicação governada de aulas técnicas Agentic SDLC, com fontes verificadas, revisão independente, rastreabilidade e aprovação humana.
---

# Skill: curadoria editorial Agentic SDLC

## Quando usar
Qualquer nova aula, atualização de capítulo, resumo, diagrama, exemplo técnico, exercício ou proposta de publicação.

## Entradas obrigatórias
- Objetivo de aprendizagem, público e nível.
- ID da aula, origem verificável e capítulo-alvo.
- Data e versão das tecnologias citadas.
- Lista de fontes com URL, autor/provedor, data de consulta e alegação sustentada.
- Limites de licenciamento, confidencialidade e riscos.

## Procedimento
1. **Learning Architect:** explicitar resultados mensuráveis, pré-requisitos e o que o aluno conseguirá demonstrar.
2. **Knowledge Curator:** separar afirmações em fato verificado, interpretação ou hipótese. Preferir documentação oficial, especificações, pesquisas e evidência reproduzível. Registrar divergências e lacunas. Não inventar referências.
3. **Content Author:** produzir definição, motivação, exemplo prático, contraprova/limitação, exercício com critério de correção e resumo para fixar. Evitar texto inflado, repetição e alegações de produtividade sem baseline.
4. **Technical Reviewer:** validar comportamento de código, compatibilidade de versões, segurança, riscos operacionais e evidências. Rejeitar exemplos não reproduzíveis.
5. **Editorial QA:** comparar com capítulos existentes e PDF V0.6 quando pertinente; testar links, terminologia, progressão, legibilidade, acessibilidade e rastreabilidade. Registrar pendências em vez de mascará-las.
6. **Release Guardian:** exigir PR Draft, CI verde, duas revisões independentes, licenças e privacidade verificadas, e aprovação humana explícita. Sem autorização, manter draft.

## Saída padronizada
- `lesson_id`, `chapter_ids`, `source_run_id` (ou null), `status`, `review_pr`, `approved`, `incorporated`.
- Resumo de 100 a 200 palavras, objetivos, referências, exemplos, exercícios e limitações.
- Evidence bundle: URLs, versão, testes executados, resultado e hash/commit.
- Lista de decisões humanas pendentes.

## Regras de qualidade
- Uma aula pode ser registrada como `draft` sem ser incorporada.
- `approved=true` e `incorporated=true` somente com evidência de revisão e aprovação.
- Conteúdo demonstrativo deve manter `status=demo`, `approved=false`, `incorporated=false`.
- Conteúdo sem fonte suficiente fica bloqueado; não transformar hipótese em fato.
- Nunca publicar diretamente a partir de uma automação de aula.

## Definition of Done
Conteúdo tecnicamente correto, verificável, didático, sem dados sensíveis, com referências auditáveis, revisão humana, CI aprovado e PR identificado. A publicação é uma decisão posterior e separada.
