#!/usr/bin/env python3
import json
import os
import sys
import time
import hashlib
import re
import subprocess
import threading
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
QUARKCLINIC_API_CLIENT = os.getenv(
    "QUARKCLINIC_API_CLIENT",
    "/root/.openclaw/workspace/snapshot/openclaw-home/workspace/snapshot/openclaw-home/workspace/skills/quarkclinic-api/scripts/quarkclinic_api.py",
)
OPENCLAW_GATEWAY_TOKEN = os.getenv("OPENCLAW_GATEWAY_TOKEN", "")
OPENCLAW_AGENT_REF = os.getenv("OPENCLAW_AGENT_REF", "openclaw/main")
OPENCLAW_MODEL_OVERRIDE = os.getenv("OPENCLAW_MODEL_OVERRIDE", "openai/gpt-5.4")
OPENCLAW_MODEL_FALLBACKS = [m.strip() for m in os.getenv("OPENCLAW_MODEL_FALLBACKS", "openai-codex/gpt-5.5,openai-codex/gpt-5.4").split(",") if m.strip()]
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
CLARA_REQUIRE_THINKING = os.getenv("CLARA_REQUIRE_THINKING", "1").strip().lower() in ("1", "true", "yes", "on")
CLARA_THINKING_TIMEOUT_SECONDS = int(os.getenv("CLARA_THINKING_TIMEOUT_SECONDS", "45"))
CLARA_ZAPI_DELAY_TYPING_SECONDS = int(os.getenv("CLARA_ZAPI_DELAY_TYPING_SECONDS", "10"))
CLARA_HUMAN_CHUNKING_ENABLED = os.getenv("CLARA_HUMAN_CHUNKING_ENABLED", "1").strip().lower() in ("1", "true", "yes", "on")
CLARA_HUMAN_CHUNK_MAX_CHARS = int(os.getenv("CLARA_HUMAN_CHUNK_MAX_CHARS", "230"))

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
# Saída de áudio da Clara: ElevenLabs é a rota principal. O TTS genérico/OpenAI fica apenas como fallback
# operacional e nunca deve passar pelo OpenRouter.
CLARA_TTS_PRIMARY = os.getenv("CLARA_TTS_PRIMARY", "elevenlabs").strip().lower()
CLARA_TTS_FALLBACK = os.getenv("CLARA_TTS_FALLBACK", "openai").strip().lower()
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
QUARKCLINIC_NO_PATIENT_CACHE_SECONDS = int(os.getenv("QUARKCLINIC_NO_PATIENT_CACHE_SECONDS", "3600"))

CLARA_PERMANENT_KNOWLEDGE_FILE = os.getenv("CLARA_PERMANENT_KNOWLEDGE_FILE", "/root/.openclaw/workspace/ops/zapi_bridge/clara_permanent_knowledge.md")
CLARA_EVENT_STATE_FILE = os.getenv("CLARA_EVENT_STATE_FILE", "/root/.openclaw/workspace/ops/zapi_bridge/clara_event_state.json")
CLARA_EXCLUSIONS_FILE = os.getenv("CLARA_EXCLUSIONS_FILE", "/root/.openclaw/workspace/ops/zapi_bridge/clara_exclusions.json")
CLARA_AUDIT_DIR = os.getenv("CLARA_AUDIT_DIR", "/root/.openclaw/workspace/ops/zapi_bridge/audit")
CLARA_BRIDGE_LOG_FILE = os.getenv("CLARA_BRIDGE_LOG_FILE", "/root/.openclaw/workspace/ops/zapi_bridge/zapi_clara_bridge_runtime.log")
IVS_RUNTIME_ENFORCEMENT_SCRIPT = os.getenv("IVS_RUNTIME_ENFORCEMENT_SCRIPT", "/root/.openclaw/workspace/skills/ivs-agent-operating-layer/scripts/runtime_enforcement.py")
CLARA_ZAPI_RUNTIME_ENFORCE = os.getenv("CLARA_ZAPI_RUNTIME_ENFORCE", "1").strip().lower() in ("1", "true", "yes", "on")
ACTIVATION_PHRASE = os.getenv("CLARA_ACTIVATION_PHRASE", "Gostaria de saber mais informações sobre o Instituto Vital Slim")
PHONE_COOLDOWN_SECONDS = int(os.getenv("PHONE_COOLDOWN_SECONDS", "45"))
REPEAT_TEXT_WINDOW_SECONDS = int(os.getenv("REPEAT_TEXT_WINDOW_SECONDS", "180"))
REPEAT_REPLY_WINDOW_SECONDS = int(os.getenv("REPEAT_REPLY_WINDOW_SECONDS", "300"))
MANUAL_TAKEOVER_WINDOW_SECONDS = int(os.getenv("MANUAL_TAKEOVER_WINDOW_SECONDS", str(6 * 60 * 60)))
# Tiaro 2026-06-01: qualquer mensagem enviada manualmente pela equipe no WhatsApp
# assume a conversa e pausa a Clara imediatamente. Por padrão fica indefinido
# até liberação manual; CLARA_HUMAN_TAKEOVER_INDEFINITE=0 volta para TTL.
CLARA_HUMAN_TAKEOVER_INDEFINITE = os.getenv("CLARA_HUMAN_TAKEOVER_INDEFINITE", "1").strip().lower() in ("1", "true", "yes", "on")
HUMAN_RECENT_MESSAGE_WINDOW_SECONDS = int(os.getenv("HUMAN_RECENT_MESSAGE_WINDOW_SECONDS", "1800"))
CLARA_ACTIVE_LEAD_WINDOW_SECONDS = int(os.getenv("CLARA_ACTIVE_LEAD_WINDOW_SECONDS", str(14 * 24 * 60 * 60)))
QUARK_CONFIRMATION_REPLY_SCRIPT = os.getenv(
    "QUARK_CONFIRMATION_REPLY_SCRIPT",
    "/root/cerebro-vital-slim/ops/quarkclinic_confirmations/process_reply.py",
)

SEEN: "OrderedDict[str, float]" = OrderedDict()
PROCESSING_PHONES_LOCK = threading.Lock()
PROCESSING_PHONES = set()


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        log_path = Path(CLARA_BRIDGE_LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # Log em arquivo nunca pode derrubar a Clara.
        pass


def redact_operational_text(text: str) -> str:
    s = str(text or "")
    s = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[email oculto]", s)
    s = re.sub(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "[CPF oculto]", s)
    s = re.sub(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b", "[CNPJ oculto]", s)
    s = re.sub(r"(\+?55\s*)?(\(?\d{2}\)?\s*)?9?\d{4}[-\s]?\d{4}\b", "[telefone oculto]", s)
    s = re.sub(r"\b\d{5}-?\d{3}\b", "[CEP oculto]", s)
    return s


def append_webhook_audit(payload: Dict[str, Any], raw: bytes, path: str) -> None:
    """Spool append-only para relatórios: preserva todo webhook recebido antes dos filtros.

    Corrige a dependência exclusiva da planilha/Apps Script e do endpoint /chats,
    que podem falhar ou retornar só metadata. O arquivo local é read-only para
    relatório e não altera WhatsApp, tags, Clara ou Z-API.
    """
    try:
        now = time.time()
        day = time.strftime("%Y-%m-%d", time.gmtime(now))
        audit_dir = Path(CLARA_AUDIT_DIR)
        audit_dir.mkdir(parents=True, exist_ok=True)
        phone = extract_phone(payload) if isinstance(payload, dict) else ""
        text = extract_text(payload) if isinstance(payload, dict) else ""
        item = {
            "received_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
            "received_at_ms": int(now * 1000),
            "path": path,
            "phone": phone,
            "message_id": extract_message_id(payload) if isinstance(payload, dict) else "",
            "from_me": is_from_me(payload) if isinstance(payload, dict) else False,
            "from_api": bool(payload.get("fromApi") is True or deep_get(payload, "data", "fromApi") is True) if isinstance(payload, dict) else False,
            "is_group": is_group_message(payload) if isinstance(payload, dict) else False,
            "sender_name": extract_sender_name(payload) if isinstance(payload, dict) else "",
            "text": redact_operational_text(text),
            "payload_keys": sorted(payload.keys()) if isinstance(payload, dict) else [],
            "payload": payload,
            "raw_sha1": hashlib.sha1(raw or b"").hexdigest(),
        }
        with (audit_dir / f"zapi_webhook_events_{day}.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
    except Exception as err:
        log(f"webhook_audit_write_failed: {err}")


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

def acquire_phone_processing(phone: str) -> bool:
    """Evita respostas concorrentes para mensagens enviadas em rajada pelo mesmo lead.

    A Z-API entrega cada bolha como webhook separado. Sem trava por telefone, duas
    mensagens curtas em sequência (ex.: "No momento nenhum" + "Obrigado") podem
    gerar duas respostas da Clara, uma delas fora de tom. O segundo evento continua
    salvo no audit/fanout, mas não dispara outra resposta enquanto a primeira está
    em processamento.
    """
    key = normalize_phone(phone) or str(phone or "")
    with PROCESSING_PHONES_LOCK:
        if key in PROCESSING_PHONES:
            return False
        PROCESSING_PHONES.add(key)
        return True


def release_phone_processing(phone: str) -> None:
    key = normalize_phone(phone) or str(phone or "")
    with PROCESSING_PHONES_LOCK:
        PROCESSING_PHONES.discard(key)


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


def get_variant_event_entry(phone: str) -> Dict[str, Any]:
    """Retorna o evento mais recente entre variantes seguras do telefone."""
    state = load_event_state()
    events = state.setdefault("events", {})
    best: Dict[str, Any] = {}
    best_updated_at = -1.0
    for candidate in phone_lookup_variants(phone):
        entry = events.get(candidate)
        if not isinstance(entry, dict):
            continue
        try:
            updated_at = float(entry.get("updated_at") or 0)
        except Exception:
            updated_at = 0.0
        if updated_at >= best_updated_at:
            best = entry
            best_updated_at = updated_at
    return best


def mirror_phone_event_entry(phone: str, patch: Dict[str, Any]) -> None:
    """Espelha um patch operacional em variantes BR com/sem nono dígito."""
    state = load_event_state()
    events = state.setdefault("events", {})
    now = int(time.time())
    for candidate in phone_lookup_variants(phone):
        entry = events.get(candidate)
        if not isinstance(entry, dict):
            entry = {}
        entry.update(patch)
        entry["updated_at"] = now
        events[candidate] = entry
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
    mirror_phone_event_entry(phone, {
        "human_recent_message_at": now,
        "human_recent_message_note": note,
    })


def set_manual_override(phone: str, active: bool, note: Optional[str] = None, until: Optional[float] = None) -> None:
    state = load_control_state()
    overrides = state.setdefault("manual_overrides", {})
    for candidate in phone_lookup_variants(phone):
        if active:
            overrides[candidate] = {
                "until": until,
                "note": note or "manual_override",
                "set_at": int(time.time()),
                "owner": "human",
            }
        else:
            overrides.pop(candidate, None)
    state["manual_overrides"] = overrides
    save_control_state(state)


def set_manual_override_for_ids(ids: list[str], active: bool, note: Optional[str] = None, until: Optional[float] = None) -> None:
    for candidate in ids:
        if candidate:
            set_manual_override(candidate, active, note=note, until=until)


def mark_human_activity_for_ids(ids: list[str], note: str = "human_recent_message") -> None:
    for candidate in ids:
        if candidate:
            mark_human_activity(candidate, note=note)


def get_payload_manual_override_reason(phone: str, payload: Dict[str, Any]) -> Optional[str]:
    for candidate in extract_payload_contact_ids(payload, phone):
        active, reason = is_manual_override_active(candidate)
        if active:
            if candidate != phone:
                log(f"manual_override_alias_match phone={phone} matched={candidate} reason={reason}")
            return reason or "manual_override"
        recent, recent_reason = has_recent_human_activity(candidate)
        if recent:
            if candidate != phone:
                log(f"human_activity_alias_match phone={phone} matched={candidate} reason={recent_reason}")
            return recent_reason or "human_recent_message"
    return None


def has_recent_human_activity(phone: str) -> Tuple[bool, Optional[str]]:
    entry = get_variant_event_entry(phone)
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

    # RC-65: duplicar a mesma pergunta no mesmo lead quebra a lógica da conversa.
    # A proteção antiga só logava e deixava enviar para evitar autopausa global, mas
    # isso gerou repetição visível ao lead (ex.: mesma pergunta de descoberta 3x).
    # A correção segura é bloquear apenas a bolha duplicada, sem pausar a Clara.
    try:
        if last_reply_hash == reply_hash and last_reply_at and (now - float(last_reply_at) <= REPEAT_REPLY_WINDOW_SECONDS):
            update_phone_event_entry(phone, {
                "last_reply_hash": reply_hash,
                "last_reply_at": now,
                "last_duplicate_reply_blocked_at": now,
            })
            log(f"duplicate_reply_blocked_no_global_pause phone={phone}")
            return True, "duplicate_reply_blocked_no_global_pause"
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
    if not digits:
        return None

    # WhatsApp/Z-API sometimes emits Brazilian mobile contacts without the
    # ninth digit (ex.: 557581418631), while the visible WhatsApp chat and
    # the reliable send target are +55 DDD 9XXXX-XXXX. Canonicalize only the
    # safe BR mobile shape: 55 + DDD + 8-digit subscriber starting with 6-9.
    # Landlines (2-5) and non-BR/LID identifiers are left untouched.
    if len(digits) == 12 and digits.startswith("55"):
        subscriber = digits[4:]
        if subscriber and subscriber[0] in "6789":
            digits = digits[:4] + "9" + subscriber
    return digits


def extract_phone_from_text(value: Any) -> Optional[str]:
    """Extrai telefone real de campos textuais como chatName/senderName.

    A Z-API às vezes envia o campo `phone` como LID numérico (ex.: 159...);
    nesses casos o número real pode aparecer no nome do chat como +55 DD XXXXX-XXXX.
    Preferimos o telefone real quando ele está visível no payload.
    """
    if value is None:
        return None
    text = str(value)
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None
    for size in (13, 12):
        for i in range(0, max(0, len(digits) - size + 1)):
            chunk = digits[i:i+size]
            if chunk.startswith("55"):
                phone = normalize_phone(chunk)
                if phone and phone.startswith("55") and len(phone) in (12, 13):
                    return phone
    for size in (11, 10):
        if len(digits) == size:
            phone = normalize_phone("55" + digits)
            if phone and phone.startswith("55") and len(phone) in (12, 13):
                return phone
    return None


def extract_phone(payload: Dict[str, Any]) -> Optional[str]:
    text_candidates = [
        payload.get("chatName"),
        payload.get("senderName"),
        payload.get("participantPhone"),
        deep_get(payload, "sender", "name"),
        deep_get(payload, "data", "chatName"),
        deep_get(payload, "data", "senderName"),
    ]
    for candidate in text_candidates:
        phone = extract_phone_from_text(candidate)
        if phone:
            return phone

    candidates = [
        payload.get("phone"),
        payload.get("from"),
        payload.get("fromNumber"),
        payload.get("senderPhone"),
        payload.get("participantPhone"),
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


def _extract_phone_candidates_from_obj(obj: Any) -> list[str]:
    """Extrai possíveis telefones de um retorno QuarkClinic sem depender do nome exato do campo."""
    found: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            k = str(key).lower()
            if isinstance(value, (dict, list)):
                found.extend(_extract_phone_candidates_from_obj(value))
            elif any(token in k for token in ("telefone", "celular", "whatsapp", "contato", "fone")):
                digits = "".join(ch for ch in str(value or "") if ch.isdigit())
                if digits:
                    found.append(digits)
    elif isinstance(obj, list):
        for item in obj:
            found.extend(_extract_phone_candidates_from_obj(item))
    return found


def _quark_response_items(data: Any) -> list[dict]:
    if not isinstance(data, dict):
        return []
    response = data.get("response")
    if isinstance(response, dict) and isinstance(response.get("response"), list):
        return [x for x in response.get("response", []) if isinstance(x, dict)]
    if isinstance(response, list):
        return [x for x in response if isinstance(x, dict)]
    return []


def _query_quarkclinic_patients_by_phone(digits_without_ddi: str) -> list[dict]:
    """Consulta pacientes via cliente seguro existente.

    Importante: alguns parâmetros da API podem retornar lista ampla mesmo com filtro.
    Por isso o chamador só considera paciente quando há telefone exato nas linhas retornadas.
    """
    client = Path(QUARKCLINIC_API_CLIENT)
    if client.exists():
        raw = subprocess.check_output([
            "python3", str(client), "GET", "/v1/pacientes",
            "--query", f"telefone={digits_without_ddi}",
            "--query", "limite=100",
            "--timeout", "20",
        ], text=True, timeout=30)
        return _quark_response_items(json.loads(raw))

    if QUARKCLINIC_AUTH_TOKEN:
        from urllib.request import Request as _Req, urlopen as _urlopen
        url = f"{QUARKCLINIC_BASE_URL}/v1/pacientes?telefone={digits_without_ddi}&limite=100"
        req = _Req(url, headers={"Auth-token": QUARKCLINIC_AUTH_TOKEN})
        with _urlopen(req, timeout=12) as resp:
            return _quark_response_items(json.loads(resp.read().decode()))

    return []


def mark_quarkclinic_cache(phone: str, ok: bool, is_patient: bool, reason: str) -> None:
    """Registra resultado recente da checagem QuarkClinic no estado do lead.

    O objetivo é evitar perda de lead por falha transitória da API segundos depois
    de um `no_match` real. Não libera paciente: match exato continua bloqueando.
    """
    try:
        state = load_leads_state()
        leads = state.setdefault("leads", {})
        entry = leads.get(phone) if isinstance(leads.get(phone), dict) else {}
        entry.update({
            "quarkclinic_checked_at": int(time.time()),
            "quarkclinic_ok": bool(ok),
            "quarkclinic_is_patient": bool(is_patient),
            "quarkclinic_reason": reason,
            "updated_at": int(time.time()),
        })
        leads[phone] = entry
        save_leads_state(state)
    except Exception as err:
        log(f"quarkclinic_cache_write_failed phone={phone}: {err}")


def has_recent_quarkclinic_no_patient_cache(phone: str) -> bool:
    try:
        _matched, entry = get_lead_lookup_entry(phone)
        if not entry:
            return False
        if not entry.get("quarkclinic_ok") or entry.get("quarkclinic_is_patient"):
            return False
        checked_at = float(entry.get("quarkclinic_checked_at") or 0)
        return checked_at > 0 and (time.time() - checked_at) <= QUARKCLINIC_NO_PATIENT_CACHE_SECONDS
    except Exception as err:
        log(f"quarkclinic_cache_read_failed phone={phone}: {err}")
        return False


def quarkclinic_patient_check(phone: str) -> Tuple[bool, bool, str]:
    """Consulta obrigatória no QuarkClinic antes da Clara responder.

    Retorna (consulta_ok, is_patient, reason).
    Regra base: sempre consultar o número de celular no QuarkClinic.
    Hotfix 2026-06-10: se a API falhar de forma transitória, mas o mesmo lead
    teve `no_match` real recente, Clara pode continuar a conversa para não perder
    lead. Match exato de paciente continua bloqueando.
    """
    variants = phone_lookup_variants(phone)
    targets = set()
    queries = []
    for candidate in variants:
        digits = "".join(ch for ch in candidate if ch.isdigit())
        if not digits:
            continue
        targets.add(digits)
        if digits.startswith("55") and len(digits) > 11:
            targets.add(digits[2:])
            queries.append(digits[2:])
        else:
            queries.append(digits)
    queries = list(dict.fromkeys(queries))
    if not queries:
        return False, False, "quarkclinic_no_phone_digits"
    try:
        for query in queries:
            patients = _query_quarkclinic_patients_by_phone(query)
            for patient in patients:
                patient_phones = set()
                for raw_phone in _extract_phone_candidates_from_obj(patient):
                    patient_phones.add(raw_phone)
                    if raw_phone.startswith("55") and len(raw_phone) > 11:
                        patient_phones.add(raw_phone[2:])
                    elif len(raw_phone) >= 10:
                        patient_phones.add("55" + raw_phone)
                if targets.intersection(patient_phones):
                    log(f"quarkclinic_patient_exact_match phone={phone} query={query}")
                    mark_quarkclinic_cache(phone, True, True, "quarkclinic_patient_exact_match")
                    return True, True, "quarkclinic_patient_exact_match"
        log(f"quarkclinic_patient_no_match phone={phone} queries={','.join(queries)}")
        mark_quarkclinic_cache(phone, True, False, "quarkclinic_patient_no_match")
        return True, False, "quarkclinic_patient_no_match"
    except Exception as err:
        if has_recent_quarkclinic_no_patient_cache(phone):
            log(f"quarkclinic_check_failed_using_recent_no_patient_cache phone={phone}: {err}")
            return True, False, "quarkclinic_recent_no_patient_cache_after_failure"
        log(f"quarkclinic_check_failed_blocking phone={phone}: {err}")
        return False, False, "quarkclinic_check_failed"


def is_existing_patient(phone: str) -> bool:
    ok, is_patient, _reason = quarkclinic_patient_check(phone)
    return bool(ok and is_patient)


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


def phone_lookup_variants(phone: str) -> list[str]:
    """Retorna variantes seguras para buscar telefone em listas legadas.

    A Z-API alterna contatos BR com/sem nono dígito. A lista de pacientes
    (`clara_exclusions.json`) pode ter sido sincronizada em qualquer uma das
    formas; por isso todo bloqueio de paciente precisa procurar por ambas.
    """
    normalized = normalize_phone(phone) or ""
    digits = "".join(ch for ch in str(phone or "") if ch.isdigit())
    variants: list[str] = []
    for candidate in (digits, normalized):
        if candidate and candidate not in variants:
            variants.append(candidate)
    # BR mobile com nono dígito: 55 + DDD + 9 + 8 dígitos -> variante sem o 9.
    if len(normalized) == 13 and normalized.startswith("55") and normalized[4] == "9":
        without_ninth = normalized[:4] + normalized[5:]
        if without_ninth not in variants:
            variants.append(without_ninth)
    # BR mobile sem nono dígito: 55 + DDD + 8 dígitos -> variante com o 9.
    if len(digits) == 12 and digits.startswith("55"):
        subscriber = digits[4:]
        if subscriber and subscriber[0] in "6789":
            with_ninth = digits[:4] + "9" + subscriber
            if with_ninth not in variants:
                variants.append(with_ninth)
    return variants


def get_exclusion_entry(phone: str) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
    state = load_exclusions_state()
    phones = state.get("phones") or {}
    if not isinstance(phones, dict):
        return None, None
    for candidate in phone_lookup_variants(phone):
        entry = phones.get(candidate)
        if isinstance(entry, dict):
            return candidate, entry
    return None, None


def get_exclusion_reason(phone: str) -> Optional[str]:
    matched_phone, entry = get_exclusion_entry(phone)
    if not isinstance(entry, dict):
        return None
    reason = str(entry.get("reason") or "excluded_phone")
    source = str(entry.get("source") or "")
    # Exceção explícita do Tiaro: alguns contatos sincronizados como pacientes podem ser leads ativos.
    if reason.startswith("lead_exception") or source == "tiaro_lead_exception":
        return None

    # Correção operacional 2026-05-18 — paciente primeiro por variante canônica:
    # A Z-API pode entregar 5571997098879 enquanto a exclusão veio como 557197098879
    # (e 5571991583056 enquanto a exclusão veio como 557191583056). Qualquer variante
    # encontrada em `clara_exclusions.json` bloqueia antes de Clara gerar/enviar resposta.
    if matched_phone and matched_phone != phone:
        log(f"exclusion_variant_match phone={phone} matched={matched_phone} reason={reason}")
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
    now = time.time()
    for candidate in phone_lookup_variants(phone):
        entry = overrides.get(candidate)
        if not isinstance(entry, dict):
            continue
        until = entry.get("until")
        note = entry.get("note")
        if until is None:
            return True, note or "manual_override"
        try:
            if float(until) > now:
                return True, note or "manual_override_until"
        except Exception:
            return True, note or "manual_override_invalid_until"
        overrides.pop(candidate, None)
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


def has_clear_lead_intent(text: str) -> bool:
    """Detecta intenção comercial explícita para evitar falso bloqueio de lead por lista de pacientes/conhecidos.

    Uso limitado: não libera paciente QuarkClinic; apenas permite que o fluxo avance
    até as demais checagens quando o contato veio de anúncio/manifestou interesse.
    """
    t = (text or "").strip().lower()
    if not t:
        return False
    phrases = [
        "tenho interesse", "tenho interêsse", "queria mais informações", "quero mais informações",
        "mais informações", "gostaria de saber", "saber valores", "quero saber valores",
        "qual o valor", "quanto custa", "vi o anúncio", "vim pelo anúncio", "anuncio", "anúncio",
        "facebook", "instagram", "meta", "emagrecer", "emagrecimento", "estômago alto",
        "estomago alto", "barriga", "reduzir medidas", "desinchar", "quero agendar",
        "quero avaliação", "quero uma avaliação", "marcar avaliação", "agendar avaliação",
    ]
    return any(p in t for p in phrases) or has_activation_phrase(text)


def should_bypass_exclusion_for_lead_intent(phone: str, text: str) -> Tuple[bool, Optional[str]]:
    reason = get_exclusion_reason(phone)
    if not reason:
        return False, None
    _, entry = get_exclusion_entry(phone)
    source = str((entry or {}).get("source") or "")

    # Bloqueios manuais/de não-resposta continuam absolutos.
    if reason == "patient_do_not_reply" or source == "manual":
        return False, reason

    # Correção operacional Tiaro/Maria 2026-05-25: `patient_bridge_known` /
    # `bridge_contexto_paciente` é base auxiliar, não fonte final de paciente.
    # Ela estava derrubando leads com mensagem comercial curta (ex.: "reposição hormonal")
    # antes da checagem real RC-12. A partir daqui, esse tipo de colisão SEMPRE
    # passa para a consulta QuarkClinic; se for paciente real, o bloqueio acontece
    # em `is_existing_patient`. Manual/do-not-reply continuam absolutos acima.
    if reason == "patient_bridge_known" or source == "bridge_contexto_paciente":
        # RC-43 (2026-05-29): paciente/contato conhecido não pode ser liberado
        # só porque apareceu em leads_state antigo. A conversa da Paola estava
        # tagueada como VIP, sem tag Lead, e a Clara entrou na conversa do Tiaro.
        # A única exceção segura é tag explícita Lead na Z-API; VIP/Paciente/etc.
        # mantêm o bloqueio humano.
        ok_tags, tag_names, tag_ids = get_zapi_contact_tag_names_safe(phone)
        if not ok_tags:
            return False, f"{reason}:zapi_tag_check_unavailable"
        if "lead" not in tag_names:
            return False, f"{reason}:zapi_not_lead_tags={','.join(tag_names or tag_ids or ['none'])}"
        if is_known_lead(phone):
            mark_lead_active(phone, "bypass_patient_bridge_known_lead_with_zapi_lead_tag")
            return True, f"bypass_patient_bridge_known_lead_with_zapi_lead_tag:{reason}"
        mark_lead_active(phone, "bypass_patient_bridge_to_quarkclinic_rc12_zapi_lead_tag")
        return True, f"bypass_patient_bridge_to_quarkclinic_rc12_zapi_lead_tag:{reason}"

    # Se já está em janela ativa de lead, a exclusão antiga não deve interromper a continuidade.
    if is_active_lead_window(phone):
        mark_lead_active(phone, "bypass_exclusion_active_lead_window")
        return True, f"bypass_exclusion_active_lead_window:{reason}"
    # Se a primeira/atual mensagem tem intenção comercial clara, permitir seguir para as demais proteções.
    if has_clear_lead_intent(text):
        mark_lead_active(phone, "bypass_exclusion_clear_lead_intent")
        return True, f"bypass_exclusion_clear_lead_intent:{reason}"
    return False, reason


def get_lead_lookup_entry(phone: str) -> Tuple[Optional[str], Dict[str, Any]]:
    """Busca lead considerando variantes BR com/sem nono dígito.

    A mesma pessoa pode chegar pela Z-API com 5571999999999 e ser registrada em
    outra base como 557199999999. Para continuidade comercial, a janela de lead
    precisa ser consultada pelas mesmas variantes usadas no bloqueio de pacientes.
    """
    state = load_leads_state()
    leads = state.get("leads") or {}
    if not isinstance(leads, dict):
        return None, {}
    for candidate in phone_lookup_variants(phone):
        entry = leads.get(candidate)
        if isinstance(entry, dict):
            return candidate, entry
    return None, {}


def is_known_lead(phone: str) -> bool:
    matched, _ = get_lead_lookup_entry(phone)
    return bool(matched)


def get_lead_entry(phone: str) -> Dict[str, Any]:
    _, entry = get_lead_lookup_entry(phone)
    return entry


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


def update_lead_entry(phone: str, patch: Dict[str, Any]) -> None:
    if not phone:
        return
    state = load_leads_state()
    leads = state.setdefault("leads", {})
    key, entry = get_lead_lookup_entry(phone)
    if not key:
        key = phone
        entry = leads.get(phone) if isinstance(leads.get(phone), dict) else {}
    entry.update(patch or {})
    entry["updated_at"] = int(time.time())
    leads[key] = entry
    save_leads_state(state)


def extract_confirmed_lead_name(text: str) -> Optional[str]:
    raw = (text or "").strip()
    if not raw:
        return None
    patterns = [
        r"\bmeu nome [ée]\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç' -]{1,40})",
        r"\bme chamo\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç' -]{1,40})",
        r"\bpode me chamar de\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç' -]{1,40})",
        r"\baqui é\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç' -]{1,40})",
        r"\beu sou\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç' -]{1,40})",
        r"\bsou a\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç' -]{1,40})",
        r"\bsou o\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç' -]{1,40})",
    ]
    for pattern in patterns:
        m = re.search(pattern, raw, flags=re.IGNORECASE)
        if not m:
            continue
        candidate = re.sub(r"\s+", " ", m.group(1)).strip(" .,!?:;\n\r\t")
        candidate = candidate.split(" ")[0].strip()
        if len(candidate) >= 2:
            return candidate
    return None


def update_confirmed_lead_name(phone: str, text: str) -> Optional[str]:
    confirmed_name = extract_confirmed_lead_name(text)
    if not confirmed_name:
        return None
    state = load_leads_state()
    leads = state.setdefault("leads", {})
    entry = leads.get(phone) if isinstance(leads.get(phone), dict) else {}
    entry["name_confirmed"] = True
    entry["confirmed_name"] = confirmed_name
    entry["name_confirmed_source"] = "lead_inbound_explicit"
    entry["name_confirmed_at"] = int(time.time())
    entry["updated_at"] = int(time.time())
    leads[phone] = entry
    save_leads_state(state)
    return confirmed_name


def has_confirmed_lead_name(phone: str) -> bool:
    entry = get_lead_entry(phone)
    # RC-34 hardening: legado de estado não basta. Só considerar nome liberado
    # quando a origem registrada for uma declaração explícita escrita pelo lead.
    return bool(
        isinstance(entry, dict)
        and entry.get("name_confirmed")
        and entry.get("confirmed_name")
        and entry.get("name_confirmed_source") == "lead_inbound_explicit"
    )


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
        # RC-43: leads_state sozinho não basta para retomar conversa se a Z-API
        # mostra tag não-comercial (VIP/Paciente/etc.) e ausência de Lead.
        ok_tags, tag_names, tag_ids = get_zapi_contact_tag_names_safe(phone)
        if ok_tags and tag_names and "lead" not in tag_names:
            return False, f"known_lead_blocked_zapi_not_lead_tags={','.join(tag_names or tag_ids)}"
        # Regra operacional Tiaro 2026-05-25: lead é conduzido pela Clara até o
        # agendamento. Janela expirada não pode matar continuidade comercial;
        # bloqueios válidos continuam sendo paciente QuarkClinic, manual takeover,
        # intervenção humana recente ou exclusão manual explícita.
        mark_lead_active(phone, "known_lead_until_scheduling")
        return True, "known_lead_until_scheduling"

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



def get_recent_lead_texts(phone: str, limit: int = 8) -> list[str]:
    """Retorna últimas mensagens reais do lead a partir do audit spool Z-API."""
    try:
        variants = set(phone_lookup_variants(phone))
        rows = []
        audit_dir = Path(CLARA_AUDIT_DIR)
        files = sorted(audit_dir.glob("zapi_webhook_events_*.jsonl"))[-3:]
        for file_path in files:
            try:
                with file_path.open("r", encoding="utf-8") as fh:
                    for line in fh:
                        try:
                            item = json.loads(line)
                        except Exception:
                            continue
                        item_phone = normalize_phone(item.get("phone")) or ""
                        if item_phone not in variants or item.get("from_me"):
                            continue
                        text = str(item.get("text") or "").strip()
                        if text:
                            rows.append((str(item.get("received_at_utc") or ""), re.sub(r"\s+", " ", text)[:700]))
            except Exception as err:
                log(f"recent_lead_texts_file_read_failed file={file_path} error={err}")
        return [text for _ts, text in rows[-limit:]]
    except Exception as err:
        log(f"recent_lead_texts_build_failed phone={phone} error={err}")
        return []


def enforce_outbound_price_safety(phone: str, message: str, inbound_text: str = "") -> str:
    """Trava final para qualquer saída, inclusive /admin/send.

    Incidente 2026-06-10: em contingência, /admin/send enviou preço após o lead
    responder só "Emagrecimento". A partir daqui, toda saída com dinheiro passa
    pela mesma política RC-40/RC-50, não apenas respostas geradas pela Clara.
    """
    text = (message or "").strip()
    if not text or text == "NO_REPLY" or not contains_money_value(text):
        return text
    entry = get_phone_event_entry(phone)
    lead_texts = get_recent_lead_texts(phone, limit=8)
    has_real_recent_context = any(has_price_context_text(t) for t in lead_texts)
    rc68_context_ready = bool(entry.get("price_context_ready")) and str(entry.get("price_context_source") or "").startswith("rc68_")
    if bool(entry.get("price_context_ready")) and (has_real_recent_context or rc68_context_ready):
        return text
    candidate = (inbound_text or "").strip() or (lead_texts[-1] if lead_texts else "")
    if is_bare_objective_category(candidate):
        log(f"rc51_outbound_price_safety_rewrite_category phone={phone} inbound={candidate[:80]!r} messagePreview={text[:120]!r}")
        return build_price_category_deepening_reply(candidate)
    if has_real_recent_context:
        return text
    log(f"rc51_outbound_price_safety_rewrite_no_context phone={phone} messagePreview={text[:120]!r}")
    return (
        "Claro, eu te explico direitinho. Antes, para eu não te passar uma informação solta: "
        "o que mais está te incomodando hoje e fez você buscar ajuda agora?"
    )


def build_recent_conversation_context(phone: str, limit: int = 14) -> str:
    """Monta contexto recente real do WhatsApp para a Clara ler antes de responder.

    RC-46: a sessão do modelo ajuda, mas não é suficiente como garantia
    operacional. Antes de pensar e antes de responder, o bridge injeta um
    recorte factual das últimas mensagens do audit Z-API, incluindo falas do
    lead e respostas enviadas pela clínica.
    """
    try:
        variants = set(phone_lookup_variants(phone))
        rows = []
        audit_dir = Path(CLARA_AUDIT_DIR)
        files = sorted(audit_dir.glob("zapi_webhook_events_*.jsonl"))[-3:]
        for file_path in files:
            try:
                with file_path.open("r", encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            item = json.loads(line)
                        except Exception:
                            continue
                        item_phone = normalize_phone(item.get("phone")) or ""
                        if item_phone not in variants:
                            continue
                        text = str(item.get("text") or "").strip()
                        if not text:
                            continue
                        # Ignora ecos/status vazios, mas mantém fromApi/fromMe porque são
                        # justamente as respostas recentes da Clara/clínica.
                        ts = str(item.get("received_at_utc") or "")
                        role = "CLARA/CLÍNICA" if item.get("from_me") else "LEAD"
                        rows.append((ts, role, re.sub(r"\s+", " ", text)[:700]))
            except Exception as err:
                log(f"rc46_context_file_read_failed file={file_path} error={err}")
        if not rows:
            return ""
        rows = rows[-limit:]
        lines = ["\n\nCONTEXTO RECENTE REAL DO WHATSAPP — LEIA ANTES DE RESPONDER:"]
        for ts, role, text in rows:
            lines.append(f"- {ts} {role}: {text}")
        lines.append(
            "REGRA RC-46: a próxima resposta deve continuar essa conversa. "
            "É proibido reiniciar atendimento, mandar 'Oi' genérico ou ignorar a última pergunta do lead."
        )
        return "\n".join(lines)
    except Exception as err:
        log(f"rc46_context_build_failed phone={phone} error={err}")
        return ""


def load_clara_prompt() -> str:
    path = Path(CLARA_SYSTEM_PROMPT_FILE)
    try:
        text = path.read_text(encoding="utf-8").strip()
        if text:
            return text
        raise RuntimeError("empty prompt file")
    except Exception as err:
        raise RuntimeError(f"failed to load Clara prompt from {path}: {err}") from err




def load_clara_permanent_knowledge() -> str:
    """Carrega conhecimento permanente validado da Clara. Falha silenciosa para não derrubar produção."""
    try:
        path = Path(CLARA_PERMANENT_KNOWLEDGE_FILE)
        if not path.exists():
            return ""
        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        if not text:
            return ""
        return text[-6000:]
    except Exception as err:
        log(f"clara_permanent_knowledge_load_failed: {err}")
        return ""


def build_lead_context(phone: str) -> str:
    entry = get_lead_entry(phone)
    if not entry:
        return ""
    safe = {k: entry.get(k) for k in ("source", "inbound_count", "reply_count", "first_seen_at", "last_inbound_at", "last_reply_at", "last_reply_preview", "internal_note") if entry.get(k) is not None}
    if not safe:
        return ""
    return "\n\nContexto operacional interno deste lead (não mencionar ao lead): " + json.dumps(safe, ensure_ascii=False)


def extract_openclaw_output_text(data: Dict[str, Any]) -> str:
    output = data.get("output") or []
    texts = []
    for item in output:
        if not isinstance(item, dict):
            continue
        for part in item.get("content") or []:
            if isinstance(part, dict) and part.get("type") == "output_text" and isinstance(part.get("text"), str):
                texts.append(part["text"])
    return "\n\n".join(part.strip() for part in texts if part and part.strip()).strip()


def openclaw_response(phone: str, text: str, instructions: str, session_key: str, timeout: int = HTTP_TIMEOUT_SECONDS) -> str:
    if not OPENCLAW_GATEWAY_TOKEN:
        raise RuntimeError("OPENCLAW_GATEWAY_TOKEN is empty")
    payload = {
        "model": OPENCLAW_AGENT_REF,
        "input": text,
        "user": f"zapi:{phone}",
        "instructions": instructions,
    }
    _agent_id_for_header = OPENCLAW_AGENT_REF.split("/", 1)[1] if "/" in OPENCLAW_AGENT_REF else OPENCLAW_AGENT_REF
    base_headers = {
        "Authorization": f"Bearer {OPENCLAW_GATEWAY_TOKEN}",
        "x-openclaw-session-key": session_key,
        "x-openclaw-message-channel": "whatsapp",
        "x-openclaw-agent-id": _agent_id_for_header,
    }
    models_to_try = []
    for candidate in [OPENCLAW_MODEL_OVERRIDE] + OPENCLAW_MODEL_FALLBACKS:
        if candidate and candidate not in models_to_try:
            models_to_try.append(candidate)
    last_error = ""
    for idx, model_name in enumerate(models_to_try):
        headers = dict(base_headers)
        headers["x-openclaw-model"] = model_name
        try:
            status, body = post_json(OPENCLAW_GATEWAY_URL, payload, headers=headers, timeout=timeout)
            if 200 <= status < 300:
                data = json.loads(body)
                if data.get("status") == "failed":
                    last_error = f"model={model_name} failed_status body={body[:600]}"
                    log(f"openclaw_model_failed phone={phone} model={model_name} idx={idx} body={body[:300]}")
                    continue
                if idx > 0:
                    log(f"openclaw_model_fallback_used phone={phone} primary={OPENCLAW_MODEL_OVERRIDE} fallback={model_name}")
                return extract_openclaw_output_text(data)
            last_error = f"model={model_name} status={status} body={body[:600]}"
            log(f"openclaw_model_http_error phone={phone} model={model_name} status={status} body={body[:300]}")
        except Exception as err:
            last_error = f"model={model_name} exception={type(err).__name__}: {err}"
            log(f"openclaw_model_exception phone={phone} model={model_name}: {err}")
    raise RuntimeError(f"OpenClaw gateway error all_models_failed {last_error[:700]}")


def call_clara_thinking_gate(phone: str, text: str, base_instructions: str, recent_context: str = "") -> str:
    """Passo obrigatório de deliberação antes da resposta ao lead.

    Não é cadeia de pensamento exposta; é um checklist operacional curto para
    forçar a Clara a classificar intenção/risco/próxima pergunta antes de redigir.
    Se este passo falhar com CLARA_REQUIRE_THINKING=1, a resposta não é enviada.
    """
    thinking_instructions = base_instructions + """

MODO INTERNO OBRIGATÓRIO — NÃO É MENSAGEM PARA O LEAD.
Antes de qualquer resposta da Clara, gere somente um JSON compacto com:
- intent: intenção provável do lead
- risk_checks: lista curta com riscos de erro que devem ser evitados
- must_answer: o que precisa ser respondido objetivamente
- must_ask: uma única pergunta útil, se fizer sentido
- forbidden: frases/atalhos que não podem aparecer
Não escreva a resposta final. Não use markdown.
"""
    gate_input = (recent_context.strip() + "\n\n" if recent_context else "") + "Mensagem atual do lead no WhatsApp:\n" + text.strip()
    plan = openclaw_response(
        phone,
        gate_input,
        thinking_instructions,
        session_key=build_session_key(phone) + ":thinking",
        timeout=CLARA_THINKING_TIMEOUT_SECONDS,
    ).strip()
    if not plan or plan == "NO_REPLY":
        raise RuntimeError("clara_thinking_gate_empty")
    return plan[:1800]


def call_clara(phone: str, text: str, sender_name: Optional[str] = None) -> str:
    recent_context = build_recent_conversation_context(phone)
    instructions = load_clara_prompt()
    permanent_knowledge = load_clara_permanent_knowledge()
    if permanent_knowledge:
        instructions += "\n\nCONHECIMENTO PERMANENTE VALIDADO DA CLARA — usar como treinamento operacional canônico, sem mencionar ao lead:\n" + permanent_knowledge
    # RC-34 (2026-05-08): não injetar nome do perfil WhatsApp no prompt da Clara.
    # Clara deve perguntar o nome diretamente ao lead e só personalizar após confirmação no chat.
    instructions += build_lead_context(phone)
    instructions += "\n\nTRAVA RC-34 INEGOCIÁVEL: não use nome do perfil, nome do contato, nome da campanha, senderName/pushName, título do WhatsApp ou metadado. Antes de chamar o lead pelo nome, ele precisa ter escrito ou confirmado o próprio nome na conversa. Se não houver confirmação explícita, cumprimente sem nome."

    thinking_plan = ""
    if CLARA_REQUIRE_THINKING:
        thinking_plan = call_clara_thinking_gate(phone, text, instructions, recent_context=recent_context)
        log(f"clara_thinking_gate_ok phone={phone} chars={len(thinking_plan)} preview={thinking_plan[:180]!r}")

    if recent_context:
        instructions += "\n\nTRAVA RC-64 — LEITURA DE CONTEXTO ANTES DE FOLLOW-UP: se o CONTEXTO RECENTE REAL DO WHATSAPP já trouxer dor/tema declarado pelo lead (ex.: menopausa, engordou/ganho de peso, ansiedade, cansaço, libido, sono, hormônios), a próxima resposta DEVE retomar esse tema nominalmente. É proibido perguntar de novo de forma genérica 'o que está te incomodando' ou 'o que te trouxe' como se fosse primeira conversa. Antes de escrever, identifique: tema declarado, última pergunta pendente e próximo micro-passo específico."
        instructions += recent_context
    if thinking_plan:
        instructions += "\n\nPlano interno obrigatório já gerado antes da resposta. Use como trava operacional, sem mencionar ao lead e sem expor JSON/checklist:\n" + thinking_plan
    instructions += "\n\nRegra de saída: responda apenas com o texto da mensagem WhatsApp. Mensagem curta, humana, uma pergunta por vez. Termine com uma pergunta útil e específica. Só proponha agenda/horário/próximo passo quando já houver contexto mínimo do lead. Em abertura genérica, é proibido usar a frase 'Posso te orientar com o próximo passo agora?'. Se não houver resposta adequada, responda exatamente NO_REPLY."

    reply = openclaw_response(phone, text, instructions, session_key=build_session_key(phone))
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


def enforce_rc39_no_generic_next_step(reply: str) -> str:
    """RC-39: remove CTA genérico de 'próximo passo' antes de contexto mínimo.

    Incidente 2026-05-21: mesmo com RC-37 no prompt, a Clara voltou a mandar
    "Posso te orientar com o próximo passo agora?" na abertura. Essa frase fica
    proibida como muleta genérica. Quando houver maturidade, o CTA precisa ser
    concreto (ex.: entender avaliação, verificar horário, pedir dado), não a
    expressão vaga "próximo passo".
    """
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"

    # Remove a frase exata e variações próximas em qualquer ponto da resposta.
    patterns = [
        r"(?is)\s*posso\s+te\s+orientar\s+com\s+o\s+pr[oó]ximo\s+passo\s+agora\s*\?",
        r"(?is)\s*posso\s+te\s+explicar\s+o\s+pr[oó]ximo\s+passo\s+agora\s*\?",
        r"(?is)\s*quer\s+que\s+eu\s+te\s+oriente\s+com\s+o\s+pr[oó]ximo\s+passo\s*\?",
    ]
    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned).strip()

    # Se ainda houver um bloco genérico de próximo passo junto com descoberta, remove o bloco.
    lower = cleaned.lower()
    discovery_markers = (
        "me conta", "o que está te incomodando", "o que esta te incomodando",
        "para eu entender", "para eu te orientar melhor", "o que fez você procurar",
        "o que fez voce procurar",
    )
    generic_next_step = ("próximo passo" in lower or "proximo passo" in lower) and any(m in lower for m in discovery_markers)
    if generic_next_step:
        blocks = [b.strip() for b in re.split(r"\n\s*\n", cleaned) if b.strip()]
        kept = [b for b in blocks if "próximo passo" not in b.lower() and "proximo passo" not in b.lower()]
        cleaned = "\n\n".join(kept).strip() or cleaned

    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip(" \n")
    if not cleaned:
        return "Para eu te orientar melhor: o que mais está te incomodando hoje?"
    return cleaned


def contains_location_question(text: str) -> bool:
    """Detecta pergunta simples de localização/unidade.

    RC-45: pergunta como "vocês atendem em Salvador?" não é abertura
    genérica. Se a Clara já está em conversa, o runtime não pode substituir
    a resposta por acolhimento inicial.
    """
    lower = (text or "").lower()
    return any(token in lower for token in (
        "onde fica", "endereço", "endereco", "localização", "localizacao",
        "local", "fica onde", "vocês atendem", "voces atendem", "atendem aqui",
        "atende aqui", "em salvador", "salvador", "lauro de freitas",
        "buraquinho", "estação villas", "estacao villas"
    ))


def is_generic_opening_reply(reply: str) -> bool:
    lower = (reply or "").strip().lower()
    if not lower:
        return False
    return (
        "que bom te receber por aqui" in lower
        and "me conta um pouquinho" in lower
        and "o que está te incomodando hoje" in lower or
        "que bom te receber por aqui" in lower
        and "me conta um pouquinho" in lower
        and "o que esta te incomodando hoje" in lower
    )


def contains_commercial_decline(text: str) -> bool:
    """Detecta recusa/escape comercial curto que exige quebra de objeção, não reabertura."""
    lower = (text or "").strip().lower()
    compact = re.sub(r"[^a-záàâãéêíóôõúç]+", " ", lower).strip()
    if compact in {
        "não obrigado", "nao obrigado", "não obrigada", "nao obrigada",
        "obrigado", "obrigada", "não", "nao", "não quero", "nao quero",
        "vou pensar", "preciso pensar", "depois eu vejo", "depois vejo",
        "agora não", "agora nao", "não por enquanto", "nao por enquanto",
        "no momento não", "no momento nao", "no momento nenhum",
    }:
        return True
    return any(token in lower for token in (
        "achei caro", "muito caro", "valor alto", "não tenho condições", "nao tenho condicoes",
        "sem condições", "sem condicoes", "não consigo pagar", "nao consigo pagar",
        "vou deixar pra depois", "vou deixar para depois", "deixa pra depois", "deixa para depois",
        "no momento não", "no momento nao", "no momento nenhum",
    ))


def contains_financial_no_fit_decline(text: str) -> bool:
    """Lead declarou impossibilidade financeira: não entra em follow-up ativo.

    RC-70: "não tenho condições" / "fora das minhas possibilidades" não é
    pausa temporária nem lead frio; é NQ financeiro até nova mensagem espontânea.
    """
    lower = (text or "").strip().lower()
    compact = re.sub(r"[^a-záàâãéêíóôõúç0-9]+", " ", lower).strip()
    if any(ok in compact for ok in (
        "dentro das minhas condicoes", "dentro das minhas condições",
        "cabe nas minhas condicoes", "cabe nas minhas condições",
    )):
        return False
    patterns = (
        r"\bn[ãa]o tenho condi[cç][õo]es\b",
        r"\bsem condi[cç][õo]es\b",
        r"\bsem condi[cç][õo]es financeiras\b",
        r"\bn[ãa]o consigo pagar\b",
        r"\bn[ãa]o posso pagar\b",
        r"\bfora (?:do meu or[cç]amento|de minhas possibilidades|das minhas possibilidades)\b",
        r"\bt[áa] fora de (?:minha|minhas) possibilidade",
    )
    return any(re.search(pattern, compact) for pattern in patterns)


def recent_context_has_financial_no_fit_decline(phone: str, limit: int = 18) -> bool:
    texts = get_recent_lead_texts(phone, limit=limit)
    return any(contains_financial_no_fit_decline(t) for t in texts)


def non_lead_tag_reason(tag_names: list[str]) -> Optional[str]:
    tag_set = {str(t or "").strip().lower() for t in (tag_names or [])}
    blocked = tag_set.intersection({
        "nao qualificado", "não qualificado", "sem condicoes financeiras", "sem condições financeiras",
        "perdeu por convenio", "perdeu por convênio", "perdeu por distancia", "perdeu por distância",
        "curioso/frio", "atendimento diferente", "nq", "sem perfil",
    })
    if blocked:
        return "zapi_non_qualified_tag=" + ",".join(sorted(blocked))
    return None


def contains_hard_final_decline(text: str) -> bool:
    """Recusa final/educada em que insistir piora a experiência."""
    lower = (text or "").strip().lower()
    compact = re.sub(r"[^a-záàâãéêíóôõúç]+", " ", lower).strip()
    return compact in {
        "no momento nenhum", "no momento não", "no momento nao",
        "não quero obrigado", "nao quero obrigado", "não quero obrigada", "nao quero obrigada",
        "não obg", "nao obg", "não obrigada", "nao obrigada", "não obrigado", "nao obrigado",
    } or "no momento não" in lower or "no momento nao" in lower or "no momento nenhum" in lower


def contains_distance_final_decline(text: str) -> bool:
    """Detecta desistência final por distância/logística.

    RC-67: se o lead já disse que distância inviabiliza e agradece/recusa,
    Clara deve encerrar com respeito. Não pode transformar em agenda.
    """
    lower = (text or "").strip().lower()
    compact = re.sub(r"[^a-záàâãéêíóôõúç]+", " ", lower).strip()
    distance_marker = any(marker in lower for marker in (
        "longe pra mim", "longe para mim", "muito longe", "distância", "distancia",
        "fica longe", "é longe", "e longe", "inviabiliza", "não consigo ir", "nao consigo ir",
    ))
    final_marker = any(marker in lower for marker in (
        "não obg", "nao obg", "não obrigada", "nao obrigada", "não obrigado", "nao obrigado",
        "obg pela atenção", "obg pela atencao", "obrigada pela atenção", "obrigado pela atenção",
        "obrigada pela atencao", "obrigado pela atencao", "pela atenção", "pela atencao",
        "deixa", "vou deixar", "não vou", "nao vou", "sem condições", "sem condicoes",
    )) or compact in {"longe para mim", "longe pra mim", "muito longe"}
    return distance_marker and final_marker


def build_distance_final_close_reply() -> str:
    return (
        "Entendo. Obrigada por me avisar.\n\n"
        "Não vou insistir. Se em outro momento fizer sentido para você vir até Lauro de Freitas, é só me chamar por aqui."
    )


def contains_polite_conversation_close(text: str) -> bool:
    """Detecta agradecimento/despedida que deve encerrar sem reabrir SPIN.

    Incidente 2026-06-30: lead disse "grata", "muito obrigada pela informação",
    "bjs"/"Deus abençoe" e a Clara reabriu a mesma pergunta de descoberta.
    """
    lower = (text or "").strip().lower()
    compact = re.sub(r"[^a-záàâãéêíóôõúç]+", " ", lower).strip()
    if compact in {
        "grata", "grato", "obrigada", "obrigado", "muito obrigada", "muito obrigado",
        "muito obrigada pela informação", "muito obrigado pela informação",
        "obrigada pela informação", "obrigado pela informação", "agradeço", "agradeco",
        "bjs", "beijos", "beijo", "um beijo", "deus abençoe", "deus abencoe",
        "deus abençoe vcs", "deus abencoe vcs", "amém", "amem",
    }:
        return True
    return any(marker in lower for marker in (
        "obrigada pela informação", "obrigado pela informação", "muito obrigada pela informação",
        "muito obrigado pela informação", "agradeço a informação", "agradeco a informacao",
        "deus abençoe", "deus abencoe",
    )) or any(re.search(rf"(?<![a-záàâãéêíóôõúç]){token}(?![a-záàâãéêíóôõúç])", lower) for token in (
        "grata", "grato", "bjs", "beijos", "beijo", "obrigada", "obrigado", "amém", "amem"
    ))


def build_polite_close_no_reopen_reply(inbound_text: str = "") -> str:
    lower = (inbound_text or "").lower()
    if "deus abençoe" in lower or "deus abencoe" in lower or "amém" in lower or "amem" in lower:
        return "Amém. Que Deus abençoe você também."
    if "bjs" in lower or "beijo" in lower:
        return "Um beijo. Se precisar no futuro, estou por aqui."
    return "Por nada. Se precisar no futuro, estou por aqui."


def recent_context_has_hard_final_decline(phone: str) -> bool:
    ctx = build_recent_conversation_context(phone, limit=5).lower()
    return any(marker in ctx for marker in ("no momento nenhum", "no momento não", "no momento nao"))


def build_respectful_final_close_reply() -> str:
    return (
        "Claro, sem problema. Obrigada por me responder.\n\n"
        "Não vou insistir. Se depois das festas você quiser retomar com calma, é só me chamar por aqui."
    )

def recent_context_mentions_price_or_schedule(phone: str) -> bool:
    """Verifica se o contexto recente indica etapa comercial explícita.

    RC-48: não tratar um "não" curto como objeção comercial só porque a conversa
    mencionou consulta/avaliação. A recuperação de preço só pode entrar quando
    o histórico recente tiver preço, investimento, desconto, reserva ou proposta
    concreta de horário/agendamento.
    """
    ctx = build_recent_conversation_context(phone, limit=8).lower()
    if not ctx:
        return False
    return any(marker in ctx for marker in (
        "r$", "valor", "investimento", "preço", "preco", "desconto",
        "900", "1.000", "1000", "300", "reserva", "sinal",
        "horários disponíveis", "horarios disponiveis", "verificar os melhores horários",
        "verificar os melhores horarios", "garantir a vaga", "agendamento hoje",
        "posso reservar", "quer que eu reserve", "vaga para",
    ))


def build_short_decline_context_reply() -> str:
    return (
        "Entendi. Obrigada por me responder.\n\n"
        "Para eu não seguir por um caminho errado: quando você disse não, quis dizer que ainda não tentou acompanhamento/tratamento antes, "
        "ou que agora não quer seguir com a avaliação?"
    )

def build_commercial_decline_recovery_reply() -> str:
    return (
        "Entendo. É um investimento, e faz sentido decidir com calma.\n\n"
        "A consulta inicial é uma avaliação médica completa com a Dra. Daniely, incluindo histórico, composição corporal e direcionamento individualizado.\n\n"
        "Para eu não te pressionar nem te deixar sem resposta: o que pesa mais agora — o investimento ou entender melhor o que está incluído?"
    )


def contains_evaluation_explanation_request(text: str) -> bool:
    """Detecta pedido direto de explicação sobre avaliação/consulta.

    RC-58: quando o lead pede "tudo que puder explicar" ou pergunta sobre
    avaliação, o runtime não pode transformar isso em nova descoberta genérica;
    deve explicar e avançar a conversa.
    """
    lower = (text or "").lower()
    explanation_markers = ("explicar", "explique", "entender", "saber", "informar", "orientar")
    evaluation_markers = ("avaliação", "avaliacao", "consulta", "atendimento", "tudo o que", "tudo que", "puder")
    return any(m in lower for m in explanation_markers) and any(m in lower for m in evaluation_markers)


def build_evaluation_explanation_reply() -> str:
    return (
        "Claro. Pelo que você me contou, faz sentido uma avaliação completa. "
        "A consulta com a Dra. Daniely serve justamente para entender esse conjunto: "
        "cansaço, sono ruim, dificuldade para emagrecer, ansiedade, libido e pressão.\n\n"
        "Primeiro ela avalia seu histórico, exames e composição corporal para identificar "
        "o que pode estar pesando no seu caso. Você quer que eu te explique como funciona essa primeira avaliação?"
    )


def contains_weight_belly_metabolism_context(text: str) -> bool:
    lower = (text or "").lower()
    return any(marker in lower for marker in (
        "barriga", "gordinha", "gordinho", "metabolismo", "perder peso",
        "emagrec", "engord", "ganho de peso", "aumento de peso", "peso",
        "menopausa", "climatério", "climaterio", "hormonal", "ansiedade",
        "117 kg", "cento e dezessete"
    ))


def contains_menopause_weight_context(text: str) -> bool:
    lower = (text or "").lower()
    return any(marker in lower for marker in ("menopausa", "climatério", "climaterio")) and any(marker in lower for marker in (
        "engord", "ganho de peso", "aumento de peso", "peso", "emagrec", "barriga"
    ))


def build_contextual_menopause_weight_reply() -> str:
    return (
        "Entendi. Pelo que você já trouxe, a menopausa e o ganho de peso merecem mesmo um olhar mais cuidadoso.\n\n"
        "Nessa fase, pode fazer sentido avaliar fatores hormonais, metabólicos, composição corporal, sono e rotina antes de qualquer conduta.\n\n"
        "Você chegou a investigar isso recentemente com exames ou ainda não olhou com profundidade?"
    )


def build_contextual_weight_belly_reply(inbound_text: str) -> str:
    if contains_inbound_scheduling_intent(inbound_text):
        return (
            "Perfeito. Pelo que você trouxe — ansiedade, dificuldade para perder peso e barriga como principal incômodo — "
            "faz sentido começar pela avaliação com a Dra. Daniely.\n\n"
            "Nessa consulta ela entende seu histórico, exames, composição corporal e rotina para direcionar um caminho seguro para o seu caso. "
            "Para eu seguir com o agendamento: você prefere que eu veja horário pela manhã ou pela tarde?"
        )
    return (
        "Entendi. Isso que você contou é uma informação importante: quando a dificuldade vem desde a infância, com sensação de metabolismo lento e barriga como principal incômodo, "
        "não adianta olhar só como dieta.\n\n"
        "A avaliação com a Dra. Daniely serve justamente para entender o que pode estar travando seu resultado e direcionar o melhor caminho com segurança. "
        "Você quer que eu veja o próximo horário para essa avaliação?"
    )


def build_text_runtime_failsafe_reply(inbound_text: str) -> str:
    """Fail-safe textual: lead elegível nunca deve ficar sem continuidade.

    Usado apenas após exceção técnica depois de todos os gates de escopo.
    """
    if contains_evaluation_explanation_request(inbound_text):
        return build_evaluation_explanation_reply()
    if contains_menopause_weight_context(inbound_text):
        return build_contextual_menopause_weight_reply()
    if contains_weight_belly_metabolism_context(inbound_text) or contains_inbound_scheduling_intent(inbound_text):
        return build_contextual_weight_belly_reply(inbound_text)
    return build_spin_continuation_reply()


def enforce_no_reopening_after_context(phone: str, inbound_text: str, reply: str) -> str:
    """RC-45: impede reabertura genérica no meio da conversa.

    Se já houve resposta da Clara ou múltiplas entradas do lead, a resposta
    não pode voltar para "Oi! Que bom te receber...". Isso corrige o caso em
    que um enforcer de descoberta transformou uma pergunta de localização em
    mensagem inicial sem sentido.
    """
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    entry = get_lead_entry(phone)
    active_context = int(entry.get("reply_count") or 0) > 0 or int(entry.get("inbound_count") or 0) > 1
    if active_context and contains_distance_final_decline(inbound_text):
        log(f"rc67_distance_final_decline_no_schedule phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        return build_distance_final_close_reply()
    if active_context and contains_polite_conversation_close(inbound_text):
        log(f"rc65_polite_close_no_reopen applied phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        return build_polite_close_no_reopen_reply(inbound_text)
    if active_context and (contains_hard_final_decline(inbound_text) or recent_context_has_hard_final_decline(phone)):
        log(f"rc49_respect_final_decline applied phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        return build_respectful_final_close_reply()
    if contains_financial_no_fit_decline(inbound_text):
        log(f"rc70_financial_no_fit_close phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        return "Entendo. Obrigada por me avisar. Não vou insistir.\n\nSe em outro momento fizer sentido para você retomar, é só me chamar por aqui."
    # RC-66: pergunta objetiva sobre acompanhamento/programa precisa ser respondida
    # antes de qualquer recuperação genérica de SPIN. Ex.: "E faz o acompanhamento?"
    # após explicação de consulta/preço não pode virar "o que te incomoda?".
    if active_context and contains_program_question(inbound_text) and is_generic_discovery_reply(text):
        log(f"rc66_program_question_recovered_before_generic phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        return build_program_followup_explanation_reply()
    if active_context and contains_commercial_decline(inbound_text) and recent_context_mentions_price_or_schedule(phone):
        log(f"rc47_commercial_decline_recovery applied phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        return build_commercial_decline_recovery_reply()
    if not is_generic_opening_reply(text):
        return text
    if not active_context:
        return text
    if contains_inbound_scheduling_intent(inbound_text):
        log(f"rc59_schedule_intent_recovered phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        return build_contextual_weight_belly_reply(inbound_text)
    if contains_location_question(inbound_text):
        return (
            "Atendemos em Lauro de Freitas, bem próximo de Salvador.\n\n"
            "O Instituto fica em Buraquinho, no Estação Villas Shopping, sala 305.\n\n"
            "Você consegue vir até Lauro de Freitas para uma avaliação?"
        )
    if contains_evaluation_explanation_request(inbound_text):
        log(f"rc58_explanation_request_recovered phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        return build_evaluation_explanation_reply()
    if is_bare_objective_category(inbound_text):
        log(f"rc65_bare_category_no_generic_reopen phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        return build_price_category_deepening_reply(inbound_text)
    log(f"rc45_no_reopening_after_context applied phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
    if contains_commercial_decline(inbound_text):
        return build_short_decline_context_reply()
    if contains_menopause_weight_context(inbound_text):
        return build_contextual_menopause_weight_reply()
    if contains_weight_belly_metabolism_context(inbound_text):
        return build_contextual_weight_belly_reply(inbound_text)
    return build_spin_continuation_reply()


def is_context_blind_generic_discovery(reply: str) -> bool:
    lower = (reply or "").lower()
    if not lower:
        return False
    generic_discovery = any(marker in lower for marker in (
        "o que mais está te incomodando", "o que mais esta te incomodando",
        "o que está te incomodando", "o que esta te incomodando",
        "o que te trouxe", "o que fez você buscar", "o que fez voce buscar",
        "me conta um pouquinho", "para eu entender melhor", "para eu continuar do ponto certo"
    ))
    if not generic_discovery:
        return False
    # Perguntas genéricas com lista de categorias ("peso, disposição...") continuam
    # sendo genéricas mesmo citando tokens como peso/hormônios. A decisão de
    # continuidade vem do histórico real, não da presença desses tokens na resposta.
    return True


def has_substantive_weight_context(text: str) -> bool:
    lower = (text or "").lower()
    score = 0
    markers = (
        "emagrec", "peso", "engord", "quilos", "kilos", "kg", "gordura abdominal",
        "barriga", "gestante", "dificuldade de manter", "resultado", "2 anos",
        "1.48", "1,48", "70 kg", "salário mínimo", "salario minimo",
        "mudança no corpo", "mudanca no corpo", "falta de energia", "gestação", "gestacao",
        "alimentação", "alimentacao", "corpo", "pele", "energia", "não me priorizei", "nao me priorizei",
    )
    score += sum(1 for marker in markers if marker in lower)
    return score >= 2 or ("peso" in lower and any(m in lower for m in ("20", "13", "70", "abdominal", "emagrec", "resultado", "quilos", "kilos", "kg", "eliminar")))


def summarize_declared_context(combined_context: str) -> str:
    lower = (combined_context or "").lower()
    parts = []
    if "gestação" in lower or "gestacao" in lower:
        parts.append("mudanças depois da gestação")
    if "energia" in lower or "disposição" in lower or "disposicao" in lower:
        parts.append("queda de energia")
    if "peso" in lower or "emagrec" in lower or "quilos" in lower or "kilos" in lower or "kg" in lower:
        parts.append("objetivo de eliminar peso")
    if "corpo" in lower:
        parts.append("mudança no corpo")
    if "alimentação" in lower or "alimentacao" in lower:
        parts.append("alimentação")
    if not parts:
        return "o que você me contou"
    return ", ".join(dict.fromkeys(parts)[:4])


def build_patient_journey_explanation(context_summary: str = "") -> str:
    prefix = f"Pelo que você trouxe — {context_summary} — o caminho aqui não é começar por uma orientação solta.\n\n" if context_summary else "O caminho aqui não é começar por uma orientação solta.\n\n"
    return (
        prefix
        + "A jornada começa pela consulta inicial com a Dra. Daniely, para entender seu histórico, rotina, exames e objetivo.\n\n"
        "No mesmo processo, a equipe faz bioimpedância e avaliação de composição corporal, para enxergar o que pode estar dificultando seu resultado.\n\n"
        "Depois disso, a Dra. define o direcionamento inicial e, se fizer sentido para o seu caso, pode indicar um Programa de Acompanhamento."
    )


def build_weight_context_no_more_spin_reply(combined_context: str) -> str:
    context_summary = summarize_declared_context(combined_context)
    if "salário mínimo" in (combined_context or "").lower() or "salario minimo" in (combined_context or "").lower() or "condições de seguir" in (combined_context or "").lower() or "condicoes de seguir" in (combined_context or "").lower():
        return build_consultation_price_reply(context_summary=context_summary)
    return (
        build_patient_journey_explanation(context_summary)
        + "\n\nQuer que eu te passe o valor da consulta inicial ou prefere que eu veja a agenda?"
    )


def enforce_context_continuity_before_send(phone: str, inbound_text: str, reply: str) -> str:
    """RC-64/69: impede follow-up cego quando o histórico já contém dor declarada.

    A memória/prompt não bastam: o runtime precisa travar respostas genéricas
    que perguntam novamente "o que incomoda" quando o WhatsApp já mostrou o tema.
    """
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    if not is_context_blind_generic_discovery(text):
        return text
    ctx = build_recent_conversation_context(phone, limit=16)
    combined = f"{ctx}\n{inbound_text or ''}"
    if contains_fatigue_complaint(combined):
        log(f"rc69_fatigue_generic_followup_blocked phone={phone} replyPreview={text[:140]!r}")
        return enforce_fatigue_complaint_no_repeat(phone, inbound_text, text)
    if contains_program_question(inbound_text) and contains_price_question(inbound_text):
        log(f"rc69_program_value_generic_followup_rewritten phone={phone} replyPreview={text[:140]!r}")
        return build_program_value_boundary_reply()
    if contains_price_question(combined) and consultation_price_context_ready(phone, inbound_text):
        log(f"rc68_context_price_generic_followup_rewritten phone={phone} replyPreview={text[:140]!r}")
        return build_consultation_price_reply()
    if contains_menopause_weight_context(combined):
        log(f"rc64_context_blind_followup_rewritten phone={phone} replyPreview={text[:140]!r}")
        return build_contextual_menopause_weight_reply()
    if has_substantive_weight_context(combined):
        log(f"rc69_weight_context_no_more_spin phone={phone} replyPreview={text[:140]!r}")
        return build_weight_context_no_more_spin_reply(combined)
    return text



def reply_contains_agendamento_invite(reply: str) -> bool:
    lower = (reply or "").lower()
    markers = (
        "agendar", "agendamento", "agenda", "horário", "horario", "horários", "horarios",
        "ver um horário", "ver um horario", "ver horários", "ver horarios",
        "melhores horários", "melhores horarios", "manhã ou tarde", "manha ou tarde",
        "pré-reserva", "pre-reserva", "reservar", "marcar", "encaixe",
        "avaliação com a dra", "avaliacao com a dra", "consulta com a dra",
    )
    return any(marker in lower for marker in markers)


def build_spin_opening_reply() -> str:
    return (
        "Oi! Que bom te receber por aqui.\n\n"
        "Me conta um pouquinho: o que está te incomodando hoje e fez você buscar ajuda agora?"
    )


def build_spin_continuation_reply() -> str:
    return (
        "Entendi. Para eu continuar do ponto certo e sem pular etapas: "
        "o que mais está te incomodando hoje — peso, disposição, hormônios ou saúde de forma geral?"
    )


def contains_service_scope_question(text: str) -> bool:
    lower = (text or "").lower()
    return any(marker in lower for marker in (
        "qual área", "qual area", "vocês trabalham", "voces trabalham", "trabalham com",
        "nutrição", "nutricao", "nutricionista", "é nutri", "e nutri",
    ))


def build_service_scope_reply() -> str:
    return (
        "Atuamos com avaliação médica para emagrecimento, saúde metabólica/hormonal, composição corporal e disposição.\n\n"
        "A nutrição pode fazer parte do cuidado, mas o primeiro passo aqui é uma avaliação com a Dra. Daniely para entender histórico, exames, bioimpedância, rotina e objetivo.\n\n"
        "Para eu te orientar melhor: o que fez você procurar ajuda agora?"
    )


def enforce_service_scope_question(inbound_text: str, reply: str) -> str:
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    if contains_service_scope_question(inbound_text) and is_generic_discovery_reply(text):
        return build_service_scope_reply()
    return text


def recent_lead_has_minimum_spin_context(phone: str, inbound_text: str = "") -> bool:
    """Contexto mínimo real para permitir agenda.

    Pergunta de preço, categoria solta, saudação ou palavra incompleta não contam.
    Precisa existir dor, objetivo, sintoma, tentativa anterior ou intenção explícita
    de agendar trazida pelo próprio lead.
    """
    if contains_inbound_scheduling_intent(inbound_text):
        return True
    candidates = [inbound_text] + get_recent_lead_texts(phone, limit=8)
    return any(has_price_context_text(t) or contains_weight_belly_metabolism_context(t) for t in candidates)


def enforce_spin_before_agendamento(phone: str, inbound_text: str, reply: str) -> str:
    """RC-50: SPIN Selling antes de qualquer agenda.

    Agendamento nunca deve ser a primeira condução. Se a resposta tenta oferecer
    agenda/horário/avaliação antes de pelo menos um ciclo mínimo de descoberta,
    substitui por acolhimento + pergunta SPIN curta.
    """
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    if not reply_contains_agendamento_invite(text):
        return text
    try:
        entry = get_lead_entry(phone) or {}
        previous_replies = int(entry.get("reply_count") or 0)
    except Exception:
        previous_replies = 0
    if previous_replies <= 0:
        log(f"rc50_spin_before_first_agendamento applied phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        return build_spin_opening_reply()
    if not recent_lead_has_minimum_spin_context(phone, inbound_text):
        log(f"rc50_spin_before_agendamento_no_context applied phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        return build_spin_continuation_reply()
    return text

def enforce_discovery_before_next_step(inbound_text: str, reply: str) -> str:
    """Impede CTA de próximo passo antes da dor/contexto mínimo do lead.

    Incidente 2026-05-20: em abertura genérica (ex.: "Iniciar atendimento"),
    Clara perguntou sobre "próximo passo" no mesmo bloco em que ainda tentava
    descobrir a dor. Regra: no primeiro contato sem dor explícita, a resposta
    deve parar em UMA pergunta de descoberta. Agenda/próximo passo só depois
    que o lead trouxer dor, objetivo ou contexto.
    """
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"

    if contains_location_question(inbound_text):
        return text

    inbound_lower = (inbound_text or "").strip().lower()
    generic_openers = {
        "iniciar atendimento", "oi", "olá", "ola", "bom dia", "boa tarde", "boa noite",
        "quero", "queroo", "querooo", "queroooo", "quero atendimento", "atendimento",
        "tenho interesse", "quero saber mais", "sim", "eu", "tudo"
    }
    has_explicit_pain_or_topic = any(token in inbound_lower for token in (
        "emagrec", "peso", "gordura", "horm", "menopausa", "libido", "cansaço", "cansaco",
        "sono", "ansiedade", "compuls", "tireoide", "consulta", "exame", "valor", "preço", "preco",
        "tratamento", "remédio", "remedio", "tirzepatida", "mounjaro", "ozempic"
    ))
    discovery_markers = (
        "o que mais está te incomodando", "o que mais esta te incomodando",
        "o que está te incomodando", "o que esta te incomodando",
        "o que te trouxe", "me conta um pouquinho", "para eu entender"
    )
    premature_next_step_markers = (
        "próximo passo", "proximo passo", "ver um horário", "ver um horario",
        "passar os horários", "passar os horarios", "horários disponíveis", "horarios disponiveis",
        "agenda", "agendar agora", "avaliação com a dra", "avaliacao com a dra", "dra. daniely"
    )

    compact_inbound = re.sub(r"[^a-záàâãéêíóôõúç]+", "", inbound_lower)
    is_generic_short_ad_reply = (
        inbound_lower in generic_openers
        or compact_inbound in generic_openers
        or (compact_inbound.startswith("quero") and len(compact_inbound) <= 8)
    )
    needs_discovery_only = (is_generic_short_ad_reply or not has_explicit_pain_or_topic)
    has_discovery = any(marker in text.lower() for marker in discovery_markers)
    has_premature_next_step = any(marker in text.lower() for marker in premature_next_step_markers)

    # RC-44 hard gate: resposta curta de anúncio não é conversa comercial ainda.
    # Nesses casos, qualquer explicação institucional, menção à Dra., avaliação, atendimento,
    # preço ou agenda é avanço prematuro. A resposta deve ser SOMENTE acolhimento + descoberta.
    rc44_banned_before_discovery = (
        "dra. daniely", "daniely", "consulta", "avaliação", "avaliacao", "atendimento",
        "horário", "horario", "agenda", "agendar", "marcar", "bioimped",
        "histórico", "historico", "exames", "composição corporal", "composicao corporal",
        "rotina", "sono", "valor", "preço", "preco", "investimento"
    )
    if is_generic_short_ad_reply:
        has_banned_content = any(marker in text.lower() for marker in rc44_banned_before_discovery)
        discovery_only_ok = has_discovery and not has_banned_content and len(text) <= 260
        if not discovery_only_ok:
            return (
                "Oi! Que bom te receber por aqui.\n\n"
                "Me conta um pouquinho: o que está te incomodando hoje e fez você buscar ajuda agora?"
            )

    if needs_discovery_only and has_premature_next_step and not has_discovery:
        return (
            "Oi! Que bom te receber por aqui.\n\n"
            "Me conta um pouquinho: o que está te incomodando hoje e fez você buscar ajuda agora?"
        )
    if not (needs_discovery_only and has_discovery and has_premature_next_step):
        return text

    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    kept = []
    for block in blocks:
        lower = block.lower()
        if any(marker in lower for marker in premature_next_step_markers):
            continue
        kept.append(block)
    cleaned = "\n\n".join(kept).strip()

    # Se a frase de próximo passo estava no mesmo bloco, remove só a sentença problemática.
    if cleaned == text:
        cleaned = re.sub(
            r"(?is)\s*(posso|consigo|quer que eu)[^.!?\n]*(pr[oó]ximo passo|ver um hor[aá]rio|agenda|agendar agora)[^.!?\n]*[.!?]?",
            "",
            text,
        ).strip()

    if "?" not in cleaned and not any(marker in cleaned.lower() for marker in discovery_markers):
        cleaned = cleaned.rstrip(" .") + ".\n\nPara eu te orientar melhor: o que mais está te incomodando hoje?"
    return cleaned


def contains_price_question(text: str) -> bool:
    lower = (text or "").lower()
    return any(token in lower for token in (
        "valor", "preço", "preco", "investimento", "quanto custa", "custa quanto",
        "consulta particular", "particular", "quanto é", "quanto e", "r$"
    ))


def contains_fatigue_complaint(text: str) -> bool:
    lower = (text or "").lower()
    return any(marker in lower for marker in (
        "cansativo", "responder a mesma coisa", "mesma coisa várias vezes", "mesma coisa varias vezes",
        "já respondi", "ja respondi", "perguntou isso", "de novo", "várias vezes", "varias vezes",
    ))


def build_consultation_price_reply(context_summary: str = "") -> str:
    return (
        build_patient_journey_explanation(context_summary)
        + "\n\nSobre o valor: a consulta inicial é R$ 1.000,00.\n\n"
        "Pode ser parcelada em até 2x sem juros, e a reserva é de R$ 300,00, abatida do valor da consulta."
    )


def contains_patient_journey_explanation(text: str) -> bool:
    lower = (text or "").lower()
    return (
        ("jornada" in lower or "caminho" in lower or "começa pela consulta" in lower or "comeca pela consulta" in lower)
        and ("dra. daniely" in lower or "daniely" in lower)
        and ("bioimpedância" in lower or "bioimpedancia" in lower or "composição corporal" in lower or "composicao corporal" in lower)
        and ("programa de acompanhamento" in lower or "direcionamento inicial" in lower)
    )


def build_evaluation_included_reply(phone: str = "", inbound_text: str = "") -> str:
    ctx = build_recent_conversation_context(phone, limit=14) if phone else ""
    context_summary = summarize_declared_context(f"{ctx}\n{inbound_text or ''}")
    return (
        build_patient_journey_explanation(context_summary)
        + "\n\nNa prática, essa avaliação inicial inclui a consulta médica, enfermagem, bioimpedância e um direcionamento inicial para você entender por onde começar com segurança."
    )


def contains_money_value(text: str) -> bool:
    """Detecta oferta comercial de preço/desconto, inclusive escrita por extenso.

    Não fica restrito a R$ 1.000/R$ 900 porque o modelo pode variar a forma:
    "mil reais", "novecentos", "cem de desconto", "desconto hoje" etc.
    """
    lower = (text or "").lower()
    if not lower:
        return False
    if "r$" in lower:
        return True
    if re.search(r"\b(?:1[.,]?000|1000|900|novecentos|mil reais|mil)\b", lower) and any(
        marker in lower for marker in ("consulta", "avaliação", "avaliacao", "fechando", "agendamento", "fica", "valor", "investimento")
    ):
        return True
    if any(marker in lower for marker in (
        "desconto", "bônus", "bonus", "condição especial", "condicao especial",
        "fechando hoje", "agendamento hoje", "fica por", "sai por", "investimento é", "investimento e",
    )):
        return True
    return False


def _strip_profile_name_from_reply(text: str, profile_name: Optional[str]) -> str:
    """Remove nome de perfil/agenda se aparecer como vocativo na resposta."""
    cleaned = text
    raw = (profile_name or "").strip()
    candidates = []
    if raw:
        # Remove prefixos operacionais comuns do nome salvo no WhatsApp: "MAIO - I - Catiane Santos".
        tail = re.sub(r"^(?:[A-ZÁÉÍÓÚÂÊÔÃÕÇ]+|\d{2}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4})\s*-\s*[A-Z]\s*-\s*", "", raw, flags=re.IGNORECASE).strip()
        tail = re.sub(r"^(Lead|Agen|Agend|Pac|Paciente)\s*-\s*", "", tail, flags=re.IGNORECASE).strip()
        for value in (raw, tail, tail.split()[0] if tail else "", raw.split()[0] if raw else ""):
            value = re.sub(r"[^A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç' -]", "", value).strip()
            if len(value) >= 2 and value.lower() not in {"maio", "abril", "lead", "agen", "agend", "pac", "paciente"}:
                candidates.append(value)
    for name in sorted(set(candidates), key=len, reverse=True):
        escaped = re.escape(name)
        cleaned = re.sub(rf"^(Oi|Olá|Ola|Bom dia|Boa tarde|Boa noite)\s*,?\s*{escaped}\s*([,!\.]?)\s*", lambda m: f"{m.group(1)}! ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(rf"^(Perfeito|Entendi|Certo|Claro|Ótimo|Otimo|Obrigada|Obrigado)\s*,?\s*{escaped}\s*,\s*", r"\1. ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(rf"^{escaped}\s*,\s*", "", cleaned, flags=re.IGNORECASE)
    return cleaned


def enforce_no_unconfirmed_name(phone: str, reply: str, inbound_text: str = "", sender_name: Optional[str] = None) -> str:
    """Bloqueia vocativo com nome antes de confirmação explícita do lead (RC-34).

    Regra do Tiaro: nome salvo no WhatsApp, nome do anúncio, nome da campanha ou
    metadado técnico NÃO autorizam personalização. Só libera quando o lead escreve
    algo como "me chamo...", "meu nome é...", "sou a/o..." na conversa.
    """
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"

    current_confirmed = extract_confirmed_lead_name(inbound_text or "")
    if current_confirmed or has_confirmed_lead_name(phone):
        return text

    cleaned = _strip_profile_name_from_reply(text, sender_name)
    patterns = [
        (r"^(Oi|Olá|Ola|Bom dia|Boa tarde|Boa noite)\s*,?\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç' -]{1,30}\s*([,!]|\.)\s*", r"\1! "),
        (r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç' -]{1,30}\s*,\s*", ""),
        (r"^(Perfeito|Entendi|Certo|Claro|Ótimo|Otimo|Obrigada|Obrigado)\s*,\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç' -]{1,30}\s*,\s*", r"\1. "),
        (r"^(Perfeito|Entendi|Certo|Claro|Ótimo|Otimo|Obrigada|Obrigado)\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç' -]{1,30}\s*,\s*", r"\1. "),
    ]
    for pattern, repl in patterns:
        cleaned = re.sub(pattern, repl, cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned or text

def compact_text_key(text: str) -> str:
    return re.sub(r"[^a-záàâãéêíóôõúç0-9]+", " ", (text or "").strip().lower()).strip()


def is_bare_objective_category(text: str) -> bool:
    """Resposta curta de categoria não é dor/contexto suficiente para preço.

    Incidente 2026-06-10: lead perguntou preço, Clara defletiu, lead respondeu só
    "Emagrecimento" e a Clara despejou valor/desconto. Isso é cedo demais.
    Categoria abre a próxima pergunta de dor; não libera preço.
    """
    compact = compact_text_key(text)
    return compact in {
        "emagrecimento", "emagrecer", "perder peso", "hormonal", "hormonios", "hormônios",
        "saude hormonal", "saúde hormonal", "longevidade", "saude", "saúde",
        "saude geral", "saúde geral", "saude de forma geral", "saúde de forma geral",
        "metabolico", "metabólico", "hormonal metabolico", "hormonal metabólico",
    }


def build_price_category_deepening_reply(inbound_text: str) -> str:
    compact = compact_text_key(inbound_text)
    if "emagrec" in compact or "peso" in compact:
        return (
            "Perfeito. Dentro do emagrecimento, o que mais está te incomodando hoje: dificuldade para perder peso, efeito sanfona, ansiedade/compulsão ou algum sinal hormonal/metabólico?"
        )
    if "horm" in compact or "metabol" in compact:
        return (
            "Perfeito. Quando você fala em saúde hormonal/metabólica, o que mais te chamou atenção: cansaço, sono, ciclo, queda de cabelo, libido, peso ou exames alterados?"
        )
    if "longevidade" in compact or "saude" in compact or "saúde" in compact:
        return (
            "Perfeito. Para eu te orientar sem passar uma informação solta: hoje você quer investigar prevenção, energia/disposição, composição corporal ou algum sintoma específico?"
        )
    return (
        "Perfeito. Para eu te orientar sem passar uma informação solta: o que mais está te incomodando hoje e fez você buscar ajuda agora?"
    )


def has_price_context_text(text: str) -> bool:
    """Contexto mínimo real antes de preço: dor/objetivo/condição trazida pelo lead.

    Categoria isolada (ex.: "Emagrecimento") não libera preço. Precisa haver uma
    dor, dificuldade, sintoma, tentativa anterior ou contexto específico.
    """
    if is_bare_objective_category(text):
        return False
    lower = (text or "").lower()
    markers = (
        "peso", "engord", "gordura", "barriga", "compuls", "ansiedade",
        "tireoide", "taxa", "metabolismo", "diabetes", "resistência", "resistencia",
        "menopausa", "libido", "cansaço", "cansaco", "sono",
        "saúde metabólica", "saude metabolica", "performance", "resultado",
        "quero perder", "preciso perder", "estou pesando", "altura", "tenho 1,",
        "já tentei", "ja tentei", "dificuldade", "travando", "incomodando", "me incomoda",
        "não consigo", "nao consigo", "efeito sanfona", "acne", "queda de cabelo",
    )
    return any(marker in lower for marker in markers)


def mark_price_context_if_present(phone: str, inbound_text: str) -> None:
    if not has_price_context_text(inbound_text):
        return
    update_phone_event_entry(phone, {
        "price_context_ready": True,
        "price_context_ready_at": time.time(),
        "price_context_source": "lead_inbound",
    })


def consultation_price_context_ready(phone: str, inbound_text: str = "") -> bool:
    """Permite responder valor da consulta sem cansar o lead.

    RC-68: se o lead já trouxe um tema mínimo (ex.: peso) ou já houve convite
    para agenda, insistir em nova pergunta antes do valor vira fricção comercial.
    """
    entry = get_phone_event_entry(phone)
    if bool(entry.get("price_context_ready")) or has_price_context_text(inbound_text):
        return True
    lead_texts = get_recent_lead_texts(phone, limit=8)
    if any(has_price_context_text(t) for t in lead_texts):
        return True
    try:
        lead_entry = get_lead_entry(phone) or {}
        last_reply_preview = str(lead_entry.get("last_reply_preview") or "")
        if int(lead_entry.get("reply_count") or 0) >= 2 and reply_contains_agendamento_invite(last_reply_preview):
            return True
    except Exception:
        pass
    if int(entry.get("price_deflections", 0) or 0) >= 1:
        return True
    return False


def enforce_price_question_after_context(phone: str, inbound_text: str, reply: str) -> str:
    """RC-68/71: pergunta explícita de valor, após contexto mínimo, recebe valor,
    mas a jornada IVS vem antes do preço.

    O lead pode pedir valor; a Clara não deve cansar com mais SPIN. Porém também
    não deve jogar R$ 1.000/R$ 900 antes de explicar a jornada: consulta médica,
    enfermagem/bioimpedância, direcionamento e possibilidade de programa.
    """
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    if not contains_price_question(inbound_text):
        return text
    if contains_program_question(inbound_text):
        update_phone_event_entry(phone, {
            "price_context_ready": True,
            "price_context_ready_at": time.time(),
            "price_context_source": "rc68_program_value_question_after_context",
        })
        log(f"rc68_program_value_question_answered phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        return build_program_value_boundary_reply()
    if consultation_price_context_ready(phone, inbound_text) or contains_fatigue_complaint(inbound_text):
        ctx = build_recent_conversation_context(phone, limit=14)
        context_summary = summarize_declared_context(f"{ctx}\n{inbound_text or ''}")
        update_phone_event_entry(phone, {
            "price_context_ready": True,
            "price_context_ready_at": time.time(),
            "price_context_source": "rc71_price_after_journey",
            "journey_explained_before_price": True,
            "journey_explained_at": time.time(),
        })
        log(f"rc71_price_after_journey_answered phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        return build_consultation_price_reply(context_summary=context_summary)
    return text


def contains_short_affirmative(text: str) -> bool:
    compact = compact_text_key(text)
    return compact in {"sim", "s", "quero", "pode", "claro", "isso", "ok", "ta", "tá"}


def recent_reply_asked_to_explain_included(phone: str) -> bool:
    entry = get_lead_entry(phone) or {}
    last = str(entry.get("last_reply_preview") or "").lower()
    return any(marker in last for marker in (
        "explique o que está incluído", "explique o que esta incluido",
        "quer que eu te explique", "o que está incluído nessa avaliação", "o que esta incluido nessa avaliacao",
    ))


def enforce_included_explanation_after_yes(phone: str, inbound_text: str, reply: str) -> str:
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    if contains_short_affirmative(inbound_text) and recent_reply_asked_to_explain_included(phone):
        if contains_money_value(text) or not contains_patient_journey_explanation(text):
            log(f"rc71_yes_explain_included_rewritten phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
            update_phone_event_entry(phone, {
                "journey_explained_before_price": True,
                "journey_explained_at": time.time(),
                "price_context_source": "rc71_yes_explain_included",
            })
            return build_evaluation_included_reply(phone, inbound_text)
    return text


def enforce_money_after_journey(phone: str, inbound_text: str, reply: str) -> str:
    text = (reply or "").strip()
    if not text or text == "NO_REPLY" or not contains_money_value(text):
        return text or "NO_REPLY"
    if contains_patient_journey_explanation(text):
        return text
    if contains_price_question(inbound_text) and consultation_price_context_ready(phone, inbound_text):
        ctx = build_recent_conversation_context(phone, limit=14)
        context_summary = summarize_declared_context(f"{ctx}\n{inbound_text or ''}")
        log(f"rc71_money_without_journey_rewritten phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        update_phone_event_entry(phone, {
            "journey_explained_before_price": True,
            "journey_explained_at": time.time(),
            "price_context_source": "rc71_money_without_journey",
        })
        return build_consultation_price_reply(context_summary=context_summary)
    return text


def enforce_fatigue_complaint_no_repeat(phone: str, inbound_text: str, reply: str) -> str:
    """Quando o lead reclama de repetição, Clara pede desculpa e para de perguntar."""
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    if not contains_fatigue_complaint(inbound_text):
        return text
    if contains_price_question(build_recent_conversation_context(phone, limit=6)) or contains_price_question(inbound_text):
        return "Você tem razão, me desculpe. Vou ser direta.\n\n" + build_consultation_price_reply()
    return "Você tem razão, me desculpe. Vou ser mais direta e não vou repetir a mesma pergunta."


def enforce_price_timing(phone: str, inbound_text: str, reply: str) -> str:
    """RC-40: impede preço antes de contexto mínimo, mesmo em segunda mensagem rápida.

    Incidente 2026-05-21: lead perguntou valor e, logo depois, "e nutricionista?".
    A primeira resposta defletiu corretamente, mas a segunda entregou R$ 1.000/R$ 900
    porque a trava antiga só bloqueava a primeira pergunta explícita de preço.

    Regra atual: qualquer resposta com valor monetário é bloqueada enquanto o lead
    não trouxer dor/objetivo/condição mínima. Insistência sem contexto não libera preço.
    """
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    if not contains_money_value(text):
        return text

    entry = get_phone_event_entry(phone)
    if contains_price_question(inbound_text):
        prior_price_questions = int(entry.get("price_questions", 0) or 0)
        update_phone_event_entry(phone, {
            "price_questions": prior_price_questions + 1,
            "last_price_question_at": time.time(),
        })
        entry = get_phone_event_entry(phone)

    context_ready = bool(entry.get("price_context_ready")) or has_price_context_text(inbound_text)
    if context_ready:
        if not entry.get("price_context_ready"):
            mark_price_context_if_present(phone, inbound_text)
        return text

    prior_price_deflections = int(entry.get("price_deflections", 0) or 0)
    update_phone_event_entry(phone, {
        "price_deflections": prior_price_deflections + 1,
        "last_price_deflection_at": time.time(),
        "last_price_block_reason": "missing_context_before_price",
    })
    if is_bare_objective_category(inbound_text):
        log(f"rc50_price_category_needs_deepening applied phone={phone} inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        return build_price_category_deepening_reply(inbound_text)
    return (
        "Claro, eu te explico direitinho. Antes, para eu não te passar uma informação solta: "
        "o que mais está te incomodando hoje e fez você buscar ajuda agora?"
    )


def contains_program_question(text: str) -> bool:
    lower = (text or "").lower()
    return any(token in lower for token in (
        "programa", "acompanhamento", "depois", "mensal", "continuidade", "continuar", "tratamento"
    ))


def build_program_followup_explanation_reply() -> str:
    return (
        "Sim. Depois da consulta inicial, se fizer sentido para o seu caso, a Dra. Daniely pode indicar um Programa de Acompanhamento individual.\n\n"
        "Esse programa é definido depois da avaliação, porque depende do seu histórico, exames, composição corporal, objetivo e do que for seguro para você.\n\n"
        "Por isso eu não te passo um valor fechado de acompanhamento por aqui antes da consulta. O primeiro passo é a avaliação inicial."
    )


def build_program_value_boundary_reply() -> str:
    return (
        "Entendo. O valor do Programa de Acompanhamento não é fechado antes da consulta, porque depende do que a Dra. Daniely indicar depois de avaliar seu histórico, exames, composição corporal e objetivo.\n\n"
        "O primeiro passo é a consulta inicial. Ela custa R$ 1.000,00, pode ser parcelada em até 2x sem juros, e a reserva é de R$ 300,00 abatida do valor da consulta."
    )


def is_generic_discovery_reply(reply: str) -> bool:
    lower = (reply or "").lower()
    return any(marker in lower for marker in (
        "o que mais está te incomodando", "o que mais esta te incomodando",
        "o que está te incomodando", "o que esta te incomodando",
        "o que te trouxe", "o que fez você buscar", "o que fez voce buscar",
        "me conta um pouquinho", "para eu entender melhor", "para eu continuar do ponto certo",
    ))


def enforce_program_reasoning(inbound_text: str, reply: str) -> str:
    """Garante raciocínio correto quando o lead pergunta sobre acompanhamento/programa.

    RC-66: pergunta objetiva como "E faz o acompanhamento?" não é convite para
    reabrir descoberta. A Clara deve responder sobre acompanhamento e seguir a
    lógica comercial já iniciada, sem repetir pergunta clichê.
    """
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
    if is_generic_discovery_reply(text) or weak_fixed_value_answer or (mentions_program and lacks_agenda_direction):
        log(f"rc66_program_question_no_generic_reopen inbound={inbound_text[:80]!r} replyPreview={text[:120]!r}")
        return build_program_followup_explanation_reply()
    return text


def contains_plan_rejection(text: str) -> bool:
    lower = (text or "").lower()
    strong_rejection = any(token in lower for token in (
        "procurar um profissional pelo plano", "procurar profissional pelo plano",
        "profissional pelo convênio", "profissional pelo convenio",
        "prefiro pelo plano", "prefiro pelo convênio", "prefiro pelo convenio",
        "preferir pelo plano", "preferir pelo convênio", "preferir pelo convenio",
        "vou procurar pelo plano", "vou procurar pelo convênio", "vou procurar pelo convenio",
        "vou preferir procurar", "vou ver pelo plano", "vou pelo plano",
        # RC-43: soft-decline após resposta sobre plano/convênio.
        # Ex.: lead responde "Saúde metabólica geral. Mas agradeço!".
        # Isso não é despedida; é objeção velada/escape. Clara deve recuperar, não agradecer e encerrar.
        "mas agradeço", "mas agradeco", "mas obrigada", "mas obrigado",
        "agradeço!", "agradeco!", "obrigada!", "obrigado!",
        "obrigada mesmo", "obrigado mesmo", "agradeço mesmo", "agradeco mesmo"
    ))
    return strong_rejection


def contains_plan_question_direct(text: str) -> bool:
    lower = (text or "").lower()
    return any(token in lower for token in (
        "aceita plano", "aceitam plano", "atende plano", "atendem plano",
        "aceita convênio", "aceita convenio", "aceitam convênio", "aceitam convenio",
        "atendimento pelo plano", "consulta pelo plano", "pelo meu plano",
        "sulamerica", "sulamérica", "bradesco", "amil", "unimed", "mamães baianas", "mamaes baianas"
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
        "eu que agradeço", "eu que agradeco", "caso em algum momento", "se em algum momento",
        "quando quiser", "fico à disposição", "fico a disposição", "agradeço seu contato",
        "agradeco seu contato", "entendo perfeitamente"
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
    direct = any(token in lower for token in (
        "posso ver um horário", "posso ver um horario", "vejo um horário", "vejo um horario",
        "quer que eu veja os horários", "quer que eu veja os horarios", "horários disponíveis", "horarios disponiveis",
        "prefere manhã ou tarde", "prefere manha ou tarde", "manhã ou tarde", "manha ou tarde",
        "agendar", "marcar a consulta", "ver agenda", "horário de consulta", "horario de consulta",
        "qual prefere", "qual fica melhor", "qual te encaixa", "pré-reserva", "pre-reserva"
    ))
    if direct:
        return True
    day_slot = any(day in lower for day in (
        "segunda", "terça", "terca", "quarta", "quinta", "sexta", "sábado", "sabado", "domingo"
    ))
    time_slot = re.search(r"\b(?:[01]?\d|2[0-3])(?:h|:00|:30)\b", lower) is not None
    return bool(day_slot and time_slot)


def has_journey_context(text: str) -> bool:
    lower = (text or "").lower()
    markers = (
        "jornada", "consulta inicial", "avaliação médica", "avaliacao medica", "dra. daniely",
        "histórico", "historico", "exames", "composição corporal", "composicao corporal",
        "bioimpedância", "bioimpedancia", "rotina", "sono", "vídeo", "video"
    )
    return sum(1 for marker in markers if marker in lower) >= 4


def has_pain_or_goal_context(text: str) -> bool:
    """RC-34: agenda só depois de dor/objetivo/contexto minimamente entendido."""
    lower = (text or "").lower()
    markers = (
        "dor", "incomoda", "incomodando", "dificulta", "dificultando", "objetivo", "meta",
        "emagrecer", "peso", "engord", "barriga", "compuls", "ansiedade", "fome",
        "menopausa", "horm", "cansaço", "cansaco", "sono", "rotina", "histórico", "historico",
        "exames", "metabolismo", "resultado", "autoestima", "disposição", "disposicao",
        "você comentou", "voce comentou", "pelo que você", "pelo que voce", "o que você trouxe", "o que voce trouxe"
    )
    return any(marker in lower for marker in markers)


def contains_inbound_scheduling_intent(text: str) -> bool:
    lower = (text or "").lower()
    return any(token in lower for token in (
        "quero marcar", "quero agendar", "queria marcar", "queria agendar",
        "marcar uma consulta", "agendar uma consulta", "tem horário", "tem horario",
        "agenda", "consulta disponível", "consulta disponivel", "ir aí", "ir ai",
        "ir na clínica", "ir na clinica"
    ))


def prior_context_has_discovery(phone: str) -> bool:
    try:
        entry = get_lead_entry(phone) or {}
        if int(entry.get("reply_count") or 0) < 1 or int(entry.get("inbound_count") or 0) < 2:
            return False
        ctx = build_recent_conversation_context(phone, limit=10)
        return contains_weight_belly_metabolism_context(ctx) or has_pain_or_goal_context(ctx)
    except Exception:
        return False


def enforce_journey_before_scheduling(phone: str, inbound_text: str, reply: str) -> str:
    """RC-34: bloqueia agenda cedo demais sem entender dor e gerar valor."""
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    wants_to_schedule = contains_scheduling_offer(text) or contains_inbound_scheduling_intent(inbound_text)
    if wants_to_schedule and contains_inbound_scheduling_intent(inbound_text) and prior_context_has_discovery(phone):
        if contains_scheduling_offer(text) and (has_journey_context(text) or "dra. daniely" in text.lower() or "consulta inicial" in text.lower()):
            return text
        return build_contextual_weight_belly_reply(inbound_text)
    if wants_to_schedule and (not has_journey_context(text) or not has_pain_or_goal_context(text)):
        return (
            "Entendi. Antes de ver agenda, quero te direcionar do jeito certo.\n\n"
            "A consulta inicial não é só para marcar um horário: a Dra. Daniely avalia histórico, exames, composição corporal, rotina, sono e o que pode estar travando seu resultado, para definir um caminho individualizado e seguro.\n\n"
            "Para eu entender se faz sentido para você: hoje o que mais está te incomodando ou qual resultado você está buscando?"
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
        "se em algum momento", "caso em algum momento", "eu que agradeço", "eu que agradeco",
        "estou por aqui", "estamos por aqui", "me chama quando", "me avise quando"
    )
    has_passive = any(marker in lower for marker in passive_markers)
    has_clear_cta = "?" in text and any(marker in lower for marker in (
        "posso", "prefere", "qual", "manhã", "manha", "tarde", "horário", "horario", "enviar", "pré-reserva", "pre-reserva", "retorno"
    ))
    if has_passive:
        cleaned = re.sub(
            r"(?i)(eu que agradeço[^.!?]*[.!?]*|eu que agradeco[^.!?]*[.!?]*|fico à disposição|fico a disposição|qualquer coisa[^.!?]*|quando quiser[^.!?]*|se tiver interesse[^.!?]*|se em algum momento[^.!?]*|caso em algum momento[^.!?]*|estou por aqui|estamos por aqui|me chama quando[^.!?]*)[.!?]*",
            "", text
        ).strip(" .\n")
        if has_clear_cta and cleaned:
            return cleaned
        return cleaned + "\n\nPara deixar isso bem encaminhado: prefere que eu veja o próximo horário pela manhã ou pela tarde?"

    if "?" not in text:
        if any(marker in inbound_lower for marker in ("valor", "preço", "preco", "plano", "convênio", "convenio", "agenda", "horário", "horario", "consulta", "exame", "prescrição", "prescricao")):
            return text.rstrip(" .") + ".\n\nQual desses pontos você quer que eu encaminhe agora: entender a avaliação ou ver o próximo horário?"
        if len(text) < 450:
            return text.rstrip(" .") + ".\n\nPosso te orientar com o próximo passo agora?"

    return text


def enforce_agendamento_reply_quality(reply: str) -> str:
    """RC-42: agenda não pode ser inventada nem usar jargão interno.

    Histórico: em 2026-05-29 a Clara enviou para Layla/Stephane
    "Hoje e amanhã não temos disponibilidade... D+2...". Esse texto nasceu
    aqui como fallback antigo. Regra atual: sem consulta real ao QuarkClinic,
    Clara não afirma disponibilidade/indisponibilidade. Ela acolhe a dor e
    coleta contexto antes de acionar/ver agenda.
    """
    text = (reply or "").strip()
    if not text or text == "NO_REPLY":
        return text or "NO_REPLY"
    text = enforce_allowed_scheduling_scope(text)
    lower = text.lower()

    forbidden_dplus = bool(re.search(r"(?i)\bD\s*\+\s*\d+\b", text))
    scheduling_context = any(token in lower for token in (
        "horário", "horario", "agenda", "agendar", "consulta", "encaixe", "marcar", "reserv",
        "disponibilidade", "disponível", "disponivel"
    ))
    unverified_availability_claim = scheduling_context and any(token in lower for token in (
        "não temos disponibilidade", "nao temos disponibilidade", "temos disponibilidade",
        "não tenho horário", "nao tenho horario", "tenho horário", "tenho horario",
        "não há horário", "nao ha horario", "há horário", "ha horario",
        "sem disponibilidade", "com disponibilidade", "tem disponibilidade",
        "hoje e amanhã", "hoje e amanha", "a partir de d+", "d+"
    ))
    if forbidden_dplus or unverified_availability_claim:
        log(f"rc42_agenda_claim_rewritten original_preview={text[:160]!r}")
        return (
            "Entendi. Antes de falar de agenda, preciso te direcionar com segurança e entender o que está por trás da sua busca pela consulta.\n\n"
            "A avaliação com a Dra. Daniely olha histórico, exames, rotina, composição corporal e o que pode estar travando seu resultado.\n\n"
            "Hoje, o que mais está te incomodando: peso, fome/ansiedade, saúde metabólica ou dificuldade de manter resultado?"
        )

    passive_markers = (
        "fico à disposição", "fico a disposição", "qualquer coisa",
        "quando quiser", "se tiver interesse", "se quiser marcar",
        "se em algum momento", "caso em algum momento", "eu que agradeço", "eu que agradeco",
        "estou por aqui", "estamos por aqui",
    )
    has_passive_close = any(marker in lower for marker in passive_markers)
    has_question = "?" in text
    has_concrete_next_step = any(token in lower for token in ("posso", "prefere", "horário", "horario", "manhã", "manha", "tarde", "agendar", "pré-reserva", "pre-reserva"))
    if has_passive_close and not (has_question or has_concrete_next_step):
        text = text.rstrip(" .") + ".\n\nPara eu te orientar melhor: o que mais está te incomodando hoje?"
    elif has_passive_close and "?" not in text:
        text = text.rstrip(" .") + ".\n\nQual seria o melhor próximo passo para você agora: entender a avaliação ou eu acionar a equipe para verificar agenda?"
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
            status, body = send_zapi_text(target, msg, source="internal_notify")
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
            status, body = send_zapi_text(target, msg, source="internal_notify")
            log(f"internal_contact_request_notify target={target} status={status} body={body[:160]}")
        except Exception as err:
            log(f"internal_contact_request_notify failed target={target}: {err}")


def notify_internal_clara_failure(phone: str, sender_name: Optional[str], inbound_text: str, stage: str, detail: str = "") -> None:
    """Fail-safe anti-perda: se Clara falhar/ficar sem resposta para lead, humano é acionado."""
    if not CLARA_NOTIFY_PHONES:
        return
    name = (sender_name or "Nome não identificado").strip()
    msg = (
        "ALERTA OPERACIONAL — Clara foi bloqueada ou pode ter perdido resposta de lead\n\n"
        f"Lead: {name}\n"
        f"Telefone: {phone}\n"
        f"Etapa/falha: {stage}\n"
        f"Detalhe: {(detail or 'sem detalhe')[:500]}\n\n"
        "Próxima ação obrigatória: Maria deve corrigir o erro da Clara e manter o atendimento ativo "
        "até agendamento ou negativa final explícita. Não deixar o lead parado.\n\n"
        f"Última mensagem recebida: {(inbound_text or '')[:500]}"
    )
    for target in CLARA_NOTIFY_PHONES:
        try:
            if normalize_phone(target) == normalize_phone(phone):
                continue
            status, body = send_zapi_text(target, msg, source="internal_notify")
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


def generate_tts_audio(text: str) -> Tuple[bytes, str]:
    """Gera áudio para espelhamento.

    Ordem governada:
    1) ElevenLabs como rota principal da voz configurada da Clara.
    2) TTS genérico/OpenAI apenas como fallback operacional, se habilitado.

    Importante: não usa OpenRouter para TTS. OpenRouter pode ser rota de LLM/texto,
    mas não deve ser usado para síntese de voz.
    """
    primary = CLARA_TTS_PRIMARY or "elevenlabs"
    fallback = CLARA_TTS_FALLBACK or "off"
    errors = []

    if primary != "elevenlabs":
        log(f"tts_primary_forced_to_elevenlabs previous={primary!r}")

    if ELEVENLABS_API_KEY:
        try:
            return generate_elevenlabs_tts(text), "elevenlabs"
        except Exception as err:
            errors.append(f"elevenlabs: {err}")
            log(f"tts_primary_failed provider=elevenlabs error={err}")
    else:
        errors.append("elevenlabs: ELEVENLABS_API_KEY not configured")
        log("tts_primary_unavailable provider=elevenlabs reason=missing_key")

    if fallback in ("0", "false", "no", "off", "none", "disabled"):
        raise RuntimeError("ElevenLabs TTS failed/unavailable and TTS fallback is disabled: " + " | ".join(errors))

    if fallback in ("openai", "tts", "generic"):
        try:
            return generate_openai_tts(text), "openai_tts_fallback"
        except Exception as err:
            errors.append(f"openai_tts_fallback: {err}")
            log(f"tts_fallback_failed provider=openai_tts error={err}")
            raise RuntimeError("TTS providers failed: " + " | ".join(errors)) from err

    raise RuntimeError(f"Unsupported CLARA_TTS_FALLBACK={fallback!r}; " + " | ".join(errors))


def evaluate_zapi_runtime_enforcement(phone: str, message: str, source: str = "clara_reply", channel: str = "text", phase: str = "preflight", status: str = "") -> Dict[str, Any]:
    """Enforcement obrigatório antes de qualquer envio Z-API.

    Consulta a camada nativa IVS/AgentScope-like: registry, dedupe persistente,
    cooldown anti-burst e tracing redigido. Não envia nada por conta própria.
    """
    if not CLARA_ZAPI_RUNTIME_ENFORCE:
        return {"ok": True, "decision": "ALLOW", "reason": "runtime_enforcement_disabled"}
    cmd = [
        "python3", IVS_RUNTIME_ENFORCEMENT_SCRIPT,
        "zapi-preflight" if phase == "preflight" else ("zapi-commit" if phase == "commit" else "zapi-fail"),
        "--phone", str(phone or ""),
        "--message", str(message or ""),
        "--source", str(source or "clara_reply"),
        "--channel", str(channel or "text"),
    ]
    if phase in ("commit", "fail"):
        cmd += ["--status", str(status or "")]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=20)
        out = (proc.stdout or "").strip()
        decision = json.loads(out) if out else {}
        if isinstance(decision, dict):
            if proc.returncode != 0 and not decision.get("reason"):
                decision.setdefault("ok", False)
                decision.setdefault("decision", "BLOCK")
                decision["reason"] = "runtime_enforcement_nonzero"
                decision["returncode"] = proc.returncode
            return decision
    except Exception as err:
        return {"ok": False, "decision": "BLOCK", "reason": "runtime_enforcement_error", "error": str(err)}
    return {"ok": False, "decision": "BLOCK", "reason": "invalid_runtime_enforcement_response"}


def send_zapi_audio(phone: str, audio_bytes: bytes, source: str = "clara_reply") -> Tuple[int, str]:
    if not ZAPI_BASE_URL:
        raise RuntimeError("ZAPI_BASE_URL is empty")
    if not ZAPI_CLIENT_TOKEN:
        raise RuntimeError("ZAPI_CLIENT_TOKEN is empty")
    guard_message = f"audio_bytes:{len(audio_bytes or b'')}"
    guard = evaluate_zapi_runtime_enforcement(phone, guard_message, source=source, channel="audio", phase="preflight")
    if not guard.get("ok"):
        raise RuntimeError(f"zapi_audio_blocked_by_runtime_enforcement: {json.dumps(guard, ensure_ascii=False)[:500]}")
    import base64
    payload = {"phone": phone, "audioBase64": base64.b64encode(audio_bytes).decode("ascii")}
    headers = {"Client-Token": ZAPI_CLIENT_TOKEN}
    url = ZAPI_BASE_URL.rstrip("/") + ZAPI_SEND_AUDIO_PATH
    status, body = post_json(url, payload, headers=headers, timeout=60)
    if 200 <= status < 300:
        evaluate_zapi_runtime_enforcement(phone, guard_message, source=source, channel="audio", phase="commit", status=str(status))
    else:
        evaluate_zapi_runtime_enforcement(phone, guard_message, source=source, channel="audio", phase="fail", status=str(status))
    return status, body




def validate_admin_send_lead_safety(payload: Dict[str, Any], phone: str, message: str) -> Tuple[bool, Dict[str, Any]]:
    """Hard gate para envios ativos via /admin/send (RC-34 + RC-44).

    Incidente 2026-06-15: follow-up ativo para leads usou nome vindo da Z-API
    e ofereceu agenda antes de conexão/contexto mínimo. Para envio ativo, o
    default agora é bloquear qualquer vocativo nominal não confirmado e qualquer
    avanço para agenda/horários sem contexto validado explicitamente no payload.
    """
    text = (message or '').strip()
    lower = text.lower()
    if not text:
        return False, {"rule": "admin_send_empty", "final": "BLOCK"}

    name_confirmed = bool(payload.get("name_confirmed") or payload.get("nameConfirmed"))
    context_validated = bool(payload.get("context_validated") or payload.get("contextValidated") or payload.get("discovery_completed") or payload.get("discoveryCompleted"))

    # RC-34: nome de WhatsApp/Z-API/perfil/lista nunca é nome confirmado.
    nominal_greeting = re.search(
        r"(?iu)^\s*(?:oi|ol[áa]|bom dia|boa tarde|boa noite)\s*,\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç' -]{1,40}[.!?,]",
        text,
    )
    if nominal_greeting and not name_confirmed:
        return False, {
            "rule": "RC34_admin_send_unconfirmed_name",
            "final": "BLOCK",
            "reason": "envio ativo não pode chamar lead pelo nome sem confirmação escrita no chat",
            "safe_example": "Oi! Tudo bem? Estou passando para retomar seu contato com o Instituto Vital Slim. O que fez você buscar ajuda agora?",
        }

    # RC-44: antes de conexão/dor/intenção, não oferecer agenda, horários ou avaliação.
    scheduling_markers = (
        "agendar", "agendamento", "agenda", "horário", "horario", "horários", "horarios",
        "ver os melhores horários", "ver melhores horários", "veja os melhores horários",
        "consulta", "avaliação com a dra", "avaliacao com a dra", "dra. daniely",
        "marcar", "reservar", "encaixe",
    )
    if any(marker in lower for marker in scheduling_markers) and not context_validated:
        return False, {
            "rule": "RC44_admin_send_premature_scheduling",
            "final": "BLOCK",
            "reason": "envio ativo não pode oferecer agenda/horários/consulta antes de conexão e contexto mínimo",
            "safe_example": "Oi! Tudo bem? Estou passando para retomar seu contato com o Instituto Vital Slim. O que fez você buscar ajuda agora?",
        }

    return True, {"rule": "admin_send_lead_safety", "final": "ALLOW"}

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


def final_scrub_banned_next_step_phrase(message: str) -> str:
    """RC-41/RC-42: trava final antes do envio.

    Cobre reintroduções pelo modelo ou por enforcers posteriores. Além do CTA
    genérico, remove a linguagem proibida de agenda interna (D+N) e impede o
    fallback antigo de disponibilidade inventada.
    """
    text = (message or "").strip()
    if not text:
        return text
    original = text
    # RC-34 hotfix 2026-06-15: nome salvo no WhatsApp/Z-API não é nome confirmado.
    # Como o modelo pode herdar vocativos de histórico contaminado, removemos
    # vocativo nominal no início da resposta por segurança.
    text = re.sub(
        r"(?iu)^(Oi|Ol[áa]|Bom dia|Boa tarde|Boa noite|Entendi|Perfeito|Certo|Que bom),\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç' -]{1,40}([.!?])",
        r"\1\2",
        text,
        count=1,
    ).strip()
    text = re.sub(r"(?iu)^Oi\.", "Oi!", text, count=1)
    text = re.sub(r"(?iu)^Ol[áa]\.", "Olá!", text, count=1)
    if re.search(r"(?i)\bD\s*\+\s*\d+\b", text) or re.search(r"(?i)hoje\s+e\s+amanh[ãa]\s+n[ãa]o\s+temos\s+disponibilidade", text):
        log(f"rc42_final_scrub_agenda_dplus applied source_text_preview={original[:160]!r}")
        return (
            "Entendi. Antes de falar de agenda, preciso te direcionar com segurança.\n\n"
            "Me conta o que mais está te incomodando hoje para eu encaminhar corretamente: peso, fome/ansiedade, saúde metabólica ou dificuldade de manter resultado?"
        )
    banned_patterns = [
        r"(?is)\s*(?:posso|consigo)\s+te\s+(?:orientar|ajudar|guiar|explicar)\s+com\s+o\s+pr[oó]ximo\s+passo\s*(?:agora)?\s*[?.!]*",
        r"(?is)\s*quer\s+que\s+eu\s+te\s+(?:oriente|ajude|guie|explique)\s+com\s+o\s+pr[oó]ximo\s+passo\s*[?.!]*",
        r"(?is)\s*(?:vamos|posso)\s+(?:para|pro|ao)?\s*pr[oó]ximo\s+passo\s*(?:agora)?\s*[?.!]*",
    ]
    for pattern in banned_patterns:
        text = re.sub(pattern, "", text).strip()
    text = re.sub(r"\n{3,}", "\n\n", text).strip(" \n.-")
    if not text:
        text = "Para eu te orientar melhor: o que mais está te incomodando hoje?"
    if text != original:
        log(f"rc41_final_scrub_next_step applied source_text_preview={original[:120]!r} result_preview={text[:120]!r}")
    return text

def split_human_conversation_chunks(message: str, max_chars: int = CLARA_HUMAN_CHUNK_MAX_CHARS) -> list[str]:
    """Transforma bloco único em bolhas humanas: frase -> digitando -> frase.

    RC-72: no WhatsApp a Clara não deve enviar textão em blocos. O runtime
    divide a resposta final em frases curtas e o envio aplica `delayTyping`
    antes de cada bolha.
    """
    text = re.sub(r"\s*\n+\s*", " ", (message or "").strip())
    text = re.sub(r"\s{2,}", " ", text).strip()
    if not text:
        return []
    protected = text
    replacements: Dict[str, str] = {}
    protected_abbrevs = {
        "Dra.": "__ABBR_DRA__",
        "Dr.": "__ABBR_DR__",
        "Sr.": "__ABBR_SR__",
        "Sra.": "__ABBR_SRA__",
    }
    for value, token in protected_abbrevs.items():
        protected = protected.replace(value, token)
        replacements[token] = value
    for i, m in enumerate(re.finditer(r"R\$\s*\d{1,3}(?:\.\d{3})*,\d{2}|\b\d+[,.]\d+\s*(?:m|kg)\b", protected)):
        token = f"__NUMTOK{i}__"
        replacements[token] = m.group(0)
        protected = protected.replace(m.group(0), token, 1)
    pieces = re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9])", protected)
    chunks: list[str] = []
    for raw in pieces:
        piece = raw.strip()
        for token, value in replacements.items():
            piece = piece.replace(token, value)
        if not piece:
            continue
        if len(piece) <= max_chars:
            chunks.append(piece)
            continue
        # Frase longa: quebra por vírgula/; mantendo leitura natural.
        current = ""
        subparts = re.split(r"(?<=[,;:])\s+", piece)
        for sub in subparts:
            if not current:
                current = sub
            elif len(current) + 1 + len(sub) <= max_chars:
                current += " " + sub
            else:
                chunks.append(current.strip())
                current = sub
        if current.strip():
            chunks.append(current.strip())
    return [c for c in chunks if c]


def send_zapi_text_human_sequence(phone: str, message: str, source: str = "clara_reply") -> Tuple[int, str]:
    chunks = split_human_conversation_chunks(message)
    if not CLARA_HUMAN_CHUNKING_ENABLED or not source.startswith("clara") or len(chunks) <= 1:
        return send_zapi_text(phone, message, source=source)
    results = []
    last_status = 0
    last_body = ""
    log(f"rc72_human_chunking_enabled phone={phone} source={source} chunks={len(chunks)}")
    for idx, chunk in enumerate(chunks, start=1):
        chunk_source = f"{source}_chunk" if source.startswith("clara") else source
        status, body = send_zapi_text(phone, chunk, source=chunk_source)
        last_status, last_body = status, body
        results.append({"idx": idx, "status": status, "preview": chunk[:80], "body": body[:200]})
        if not (200 <= int(status) < 300):
            break
    return last_status, json.dumps({"chunked": True, "chunks": len(chunks), "results": results, "last_body": last_body[:500]}, ensure_ascii=False)


def send_zapi_text(phone: str, message: str, source: str = "clara_reply") -> Tuple[int, str]:
    if not ZAPI_BASE_URL:
        raise RuntimeError("ZAPI_BASE_URL is empty")
    if not ZAPI_CLIENT_TOKEN:
        raise RuntimeError("ZAPI_CLIENT_TOKEN is empty")
    if source in {"clara_reply", "admin_send"}:
        original_message = message
        message = enforce_outbound_price_safety(phone, final_scrub_banned_next_step_phrase(message))
        if message != original_message:
            log(f"rc52_transport_rewrote_commercial_output phone={phone} source={source} originalPreview={original_message[:120]!r} newPreview={message[:120]!r}")
    guard = evaluate_zapi_runtime_enforcement(phone, message, source=source, channel="text", phase="preflight")
    if not guard.get("ok"):
        raise RuntimeError(f"zapi_text_blocked_by_runtime_enforcement: {json.dumps(guard, ensure_ascii=False)[:500]}")
    payload = {"phone": phone, "message": message}
    if source.startswith("clara") and CLARA_ZAPI_DELAY_TYPING_SECONDS > 0:
        # Z-API /send-text: delayTyping exibe “digitando...” por 1–15s antes de cada bolha.
        # RC-72: frase -> digitando -> frase, sem textão em bloco.
        payload["delayTyping"] = max(1, min(15, CLARA_ZAPI_DELAY_TYPING_SECONDS))
        log(f"zapi_delay_typing_enabled phone={phone} seconds={payload['delayTyping']} source={source}")
    headers = {"Client-Token": ZAPI_CLIENT_TOKEN}
    url = ZAPI_BASE_URL.rstrip("/") + ZAPI_SEND_TEXT_PATH
    status, body = post_json(url, payload, headers=headers, timeout=30)
    if 200 <= status < 300:
        evaluate_zapi_runtime_enforcement(phone, message, source=source, channel="text", phase="commit", status=str(status))
    else:
        evaluate_zapi_runtime_enforcement(phone, message, source=source, channel="text", phase="fail", status=str(status))
    return status, body


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


def phone_lookup_variants_for_tags(phone: str) -> list[str]:
    normalized = normalize_phone(phone) or ""
    variants: list[str] = []
    for candidate in ("".join(ch for ch in str(phone or "") if ch.isdigit()), normalized):
        if candidate and candidate not in variants:
            variants.append(candidate)
    if len(normalized) == 13 and normalized.startswith("55") and normalized[4] == "9":
        v = normalized[:4] + normalized[5:]
        if v not in variants:
            variants.append(v)
    if len(normalized) == 12 and normalized.startswith("55"):
        subscriber = normalized[4:]
        if subscriber and subscriber[0] in "6789":
            v = normalized[:4] + "9" + subscriber
            if v not in variants:
                variants.append(v)
    return variants


def load_cached_contact_tags_snapshot() -> Dict[str, Any]:
    out_dir = Path("/root/cerebro-vital-slim/sistemas/marketing-ivs/data/whatsapp-readonly")
    try:
        files = sorted(out_dir.glob("zapi_admin_contact_tags*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    except Exception:
        files = []
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue
        if not isinstance(data, list):
            continue
        by_phone: Dict[str, Any] = {}
        catalog: Dict[str, Dict[str, Any]] = {}
        for item in data:
            if not isinstance(item, dict):
                continue
            phone = normalize_phone(item.get("phone"))
            if phone:
                for variant in phone_lookup_variants_for_tags(phone):
                    by_phone[variant] = item
            tag_ids = item.get("tag_ids") or item.get("tagIds") or []
            tag_names = item.get("tags") or item.get("tag_names") or []
            if isinstance(tag_ids, list) and isinstance(tag_names, list):
                for idx, name in enumerate(tag_names):
                    if not name:
                        continue
                    tid = str(tag_ids[idx]) if idx < len(tag_ids) and tag_ids[idx] is not None else str(name)
                    catalog[tid] = {"id": tid, "name": str(name), "source": "cached_contact_tags"}
        if by_phone:
            return {"path": str(path), "by_phone": by_phone, "catalog": list(catalog.values())}
    return {"path": None, "by_phone": {}, "catalog": []}


def cached_contact_tags_payload(phone: str, *, reason: str = "zapi_unavailable") -> Optional[Dict[str, Any]]:
    snapshot = load_cached_contact_tags_snapshot()
    by_phone = snapshot.get("by_phone") if isinstance(snapshot, dict) else {}
    if not isinstance(by_phone, dict):
        return None
    found = None
    for variant in phone_lookup_variants_for_tags(phone):
        item = by_phone.get(variant)
        if isinstance(item, dict):
            found = item
            break
    if not isinstance(found, dict):
        return None
    tag_ids = [str(x) for x in (found.get("tag_ids") or found.get("tagIds") or []) if x is not None]
    tag_names = [str(x) for x in (found.get("tags") or found.get("tag_names") or []) if x]
    resolved = []
    for idx, name in enumerate(tag_names):
        tid = tag_ids[idx] if idx < len(tag_ids) else name
        resolved.append({"id": tid, "name": name, "source": "cached_contact_tags"})
    return {
        "ok": True,
        "phone": normalize_phone(phone) or phone,
        "source": "cached_contact_tags",
        "fallbackReason": reason,
        "snapshot": snapshot.get("path"),
        "chatStatus": 503,
        "tagsStatus": 503,
        "tagIds": tag_ids,
        "tags": resolved,
        "chat": {"phone": found.get("phone"), "name": found.get("name")},
        "catalog": snapshot.get("catalog") or [],
    }


def fetch_zapi_chat_metadata(phone: str) -> Tuple[int, str, Any]:
    status, body = zapi_get(f"/chats/{phone}", timeout=30)
    return status, body, parse_json_body(body)


def unwrap_zapi_list(payload: Any, preferred_keys=("data", "items", "chats", "tags", "results")) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in preferred_keys:
            value = payload.get(key)
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                nested = unwrap_zapi_list(value, preferred_keys)
                if nested:
                    return nested
    return []


def zapi_tag_id(value: Any) -> Optional[str]:
    if isinstance(value, dict):
        for key in ("id", "tagId", "tag_id", "value"):
            if value.get(key) is not None:
                return str(value.get(key))
        return None
    if value is None:
        return None
    return str(value)


def zapi_tag_name(value: Any) -> Optional[str]:
    if not isinstance(value, dict):
        return None
    for key in ("name", "label", "title", "tag", "description"):
        if value.get(key):
            return str(value.get(key))
    return None


def build_chat_tags_payload(phone: str) -> Dict[str, Any]:
    chat_status, chat_body, chat = fetch_zapi_chat_metadata(phone)
    tags_status, tags_body, catalog_payload = fetch_zapi_tags_catalog()
    catalog = unwrap_zapi_list(catalog_payload, preferred_keys=("tags", "data", "items", "results"))

    tag_ids: list[str] = []
    direct_names: list[str] = []
    if isinstance(chat, dict):
        raw_tags = chat.get("tags") or chat.get("tagIds") or chat.get("labels") or []
        if isinstance(raw_tags, dict):
            raw_tags = unwrap_zapi_list(raw_tags, preferred_keys=("tags", "data", "items", "results"))
        if isinstance(raw_tags, list):
            for item in raw_tags:
                tid = zapi_tag_id(item)
                name = zapi_tag_name(item)
                if tid is not None and tid not in tag_ids:
                    tag_ids.append(tid)
                if name and name not in direct_names:
                    direct_names.append(name)

    catalog_by_id: Dict[str, Any] = {}
    for item in catalog:
        if isinstance(item, dict):
            tid = zapi_tag_id(item)
            if tid is not None:
                catalog_by_id[tid] = item

    resolved = []
    for tag_id in tag_ids:
        meta = catalog_by_id.get(tag_id, {}) if isinstance(catalog_by_id.get(tag_id), dict) else {}
        resolved.append({
            "id": tag_id,
            "name": zapi_tag_name(meta) or tag_id,
            "color": meta.get("color") if isinstance(meta, dict) else None,
            "colorHex": meta.get("colorHex") if isinstance(meta, dict) else None,
        })
    for name in direct_names:
        if not any(t.get("name") == name for t in resolved):
            resolved.append({"id": name, "name": name, "color": None, "colorHex": None})

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


def get_zapi_contact_tag_names_safe(phone: str) -> Tuple[bool, list[str], list[str]]:
    """Retorna tags Z-API normalizadas para decisões de escopo da Clara.

    Falha não deve liberar paciente conhecido. Chamadores decidem fail-open ou
    fail-closed conforme o risco.
    """
    try:
        payload = build_chat_tags_payload(phone)
        if not payload.get("ok"):
            return False, [], []
        names = []
        ids = []
        for tag in payload.get("tags") or []:
            if isinstance(tag, dict):
                if tag.get("name") is not None:
                    names.append(str(tag.get("name")).strip().lower())
                if tag.get("id") is not None:
                    ids.append(str(tag.get("id")).strip())
        return True, names, ids
    except Exception as err:
        log(f"zapi_tag_check_failed phone={phone}: {err}")
        return False, [], []


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


def extract_payload_contact_ids(payload: Dict[str, Any], phone: Optional[str] = None) -> list[str]:
    """IDs que podem representar o mesmo chat na Z-API: telefone real, telefone sem 9 e LID."""
    ids: list[str] = []
    def add(value: Any) -> None:
        raw = str(value or "").strip()
        if not raw:
            return
        digits = "".join(ch for ch in raw if ch.isdigit())
        for candidate in (raw, digits):
            if candidate and candidate not in ids:
                ids.append(candidate)
        if digits:
            for variant in phone_lookup_variants(digits):
                if variant and variant not in ids:
                    ids.append(variant)
    add(phone)
    for key in ("phone", "chatLid", "participantLid", "participantPhone", "senderLid", "chatId"):
        add(payload.get(key))
    for path in (
        ("data", "phone"), ("data", "chatLid"), ("data", "participantLid"), ("data", "participantPhone"),
        ("sender", "phone"), ("sender", "lid"), ("message", "chatLid"), ("message", "participantLid"),
    ):
        add(deep_get(payload, *path))
    return ids


def chat_name_has_patient_marker(payload: Dict[str, Any]) -> bool:
    """Detecta marcador operacional de paciente no nome salvo do WhatsApp.

    Exemplos bloqueados: "Renata Souza - Pac", "Pac - Maria", "Maria PAC",
    "Maria Paciente", "Maria - Pcte". Evita falso positivo em palavras como
    "pacote" ou "impacto".
    """
    values = [
        payload.get("chatName"),
        payload.get("contactName"),
        deep_get(payload, "data", "chatName"),
        deep_get(payload, "data", "contactName"),
        deep_get(payload, "chat", "name"),
        deep_get(payload, "contact", "name"),
    ]
    for value in values:
        text = str(value or "").strip().lower()
        if not text:
            continue
        normalized = re.sub(r"[._/\\|]+", " ", text)
        # Marcadores usados pela equipe no contato WhatsApp.
        if re.search(r"(?:^|[\s\-–—()\[\]:;,.])(?:pac|pcte|paciente)(?:$|[\s\-–—()\[\]:;,.])", normalized):
            return True
    return False


def add_exclusion_alias(phone: str, name: str, reason: str, source: str) -> None:
    if not phone:
        return
    state = load_exclusions_state()
    phones = state.setdefault("phones", {})
    if not isinstance(phones, dict):
        state["phones"] = phones = {}
    now = int(time.time())
    for candidate in phone_lookup_variants(phone):
        if not candidate:
            continue
        current = phones.get(candidate)
        if isinstance(current, dict) and str(current.get("source") or "") == "tiaro_lead_exception":
            continue
        phones[candidate] = {"name": name or "Paciente", "reason": reason, "source": source, "updated_at": now}
    state["updated_at"] = now
    try:
        Path(CLARA_EXCLUSIONS_FILE).write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as err:
        log(f"exclusion_alias_write_failed phone={phone}: {err}")


def get_payload_exclusion_reason(phone: str, payload: Dict[str, Any]) -> Optional[str]:
    # 1) bloqueio por telefone/LID/aliases já conhecidos.
    for candidate in extract_payload_contact_ids(payload, phone):
        reason = get_exclusion_reason(candidate)
        if reason:
            if candidate != phone:
                add_exclusion_alias(phone, str(payload.get("chatName") or payload.get("senderName") or "Paciente"), reason, "payload_exclusion_alias")
                log(f"payload_exclusion_alias phone={phone} matched={candidate} reason={reason}")
            return reason

    # 2) nome operacional do chat indicando paciente antigo. Ex.: "Renata Souza - Pac".
    if chat_name_has_patient_marker(payload):
        add_exclusion_alias(phone, str(payload.get("chatName") or payload.get("senderName") or "Paciente"), "patient_chat_name_marker", "zapi_chat_name_patient_marker")
        return "patient_chat_name_marker"

    # 3) tags Z-API de paciente/programa/VIP/agendou também bloqueiam Clara comercial.
    ok_tags, tag_names, tag_ids = get_zapi_contact_tag_names_safe(phone)
    if ok_tags:
        non_lead_reason = non_lead_tag_reason(tag_names)
        if non_lead_reason:
            add_exclusion_alias(phone, str(payload.get("chatName") or payload.get("senderName") or "Lead não qualificado"), "not_qualified_do_not_followup", non_lead_reason)
            return non_lead_reason
        tag_set = {str(t or "").strip().lower() for t in tag_names}
        if tag_set.intersection({"paciente", "programa", "vip", "agendou", "compareceu", "fechou"}):
            add_exclusion_alias(phone, str(payload.get("chatName") or payload.get("senderName") or "Paciente"), "zapi_non_lead_tag", "zapi_tag_scope_guard")
            return "zapi_non_lead_tag=" + ",".join(sorted(tag_set))
    return None


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

        if path == "/public/video-bioimpedancia-ivs.mp4":
            media_path = Path("/root/.openclaw/media/outbound/clara-assets/video-bioimpedancia-ivs.mp4")
            if not media_path.exists():
                self._send_json(404, {"ok": False, "error": "media_not_found"})
                return
            data = media_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "public, max-age=86400")
            self.end_headers()
            self.wfile.write(data)
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
                if 200 <= status < 300 and isinstance(catalog, list):
                    self._send_json(200, {
                        "ok": True,
                        "zapiStatus": status,
                        "tags": catalog,
                        "zapiBody": None,
                    })
                else:
                    snapshot = load_cached_contact_tags_snapshot()
                    cached_catalog = snapshot.get("catalog") if isinstance(snapshot, dict) else []
                    self._send_json(200 if cached_catalog else 502, {
                        "ok": bool(cached_catalog),
                        "source": "cached_contact_tags" if cached_catalog else "zapi",
                        "fallbackReason": "zapi_unavailable",
                        "snapshot": snapshot.get("path") if isinstance(snapshot, dict) else None,
                        "zapiStatus": status,
                        "tags": cached_catalog if isinstance(cached_catalog, list) else [],
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
                if payload.get("ok") and payload.get("tags"):
                    self._send_json(200, payload)
                else:
                    cached = cached_contact_tags_payload(phone, reason="zapi_unavailable_or_empty_tags")
                    self._send_json(200 if cached else 502, cached or payload)
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

            safety_ok, safety_decision = validate_admin_send_lead_safety(payload, phone, message)
            if not safety_ok:
                log(f"admin_send blocked_by_lead_safety phone={phone} decision={str(safety_decision)[:300]}")
                self._send_json(422, {"ok": False, "phone": phone, "blocked": "lead_safety", "decision": safety_decision})
                return

            exclusion_reason = get_exclusion_reason(phone)
            if not exclusion_reason and not force:
                ok_tags, tag_names, _tag_ids = get_zapi_contact_tag_names_safe(phone)
                if ok_tags:
                    exclusion_reason = non_lead_tag_reason(tag_names)
                    if exclusion_reason:
                        add_exclusion_alias(phone, "Lead não qualificado", "not_qualified_do_not_followup", exclusion_reason)
                if not exclusion_reason and recent_context_has_financial_no_fit_decline(phone):
                    exclusion_reason = "not_qualified_financial_no_fit"
                    add_exclusion_alias(phone, "Lead sem perfil financeiro", exclusion_reason, "admin_send_recent_audit_financial_decline")
            if exclusion_reason and not force:
                matched_exclusion_phone, exclusion_entry = get_exclusion_entry(phone)
                exclusion_source = str((exclusion_entry or {}).get("source") or "")
                # Incidente 2026-06-24: follow-up em lote ignorou a classificação
                # `paciente_ativo` do histórico e o bypass de `patient_bridge_known`
                # permitiu envio a pacientes. A partir daqui, qualquer marcador
                # paciente-like bloqueia /admin/send fail-closed; exceção só pode ser
                # tratada por fluxo específico, manual e auditado fora do lote.
                if str(exclusion_reason).startswith("lead_exception"):
                    mark_followup_outbound(phone, "admin_send_lead_exception_allowed")
                    log(f"admin_send_exclusion_allowed phone={phone} reason={exclusion_reason} matched={matched_exclusion_phone}")
                elif exclusion_reason == "patient_bridge_known" or exclusion_source == "bridge_contexto_paciente":
                    self._send_json(409, {"ok": False, "phone": phone, "blocked": True, "reason": "patient_bridge_known_fail_closed"})
                    return
                else:
                    self._send_json(409, {"ok": False, "phone": phone, "blocked": True, "reason": exclusion_reason})
                    return

            message = enforce_outbound_price_safety(phone, final_scrub_banned_next_step_phrase(message))

            if dry_run:
                preview = message
                self._send_json(200, {"ok": True, "dry_run": True, "phone": phone, "message_preview": preview[:160]})
                return

            try:
                gate_ok, gate_decision = evaluate_admin_send_action_gate(payload)
                if not gate_ok:
                    log(f"admin_send blocked_by_action_gate phone={phone} decision={str(gate_decision)[:300]}")
                    self._send_json(403, {"ok": False, "phone": phone, "blocked": "action_gate", "decision": gate_decision})
                    return
                zapi_status, zapi_body = send_zapi_text(phone, message, source="admin_send")
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

        append_webhook_audit(payload, raw, path)

        # Planilha operacional: registrar também mensagens outbound/fromMe.
        # Antes, o fanout para Apps Script acontecia só depois do filtro fromMe;
        # com isso respostas da Clara/admin/equipe eram preservadas no audit local,
        # mas não chegavam à planilha. Mantemos grupos fora para não poluir o CRM.
        if not is_group_message(payload):
            fanout_to_apps_script(payload)

        if is_from_me(payload):
            phone = extract_phone(payload)
            from_api = payload.get("fromApi") is True or deep_get(payload, "data", "fromApi") is True
            ids = extract_payload_contact_ids(payload, phone)
            if phone and from_api:
                for candidate in ids or [phone]:
                    mark_followup_outbound(candidate, "zapi_from_api_outbound")
            elif phone:
                # Takeover humano deve travar todos os aliases do mesmo chat.
                # A Z-API pode registrar a saída pelo LID e a resposta do paciente pelo telefone real.
                mark_human_activity_for_ids(ids or [phone], note="from_me_outbound_detected")
                takeover_until = None if CLARA_HUMAN_TAKEOVER_INDEFINITE else time.time() + MANUAL_TAKEOVER_WINDOW_SECONDS
                set_manual_override_for_ids(ids or [phone], True, note="from_me_outbound_detected", until=takeover_until)
            reason = "from_api_outbound" if from_api else "from_me"
            log(f"ignored phone={phone or 'missing'} reason={reason} ids={','.join(ids)} payload_keys={','.join(sorted(payload.keys()))}")
            self._send_json(200, {"ok": True, "ignored": reason})
            return
        if is_group_message(payload):
            log(f"ignored reason=group_message payload_keys={','.join(sorted(payload.keys()))}")
            self._send_json(200, {"ok": True, "ignored": "group_message"})
            return

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

        def process_async():
            if not acquire_phone_processing(phone):
                log(f"ignored phone={phone} message_id={message_id} reason=concurrent_phone_processing text={event_text[:120]!r}")
                return
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
                mark_price_context_if_present(phone, processed_text)
                financial_no_fit_current = contains_financial_no_fit_decline(processed_text)

                # Regra Tiaro 2026-05-30: SEMPRE consultar QuarkClinic pelo celular
                # antes de qualquer decisão comercial da Clara. Falha na consulta = não responde.
                quark_ok, patient_flag, quark_reason = quarkclinic_patient_check(phone)
                if not quark_ok:
                    log(f"blocked phone={phone} reason={quark_reason}")
                    notify_internal_clara_failure(phone, sender_name, processed_text, "quarkclinic_check_unavailable", quark_reason)
                    return
                if patient_flag:
                    add_exclusion_alias(phone, str(sender_name or payload.get("chatName") or "Paciente"), "quarkclinic_patient_rc12", "quarkclinic_live_check")
                    log(f"patient_detected phone={phone} source=quarkclinic blocked=RC12")
                    return

                bypass_exclusion, bypass_reason = should_bypass_exclusion_for_lead_intent(phone, processed_text)
                exclusion_reason = get_payload_exclusion_reason(phone, payload)
                # RC-55: se o QuarkClinic confirmou que NÃO é paciente, uma marca antiga
                # patient_bridge_known/bridge_contexto_paciente não pode silenciar lead ativo.
                # Mantém bloqueio de paciente real quando QuarkClinic sinaliza patient_flag acima.
                if exclusion_reason in ("patient_bridge_known", "bridge_contexto_paciente") and quark_ok and not patient_flag:
                    bypass_exclusion = True
                    bypass_reason = "quarkclinic_no_match_overrides_stale_patient_bridge_exclusion"
                if exclusion_reason and not bypass_exclusion:
                    log(f"blocked phone={phone} reason=exclusion:{exclusion_reason}")
                    return
                if exclusion_reason and bypass_exclusion:
                    log(f"lead_exclusion_bypassed phone={phone} reason={bypass_reason}")
                alias_override_reason = get_payload_manual_override_reason(phone, payload)
                if alias_override_reason:
                    log(f"blocked phone={phone} reason={alias_override_reason}")
                    return
                paused, reason = should_pause_clara(phone)
                if paused:
                    log(f"blocked phone={phone} reason={reason}")
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
                    if is_audio:
                        reply = "Te ouvi. Para eu te orientar melhor, isso que você contou tem relação mais com emagrecimento, falta de energia ou dificuldade de manter resultado?"
                        log(f"audio_no_reply_failsafe phone={phone} replyPreview={reply[:120]!r}")
                    else:
                        reply = build_text_runtime_failsafe_reply(processed_text)
                        log(f"text_no_reply_failsafe phone={phone} replyPreview={reply[:120]!r}")
                update_confirmed_lead_name(phone, processed_text)
                reply = enforce_no_first_time_question(reply)
                reply = enforce_no_unconfirmed_name(phone, reply, processed_text, sender_name=sender_name)
                reply = enforce_service_scope_question(processed_text, reply)
                reply = enforce_discovery_before_next_step(processed_text, reply)
                reply = enforce_spin_before_agendamento(phone, processed_text, reply)
                reply = enforce_no_reopening_after_context(phone, processed_text, reply)
                reply = enforce_context_continuity_before_send(phone, processed_text, reply)
                reply = enforce_included_explanation_after_yes(phone, processed_text, reply)
                reply = enforce_price_question_after_context(phone, processed_text, reply)
                reply = enforce_money_after_journey(phone, processed_text, reply)
                reply = enforce_fatigue_complaint_no_repeat(phone, processed_text, reply)
                reply = enforce_rc39_no_generic_next_step(reply)
                reply = enforce_price_timing(phone, processed_text, reply)
                reply = enforce_program_reasoning(processed_text, reply)
                reply = enforce_plan_question_response(processed_text, reply)
                reply = enforce_objection_handling(processed_text, reply)
                reply = enforce_call_request_response(processed_text, reply)
                reply = enforce_journey_before_scheduling(phone, processed_text, reply)
                reply = enforce_vitor_video_practical_application(processed_text, reply)
                reply = enforce_agendamento_reply_quality(reply)
                reply = final_scrub_banned_next_step_phrase(reply)
                reply = enforce_no_reopening_after_context(phone, processed_text, reply)
                reply = enforce_context_continuity_before_send(phone, processed_text, reply)
                reply = enforce_included_explanation_after_yes(phone, processed_text, reply)
                reply = enforce_price_question_after_context(phone, processed_text, reply)
                reply = enforce_money_after_journey(phone, processed_text, reply)
                reply = enforce_fatigue_complaint_no_repeat(phone, processed_text, reply)
                reply = enforce_outbound_price_safety(phone, reply, processed_text)
                block_reply, block_reason = should_block_reply(phone, reply)
                if block_reply:
                    log(f"blocked_reply phone={phone} reason={block_reason} replyPreview={reply[:120]!r}")
                    notify_internal_clara_failure(phone, sender_name, processed_text, "blocked_reply", block_reason or "resposta bloqueada por segurança")
                    return
                sent_as_audio = False
                if is_audio and CLARA_AUDIO_MIRRORING and (ELEVENLABS_API_KEY or OPENAI_API_KEY):
                    try:
                        audio_reply, tts_provider = generate_tts_audio(reply)
                        status, body = send_zapi_audio(phone, audio_reply, source="clara_reply")
                        sent_as_audio = 200 <= int(status) < 300
                        if sent_as_audio:
                            log(f"audio_reply_sent phone={phone} provider={tts_provider} status={status}")
                        else:
                            log(f"audio_send_failed phone={phone} provider={tts_provider} status={status} body={body[:200]} falling_back=text")
                    except Exception as audio_err:
                        log(f"audio_reply_failed phone={phone}: {audio_err}; falling_back=text")
                        sent_as_audio = False
                if not sent_as_audio:
                    status, body = send_zapi_text_human_sequence(phone, reply, source="clara_reply")
                if 200 <= int(status) < 300:
                    mark_lead_replied(phone, reply)
                    if financial_no_fit_current:
                        add_exclusion_alias(phone, str(sender_name or payload.get("chatName") or "Lead sem perfil financeiro"), "not_qualified_financial_no_fit", "lead_inbound_financial_decline")
                        update_lead_entry(phone, {
                            "followup_blocked": True,
                            "not_qualified": True,
                            "not_qualified_reason": "financial_no_fit",
                            "not_qualified_at": time.time(),
                        })
                        log(f"rc70_financial_no_fit_exclusion_added phone={phone} text={processed_text[:120]!r}")
                    if is_agendamento_event(reply):
                        notify_internal_agendamento(phone, sender_name, processed_text, reply)
                    if contains_call_request(processed_text):
                        notify_internal_contact_request(phone, sender_name, processed_text, reply)
                log(f"sent phone={phone} mode={'audio' if sent_as_audio else 'text'} zapiStatus={status} replyPreview={reply[:120]!r} zapiBody={body[:200]}")
            except Exception as err:
                log(f"bridge error phone={phone}: {err}")
                if is_audio:
                    fallback_reply = "Recebi seu áudio, mas ele não abriu direito por aqui. Pode me mandar de novo ou me resumir em uma frase o principal? Quero te orientar sem deixar sua mensagem parada."
                    try:
                        sent_as_audio = False
                        status = 0
                        body = ""
                        if CLARA_AUDIO_MIRRORING and (ELEVENLABS_API_KEY or OPENAI_API_KEY):
                            try:
                                audio_reply, tts_provider = generate_tts_audio(fallback_reply)
                                status, body = send_zapi_audio(phone, audio_reply, source="clara_audio_failsafe")
                                sent_as_audio = 200 <= int(status) < 300
                                if sent_as_audio:
                                    log(f"audio_failsafe_sent phone={phone} provider={tts_provider} status={status}")
                            except Exception as audio_err:
                                log(f"audio_failsafe_audio_failed phone={phone}: {audio_err}; falling_back=text")
                        if not sent_as_audio:
                            status, body = send_zapi_text_human_sequence(phone, fallback_reply, source="clara_audio_failsafe")
                            log(f"audio_failsafe_text_sent phone={phone} status={status}")
                        if 200 <= int(status) < 300:
                            mark_lead_replied(phone, fallback_reply)
                    except Exception as failsafe_err:
                        log(f"audio_failsafe_failed phone={phone}: {failsafe_err}")
                if not is_audio:
                    try:
                        fallback_reply = build_text_runtime_failsafe_reply(processed_text or event_text)
                        status, body = send_zapi_text_human_sequence(phone, fallback_reply, source="clara_text_failsafe")
                        log(f"text_failsafe_sent phone={phone} status={status} replyPreview={fallback_reply[:120]!r} body={body[:200]}")
                        if 200 <= int(status) < 300:
                            mark_lead_replied(phone, fallback_reply)
                    except Exception as failsafe_err:
                        log(f"text_failsafe_failed phone={phone}: {failsafe_err}")
                try:
                    notify_internal_clara_failure(phone, sender_name, processed_text or event_text, "runtime_exception", str(err))
                except Exception as notify_err:
                    log(f"bridge error notification failed phone={phone}: {notify_err}")
            finally:
                release_phone_processing(phone)

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
