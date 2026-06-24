#!/usr/bin/env python3
"""IVS inter-agent mailbox.

Local governed communication bus for Maria, Ana, Joao, Clara, Pedro, Jarvis and councils.
Does not contact patients/leads, does not publish externally, and stores only sanitized operational messages.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import sys
import textwrap
from pathlib import Path

DB_PATH = Path(os.environ.get("IVS_AGENT_MESSAGE_DB", "/root/.openclaw/workspace/ops/ivs_agent_layer/inter_agent_messages.db"))
EVENTS_PATH = Path(os.environ.get("IVS_AGENT_MESSAGE_EVENTS", "/root/.openclaw/workspace/ops/ivs_agent_layer/inter_agent_messages.jsonl"))

AGENTS = {
    "maria": {"id": "maria-gerente", "name": "Maria", "scope": "Gerência geral / operação"},
    "maria-gerente": {"id": "maria-gerente", "name": "Maria", "scope": "Gerência geral / operação"},
    "ana": {"id": "ana-medica-cientifica", "name": "Ana", "scope": "Médica/científica"},
    "ana-medica-cientifica": {"id": "ana-medica-cientifica", "name": "Ana", "scope": "Médica/científica"},
    "joao": {"id": "agente-reels-intel", "name": "João", "scope": "Marketing/Reels/Conteúdo"},
    "joão": {"id": "agente-reels-intel", "name": "João", "scope": "Marketing/Reels/Conteúdo"},
    "agente-reels-intel": {"id": "agente-reels-intel", "name": "João", "scope": "Marketing/Reels/Conteúdo"},
    "clara": {"id": "clara-whatsapp", "name": "Clara", "scope": "Concierge WhatsApp"},
    "clara-whatsapp": {"id": "clara-whatsapp", "name": "Clara", "scope": "Concierge WhatsApp"},
    "pedro": {"id": "pedro-controller-ivs", "name": "Pedro", "scope": "Financeiro/Controller"},
    "pedro-controller-ivs": {"id": "pedro-controller-ivs", "name": "Pedro", "scope": "Financeiro/Controller"},
    "jarvis": {"id": "jarvis-ivs", "name": "Jarvis", "scope": "Assessor/orquestrador"},
    "jarvis-ivs": {"id": "jarvis-ivs", "name": "Jarvis", "scope": "Assessor/orquestrador"},
    "eduardo": {"id": "eduardo-ivs", "name": "Eduardo", "scope": "Agente IVS"},
    "eduardo-ivs": {"id": "eduardo-ivs", "name": "Eduardo", "scope": "Agente IVS"},
    "conselho-growth": {"id": "conselho-growth-vital-slim", "name": "Conselho Growth", "scope": "Growth"},
    "conselho-growth-vital-slim": {"id": "conselho-growth-vital-slim", "name": "Conselho Growth", "scope": "Growth"},
    "llm-council": {"id": "llm-council", "name": "LLM Council", "scope": "Stress-test decisões"},
}

SENSITIVITIES = {"internal", "marketing", "clinical", "lead", "patient", "financial", "tech", "compliance"}
STATUSES = {"open", "ack", "done", "blocked", "cancelled"}

PII_PATTERNS = [
    (re.compile(r"\b(?:\+?55\s?)?\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4}\b"), "[telefone-redigido]"),
    (re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"), "[cpf-redigido]"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[email-redigido]"),
]


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def canonical(agent: str) -> str:
    key = (agent or "").strip().lower()
    if key not in AGENTS:
        raise SystemExit(f"Agente desconhecido: {agent}. Use: {', '.join(sorted(set(a['id'] for a in AGENTS.values())))}")
    return AGENTS[key]["id"]


def sanitize(text: str) -> tuple[str, list[str]]:
    out = text or ""
    flags: list[str] = []
    for pattern, repl in PII_PATTERNS:
        if pattern.search(out):
            flags.append(repl.strip("[]"))
            out = pattern.sub(repl, out)
    # Avoid huge dumps; the sender can reference a file/evidence path instead.
    if len(out) > 6000:
        out = out[:6000] + "\n[conteúdo truncado — envie evidência por arquivo/path]"
        flags.append("truncated")
    return out.strip(), flags


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("pragma journal_mode=wal")
    conn.execute(
        """
        create table if not exists messages (
          id text primary key,
          created_at text not null,
          updated_at text not null,
          from_agent text not null,
          to_agent text not null,
          subject text not null,
          body text not null,
          next_action text not null default '',
          sensitivity text not null default 'internal',
          priority text not null default 'normal',
          status text not null default 'open',
          reply_to text,
          correlation_id text,
          evidence text not null default '[]',
          redaction_flags text not null default '[]'
        )
        """
    )
    conn.execute("create index if not exists idx_messages_to_status on messages(to_agent,status,created_at desc)")
    conn.execute("create index if not exists idx_messages_from on messages(from_agent,created_at desc)")
    return conn


def event(payload: dict) -> None:
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def make_id(from_agent: str, to_agent: str, subject: str, body: str) -> str:
    h = hashlib.sha256(f"{now()}|{from_agent}|{to_agent}|{subject}|{body}".encode()).hexdigest()[:12]
    return f"iam-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}-{h}"


def row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for k in ("evidence", "redaction_flags"):
        try:
            d[k] = json.loads(d.get(k) or "[]")
        except Exception:
            d[k] = []
    return d


def send(args: argparse.Namespace) -> dict:
    from_agent = canonical(args.from_agent)
    to_agent = canonical(args.to_agent)
    if args.sensitivity not in SENSITIVITIES:
        raise SystemExit(f"Sensibilidade inválida: {args.sensitivity}")
    body, body_flags = sanitize(args.body)
    subject, subject_flags = sanitize(args.subject)
    next_action, na_flags = sanitize(args.next_action or "")
    evidence = args.evidence or []
    redaction_flags = sorted(set(body_flags + subject_flags + na_flags))
    mid = make_id(from_agent, to_agent, subject, body)
    correlation_id = args.correlation_id or mid
    conn = connect()
    with conn:
        conn.execute(
            """
            insert into messages(id, created_at, updated_at, from_agent, to_agent, subject, body, next_action,
                                 sensitivity, priority, status, reply_to, correlation_id, evidence, redaction_flags)
            values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (mid, now(), now(), from_agent, to_agent, subject, body, next_action, args.sensitivity, args.priority,
             "open", args.reply_to, correlation_id, json.dumps(evidence, ensure_ascii=False), json.dumps(redaction_flags, ensure_ascii=False)),
        )
    payload = {"event": "inter_agent_message_sent", "id": mid, "from": from_agent, "to": to_agent, "subject": subject, "sensitivity": args.sensitivity, "priority": args.priority, "created_at": now(), "redaction_flags": redaction_flags}
    event(payload)
    return {"ok": True, "message": row_to_dict(conn.execute("select * from messages where id=?", (mid,)).fetchone())}


def list_messages(args: argparse.Namespace) -> dict:
    agent = canonical(args.agent)
    status = args.status
    if status != "all" and status not in STATUSES:
        raise SystemExit(f"Status inválido: {status}")
    q = "select * from messages where to_agent=?"
    vals: list[object] = [agent]
    if status != "all":
        q += " and status=?"
        vals.append(status)
    q += " order by created_at desc limit ?"
    vals.append(args.limit)
    rows = [row_to_dict(r) for r in connect().execute(q, vals).fetchall()]
    return {"ok": True, "agent": agent, "count": len(rows), "messages": rows}


def outbox(args: argparse.Namespace) -> dict:
    agent = canonical(args.agent)
    rows = [row_to_dict(r) for r in connect().execute("select * from messages where from_agent=? order by created_at desc limit ?", (agent, args.limit)).fetchall()]
    return {"ok": True, "agent": agent, "count": len(rows), "messages": rows}


def update(args: argparse.Namespace) -> dict:
    status = args.status
    if status not in STATUSES:
        raise SystemExit(f"Status inválido: {status}")
    conn = connect()
    with conn:
        cur = conn.execute("update messages set status=?, updated_at=? where id=? returning *", (status, now(), args.id))
        row = cur.fetchone()
    if not row:
        raise SystemExit(f"Mensagem não encontrada: {args.id}")
    d = row_to_dict(row)
    event({"event": "inter_agent_message_status", "id": args.id, "status": status, "updated_at": now()})
    return {"ok": True, "message": d}


def agents(_: argparse.Namespace) -> dict:
    uniq = {}
    for v in AGENTS.values():
        uniq[v["id"]] = v
    return {"ok": True, "agents": list(uniq.values())}


def print_human(result: dict) -> None:
    if "message" in result and result.get("message"):
        m = result["message"]
        print(f"{m['id']} | {m['from_agent']} → {m['to_agent']} | {m['status']} | {m['sensitivity']} | {m['priority']}")
        print(f"Assunto: {m['subject']}")
        print(textwrap.fill(m['body'], width=100))
        if m.get("next_action"):
            print("Próxima ação:", m["next_action"])
        return
    if "messages" in result:
        print(f"Inbox/outbox de {result.get('agent')} — {result.get('count')} mensagem(ns)")
        for m in result["messages"]:
            print(f"- {m['id']} | {m['from_agent']} → {m['to_agent']} | {m['status']} | {m['priority']} | {m['subject']}")
        return
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description="IVS inter-agent mailbox")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("send", help="send a governed message to another agent")
    p.add_argument("--from", dest="from_agent", required=True)
    p.add_argument("--to", dest="to_agent", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--next-action", default="")
    p.add_argument("--sensitivity", choices=sorted(SENSITIVITIES), default="internal")
    p.add_argument("--priority", choices=["low", "normal", "high", "urgent"], default="normal")
    p.add_argument("--reply-to")
    p.add_argument("--correlation-id")
    p.add_argument("--evidence", action="append", default=[])
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=send)

    p = sub.add_parser("inbox", help="list messages addressed to agent")
    p.add_argument("--agent", required=True)
    p.add_argument("--status", default="open")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=list_messages)

    p = sub.add_parser("outbox", help="list messages sent by agent")
    p.add_argument("--agent", required=True)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=outbox)

    p = sub.add_parser("update", help="update message status")
    p.add_argument("--id", required=True)
    p.add_argument("--status", choices=sorted(STATUSES), required=True)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=update)

    p = sub.add_parser("agents", help="list known agents")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=agents)

    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = args.func(args)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
