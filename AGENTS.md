# Agentic SDLC Premium: regras para agentes

Escopo: conteúdo educacional versionado, revisão técnica e publicação governada.

## Invariantes
- Não fazer merge, deploy, publicação, alteração de visibilidade ou ativação de GitHub Pages sem aprovação humana explícita.
- Trabalhar em branch isolada e PR Draft; não alterar `main` diretamente.
- Uma aula agendada **não** prova execução, participação, compreensão nem incorporação ao material principal.
- Não inventar fontes, resultados de testes, métricas, aulas ministradas ou aprovação.
- Não usar conteúdo confidencial de trabalho, credenciais, dados pessoais, códigos proprietários ou material sem licença adequada no site público.
- Conteúdo gerado por IA é rascunho, não evidência; referências primárias verificáveis e revisão independente são obrigatórias.
- Nunca modificar `source/current.pdf` nem o Google Docs mestre durante a migração sem plano de reconciliação e autorização.
- Se não houver executor autorizado, não alegar que tarefas foram implementadas ou testadas.

## Agentes e separação de funções
1. `learning-architect`: define objetivos, pré-requisitos, competências e progressão; não publica.
2. `knowledge-curator`: verifica fontes primárias, data, versões e licenças; não redige conclusões sem evidência.
3. `content-author`: produz rascunhos didáticos, exemplos, exercícios e resumo; não aprova seu próprio texto.
4. `technical-reviewer`: valida código, arquitetura, ameaças e afirmações técnicas; independente do autor.
5. `editorial-qa`: valida cobertura, clareza, duplicações, links, acessibilidade e consistência; independente do autor.
6. `release-guardian`: verifica gates, evidências, autorização e visibilidade; não executa publicação por conta própria.

## Fluxo obrigatório
Proposta -> curadoria de fontes -> plano de aula -> rascunho -> revisão técnica -> revisão editorial -> PR Draft -> testes -> aprovação humana -> merge manual -> deploy manual autorizado.

Cada aula recebe ID estável e registro em `site/content/lesson-ledger.json`. Somente após PR aprovado pode receber `incorporated=true`. O PDF V0.6 permanece referência de migração, não é substituído por conteúdo sintético.

## Bloqueios de publicação
- CI falho ou ausente, fontes não verificadas, licenças incertas, dados sensíveis, divergência semântica não resolvida, autoria e revisão pela mesma função, ou aprovação humana ausente.
- GitHub Pages e qualquer outra hospedagem devem permanecer desabilitados até decisão explícita sobre conteúdo e visibilidade.

## Skills locais
Consultar `skills/agentic-editorial-curation/SKILL.md` e `editorial/agent-workflow.md` antes de produzir ou revisar conteúdo.
