#!/usr/bin/env python3
import json
import os
import sys
import time
import hashlib
import re
import subprocess
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional, Tuple
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen


BRIDGE_HOST = os.getenv("BRIDGE_HOST", "127.0.0.1")
BRIDGE_PORT = int(os.getenv("BRIDGE_PORT", "8787"))
OPENCLAW_GATEWAY_URL = os.getenv("OPENCLAW_GATEWAY_URL", "http://127.0.0.1:18789/v1/responses")

# QuarckClinic — verificação de pacientes
QUARKCLINIC_AUTH_TOKEN = os.getenv("QUARKCLINIC_AUTH_TOKEN", "")
QUARKCLINIC_BASE_URL = os.getenv("QUARKCLINIC_BASE_URL", "https://api.quark.tec.br/clinic/ext").rstrip("/")
OPENCLAW_GATEWAY_TOKEN = os.getenv("OPENCLAW_GATEWAY_TOKEN", "")
OPENCLAW_AGENT_REF = os.getenv("OPENCLAW_AGENT_REF", "openclaw/main")
OPENCLAW_MODEL_OVERRIDE = os.getenv("OPENCLAW_MODEL_OVERRIDE", "openai/gpt-5.4")
OPENCLAW_SESSION_PREFIX = os.getenv("OPENCLAW_SESSION_PREFIX", "bridge:zapi")
APPS_SCRIPT_FANOUT_URL = os.getenv("APPS_SCRIPT_FANOUT_URL", "")
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID", "")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN", "")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN", "")
ZAPI_BASE_URL = os.getenv("ZAPI_BASE_URL", "").strip() or (
    f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}" if ZAPI_INSTANCE_ID and ZAPI_TOKEN else ""
)
ZAPI_SEND_TEXT_PATH = os.getenv("ZAPI_SEND_TEXT_PATH", "/send-text")
ZAPI_SEND_AUDIO_PATH = os.getenv("ZAPI_SEND_AUDIO_PATH", "/send-audio")

# Áudio inbound/outbound — habilitado por variável de ambiente.
# Sem as chaves, o bridge mantém fallback seguro para texto.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")
OPENAI_TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
OPENAI_TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "nova")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")
ELEVENLABS_URL = "https://api.elevenlabs.io/v1/text-to-speech"
CLARA_AUDIO_MIRRORING = os.getenv("CLARA_AUDIO_MIRRORING", "1").strip().lower() not in ("0", "false", "no", "off")
CLARA_NOTIFY_PHONE = os.getenv("CLARA_NOTIFY_PHONE", "5571986968887")  # Tiaro
CLARA_NOTIFY_PHONES = [p.strip() for p in os.getenv("CLARA_NOTIFY_PHONES", "5571986968887,5571991574827").split(",") if p.strip()]
CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE = os.getenv("CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE", "0").strip().lower() in ("1", "true", "yes", "on")
BRIDGE_SHARED_SECRET = os.getenv("BRIDGE_SHARED_SECRET", "")
WEBHOOK_PATH_TOKEN = os.getenv("WEBHOOK_PATH_TOKEN", "")
DEDUP_TTL_SECONDS = int(os.getenv("DEDUP_TTL_SECONDS", "600"))
HTTP_TIMEOUT_SECONDS = int(os.getenv("HTTP_TIMEOUT_SECONDS", "90"))
CLARA_CONTROL_FILE = os.getenv("CLARA_CONTROL_FILE", "/root/.openclaw/workspace/ops/zapi_bridge/clara_control_state.json")
CLARA_SYSTEM_PROMPT_FILE = os.getenv("CLARA_SYSTEM_PROMPT_FILE", "/root/.openclaw/workspace/ops/zapi_bridge/clara_system_prompt.md")
CLARA_LEADS_FILE = os.getenv("CLARA_LEADS_FILE", "/root/.openclaw/workspace/ops/zapi_bridge/clara_leads_state.json")
CLARA_EVENT_STATE_FILE = os.getenv("CLARA_EVENT_STATE_FILE", "/root/.openclaw/workspace/ops/zapi_bridge/clara_event_state.json")
CLARA_EXCLUSIONS_FILE = os.getenv("CLARA_EXCLUSIONS_FILE", "/root/.openclaw/workspace/ops/zapi_bridge/clara_exclusions.json")
ACTIVATION_PHRASE = os.getenv("CLARA_ACTIVATION_PHRASE", "Gostaria de saber mais informações sobre o Instituto Vital Slim")
PHONE_COOLDOWN_SECONDS = int(os.getenv("PHONE_COOLDOWN_SECONDS", "45"))
REPEAT_TEXT_WINDOW_SECONDS = int(os.getenv("REPEAT_TEXT_WINDOW_SECONDS", "180"))
REPEAT_REPLY_WINDOW_SECONDS = int(os.getenv("REPEAT_REPLY_WINDOW_SECONDS", "300"))
MANUAL_TAKEOVER_WINDOW_SECONDS = int(os.getenv("MANUAL_TAKEOVER_WINDOW_SECONDS", str(6 * 60 * 60)))
HUMAN_RECENT_MESSAGE_WINDOW_SECONDS = int(os.getenv("HUMAN_RECENT_MESSAGE_WINDOW_SECONDS", "1800"))
CLARA_ACTIVE_LEAD_WINDOW_SECONDS = int(os.getenv("CLARA_ACTIVE_LEAD_WINDOW_SECONDS", str(14 * 24 * 60 * 60)))
QUARK_CONFIRMATION_REPLY_SCRIPT = os.getenv(
    "QUARK_CONFIRMATION_REPLY_SCRIPT",
    "/root/cerebro-vital-slim/ops/quarkclinic_confirmations/process_reply.py",
)

SEEN: "OrderedDict[str, float]" = OrderedDict()


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    print(f"[{ts}] {msg}", flush=True)


def compact_seen() -> None:
    cutoff = time.time() - DEDUP_TTL_SECONDS
    stale = [k for k, ts in SEEN.items() if ts < cutoff]
    for key in stale:
        SEEN.pop(key, None)
    while len(SEEN) > 5000:
        SEEN.popitem(last=False)


def remember_message(message_id: str) -> bool:
    compact_seen()
    if message_id in SEEN:
        return False
    SEEN[message_id] = time.time()
    return True


def sha1_text(value: str) -> str:
    return hashlib.sha1(value.strip().encode("utf-8", errors="ignore")).hexdigest()


def load_event_state() -> Dict[str, Any]:
    path = Path(CLARA_EVENT_STATE_FILE)
    if not path.exists():
        return {"events": {}, "updated_at": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"events": {}, "updated_at": None}
        events = data.get("events")
        if not isinstance(events, dict):
            events = {}
        return {"events": events, "updated_at": data.get("updated_at")}
    except Exception as err:
        log(f"event state read failed: {err}")
        return {"events": {}, "updated_at": None}


def save_event_state(state: Dict[str, Any]) -> None:
    state["updated_at"] = int(time.time())
    path = Path(CLARA_EVENT_STATE_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def get_phone_event_entry(phone: str) -> Dict[str, Any]:
    state = load_event_state()
    events = state.setdefault("events", {})
    entry = events.get(phone)
    if not isinstance(entry, dict):
        entry = {}
    return entry


def update_phone_event_entry(phone: str, patch: Dict[str, Any]) -> None:
    state = load_event_state()
    events = state.setdefault("events", {})
    entry = events.get(phone)
    if not isinstance(entry, dict):
        entry = {}
    entry.update(patch)
    entry["updated_at"] = int(time.time())
    events[phone] = entry
    save_event_state(state)


def should_skip_event(phone: str, message_id: str, text: str) -> Tuple[bool, str]:
    now = time.time()
    entry = get_phone_event_entry(phone)
    text_hash = sha1_text(text)
    last_message_id = entry.get("last_message_id")
    last_text_hash = entry.get("last_text_hash")
    last_inbound_at = entry.get("last_inbound_at")

    if isinstance(last_message_id, str) and last_message_id == message_id:
        return True, "duplicate_message_id_persistent"

    try:
        if last_text_hash == text_hash and last_inbound_at and (now - float(last_inbound_at) <= REPEAT_TEXT_WINDOW_SECONDS):
            return True, "duplicate_text_window"
    except Exception:
        pass

    update_phone_event_entry(phone, {
        "last_message_id": message_id,
        "last_text_hash": text_hash,
        "last_inbound_at": now,
    })
    return False, "ok"


def mark_human_activity(phone: str, note: str = "human_recent_message") -> None:
    now = time.time()
    update_phone_event_entry(phone, {
        "human_recent_message_at": now,
        "human_recent_message_note": note,
    })


def set_manual_override(phone: str, active: bool, note: Optional[str] = None, until: Optional[float] = None) -> None:
    state = load_control_state()
    overrides = state.setdefault("manual_overrides", {})
    if active:
        overrides[phone] = {
            "until": until,
            "note": note or "manual_override",
            "set_at": int(time.time()),
            "owner": "human",
        }
    else:
        overrides.pop(phone, None)
    state["manual_overrides"] = overrides
    save_control_state(state)


def has_recent_human_activity(phone: str) -> Tuple[bool, Optional[str]]:
    entry = get_phone_event_entry(phone)
    at = entry.get("human_recent_message_at")
    if not at:
        return False, None
    try:
        if time.time() - float(at) <= HUMAN_RECENT_MESSAGE_WINDOW_SECONDS:
            return True, entry.get("human_recent_message_note") or "human_recent_message"
    except Exception:
        return True, "human_recent_message_invalid_timestamp"
    return False, None


def should_block_reply(phone: str, reply: str) -> Tuple[bool, str]:
    now = time.time()
    entry = get_phone_event_entry(phone)
    reply_hash = sha1_text(reply)
    last_reply_hash = entry.get("last_reply_hash")
    last_reply_at = entry.get("last_reply_at")

    # Não bloquear continuidade por tempo entre mensagens: leads respondem rápido no WhatsApp.
    # A proteção real contra loop fica no bloqueio de resposta duplicada abaixo.
    try:
        if last_reply_hash == reply_hash and last_reply_at and (now - float(last_reply_at) <= REPEAT_REPLY_WINDOW_SECONDS):
            state = load_control_state()
            state["paused"] = True
            state["paused_at"] = int(now)
            state["paused_until"] = None
            state["paused_reason"] = "auto_pause_duplicate_reply_same_phone"
            state["paused_by"] = "bridge_guardrail"
            save_control_state(state)
            return True, "duplicate_reply_auto_paused"
    except Exception:
        pass

    update_phone_event_entry(phone, {
        "last_reply_hash": reply_hash,
        "last_reply_at": now,
    })
    return False, "ok"


def first_nonempty(*values: Any) -> Optional[str]:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def deep_get(data: Any, *path: str) -> Any:
    cur = data
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def extract_text(payload: Dict[str, Any]) -> Optional[str]:
    candidates = [
        deep_get(payload, "text", "message"),
        deep_get(payload, "text", "body"),
        deep_get(payload, "text", "text"),
        deep_get(payload, "text"),
        deep_get(payload, "message", "text", "message"),
        deep_get(payload, "message", "text", "body"),
        deep_get(payload, "message", "text"),
        deep_get(payload, "message", "body"),
        deep_get(payload, "message", "conversation"),
        deep_get(payload, "message", "extendedTextMessage", "text"),
        deep_get(payload, "body"),
        deep_get(payload, "conversation"),
        deep_get(payload, "msg", "body"),
        deep_get(payload, "data", "text", "message"),
        deep_get(payload, "data", "text", "body"),
        deep_get(payload, "data", "text"),
        deep_get(payload, "data", "message", "text", "message"),
        deep_get(payload, "data", "message", "text"),
        deep_get(payload, "data", "message", "body"),
    ]
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


def normalize_phone(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    digits = "".join(ch for ch in value if ch.isdigit())
    return digits or None


def extract_phone(payload: Dict[str, Any]) -> Optional[str]:
    candidates = [
        payload.get("phone"),
        payload.get("from"),
        payload.get("fromNumber"),
        payload.get("senderPhone"),
        deep_get(payload, "sender", "phone"),
        deep_get(payload, "sender", "id"),
        deep_get(payload, "message", "from"),
        deep_get(payload, "message", "sender", "id"),
        deep_get(payload, "data", "phone"),
        deep_get(payload, "data", "from"),
        deep_get(payload, "key", "remoteJid"),
        deep_get(payload, "data", "key", "remoteJid"),
        deep_get(payload, "message", "key", "remoteJid"),
        payload.get("remoteJid"),
    ]
    for candidate in candidates:
        phone = normalize_phone(candidate)
        if phone:
            return phone
    return None


def extract_message_id(payload: Dict[str, Any]) -> Optional[str]:
    candidates = [
        payload.get("messageId"),
        payload.get("id"),
        payload.get("zaapId"),
        deep_get(payload, "message", "id"),
        deep_get(payload, "messageId", "_serialized"),
        deep_get(payload, "data", "messageId"),
    ]
    return first_nonempty(*candidates)


def is_group_message(payload: Dict[str, Any]) -> bool:
    values = [
        payload.get("isGroup"),
        payload.get("groupMessage"),
        deep_get(payload, "message", "isGroup"),
        deep_get(payload, "data", "isGroup"),
    ]
    return any(value is True for value in values)


def is_from_me(payload: Dict[str, Any]) -> bool:
    values = [
        payload.get("fromMe"),
        deep_get(payload, "message", "fromMe"),
        deep_get(payload, "data", "fromMe"),
    ]
    return any(value is True for value in values)


def is_existing_patient(phone: str) -> bool:
    """Consulta QuarckClinic — retorna True se o telefone pertence a um paciente cadastrado."""
    if not QUARKCLINIC_AUTH_TOKEN:
        return False
    # Normalizar: remover DDI 55 para busca (API aceita só DDD+número)
    digits = "".join(ch for ch in phone if ch.isdigit())
    if digits.startswith("55") and len(digits) > 11:
        digits = digits[2:]  # remove DDI
    try:
        from urllib.request import Request as _Req, urlopen as _urlopen
        url = f"{QUARKCLINIC_BASE_URL}/v1/pacientes?telefone={digits}&limite=1"
        req = _Req(url, headers={"Auth-token": QUARKCLINIC_AUTH_TOKEN})
        with _urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
            patients = data.get("response", {}).get("response", []) if isinstance(data.get("response"), dict) else data.get("response", [])
            return bool(patients)
    except Exception as err:
        log(f"quarkclinic check failed (allowing through): {err}")
        return False  # em caso de erro, deixa passar para não bloquear leads


def post_json(url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = HTTP_TIMEOUT_SECONDS) -> Tuple[int, str]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=body, headers={"Content-Type": "application/json", **(headers or {})}, method="POST")
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except HTTPError as err:
        return err.code, err.read().decode("utf-8", errors="replace")
    except URLError as err:
        raise RuntimeError(f"network error calling {url}: {err}") from err


def get_json(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = HTTP_TIMEOUT_SECONDS) -> Tuple[int, str]:
    req = Request(url, headers=headers or {}, method="GET")
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except HTTPError as err:
        return err.code, err.read().decode("utf-8", errors="replace")
    except URLError as err:
        raise RuntimeError(f"network error calling {url}: {err}") from err


def parse_json_body(body: str) -> Any:
    try:
        return json.loads(body) if body else None
    except Exception:
        return None


def default_control_state() -> Dict[str, Any]:
    return {
        "paused": False,
        "paused_at": None,
        "paused_until": None,
        "paused_reason": None,
        "paused_by": None,
        "manual_overrides": {},
        "updated_at": None,
    }


def save_control_state(state: Dict[str, Any]) -> None:
    """Persist control state to disk. Always updates 'updated_at'."""
    path = Path(CLARA_CONTROL_FILE)
    state["updated_at"] = int(time.time())
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as err:
        log(f"control state write failed: {err}")


def load_exclusions_state() -> Dict[str, Any]:
    path = Path(CLARA_EXCLUSIONS_FILE)
    if not path.exists():
        return {"phones": {}, "updated_at": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"phones": {}, "updated_at": None}
        if not isinstance(data.get("phones"), dict):
            data["phones"] = {}
        return data
    except Exception as err:
        log(f"exclusions state read failed: {err}")
        return {"phones": {}, "updated_at": None}


def get_exclusion_reason(phone: str) -> Optional[str]:
    state = load_exclusions_state()
    entry = (state.get("phones") or {}).get(phone)
    if not isinstance(entry, dict):
        return None
    reason = str(entry.get("reason") or "excluded_phone")
    source = str(entry.get("source") or "")
    # Exceção explícita do Tiaro: alguns contatos sincronizados como pacientes podem ser leads ativos.
    if reason.startswith("lead_exception") or source == "tiaro_lead_exception":
        return None

    # Correção operacional 2026-05-09 — RC paciente primeiro:
    # Nunca liberar `patient_bridge_known` apenas porque houve entrada em clara_leads_state.
    # Um paciente que escreve no WhatsApp pode criar `active=True` como "new_contact" e,
    # se liberado automaticamente, a Clara responde paciente real. A única liberação aceita
    # é exceção explícita acima (`lead_exception*` / `tiaro_lead_exception`).
    return reason


def load_control_state() -> Dict[str, Any]:
    path = Path(CLARA_CONTROL_FILE)
    if not path.exists():
        return default_control_state()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return default_control_state()
        state = default_control_state()
        state.update(data)
        if not isinstance(state.get("manual_overrides"), dict):
            state["manual_overrides"] = {}
        return state
    except Exception as err:
        log(f"control state read failed: {err}")
        return default_control_state()


def is_manual_override_active(phone: str) -> Tuple[bool, Optional[str]]:
    state = load_control_state()
    overrides = state.get("manual_overrides") or {}
    entry = overrides.get(phone)
    if not isinstance(entry, dict):
        return False, None
    until = entry.get("until")
    note = entry.get("note")
    now = time.time()
    if until is None:
        return True, note or "manual_override"
    try:
        if float(until) > now:
            return True, note or "manual_override_until"
    except Exception:
        return True, note or "manual_override_invalid_until"
    overrides.pop(phone, None)
    state["manual_overrides"] = overrides
    save_control_state(state)
    return False, None


def should_pause_clara(phone: str) -> Tuple[bool, Optional[str]]:
    exclusion_reason = get_exclusion_reason(phone)
    if exclusion_reason:
        return True, f"exclusion:{exclusion_reason}"
    state = load_control_state()
    if state.get("paused") is True:
        until = state.get("paused_until")
        if until is not None:
            try:
                if float(until) <= time.time():
                    # TTL expired -> auto-release
                    state["paused"] = False
                    state["paused_until"] = None
                    state["paused_reason"] = None
                    state["paused_by"] = None
                    save_control_state(state)
                    log(f"global_pause auto_released (TTL expired)")
                    return is_manual_override_active(phone)
            except (TypeError, ValueError):
                pass
        return True, "global_pause"
    return is_manual_override_active(phone)


def handle_admin_pause(payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """Handle pause/unpause/status/admin override actions. Returns (http_status, body)."""
    action = (payload.get("action") or "").lower().strip()
    state = load_control_state()
    now = int(time.time())
    phone = normalize_phone(payload.get("phone") if isinstance(payload.get("phone"), str) else None)

    if action == "pause":
        # Default: 2 hours
        duration_minutes = payload.get("duration_minutes", 120)
        try:
            duration_minutes = int(duration_minutes)
        except (TypeError, ValueError):
            duration_minutes = 120
        if duration_minutes <= 0:
            duration_minutes = 120
        state["paused"] = True
        state["paused_at"] = now
        state["paused_until"] = now + duration_minutes * 60
        state["paused_reason"] = (payload.get("reason") or "").strip() or None
        state["paused_by"] = (payload.get("by") or "").strip() or None
        save_control_state(state)
        log(f"admin pause duration={duration_minutes}min by={state['paused_by']!r} reason={state['paused_reason']!r}")
        return 200, {
            "ok": True,
            "action": "paused",
            "paused_until": state["paused_until"],
            "duration_minutes": duration_minutes,
            "reason": state["paused_reason"],
            "by": state["paused_by"],
        }

    if action == "pause_indefinite":
        state["paused"] = True
        state["paused_at"] = now
        state["paused_until"] = None
        state["paused_reason"] = (payload.get("reason") or "").strip() or None
        state["paused_by"] = (payload.get("by") or "").strip() or None
        save_control_state(state)
        log(f"admin pause_indefinite by={state['paused_by']!r} reason={state['paused_reason']!r}")
        return 200, {
            "ok": True,
            "action": "paused_indefinite",
            "reason": state["paused_reason"],
            "by": state["paused_by"],
        }

    if action == "unpause":
        was_paused = state.get("paused", False)
        state["paused"] = False
        state["paused_at"] = None
        state["paused_until"] = None
        state["paused_reason"] = None
        state["paused_by"] = None
        save_control_state(state)
        log(f"admin unpause (was_paused={was_paused})")
        return 200, {"ok": True, "action": "unpaused", "was_paused": was_paused}

    if action == "status":
        until = state.get("paused_until")
        remaining = None
        if until and state.get("paused"):
            try:
                remaining = max(0, int(float(until) - now))
            except Exception:
                pass
        body = {
            "ok": True,
            "paused": state.get("paused", False),
            "paused_at": state.get("paused_at"),
            "paused_until": until,
            "remaining_seconds": remaining,
            "paused_reason": state.get("paused_reason"),
            "paused_by": state.get("paused_by"),
        }
        if phone:
            active, reason = is_manual_override_active(phone)
            body["phone"] = phone
            body["manual_override_active"] = active
            body["manual_override_reason"] = reason
        return 200, body

    if action == "manual_assume":
        if not phone:
            return 400, {"ok": False, "error": "phone required"}
        duration_seconds = payload.get("duration_seconds", MANUAL_TAKEOVER_WINDOW_SECONDS)
        try:
            duration_seconds = int(duration_seconds)
        except (TypeError, ValueError):
            duration_seconds = MANUAL_TAKEOVER_WINDOW_SECONDS
        if duration_seconds <= 0:
            duration_seconds = MANUAL_TAKEOVER_WINDOW_SECONDS
        until = now + duration_seconds
        note = (payload.get("reason") or "manual_takeover_active").strip()
        set_manual_override(phone, True, note=note, until=until)
        mark_human_activity(phone, note=note)
        return 200, {"ok": True, "action": "manual_assume", "phone": phone, "until": until, "reason": note}

    if action == "manual_release":
        if not phone:
            return 400, {"ok": False, "error": "phone required"}
        set_manual_override(phone, False)
        return 200, {"ok": True, "action": "manual_release", "phone": phone}

    return 400, {"ok": False, "error": "invalid action", "valid_actions": ["pause", "pause_indefinite", "unpause", "status", "manual_assume", "manual_release"]}


def load_leads_state() -> Dict[str, Any]:
    path = Path(CLARA_LEADS_FILE)
    if not path.exists():
        return {"leads": {}, "updated_at": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"leads": {}, "updated_at": None}
        leads = data.get("leads")
        if not isinstance(leads, dict):
            leads = {}
        return {"leads": leads, "updated_at": data.get("updated_at")}
    except Exception as err:
        log(f"leads state read failed: {err}")
        return {"leads": {}, "updated_at": None}


def save_leads_state(state: Dict[str, Any]) -> None:
    state["updated_at"] = int(time.time())
    path = Path(CLARA_LEADS_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def has_activation_phrase(text: str) -> bool:
    return ACTIVATION_PHRASE.strip().lower() in text.strip().lower()


def is_known_lead(phone: str) -> bool:
    state = load_leads_state()
    return phone in (state.get("leads") or {})


def get_lead_entry(phone: str) -> Dict[str, Any]:
    state = load_leads_state()
    leads = state.get("leads") or {}
    entry = leads.get(phone)
    return entry if isinstance(entry, dict) else {}


def mark_lead_active(phone: str, source: str) -> None:
    state = load_leads_state()
    leads = state.setdefault("leads", {})
    entry = leads.get(phone) if isinstance(leads.get(phone), dict) else {}
    now = int(time.time())
    if not entry.get("first_seen_at"):
        entry["first_seen_at"] = now
    entry.update({
        "active": True,
        "source": source,
        "last_inbound_at": now,
        "active_until": now + CLARA_ACTIVE_LEAD_WINDOW_SECONDS,
        "inbound_count": int(entry.get("inbound_count") or 0) + 1,
        "updated_at": now,
    })
    leads[phone] = entry
    save_leads_state(state)


def mark_followup_outbound(phone: str, source: str) -> None:
    """Abre janela de continuidade quando a Clara dispara follow-up ativo.

    Z-API pode ecoar o mesmo envio com telefone normalizado de forma diferente
    (ex.: com/sem nono dígito). Por isso registramos tanto no /admin/send
    quanto no webhook `fromApi`, usando o telefone que vier em cada etapa.
    Sem isso, o lead responde ao follow-up e cai em
    `existing_lead_requires_manual_release`, interrompendo a conversa.
    """
    if not phone:
        return
    # Não transforma telefone bloqueado em elegível. A checagem de exclusão/paciente
    # continua mandando em should_pause_clara/is_existing_patient.
    mark_lead_active(phone, source)


def mark_lead_replied(phone: str, reply: str) -> None:
    state = load_leads_state()
    leads = state.setdefault("leads", {})
    entry = leads.get(phone) if isinstance(leads.get(phone), dict) else {}
    now = int(time.time())
    entry.update({
        "active": True,
        "last_reply_at": now,
        "last_reply_preview": (reply or "")[:160],
        "active_until": now + CLARA_ACTIVE_LEAD_WINDOW_SECONDS,
        "reply_count": int(entry.get("reply_count") or 0) + 1,
        "updated_at": now,
    })
    leads[phone] = entry
    save_leads_state(state)


def is_active_lead_window(phone: str) -> bool:
    entry = get_lead_entry(phone)
    if not entry:
        return False
    try:
        return bool(entry.get("active")) and float(entry.get("active_until") or 0) > time.time()
    except Exception:
        return False


def should_respond_to_lead(phone: str, text: str) -> Tuple[bool, str]:
    manual_active, manual_reason = is_manual_override_active(phone)
    if manual_active:
        return False, manual_reason or "manual_override_active"

    human_recent, human_reason = has_recent_human_activity(phone)
    if human_recent:
        return False, human_reason or "human_recent_message"

    if is_known_lead(phone):
        if is_active_lead_window(phone):
            mark_lead_active(phone, "active_lead_window")
            return True, "active_lead_window"
        return False, "existing_lead_requires_manual_release"

    if has_activation_phrase(text):
        mark_lead_active(phone, "activation_phrase")
        return True, "activation_phrase"

    mark_lead_active(phone, "new_contact")
    return True, "new_contact"


def fanout_to_apps_script(payload: Dict[str, Any]) -> None:
    if not APPS_SCRIPT_FANOUT_URL:
        return

    def _send() -> None:
        try:
            status, body = post_json(APPS_SCRIPT_FANOUT_URL, payload, timeout=8)
            log(f"apps-script fanout status={status} body={body[:300]}")
        except Exception as err:
            log(f"apps-script fanout failed: {err}")

    import threading
    threading.Thread(target=_send, daemon=True).start()


def build_session_key(phone: str) -> str:
    return f"{OPENCLAW_SESSION_PREFIX}:{phone}"


def load_clara_prompt() -> str:
    path = Path(CLARA_SYSTEM_PROMPT_FILE)
    try:
        text = path.read_text(encoding="utf-8").strip()
        if text:
            return text
        raise RuntimeError("empty prompt file")
    except Exception as err:
        raise RuntimeError(f"failed to load Clara prompt from {path}: {err}") from err


def build_lead_context(phone: str) -> str:
    entry = get_lead_entry(phone)
    if not entry:
        return ""
    safe = {k: entry.get(k) for k in ("source", "inbound_count", "reply_count", "first_seen_at", "last_inbound_at", "last_reply_at", "last_reply_preview", "internal_note") if entry.get(k) is not None}
    if not safe:
        return ""
    return "\n\nContexto operacional interno deste lead (não mencionar ao lead): " + json.dumps(safe, ensure_ascii=False)


def call_clara(phone: str, text: str, sender_name: Optional[str] = None) -> str:
    if not OPENCLAW_GATEWAY_TOKEN:
        raise RuntimeError("OPENCLAW_GATEWAY_TOKEN is empty")
    instructions = load_clara_prompt()
    # RC-34 (2026-05-08): não injetar nome do perfil WhatsApp no prompt da Clara.
    # Clara deve perguntar o nome diretamente ao lead e só personalizar após confirmação no chat.
    instructions += build_lead_context(phone)
    instructions += "\n\nRegra de saída: responda apenas com o texto da mensagem WhatsApp. Mensagem curta, humana, uma pergunta por vez. Termine com pergunta útil, proposta de horário específico, ou próximo passo claro. Se não houver resposta adequada, responda exatamente NO_REPLY."
    payload = {
        "model": OPENCLAW_AGENT_REF,
        "input": text,
        "user": f"zapi:{phone}",
        "instructions": instructions,
    }
    _agent_id_for_header = OPENCLAW_AGENT_REF.split("/", 1)[1] if "/" in OPENCLAW_AGENT_REF else OPENCLAW_AGENT_REF
    headers = {
        "Authorization": f"Bearer {OPENCLAW_GATEWAY_TOKEN}",
        "x-openclaw-session-key": build_session_key(phone),
        "x-openclaw-message-channel": "whatsapp",
        "x-openclaw-model": OPENCLAW_MODEL_OVERRIDE,
        "x-openclaw-agent-id": _agent_id_for_header,
    }
    status, body = post_json(OPENCLAW_GATEWAY_URL, payload, headers=headers)
    if status < 200 or status >= 300:
        raise RuntimeError(f"OpenClaw gateway error status={status} body={body[:600]}")
    data = json.loads(body)
    output = data.get("output") or []
    texts = []
    for item in output:
        if not isinstance(item, dict):
            continue
        for part in item.get("content") or []:
            if isinstance(part, dict) and part.get("type") == "output_text" and isinstance(part.get("text"), str):
                texts.append(part["text"])
    reply = "\n\n".join(part.strip() for part in texts if part and part.strip()).strip()
    return reply or "NO_REPLY"






def enforce_no_first_time_question(reply: str) -> str:
    """Remove pergunta redundante sobre primeira vez; o bridge já classifica lead via QuarkClinic."""
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    patterns = [
        r"\s*para eu te orientar[^.!?\n]*,?\s*é\s+(a\s+)?sua primeira vez no instituto vital slim\??",
        r"\s*me confirma[^.!?\n]*,?\s*é\s+(a\s+)?sua primeira vez no instituto vital slim\??",
        r"\s*é\s+(a\s+)?sua primeira vez no instituto vital slim\??",
        r"\s*você já (veio|esteve|passou|consultou)[^.!?\n]*(aqui|instituto|cl[ií]nica)[^.!?\n]*\??",
        r"\s*j[aá] é paciente[^.!?\n]*(cl[ií]nica|instituto)[^.!?\n]*\??",
    ]
    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip(" \n.-")
    if not cleaned:
        return "Para eu te orientar melhor: o que mais está te incomodando hoje e fez você buscar ajuda agora?"
    return cleaned


def contains_price_question(text: str) -> bool:
    lower = (text or "").lower()
    return any(token in lower for token in (
        "valor", "preço", "preco", "investimento", "quanto custa", "custa quanto",
        "consulta particular", "particular", "quanto é", "quanto e", "r$"
    ))


def contains_money_value(text: str) -> bool:
    lower = (text or "").lower()
    return ("r$" in lower) or ("1.000" in lower) or ("1000" in lower) or ("900" in lower and "consulta" in lower)


def enforce_price_timing(phone: str, inbound_text: str, reply: str) -> str:
    """Impede preço cedo demais na primeira pergunta de valor.

    Regra operacional: primeira pergunta de preço sem qualificação suficiente recebe deflexão SPIN.
    Se o lead insistir depois, Clara pode informar o valor.
    """
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    if not contains_price_question(inbound_text) or not contains_money_value(text):
        return text

    entry = get_phone_event_entry(phone)
    prior_price_deflections = int(entry.get("price_deflections", 0) or 0)
    prior_price_questions = int(entry.get("price_questions", 0) or 0)
    update_phone_event_entry(phone, {
        "price_questions": prior_price_questions + 1,
        "last_price_question_at": time.time(),
    })

    if prior_price_deflections >= 1:
        return text

    update_phone_event_entry(phone, {
        "price_deflections": prior_price_deflections + 1,
        "last_price_deflection_at": time.time(),
    })
    return (
        "Claro, eu te explico direitinho. Antes, para eu não te passar uma informação solta: "
        "o que mais está te incomodando hoje e fez você buscar ajuda agora?"
    )


def contains_program_question(text: str) -> bool:
    lower = (text or "").lower()
    return any(token in lower for token in (
        "programa", "acompanhamento", "depois", "mensal", "continuidade", "continuar", "tratamento"
    ))


def enforce_program_reasoning(inbound_text: str, reply: str) -> str:
    """Garante raciocínio correto antes de falar do Programa de Acompanhamento."""
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    if not contains_program_question(inbound_text):
        return text
    lower = text.lower()
    mentions_program = "programa" in lower or "acompanhamento" in lower
    weak_fixed_value_answer = ("não tem um valor fixo" in lower or "nao tem um valor fixo" in lower) and not any(
        marker in lower for marker in ("primeiro passo", "histórico", "historico", "composição corporal", "composicao corporal", "manhã", "manha", "tarde")
    )
    lacks_agenda_direction = not any(marker in lower for marker in ("horário", "horario", "manhã", "manha", "tarde", "agendar", "consulta inicial"))
    if weak_fixed_value_answer or (mentions_program and lacks_agenda_direction):
        return (
            "Sim, existe essa possibilidade. A consulta inicial é justamente o primeiro passo para a Dra. Daniely entender seu caso com profundidade: "
            "histórico, exames, composição corporal, rotina e objetivo.\n\n"
            "A partir disso, se fizer sentido, ela pode desenhar um Programa de Acompanhamento individual para você, com conduta, metas e ajustes ao longo do processo.\n\n"
            "Por isso o programa não tem valor fechado antes da avaliação: ele depende do que for indicado para o seu caso.\n\n"
            "Para começar certo, o melhor passo é agendar a consulta inicial. Você prefere que eu veja um horário pela manhã ou pela tarde?"
        )
    return text


def contains_plan_rejection(text: str) -> bool:
    lower = (text or "").lower()
    strong_rejection = any(token in lower for token in (
        "procurar um profissional pelo plano", "procurar profissional pelo plano",
        "profissional pelo convênio", "profissional pelo convenio",
        "prefiro pelo plano", "prefiro pelo convênio", "prefiro pelo convenio",
        "preferir pelo plano", "preferir pelo convênio", "preferir pelo convenio",
        "vou procurar pelo plano", "vou procurar pelo convênio", "vou procurar pelo convenio",
        "vou preferir procurar", "vou ver pelo plano", "vou pelo plano"
    ))
    return strong_rejection


def contains_plan_question_direct(text: str) -> bool:
    lower = (text or "").lower()
    return any(token in lower for token in (
        "aceita plano", "aceitam plano", "atende plano", "atendem plano",
        "aceita convênio", "aceita convenio", "aceitam convênio", "aceitam convenio",
        "atendimento pelo plano", "consulta pelo plano", "pelo meu plano",
        "sulamerica", "sulamérica", "bradesco", "amil", "mamães baianas", "mamaes baianas"
    ))


def enforce_plan_question_response(inbound_text: str, reply: str) -> str:
    """Garante resposta correta para pergunta direta sobre plano/convênio antes de virar perda."""
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    if not contains_plan_question_direct(inbound_text) or contains_plan_rejection(inbound_text):
        return text
    lower = text.lower()
    mentions_no_direct_plan = any(marker in lower for marker in (
        "não trabalhamos com convênio direto", "nao trabalhamos com convenio direto",
        "não atendemos por convênio direto", "nao atendemos por convenio direto",
        "atendimento é particular", "atendimento e particular", "consulta particular"
    ))
    mentions_reimbursement_when_applicable = any(marker in lower for marker in (
        "reembolso", "bradesco", "sulamérica", "sulamerica", "amil"
    ))
    has_next_question = "?" in text
    risky_price_push = any(marker in lower for marker in (
        "valores são acessíveis", "valores sao acessiveis", "posso te passar os valores", "passar os valores"
    ))
    if risky_price_push or not (mentions_no_direct_plan and mentions_reimbursement_when_applicable and has_next_question):
        return (
            "Hoje não trabalhamos com convênio direto. Em Bradesco, SulAmérica e Amil, a equipe pode ajudar a estimar e dar entrada no reembolso da consulta inicial, sem promessa de valor específico.\n\n"
            "A consulta aqui é uma avaliação médica integrada, com composição corporal e plano de ação individualizado — não uma consulta rápida de convênio.\n\n"
            "O que pesa mais para você agora: conseguir reembolso ou entender se a avaliação vale o investimento particular?"
        )
    return text


def enforce_objection_handling(inbound_text: str, reply: str) -> str:
    """Impede encerramento passivo diante de objeção de plano/convênio."""
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    if not contains_plan_rejection(inbound_text):
        return text
    lower = text.lower()
    passive_close = any(marker in lower for marker in (
        "estaremos por aqui", "estou por aqui", "obrigada por avisar", "obrigado por avisar",
        "caso em algum momento", "quando quiser", "fico à disposição", "fico a disposição",
        "entendo perfeitamente"
    ))
    has_real_objection_question = ("?" in text) and any(marker in lower for marker in (
        "o que pesa", "custo", "vale a pena", "dúvida", "duvida", "investimento", "confiança", "confianca", "reembolso"
    ))
    if passive_close or not has_real_objection_question:
        return (
            "Entendo, faz sentido você considerar o plano. Só para te orientar com justiça: aqui a consulta particular não é para substituir seu plano, "
            "e sim para fazer uma avaliação mais profunda e integrada, com olhar médico, composição corporal e plano de ação individualizado.\n\n"
            "Se for Bradesco, SulAmérica ou Amil, a equipe ainda pode te ajudar a estimar o reembolso antes da consulta e dar entrada no pedido com você, sem promessa de valor específico.\n\n"
            "O que pesa mais para você agora: o custo inicial ou a dúvida se vale a pena fazer uma avaliação mais completa?"
        )
    return text


def contains_call_request(text: str) -> bool:
    lower = (text or "").lower()
    return any(token in lower for token in (
        "pode ligar", "pode me ligar", "me liga", "ligar pra mim", "ligação", "ligacao",
        "whatsapp é silencioso", "whatsapp e silencioso", "zap silencioso", "telefone silencioso"
    ))


def enforce_call_request_response(inbound_text: str, reply: str) -> str:
    """Transforma pedido de ligação/preferência de canal em próximo passo com dono."""
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    if not contains_call_request(inbound_text):
        return text
    lower = text.lower()
    if "lig" in lower and "?" in text and any(marker in lower for marker in ("horário", "horario", "melhor", "equipe")):
        return text
    return "Consigo pedir para a equipe te ligar, sim. Qual é o melhor horário para receber a ligação?"


def contains_scheduling_offer(text: str) -> bool:
    lower = (text or "").lower()
    return any(token in lower for token in (
        "posso ver um horário", "posso ver um horario", "vejo um horário", "vejo um horario",
        "prefere manhã ou tarde", "prefere manha ou tarde", "manhã ou tarde", "manha ou tarde",
        "agendar", "marcar a consulta", "ver agenda", "horário de consulta", "horario de consulta"
    ))


def has_journey_context(text: str) -> bool:
    lower = (text or "").lower()
    markers = (
        "jornada", "consulta inicial", "avaliação médica", "avaliacao medica", "dra. daniely",
        "histórico", "historico", "exames", "composição corporal", "composicao corporal",
        "bioimpedância", "bioimpedancia", "rotina", "sono", "vídeo", "video"
    )
    return sum(1 for marker in markers if marker in lower) >= 4


def contains_inbound_scheduling_intent(text: str) -> bool:
    lower = (text or "").lower()
    return any(token in lower for token in (
        "quero marcar", "quero agendar", "queria marcar", "queria agendar",
        "marcar uma consulta", "agendar uma consulta", "tem horário", "tem horario",
        "agenda", "consulta disponível", "consulta disponivel"
    ))


def enforce_journey_before_scheduling(inbound_text: str, reply: str) -> str:
    """Bloqueia agenda cedo demais sem explicar a jornada IVS."""
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    if (contains_scheduling_offer(text) or contains_inbound_scheduling_intent(inbound_text)) and not has_journey_context(text):
        return (
            "Entendi. Antes de ver agenda, deixa eu te explicar rapidinho como funciona a jornada aqui.\n\n"
            "A consulta inicial é uma avaliação médica completa com a Dra. Daniely. Ela olha seu histórico, exames, composição corporal pela bioimpedância, rotina, sono e o que pode estar dificultando seu resultado.\n\n"
            "A partir disso, ela define o caminho mais seguro para você, de forma individualizada.\n\n"
            "Posso te enviar um vídeo curtinho da Dra. explicando como funciona o atendimento?"
        )
    return text


def enforce_allowed_scheduling_scope(reply: str) -> str:
    """Clara só pode agendar Consulta ou Exame de Bioimpedância."""
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    lower = text.lower()
    scheduling_context = any(token in lower for token in (
        "agend", "marc", "reserv", "horário", "horario", "agenda", "encaixe", "consulta ficou", "consulta está", "consulta esta"
    ))
    if not scheduling_context:
        return text
    allowed = any(token in lower for token in (
        "consulta", "avaliação", "avaliacao", "bioimpedância", "bioimpedancia", "exame de bio"
    ))
    forbidden = any(token in lower for token in (
        "procedimento", "aplicação", "aplicacao", "injetável", "injetavel", "injetáveis", "injetaveis",
        "soro", "soroterapia", "implante", "hormonal", "tirzepatida", "medicação", "medicacao",
        "programa", "acompanhamento", "retorno", "botox", "preenchimento", "fórmula", "formula"
    ))
    if forbidden and not allowed:
        return (
            "Para organizar corretamente, pela Clara eu consigo te ajudar com o agendamento de Consulta ou Exame de Bioimpedância. "
            "Outros procedimentos precisam ser alinhados pela equipe após avaliação. "
            "Você quer que eu veja Consulta ou Bioimpedância?"
        )
    return text

def contains_spouse_decision(text: str) -> bool:
    lower = (text or "").lower()
    return any(token in lower for token in (
        "minha esposa", "meu esposo", "minha mulher", "meu marido",
        "conversar com minha esposa", "conversar com meu esposo", "conversar com minha mulher", "conversar com meu marido",
        "falar com minha esposa", "falar com meu esposo", "falar com minha mulher", "falar com meu marido",
        "ver com minha esposa", "ver com meu esposo", "ver com minha mulher", "ver com meu marido",
        "vou conversar com ela", "vou conversar com ele", "vou falar com ela", "vou falar com ele"
    ))


def enforce_vitor_video_practical_application(inbound_text: str, reply: str) -> str:
    """Transforma o treino Vitor/RapidAPI em execução obrigatória, não apenas memória.

    Regras determinísticas aplicadas no runtime:
    - cônjuge envolvido = facilitar decisão familiar com próximo passo;
    - não empurrar lead para outro contato sem assumir condução;
    - não encerrar sem CTA claro;
    - não deixar resposta burocrática substituir condução comercial.
    """
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    lower = text.lower()
    inbound_lower = (inbound_text or "").lower()

    if contains_spouse_decision(inbound_text):
        has_family_facilitation = any(marker in lower for marker in (
            "esposa", "esposo", "marido", "mulher", "decid", "avaliar juntos", "conversar com",
            "resumo", "encaminhado", "posso te enviar", "posso enviar", "retorno"
        ))
        has_clear_cta = "?" in text and any(marker in lower for marker in (
            "posso", "prefere", "qual", "melhor horário", "melhor horario", "envio", "enviar", "retorno"
        ))
        if not (has_family_facilitation and has_clear_cta):
            return (
                "Claro, faz sentido conversar com sua esposa. Para vocês decidirem com segurança e não deixar isso esfriar, "
                "posso te mandar um resumo simples do próximo passo e deixar a orientação encaminhada para vocês avaliarem juntos. "
                "Posso te enviar agora?"
            )

    transfer_without_ownership = any(marker in lower for marker in (
        "entre em contato com", "precisa entrar em contato", "você vai precisar entrar em contato",
        "procure a equipe", "fale com a equipe", "ligue para a clínica", "ligue para a clinica"
    )) and not any(marker in lower for marker in (
        "vou acionar", "vou avisar", "eu aciono", "deixo encaminhado", "vou encaminhar", "peço para a equipe"
    ))
    if transfer_without_ownership:
        return (
            "Eu conduzo isso por aqui para você não perder tempo. Vou acionar a equipe internamente e já deixo o próximo passo encaminhado. "
            "Para eu direcionar certo: você prefere seguir com a avaliação pela manhã ou pela tarde?"
        )

    passive_markers = (
        "fico à disposição", "fico a disposição", "qualquer coisa", "quando quiser", "se tiver interesse",
        "estou por aqui", "estamos por aqui", "me chama quando", "me avise quando"
    )
    has_passive = any(marker in lower for marker in passive_markers)
    has_clear_cta = "?" in text and any(marker in lower for marker in (
        "posso", "prefere", "qual", "manhã", "manha", "tarde", "horário", "horario", "enviar", "pré-reserva", "pre-reserva", "retorno"
    ))
    if has_passive and not has_clear_cta:
        return re.sub(r"(?i)(fico à disposição|fico a disposição|qualquer coisa[^.!?]*|quando quiser[^.!?]*|se tiver interesse[^.!?]*|estou por aqui|estamos por aqui|me chama quando[^.!?]*)[.!?]*", "", text).strip(" .\n") + \
            "\n\nPara deixar isso bem encaminhado: prefere que eu veja o próximo horário pela manhã ou pela tarde?"

    if "?" not in text:
        if any(marker in inbound_lower for marker in ("valor", "preço", "preco", "plano", "convênio", "convenio", "agenda", "horário", "horario", "consulta", "exame", "prescrição", "prescricao")):
            return text.rstrip(" .") + ".\n\nQual desses pontos você quer que eu encaminhe agora: entender a avaliação ou ver o próximo horário?"
        if len(text) < 450:
            return text.rstrip(" .") + ".\n\nPosso te orientar com o próximo passo agora?"

    return text


def enforce_agendamento_reply_quality(reply: str) -> str:
    """Remove fechamento passivo e bloqueia oferta de agenda para D0/D1."""
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    text = enforce_allowed_scheduling_scope(text)
    lower = text.lower()

    same_day_or_tomorrow = ("hoje" in lower) or ("amanhã" in lower) or ("amanha" in lower)
    scheduling_context = any(token in lower for token in ("horário", "horario", "agenda", "agendar", "consulta", "encaixe", "marcar", "reserv"))
    explicit_block = any(token in lower for token in (
        "não marcamos", "nao marcamos", "não marco", "nao marco",
        "não conseguimos marcar", "nao conseguimos marcar",
        "não oferecemos", "nao oferecemos",
        "não é possível", "nao e possivel", "não consigo", "nao consigo",
    ))
    positive_offer_markers = any(token in lower for token in (
        "tenho", "consigo", "posso", "temos", "há horário", "ha horario",
        "disponível", "disponivel", "encaixe", "reservar", "marcar", "agendar"
    ))
    if same_day_or_tomorrow and scheduling_context and positive_offer_markers and not explicit_block:
        return (
            "Hoje e amanhã não temos disponibilidade. "
            "Consigo verificar para você a partir de D+2. "
            "Prefere manhã ou tarde?"
        )
    passive_markers = (
        "fico à disposição", "fico a disposição", "qualquer coisa",
        "quando quiser", "se tiver interesse", "se quiser marcar",
        "estou por aqui", "estamos por aqui",
    )
    has_passive_close = any(marker in lower for marker in passive_markers)
    has_question = "?" in text
    has_concrete_next_step = any(token in lower for token in ("posso", "prefere", "horário", "horario", "manhã", "manha", "tarde", "agendar", "pré-reserva", "pre-reserva"))
    if has_passive_close and not (has_question or has_concrete_next_step):
        text = text.rstrip(" .") + ".\n\nPara eu te orientar melhor: prefere que eu veja um horário no período da manhã ou da tarde?"
    elif has_passive_close and "?" not in text:
        text = text.rstrip(" .") + ".\n\nQual seria o melhor próximo passo para você agora: entender a avaliação ou ver um horário?"
    return text



def is_agendamento_event(reply: str) -> bool:
    """Detecta quando Clara avançou para agendamento/reserva/pré-consulta."""
    text = (reply or "").strip().lower()
    if not text or text == "no_reply":
        return False
    scheduling_tokens = (
        "agendamento", "agendada", "agendado", "marcada", "marcado",
        "consulta ficou", "consulta está", "consulta esta", "horário reservado", "horario reservado",
        "reserva", "pré-reserva", "pre-reserva", "vou solicitar o link", "link à equipe financeira",
        "link a equipe financeira", "pré-consulta", "pre-consulta", "sua consulta"
    )
    action_tokens = (
        "confirm", "reserv", "marc", "agend", "solicitar o link", "envio aqui em seguida",
        "dados para", "pré-consulta", "pre-consulta"
    )
    # Evita notificar mera pergunta aberta muito genérica, mas captura pré-reserva e link.
    return any(t in text for t in scheduling_tokens) and any(t in text for t in action_tokens)


def notify_internal_agendamento(phone: str, sender_name: Optional[str], inbound_text: str, reply: str) -> None:
    """Notifica Tiaro e Liane por WhatsApp quando Clara agenda/avança agendamento."""
    if not CLARA_NOTIFY_PHONES:
        return
    name = (sender_name or "Nome não identificado").strip()
    msg = (
        "AVISO INTERNO — Clara avançou um agendamento\n\n"
        f"Lead: {name}\n"
        f"Telefone: {phone}\n"
        "Etapa: agendamento/reserva/pré-consulta detectado pelo runtime\n"
        "Próxima ação: conferir agenda, pagamento/pré-consulta e preparo operacional.\n\n"
        f"Mensagem Clara: {(reply or '')[:700]}"
    )
    for target in CLARA_NOTIFY_PHONES:
        try:
            if normalize_phone(target) == normalize_phone(phone):
                continue
            status, body = send_zapi_text(target, msg)
            log(f"internal_agendamento_notify target={target} status={status} body={body[:160]}")
        except Exception as err:
            log(f"internal_agendamento_notify failed target={target}: {err}")


def notify_internal_contact_request(phone: str, sender_name: Optional[str], inbound_text: str, reply: str) -> None:
    """Notifica equipe quando lead pede ligação ou indica preferência por telefone."""
    if not CLARA_NOTIFY_PHONES:
        return
    name = (sender_name or "Nome não identificado").strip()
    msg = (
        "AVISO INTERNO — lead pediu contato por ligação\n\n"
        f"Lead: {name}\n"
        f"Telefone: {phone}\n"
        "Etapa: preferência por ligação detectada pelo runtime\n"
        "Próxima ação: equipe deve assumir/retornar no horário informado pelo lead.\n\n"
        f"Mensagem recebida: {(inbound_text or '')[:500]}\n\n"
        f"Mensagem Clara: {(reply or '')[:500]}"
    )
    for target in CLARA_NOTIFY_PHONES:
        try:
            if normalize_phone(target) == normalize_phone(phone):
                continue
            status, body = send_zapi_text(target, msg)
            log(f"internal_contact_request_notify target={target} status={status} body={body[:160]}")
        except Exception as err:
            log(f"internal_contact_request_notify failed target={target}: {err}")


def notify_internal_clara_failure(phone: str, sender_name: Optional[str], inbound_text: str, stage: str, detail: str = "") -> None:
    """Fail-safe anti-perda: se Clara falhar/ficar sem resposta para lead, humano é acionado."""
    if not CLARA_NOTIFY_PHONES:
        return
    name = (sender_name or "Nome não identificado").strip()
    msg = (
        "ALERTA OPERACIONAL — Clara pode ter perdido resposta de lead\n\n"
        f"Lead: {name}\n"
        f"Telefone: {phone}\n"
        f"Etapa/falha: {stage}\n"
        f"Detalhe: {(detail or 'sem detalhe')[:500]}\n\n"
        "Próxima ação: humano deve conferir a conversa e assumir se a Clara não respondeu.\n\n"
        f"Última mensagem recebida: {(inbound_text or '')[:500]}"
    )
    for target in CLARA_NOTIFY_PHONES:
        try:
            if normalize_phone(target) == normalize_phone(phone):
                continue
            status, body = send_zapi_text(target, msg)
            log(f"internal_clara_failure_notify target={target} stage={stage} status={status} body={body[:160]}")
        except Exception as err:
            log(f"internal_clara_failure_notify failed target={target} stage={stage}: {err}")


def extract_audio_url(payload: Dict[str, Any]) -> Optional[str]:
    """Extrai URL de áudio de payloads comuns da Z-API/WA."""
    candidates = [
        deep_get(payload, "audio", "audioUrl"),
        deep_get(payload, "audio", "url"),
        deep_get(payload, "message", "audioMessage", "url"),
        deep_get(payload, "message", "audio", "url"),
        deep_get(payload, "message", "mediaUrl"),
        deep_get(payload, "data", "audio", "audioUrl"),
        deep_get(payload, "data", "audio", "url"),
        deep_get(payload, "data", "message", "audioMessage", "url"),
        deep_get(payload, "data", "message", "audio", "url"),
        deep_get(payload, "data", "message", "mediaUrl"),
        deep_get(payload, "data", "mediaUrl"),
        payload.get("mediaUrl"),
        payload.get("audioUrl"),
        payload.get("url"),
    ]
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


def is_audio_message(payload: Dict[str, Any]) -> bool:
    if extract_audio_url(payload):
        return True
    types = [
        payload.get("type"),
        payload.get("messageType"),
        deep_get(payload, "message", "type"),
        deep_get(payload, "data", "type"),
        deep_get(payload, "data", "messageType"),
        deep_get(payload, "data", "message", "type"),
    ]
    return any(str(t).strip().lower() in ("audio", "ptt", "voice", "audio_message") for t in types if t is not None)


def download_audio(url: str, timeout: int = 30) -> bytes:
    req = Request(url, method="GET")
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.ogg") -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not configured for audio transcription")
    boundary = "----OpenClawClaraAudioBoundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: audio/ogg\r\n\r\n"
    ).encode("utf-8") + audio_bytes + (
        f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\n{WHISPER_MODEL}\r\n"
        f"--{boundary}--\r\n"
    ).encode("utf-8")
    req = Request(
        "https://api.openai.com/v1/audio/transcriptions",
        data=body,
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
            return (data.get("text") or "").strip()
    except HTTPError as err:
        error_body = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI transcription error {err.code}: {error_body[:400]}") from err


def generate_elevenlabs_tts(text: str) -> bytes:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY not configured for audio reply")
    url = f"{ELEVENLABS_URL}/{ELEVENLABS_VOICE_ID}"
    payload = {
        "text": text,
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    req = Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=60) as resp:
            return resp.read()
    except HTTPError as err:
        error_body = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs TTS error {err.code}: {error_body[:400]}") from err


def generate_openai_tts(text: str) -> bytes:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not configured for audio reply")
    payload = {"model": OPENAI_TTS_MODEL, "voice": OPENAI_TTS_VOICE, "input": text, "format": "mp3"}
    req = Request(
        "https://api.openai.com/v1/audio/speech",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=60) as resp:
            return resp.read()
    except HTTPError as err:
        error_body = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI TTS error {err.code}: {error_body[:400]}") from err


def generate_tts_audio(text: str) -> bytes:
    """Gera áudio para espelhamento. Prioriza ElevenLabs se configurado; senão usa OpenAI TTS."""
    if ELEVENLABS_API_KEY:
        return generate_elevenlabs_tts(text)
    return generate_openai_tts(text)


def send_zapi_audio(phone: str, audio_bytes: bytes) -> Tuple[int, str]:
    if not ZAPI_BASE_URL:
        raise RuntimeError("ZAPI_BASE_URL is empty")
    if not ZAPI_CLIENT_TOKEN:
        raise RuntimeError("ZAPI_CLIENT_TOKEN is empty")
    import base64
    payload = {"phone": phone, "audioBase64": base64.b64encode(audio_bytes).decode("ascii")}
    headers = {"Client-Token": ZAPI_CLIENT_TOKEN}
    url = ZAPI_BASE_URL.rstrip("/") + ZAPI_SEND_AUDIO_PATH
    return post_json(url, payload, headers=headers, timeout=60)



def evaluate_admin_send_action_gate(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Optional enforcement for manual/admin WhatsApp sends.

    Default is off to avoid breaking Clara production continuity. When
    CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE=1, /admin/send must include
    approval_id for the Action Gate. This guard never sends by itself; it only
    blocks/permits the existing send path.
    """
    if not CLARA_ADMIN_SEND_ENFORCE_ACTION_GATE:
        return True, {"mode": "action_gate_not_enforced"}
    approval_id = str(payload.get("approval_id") or "").strip()
    if not approval_id:
        return False, {"mode": "action_gate_enforced", "error": "missing_approval_id", "final": "BLOCK_APPROVAL_ID_REQUIRED"}
    evidence = str(payload.get("approval_evidence") or payload.get("reason") or "admin_send").strip()
    cmd = [
        "python3",
        "/root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/action_gate.py",
        "--agent", "clara-whatsapp",
        "--action", "followup_whatsapp",
        "--sensitivity", "lead",
    ]
    if approval_id:
        cmd += ["--approval-id", approval_id]
    if evidence:
        cmd += ["--evidence", evidence]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=20)
        decision = json.loads(out)
    except Exception as err:
        return False, {"mode": "action_gate_error", "error": str(err)}
    return decision.get("final") == "ALLOW_BY_POLICY_BUT_NO_EXECUTION", decision

def send_zapi_text(phone: str, message: str) -> Tuple[int, str]:
    if not ZAPI_BASE_URL:
        raise RuntimeError("ZAPI_BASE_URL is empty")
    if not ZAPI_CLIENT_TOKEN:
        raise RuntimeError("ZAPI_CLIENT_TOKEN is empty")
    payload = {"phone": phone, "message": message}
    headers = {"Client-Token": ZAPI_CLIENT_TOKEN}
    url = ZAPI_BASE_URL.rstrip("/") + ZAPI_SEND_TEXT_PATH
    return post_json(url, payload, headers=headers, timeout=30)


def zapi_get(path: str, timeout: int = 30) -> Tuple[int, str]:
    if not ZAPI_BASE_URL:
        raise RuntimeError("ZAPI_BASE_URL is empty")
    if not ZAPI_CLIENT_TOKEN:
        raise RuntimeError("ZAPI_CLIENT_TOKEN is empty")
    headers = {"Client-Token": ZAPI_CLIENT_TOKEN}
    url = ZAPI_BASE_URL.rstrip("/") + path
    return get_json(url, headers=headers, timeout=timeout)


def fetch_zapi_tags_catalog() -> Tuple[int, str, Any]:
    status, body = zapi_get("/tags", timeout=30)
    return status, body, parse_json_body(body)


def fetch_zapi_chat_metadata(phone: str) -> Tuple[int, str, Any]:
    status, body = zapi_get(f"/chats/{phone}", timeout=30)
    return status, body, parse_json_body(body)


def build_chat_tags_payload(phone: str) -> Dict[str, Any]:
    chat_status, chat_body, chat = fetch_zapi_chat_metadata(phone)
    tags_status, tags_body, catalog = fetch_zapi_tags_catalog()

    tag_ids = []
    if isinstance(chat, dict):
        raw_tags = chat.get("tags") or []
        if isinstance(raw_tags, list):
            tag_ids = [str(t) for t in raw_tags]

    catalog_by_id: Dict[str, Any] = {}
    if isinstance(catalog, list):
        for item in catalog:
            if isinstance(item, dict) and item.get("id") is not None:
                catalog_by_id[str(item.get("id"))] = item

    resolved = []
    for tag_id in tag_ids:
        meta = catalog_by_id.get(tag_id, {}) if isinstance(catalog_by_id.get(tag_id), dict) else {}
        resolved.append({
            "id": tag_id,
            "name": meta.get("name") or tag_id,
            "color": meta.get("color"),
            "colorHex": meta.get("colorHex"),
        })

    return {
        "ok": 200 <= chat_status < 300 and 200 <= tags_status < 300,
        "phone": phone,
        "chatStatus": chat_status,
        "tagsStatus": tags_status,
        "tagIds": tag_ids,
        "tags": resolved,
        "chat": chat if isinstance(chat, dict) else chat_body[:1000],
        "catalog": catalog if isinstance(catalog, list) else tags_body[:1000],
    }


def allowed_webhook_paths() -> set[str]:
    base_paths = {"/webhook", "/zapi/webhook"}
    if WEBHOOK_PATH_TOKEN:
        return {f"/webhook/{WEBHOOK_PATH_TOKEN}", f"/zapi/webhook/{WEBHOOK_PATH_TOKEN}"}
    return base_paths


def extract_sender_name(payload: Dict[str, Any]) -> Optional[str]:
    return first_nonempty(
        deep_get(payload, "sender", "name"),
        deep_get(payload, "sender", "pushName"),
        deep_get(payload, "message", "senderName"),
        payload.get("senderName"),
        payload.get("pushName"),
    )


def process_quarkclinic_confirmation_reply(phone: str, text: str) -> bool:
    """Atualiza confirmação/cancelamento pendente no QuarkClinic antes do bloqueio RC12.

    Retorna True quando a mensagem pertence ao fluxo de confirmação de agenda,
    mesmo se a resposta for ambígua, para não cair no atendimento comercial da Clara.
    """
    script = Path(QUARK_CONFIRMATION_REPLY_SCRIPT)
    if not script.exists():
        log(f"confirmation_reply_bridge script_missing path={script}")
        return False
    try:
        raw = subprocess.check_output(
            [sys.executable or "python3", str(script), phone, text],
            text=True,
            stderr=subprocess.STDOUT,
            timeout=45,
        )
        result = json.loads(raw.strip().splitlines()[-1]) if raw.strip() else {}
    except Exception as err:
        log(f"confirmation_reply_bridge error phone={phone}: {err}")
        return False

    if not result.get("matched"):
        return False
    log(
        "confirmation_reply_bridge matched "
        f"phone={phone} decision={result.get('decision')} "
        f"updated={result.get('updated', result.get('decision') not in (None, 'unknown'))} "
        f"agendamentoId={result.get('agendamentoId')}"
    )
    return True


class Handler(BaseHTTPRequestHandler):
    server_version = "ZapiClaraBridge/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        log(format % args)

    def _send_json(self, code: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _check_admin_secret(self) -> bool:
        if not BRIDGE_SHARED_SECRET:
            return True
        return self.headers.get("X-Bridge-Secret", "") == BRIDGE_SHARED_SECRET

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query or "")

        if path in ("/healthz", "/health"):
            self._send_json(200, {"ok": True, "service": "zapi-clara-bridge"})
            return
        if path == "/admin/status":
            if not self._check_admin_secret():
                self._send_json(403, {"ok": False, "error": "forbidden"})
                return
            status, body = handle_admin_pause({"action": "status"})
            self._send_json(status, body)
            return
        if path == "/admin/tags":
            if not self._check_admin_secret():
                self._send_json(403, {"ok": False, "error": "forbidden"})
                return
            try:
                status, body, catalog = fetch_zapi_tags_catalog()
                self._send_json(200 if 200 <= status < 300 else 502, {
                    "ok": 200 <= status < 300,
                    "zapiStatus": status,
                    "tags": catalog if isinstance(catalog, list) else [],
                    "zapiBody": body[:1000] if not isinstance(catalog, list) else None,
                })
            except Exception as err:
                log(f"admin_tags failed: {err}")
                self._send_json(500, {"ok": False, "error": str(err)})
            return
        if path == "/admin/contact-tags":
            if not self._check_admin_secret():
                self._send_json(403, {"ok": False, "error": "forbidden"})
                return
            raw_phone = (query.get("phone") or [""])[0]
            phone = normalize_phone(raw_phone)
            if not phone:
                self._send_json(400, {"ok": False, "error": "missing phone"})
                return
            try:
                payload = build_chat_tags_payload(phone)
                self._send_json(200 if payload.get("ok") else 502, payload)
            except Exception as err:
                log(f"admin_contact_tags failed phone={phone}: {err}")
                self._send_json(500, {"ok": False, "phone": phone, "error": str(err)})
            return
        self._send_json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        # Admin: pause/unpause/status (also via POST for actions)
        if path == "/admin/pause":
            if not self._check_admin_secret():
                self._send_json(403, {"ok": False, "error": "forbidden"})
                return
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length or 0)
            try:
                payload = json.loads(raw.decode("utf-8")) if raw else {}
            except json.JSONDecodeError:
                self._send_json(400, {"ok": False, "error": "invalid json"})
                return
            status, body = handle_admin_pause(payload)
            self._send_json(status, body)
            return

        # Admin: envio ativo WhatsApp via Z-API. Uso interno por Clara/Maria em ações reais
        # solicitadas por Tiaro/equipe, sem passar pelo canal Telegram.
        if path == "/admin/send":
            if not self._check_admin_secret():
                self._send_json(403, {"ok": False, "error": "forbidden"})
                return
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length or 0)
            try:
                payload = json.loads(raw.decode("utf-8")) if raw else {}
            except json.JSONDecodeError:
                self._send_json(400, {"ok": False, "error": "invalid json"})
                return

            phone = normalize_phone(str(payload.get("phone", "")))
            message = str(payload.get("message", "")).strip()
            dry_run = bool(payload.get("dry_run") or payload.get("dryRun"))
            force = bool(payload.get("force"))

            if not phone:
                self._send_json(400, {"ok": False, "error": "missing phone"})
                return
            if not message:
                self._send_json(400, {"ok": False, "error": "missing message"})
                return

            exclusion_reason = get_exclusion_reason(phone)
            if exclusion_reason and not force:
                self._send_json(409, {"ok": False, "phone": phone, "blocked": True, "reason": exclusion_reason})
                return

            if dry_run:
                self._send_json(200, {"ok": True, "dry_run": True, "phone": phone, "message_preview": message[:160]})
                return

            try:
                gate_ok, gate_decision = evaluate_admin_send_action_gate(payload)
                if not gate_ok:
                    log(f"admin_send blocked_by_action_gate phone={phone} decision={str(gate_decision)[:300]}")
                    self._send_json(403, {"ok": False, "phone": phone, "blocked": "action_gate", "decision": gate_decision})
                    return
                zapi_status, zapi_body = send_zapi_text(phone, message)
                if 200 <= zapi_status < 300:
                    mark_followup_outbound(phone, "admin_send_followup")
                log(f"admin_send phone={phone} status={zapi_status} preview={message[:120]!r} body={zapi_body[:200]}")
                self._send_json(200 if 200 <= zapi_status < 300 else 502, {
                    "ok": 200 <= zapi_status < 300,
                    "phone": phone,
                    "zapiStatus": zapi_status,
                    "zapiBody": zapi_body[:1000],
                    "actionGate": gate_decision,
                })
            except Exception as err:
                log(f"admin_send failed phone={phone}: {err}")
                self._send_json(500, {"ok": False, "phone": phone, "error": str(err)})
            return

        if path not in allowed_webhook_paths():
            self._send_json(404, {"ok": False, "error": "not found"})
            return
        if BRIDGE_SHARED_SECRET:
            supplied = self.headers.get("X-Bridge-Secret", "")
            if supplied != BRIDGE_SHARED_SECRET:
                self._send_json(403, {"ok": False, "error": "forbidden"})
                return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length or 0)
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {}
        except json.JSONDecodeError:
            self._send_json(400, {"ok": False, "error": "invalid json"})
            return

        if is_from_me(payload):
            phone = extract_phone(payload)
            from_api = payload.get("fromApi") is True or deep_get(payload, "data", "fromApi") is True
            if phone and from_api:
                mark_followup_outbound(phone, "zapi_from_api_outbound")
            elif phone:
                mark_human_activity(phone, note="from_me_outbound_detected")
                set_manual_override(phone, True, note="from_me_outbound_detected", until=time.time() + MANUAL_TAKEOVER_WINDOW_SECONDS)
            reason = "from_api_outbound" if from_api else "from_me"
            log(f"ignored phone={phone or 'missing'} reason={reason} payload_keys={','.join(sorted(payload.keys()))}")
            self._send_json(200, {"ok": True, "ignored": reason})
            return
        if is_group_message(payload):
            log(f"ignored reason=group_message payload_keys={','.join(sorted(payload.keys()))}")
            self._send_json(200, {"ok": True, "ignored": "group_message"})
            return

        fanout_to_apps_script(payload)
        phone = extract_phone(payload)
        text = extract_text(payload)
        is_audio = is_audio_message(payload)
        audio_url = extract_audio_url(payload) if is_audio else None
        sender_name = extract_sender_name(payload)
        message_id = extract_message_id(payload) or f"anon:{phone}:{hash(raw)}"

        if not phone:
            log(f"ignored reason=missing_phone payload_keys={','.join(sorted(payload.keys()))}")
            self._send_json(200, {"ok": True, "ignored": "missing_phone"})
            return
        if not text and not is_audio:
            log(f"ignored phone={phone} reason=non_text_or_empty payload_keys={','.join(sorted(payload.keys()))}")
            self._send_json(200, {"ok": True, "ignored": "non_text_or_empty"})
            return
        event_text = text or "[audio recebido]"
        if not remember_message(message_id):
            log(f"ignored phone={phone} message_id={message_id} reason=duplicate")
            self._send_json(200, {"ok": True, "ignored": "duplicate", "messageId": message_id})
            return
        skip_event, skip_reason = should_skip_event(phone, message_id, event_text)
        if skip_event:
            self._send_json(200, {"ok": True, "ignored": skip_reason, "messageId": message_id, "phone": phone})
            log(f"ignored phone={phone} message_id={message_id} reason={skip_reason} text={event_text[:120]!r}")
            return

        # Respond immediately to avoid webhook timeout, then process async
        self._send_json(200, {"ok": True, "queued": True, "phone": phone})

        import threading
        def process_async():
            processed_text = text or ""
            log(f"processing phone={phone} message_id={message_id} is_audio={is_audio} text={event_text[:180]!r}")
            try:
                if is_audio:
                    if not audio_url:
                        raise RuntimeError("audio message detected but no audio URL found in payload")
                    audio_bytes = download_audio(audio_url)
                    processed_text = transcribe_audio(audio_bytes)
                    if not processed_text:
                        raise RuntimeError("audio transcription returned empty text")
                    log(f"audio_transcribed phone={phone} chars={len(processed_text)}")
                if process_quarkclinic_confirmation_reply(phone, processed_text):
                    return
                paused, reason = should_pause_clara(phone)
                if paused:
                    log(f"blocked phone={phone} reason={reason}")
                    return
                patient_flag = is_existing_patient(phone)
                if patient_flag:
                    log(f"patient_detected phone={phone} source=quarkclinic blocked=RC12")
                    return
                should_reply, reason = should_respond_to_lead(phone, processed_text)
                if not should_reply:
                    log(f"blocked phone={phone} reason={reason}")
                    return
                log(f"lead_allowed phone={phone} reason={reason}")
                clara_input = processed_text
                if is_audio:
                    clara_input = "Mensagem recebida por áudio. Transcrição para resposta comercial: " + processed_text
                reply = call_clara(phone, clara_input, sender_name=sender_name)
                if reply.strip() == "NO_REPLY":
                    log(f"reply=NO_REPLY phone={phone}")
                    notify_internal_clara_failure(phone, sender_name, text, "NO_REPLY", "Modelo retornou NO_REPLY para lead elegível")
                    return
                reply = enforce_no_first_time_question(reply)
                reply = enforce_price_timing(phone, processed_text, reply)
                reply = enforce_program_reasoning(processed_text, reply)
                reply = enforce_plan_question_response(processed_text, reply)
                reply = enforce_objection_handling(processed_text, reply)
                reply = enforce_call_request_response(processed_text, reply)
                reply = enforce_journey_before_scheduling(processed_text, reply)
                reply = enforce_vitor_video_practical_application(processed_text, reply)
                reply = enforce_agendamento_reply_quality(reply)
                block_reply, block_reason = should_block_reply(phone, reply)
                if block_reply:
                    log(f"blocked_reply phone={phone} reason={block_reason} replyPreview={reply[:120]!r}")
                    notify_internal_clara_failure(phone, sender_name, processed_text, "blocked_reply", block_reason or "resposta bloqueada por segurança")
                    return
                sent_as_audio = False
                if is_audio and CLARA_AUDIO_MIRRORING and (ELEVENLABS_API_KEY or OPENAI_API_KEY):
                    try:
                        audio_reply = generate_tts_audio(reply)
                        status, body = send_zapi_audio(phone, audio_reply)
                        sent_as_audio = 200 <= int(status) < 300
                        if not sent_as_audio:
                            log(f"audio_send_failed phone={phone} status={status} body={body[:200]} falling_back=text")
                    except Exception as audio_err:
                        log(f"audio_reply_failed phone={phone}: {audio_err}; falling_back=text")
                        sent_as_audio = False
                if not sent_as_audio:
                    status, body = send_zapi_text(phone, reply)
                if 200 <= int(status) < 300:
                    mark_lead_replied(phone, reply)
                    if is_agendamento_event(reply):
                        notify_internal_agendamento(phone, sender_name, processed_text, reply)
                    if contains_call_request(processed_text):
                        notify_internal_contact_request(phone, sender_name, processed_text, reply)
                log(f"sent phone={phone} mode={'audio' if sent_as_audio else 'text'} zapiStatus={status} replyPreview={reply[:120]!r} zapiBody={body[:200]}")
            except Exception as err:
                log(f"bridge error phone={phone}: {err}")
                try:
                    notify_internal_clara_failure(phone, sender_name, processed_text or event_text, "runtime_exception", str(err))
                except Exception as notify_err:
                    log(f"bridge error notification failed phone={phone}: {notify_err}")

        threading.Thread(target=process_async, daemon=True).start()


def main() -> int:
    missing = []
    if not OPENCLAW_GATEWAY_TOKEN:
        missing.append("OPENCLAW_GATEWAY_TOKEN")
    if not ZAPI_CLIENT_TOKEN:
        missing.append("ZAPI_CLIENT_TOKEN")
    if not ZAPI_BASE_URL:
        missing.append("ZAPI_BASE_URL or ZAPI_INSTANCE_ID+ZAPI_TOKEN")
    if missing:
        log("warning: missing required env vars: " + ", ".join(missing))
    server = ThreadingHTTPServer((BRIDGE_HOST, BRIDGE_PORT), Handler)
    webhook_suffix = f"/webhook/{WEBHOOK_PATH_TOKEN}" if WEBHOOK_PATH_TOKEN else "/webhook"
    log(f"listening on http://{BRIDGE_HOST}:{BRIDGE_PORT} webhook={webhook_suffix} health=/healthz")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("shutting down")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
