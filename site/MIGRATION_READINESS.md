# Migração do PDF para o site: evidências obrigatórias

Status: **bloqueado para incorporação e publicação**. Este documento não atesta equivalência entre fontes.

## Fonte e rastreabilidade
- [ ] Registrar SHA-256 do `source/current.pdf` na revisão atual.
- [ ] Confirmar qual documento editável é a fonte canônica e sua revisão.
- [ ] Comparar sumário, capítulos, seções, exercícios, tabelas e referências com o PDF.
- [ ] Registrar diferenças, omissões e decisões editoriais em PR revisável.
- [ ] Vincular cada aula à localização verificável na fonte e à revisão correspondente.

## Critérios para uma aula real
- [ ] Conteúdo transcrito/adaptado com proveniência verificável.
- [ ] Fontes e direitos de uso analisados, sem links inventados.
- [ ] Revisão técnica independente da autoria.
- [ ] Revisão editorial e acessibilidade.
- [ ] Testes automatizados do ledger, backlinks e estados.
- [ ] Aprovação humana explícita de incorporação.

## Gate de release
Mesmo com CI verde, **não** autorizar merge, deploy, GitHub Pages ou mudança de visibilidade sem aprovação explícita do proprietário. Conteúdo `demo` permanece identificado como demonstração.

## Bloqueios conhecidos
- `site/content/lesson-ledger.json` informa `migration_status: not_started`.
- Não existe comprovação de reconciliação PDF/documento editável/site.
- Integração de code review do Codex não comprovada como restabelecida.
- PR #4 não tem revisão independente registrada na última consulta.
