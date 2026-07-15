# Frota Hermes — manifesto (2026-07-15T06:45:04Z)
## Gateways
## Crons
*/15 * * * * /usr/bin/python3 /root/.openclaw/workspace/ops/zapi_bridge/zapi_connection_watchdog.py >/dev/null 2>&1
*/20 * * * * /root/.openclaw/workspace/ops/llm-audit/run_audit_with_telegram_alert.sh
*/5 * * * * /usr/bin/python3 /root/.openclaw/workspace/ops/zapi_bridge/monitor_clara_pause.py >/dev/null 2>&1
0 3 * * * /root/.acme.sh/acme.sh --cron --home /root/.acme.sh > /dev/null 2>&1
0 3 * * * /root/backup-openclaw/scripts/run-backup-and-push-linux-cron.sh
30 4 * * * /root/backup-openclaw/scripts/check-backup-health.sh >/dev/null 2>&1
40 10 * * * /usr/bin/python3 /root/cerebro-vital-slim/scripts/gbrain_ivs_sync.py --mode cron >> /root/.local/share/ivs-gbrain/reports/cron.log 2>&1
10 8 * * * cd /root/cerebro-vital-slim/sistemas/content-engine-os/scrapers && /usr/bin/python3 monitor_fontes_diario.py >> /tmp/monitor_fontes.log 2>&1
7 * * * * /usr/bin/python3 /root/.openclaw/workspace/ops/zapi_bridge/clara_followup_cadence.py --execute --approval-id appr-bdbe3491fd39 --max-per-run 20 >> /root/.openclaw/workspace/ops/zapi_bridge/clara_followup_cadence_cron.log 2>&1
30 2 * * * /usr/bin/python3 /root/.openclaw/workspace/ops/zapi_bridge/clara_learning_promote_daily.py >> /root/.openclaw/workspace/ops/zapi_bridge/clara_learning_promote_daily.log 2>&1  # Clara: ponte de aprendizado diaria (audit->Opus->permanent + portao regressao + alerta)
* * * * * /usr/bin/flock -n /tmp/maria_supervisor.lock /usr/bin/python3 /root/.hermes/maria_supervisor.py >> /root/.hermes/maria_supervisor.log 2>&1  # Maria: supervisao proativa (1min, flock)
*/30 * * * * systemd-run --collect --quiet -p CPUQuota=100% -p CPUWeight=20 -p Nice=19 -p IOWeight=10 /root/clone_dra/batch_cursos.sh  # cursos: assistir+aprender
@reboot /root/clone_dra/course_browser_ensure.sh  # Chrome logado CDP (cursos + NotebookLM Ana)
*/10 * * * * /root/clone_dra/higgsfield_watchdog.sh  # Higgsfield auto-relogin (Joao)
*/15 * * * * /root/clone_dra/hermes_autoheal.sh  # autoheal Hermes (6 gateways + WhatsApp Clara)
45 3 * * * /root/clone_dra/hermes_fleet_backup.sh >> /root/clone_dra/hermes_fleet_backup.log 2>&1  # backup diario inteligencia Hermes -> git cerebro
*/15 * * * * /root/.openclaw/workspace/ops/zapi_bridge/sync_exclusions_op.sh >/dev/null 2>&1  # exclusoes pacientes (senha via 1Password)
10 6 * * * docker exec content-engine-api python scripts/instagram_ingest.py >> /var/log/ig-ingest.log 2>&1  # IG scraper Dra -> Content OS
25 6 * * * docker exec --env-file /root/.openclaw/secure/meta_insights.env content-engine-api python scripts/meta_insights_ingest.py >> /var/log/meta-insights-ingest.log 2>&1  # Meta Insights (privadas) -> Content OS
40 6 * * * docker exec --env-file /root/.openclaw/secure/meta_insights.env content-engine-api python scripts/meta_social_ingest.py >> /var/log/meta-social-ingest.log 2>&1  # Interacoes IG -> Social Selling
50 6 * * * docker exec --env-file /root/.openclaw/secure/meta_insights.env content-engine-api python scripts/meta_ads_ingest.py >> /var/log/meta-ads-ingest.log 2>&1  # Meta Ads -> Content OS
55 6 * * * cd /root/cerebro-vital-slim/sistemas/content-engine-os && python3 apps/api/scripts/google_ads_fetch.py 2>>/var/log/google-ads-ingest.log | docker exec -i content-engine-api python scripts/google_ads_load.py >> /var/log/google-ads-ingest.log 2>&1  # Google Ads -> Content OS
