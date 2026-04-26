# Auditoria de Segurança — Skills Instaladas (2026-04-26)

## Resumo Executivo
**Total de skills instaladas:** 27 (ClawHub) + skills customizadas + skills do sistema
**Skills removidas:** 26 (design gráfico)
**Skills bloqueadas pelo VirusTotal:** 8
**Skills com API externa:** 4
**Skills puramente locais/documentação:** 23

---

## Classificação por Risco

### 🔴 BLOQUEADAS (VirusTotal — não instaladas)
| Skill | Motivo |
|-------|--------|
| crm-in-a-box | Flagged: crypto keys, external APIs, eval |
| lead-generation | Flagged: crypto keys, external APIs, eval |
| google-sheets-api | Flagged: crypto keys, external APIs, eval |
| lead-researcher | Flagged: crypto keys, external APIs, eval |
| csv-data-explorer | Flagged: crypto keys, external APIs, eval |
| data-visualizer | Flagged: crypto keys, external APIs, eval |
| email-daily-summary | Flagged: crypto keys, external APIs, eval |
| cold-email-outreach | Flagged: crypto keys, external APIs, eval |

### 🟡 API EXTERNA (Requer Token/Key)
| Skill | API | Requer | Risco |
|-------|-----|--------|-------|
| google-sheets | maton.ai gateway | MATON_API_KEY | Médio — proxy OAuth para Google Sheets |
| porteden-email | porteden.com | PE_API_KEY | Médio-Alto — acesso total a email (ler/enviar/deletar) |
| meta-ads-analytics | brijr/meta-mcp (MCP) | MCP config | Médio — leitura de dados Meta Ads |
| whatsapp-business-api | Meta Cloud API | WHATSAPP_ACCESS_TOKEN | Médio — envio de mensagens WhatsApp |

### 🟢 PURAMENTE LOCAL/SEGURA
| Skill | Descrição |
|-------|-----------|
| copywriting-pro | Apenas documentação/texto |
| content-marketing | Apenas documentação/texto |
| social-media-scheduler | Apenas documentação/texto |
| marketing-analytics | Apenas documentação/texto |
| sales-mastery | Apenas documentação/texto |
| sales-pipeline-tracker | Apenas documentação/texto |
| lead-scorer | Apenas documentação/texto (framework de pontuação) |
| lead-extractor | Apenas documentação/texto (regras de extração) |
| mini-crm | Apenas documentação/texto (chinês) |
| market-research-agent | Apenas documentação/texto |
| data-analyst-pro | Análise local de arquivos |
| check-analytics | Apenas documentação/texto |
| in-depth-research | Apenas documentação/texto |
| automation-workflows | Apenas documentação/texto |
| n8n-workflow-automation | Apenas documentação/texto (gera JSON) |
| n8n-monitor | Apenas documentação/texto |
| n8n-api | Apenas documentação/texto |
| web-scraping | Apenas documentação/texto (guia de uso) |
| project-planner | Apenas documentação/texto |
| ai-presentation-maker | Export local (HTML, PPTX, PDF) |
| communication-skill | Apenas documentação/texto |
| biz-hospitality | Apenas documentação/texto |
| notion-skill | Apenas documentação/texto |

---

## Skills Customizadas (Workspace)
| Skill | Tipo | Risco |
|-------|------|-------|
| agenda-diaria-whatsapp | Script local + API Z-API | 🟡 Médio |
| historico-conversas | Script local + API Google Sheets | 🟡 Médio |
| omie-boletos | Script local + API Omie | 🟡 Médio |
| omie-linha-corte | Script local + API Omie | 🟡 Médio |
| tweet-carrossel | Script local + geração de imagem | 🟢 Baixo |
| llm-council | Apenas documentação | 🟢 Baixo |
| deep-research | Script local | 🟢 Baixo |
| prompt-imagens | Script local | 🟢 Baixo |
| homematch-brand | Apenas documentação | 🟢 Baixo |
| vitalslim-atendimento | Apenas documentação | 🟢 Baixo |

---

## Recomendações

1. **NÃO configurar tokens sem necessidade imediata** — skills com API externa só precisam de configuração quando forem usar
2. **Manter monitoramento** das skills com API externa (rate limits, custos)
3. **PULAR skills flagged pelo VirusTotal** — nunca forçar instalação
4. **Preferir skills locais** quando possível
5. **Revisar código** antes de usar skills desconhecidas

---

## Próximos Passos
- [ ] Configurar `MATON_API_KEY` para Google Sheets (se/quando necessário)
- [ ] Configurar `PE_API_KEY` para email (se/quando necessário)
- [ ] Configurar `WHATSAPP_ACCESS_TOKEN` para WhatsApp Business API (se/quando necessário)
- [ ] Configurar MCP `brijr/meta-mcp` para Meta Ads Analytics (se/quando necessário)
- [ ] Criar skill de integração QuarkClinic (segura, local)
- [ ] Criar skill de métricas da clínica (segura, local)
