# Backlog editorial priorizado

## P0 - Concluido
- [x] Localizar PDF-base privado no Google Drive
- [x] Registrar SHA-256, volume, sumario e links em manifesto
- [x] Importar PDF V0.6 para `source/current.pdf` no repositorio privado
- [x] Executar build e QA estruturais sem OpenAI API; ultimo gate deve ficar verde antes de ativar agendamento

## P1 - Em andamento
- [x] Gerar relatorio editorial Markdown por execucao
- [x] Produzir imagens de paginas sinalizadas para revisao humana, armazenadas em artefatos privados
- [ ] Revisar manualmente 14 paginas com baixa ocupacao (27, 31, 35, 42, 60, 71, 82, 89, 96, 100, 112, 115, 159, 315)
- [ ] Definir fonte editavel e mecanismo de recompilacao/reflow antes de corrigir paginas
- [ ] Adicionar gate de preservacao semantica de trechos/diagramas entre versoes
- [ ] Revisar contraste, clipping, sobreposicao de diagramas e indice

## P2 - Melhoria continua
- [ ] Gerar diff visual antes/depois de cada mudanca editorial
- [ ] Medir densidade de conteudo, tempo de revisao, aprovacoes e bloqueios
- [ ] Exportar copia aprovada ao Drive somente apos revisao; nunca publicar externamente sem autorizacao

## Regras
Sem OPENAI_API_KEY. Os workflows nao geram texto por IA. Qualquer edicao do livro requer revisao humana e PR; nenhum processo publica ou efetua deploy. Os minutos de GitHub Actions seguem os limites do plano contratado.
