# Pré-consulta — Erick não aparece após preenchimento novamente

Data: 2026-05-09

## Verificação
Após Tiaro reportar que Erick preencheu novamente e não apareceu no painel, foram verificados:
- `/root/ivs-preconsulta-data`
- `cerebro/empresa/pacientes`
- logs nginx `/api/submit`
- logs PM2 `ivs-preconsulta`

Resultado: houve acesso ao formulário por um IP de usuário às 13:18 UTC, mas não houve `POST /api/submit` correspondente. Portanto, o backend não recebeu a submissão final de Erick.

## Correção operacional aplicada
Para evitar perda quando paciente preenche mas não conclui ou há falha no envio final:
1. Adicionada persistência local no navegador (`localStorage`) do formulário e etapa atual.
2. Criado endpoint `/api/draft` para salvar rascunhos no servidor.
3. Formulário passa a autosalvar rascunho enquanto é preenchido.
4. Painel `/pacientes` passa a exibir rascunhos como `[RASCUNHO]`, permitindo recuperar dados mesmo sem submissão final.

## Validação
- Build Next.js concluído com sucesso.
- PM2 `ivs-preconsulta` reiniciado.
- `/api/draft` validado com teste técnico e arquivo de teste removido.
- Nenhum `POST /api/submit` real de Erick foi encontrado até o momento da correção.

## Regra canônica
Pré-consulta deve ter salvamento incremental; não depender apenas do botão final para preservar dados preenchidos pelo paciente.
