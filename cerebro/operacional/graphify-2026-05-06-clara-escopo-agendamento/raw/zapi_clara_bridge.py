#!/usr/bin/env python3
import json
import os
import sys
import time
import hashlib
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional, Tuple
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
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
CLARA_NOTIFY_PHONE = os.getenv("CLARA_NOTIFY_PHONE", "5571986968887")  # Tiaro
CLARA_NOTIFY_PHONES = [p.strip() for p in os.getenv("CLARA_NOTIFY_PHONES", "5571986968887,5571991574827").split(",") if p.strip()]
BRIDGE_SHARED_SECRET = os.getenv("BRIDGE_SHARED_SECRET", "")
WEBHOOK_PATH_TOKEN = os.getenv("WEBHOOK_PATH_TOKEN", "")
DEDUP_TTL_SECONDS = int(os.getenv("DEDUP_TTL_SECONDS", "600"))
HTTP_TIMEOUT_SECONDS = int(os.getenv("HTTP_TIMEOUT_SECONDS", "90"))
CLARA_CONTROL_FILE = os.getenv("CLARA_CONTROL_FILE", "/root/.openclaw/workspace/ops/zapi_bridge/clara_control_state.json")
CLARA_SYSTEM_PROMPT_FILE = os.getenv("CLARA_SYSTEM_PROMPT_FILE", "/root/.openclaw/workspace/ops/zapi_bridge/clara_system_prompt.md")
CLARA_LEADS_FILE = os.getenv("CLARA_LEADS_FILE", "/root/.openclaw/workspace/ops/zapi_bridge/clara_leads_state.json")
CLARA_EVENT_STATE_FILE = os.getenv("CLARA_EVENT_STATE_FILE", "/root/.openclaw/workspace/ops/zapi_bridge/clara_event_state.json")
ACTIVATION_PHRASE = os.getenv("CLARA_ACTIVATION_PHRASE", "Gostaria de saber mais informações sobre o Instituto Vital Slim")
PHONE_COOLDOWN_SECONDS = int(os.getenv("PHONE_COOLDOWN_SECONDS", "45"))
REPEAT_TEXT_WINDOW_SECONDS = int(os.getenv("REPEAT_TEXT_WINDOW_SECONDS", "180"))
REPEAT_REPLY_WINDOW_SECONDS = int(os.getenv("REPEAT_REPLY_WINDOW_SECONDS", "300"))
MANUAL_TAKEOVER_WINDOW_SECONDS = int(os.getenv("MANUAL_TAKEOVER_WINDOW_SECONDS", str(6 * 60 * 60)))
HUMAN_RECENT_MESSAGE_WINDOW_SECONDS = int(os.getenv("HUMAN_RECENT_MESSAGE_WINDOW_SECONDS", "1800"))
CLARA_ACTIVE_LEAD_WINDOW_SECONDS = int(os.getenv("CLARA_ACTIVE_LEAD_WINDOW_SECONDS", str(14 * 24 * 60 * 60)))

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

    try:
        if last_reply_at and (now - float(last_reply_at) <= PHONE_COOLDOWN_SECONDS):
            return True, "phone_cooldown_active"
    except Exception:
        pass

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
        deep_get(payload, "text"),
        deep_get(payload, "message", "text"),
        deep_get(payload, "message", "body"),
        deep_get(payload, "message", "conversation"),
        deep_get(payload, "message", "extendedTextMessage", "text"),
        deep_get(payload, "body"),
        deep_get(payload, "conversation"),
        deep_get(payload, "msg", "body"),
        deep_get(payload, "data", "text", "message"),
        deep_get(payload, "data", "message", "text"),
    ]
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


def normalize_phone(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
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
    ]
    for candidate in candidates:
        phone = normalize_phone(candidate if isinstance(candidate, str) else None)
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
    safe = {k: entry.get(k) for k in ("source", "inbound_count", "reply_count", "first_seen_at", "last_inbound_at", "last_reply_at") if entry.get(k) is not None}
    if not safe:
        return ""
    return "\n\nContexto operacional interno deste lead (não mencionar ao lead): " + json.dumps(safe, ensure_ascii=False)


def call_clara(phone: str, text: str, sender_name: Optional[str] = None) -> str:
    if not OPENCLAW_GATEWAY_TOKEN:
        raise RuntimeError("OPENCLAW_GATEWAY_TOKEN is empty")
    instructions = load_clara_prompt()
    if sender_name:
        instructions += f"\n\nNome do contato nesta conversa: {sender_name}."
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
            "Para garantir que tudo fique bem organizado para você, nós não marcamos para o mesmo dia nem para o dia seguinte. "
            "O ideal é reservar a partir de D+2, assim a equipe consegue preparar sua pré-consulta e todos os detalhes com cuidado. "
            "Prefere que eu veja um horário pela manhã ou pela tarde?"
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

def send_zapi_text(phone: str, message: str) -> Tuple[int, str]:
    if not ZAPI_BASE_URL:
        raise RuntimeError("ZAPI_BASE_URL is empty")
    if not ZAPI_CLIENT_TOKEN:
        raise RuntimeError("ZAPI_CLIENT_TOKEN is empty")
    payload = {"phone": phone, "message": message}
    headers = {"Client-Token": ZAPI_CLIENT_TOKEN}
    url = ZAPI_BASE_URL.rstrip("/") + ZAPI_SEND_TEXT_PATH
    return post_json(url, payload, headers=headers, timeout=30)


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
        if self.path in ("/healthz", "/health"):
            self._send_json(200, {"ok": True, "service": "zapi-clara-bridge"})
            return
        if self.path == "/admin/status":
            if not self._check_admin_secret():
                self._send_json(403, {"ok": False, "error": "forbidden"})
                return
            status, body = handle_admin_pause({"action": "status"})
            self._send_json(status, body)
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
            if phone:
                mark_human_activity(phone, note="from_me_outbound_detected")
                set_manual_override(phone, True, note="from_me_outbound_detected", until=time.time() + MANUAL_TAKEOVER_WINDOW_SECONDS)
            self._send_json(200, {"ok": True, "ignored": "from_me"})
            return
        if is_group_message(payload):
            self._send_json(200, {"ok": True, "ignored": "group_message"})
            return

        fanout_to_apps_script(payload)
        phone = extract_phone(payload)
        text = extract_text(payload)
        sender_name = extract_sender_name(payload)
        message_id = extract_message_id(payload) or f"anon:{phone}:{hash(raw)}"

        if not phone:
            self._send_json(200, {"ok": True, "ignored": "missing_phone"})
            return
        if not text:
            self._send_json(200, {"ok": True, "ignored": "non_text_or_empty"})
            return
        if not remember_message(message_id):
            self._send_json(200, {"ok": True, "ignored": "duplicate", "messageId": message_id})
            return
        skip_event, skip_reason = should_skip_event(phone, message_id, text)
        if skip_event:
            self._send_json(200, {"ok": True, "ignored": skip_reason, "messageId": message_id, "phone": phone})
            log(f"ignored phone={phone} message_id={message_id} reason={skip_reason} text={text[:120]!r}")
            return

        # Respond immediately to avoid webhook timeout, then process async
        self._send_json(200, {"ok": True, "queued": True, "phone": phone})

        import threading
        def process_async():
            log(f"processing phone={phone} message_id={message_id} text={text[:180]!r}")
            try:
                paused, reason = should_pause_clara(phone)
                if paused:
                    log(f"blocked phone={phone} reason={reason}")
                    return
                patient_flag = is_existing_patient(phone)
                if patient_flag:
                    log(f"patient_detected phone={phone} source=quarkclinic blocked=RC12")
                    return
                should_reply, reason = should_respond_to_lead(phone, text)
                if not should_reply:
                    log(f"blocked phone={phone} reason={reason}")
                    return
                log(f"lead_allowed phone={phone} reason={reason}")
                reply = call_clara(phone, text, sender_name=sender_name)
                if reply.strip() == "NO_REPLY":
                    log(f"reply=NO_REPLY phone={phone}")
                    return
                reply = enforce_agendamento_reply_quality(reply)
                block_reply, block_reason = should_block_reply(phone, reply)
                if block_reply:
                    log(f"blocked_reply phone={phone} reason={block_reason} replyPreview={reply[:120]!r}")
                    return
                status, body = send_zapi_text(phone, reply)
                if 200 <= int(status) < 300:
                    mark_lead_replied(phone, reply)
                    if is_agendamento_event(reply):
                        notify_internal_agendamento(phone, sender_name, text, reply)
                log(f"sent phone={phone} zapiStatus={status} replyPreview={reply[:120]!r} zapiBody={body[:200]}")
            except Exception as err:
                log(f"bridge error phone={phone}: {err}")

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
