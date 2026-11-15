# Workflow de agentes e política de publicação

## Responsabilidades e handoffs

| Papel | Entrada | Entrega | Proibido |
|---|---|---|---|
| Learning Architect | Backlog, público, lacunas | Plano de aula e critérios de aprendizagem | Publicar |
| Knowledge Curator | Plano e fontes | Registro de alegações, fontes e licenças | Inventar evidência |
| Content Author | Plano e fontes verificadas | Rascunho, exemplo, exercício, resumo | Aprovar o próprio conteúdo |
| Technical Reviewer | Rascunho e código | Parecer técnico, testes, riscos | Omitir limitações |
| Editorial QA | Parecer e capítulos | Parecer didático e diff semântico | Tratar páginas esparsas como defeito comprovado |
| Release Guardian | PR, CI e pareceres | Checklist de liberação ou bloqueio | Fazer merge/deploy sem aprovação |

## Estados
`proposed -> researched -> drafted -> technical_review -> editorial_review -> ready_for_human_approval -> approved -> incorporated -> published`.

`blocked` pode ser aplicado em qualquer estado, com motivo e ação corretiva. Estados não são prova de execução; cada transição precisa de evidência em PR.

## Gate de conteúdo
- Fontes primárias acessíveis, citações que sustentam alegações, tecnologia/versionamento corretos.
- Revisão de segurança e propriedade intelectual para publicação pública.
- Sem nomes, dados internos, exemplos proprietários ou segredos.
- Exemplo técnico com comportamento verificável, limites e casos de erro.
- Exercício com resposta ou rubrica, resumo de fixação e vínculo com capítulo.

## Gate de CI
- Testes unitários e integridade do ledger.
- Validação de IDs, estados, capítulos e referências.
- Build do site e links internos; QA visual responsivo antes da publicação.
- Nenhum passo de upload, deploy, GitHub Pages, merge ou mudança de visibilidade em PR de protótipo.

## Gate de aprovação
- Autor, revisor técnico e revisor editorial identificados e independentes.
- PR Draft revisado; checklist de riscos e evidências preenchido.
- Aprovação explícita do proprietário antes de merge.
- Autorização de publicação separada da aprovação de conteúdo, incluindo confirmação de licença, privacidade e domínio.

## Aulas agendadas
Automação diária pode gerar um resumo preliminar com `source_run_id`, timestamp, fontes e `status=draft`. Se não existir execução comprovada, registrar `source_run_id=null` e não alegar aula concluída. Nunca promover automaticamente um resumo a capítulo publicado.

## Migração V0.6
Preservar PDF de 323 páginas e documento mestre. Mapear seções, exemplos, diagramas e glossário para conteúdo versionado. Conteúdo ainda não reconciliado permanece sinalizado, sem status canônico.
