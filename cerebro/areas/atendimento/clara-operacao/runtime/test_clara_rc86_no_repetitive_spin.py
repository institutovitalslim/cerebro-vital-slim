import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("zapi_clara_bridge", ROOT / "zapi_clara_bridge.py")
assert spec is not None and spec.loader is not None
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def setup_history(text):
    setattr(b, "build_recent_conversation_context", lambda phone, limit=14: text)
    setattr(b, "get_recent_lead_texts", lambda phone, limit=8: [text])
    setattr(b, "get_lead_entry", lambda phone: {"reply_count": 1, "inbound_count": 2})
    setattr(b, "get_phone_event_entry", lambda phone: {})
    setattr(b, "update_phone_event_entry", lambda phone, payload: None)
    setattr(b, "log", lambda message: None)


def test_bare_peso_does_not_get_reflective_confirmation_loop():
    setup_history(
        "Clara: Para eu continuar do ponto certo e sem pular etapas: o que mais está te incomodando hoje — peso, disposição, hormônios ou saúde de forma geral?"
    )
    repetitive = "Entendi. Então o foco principal hoje é reduzir peso, desinchar e melhorar a forma como a roupa veste, certo?"
    fixed = b.enforce_no_repetitive_discovery_after_declared_context("5571000000000", "Peso", repetitive)
    lower = fixed.lower()
    assert "foco principal" not in lower, fixed
    assert "certo?" not in lower, fixed
    assert "dentro do emagrecimento" in lower or "dentro do peso" in lower, fixed
    assert "efeito sanfona" in lower or "sinal hormonal" in lower, fixed


def test_weight_plus_hormone_context_advances_to_journey_not_more_spin():
    setup_history(
        "Clara: o que mais está te incomodando hoje — peso, disposição, hormônios ou saúde de forma geral?\n"
        "Lead: Peso\n"
        "Clara: Então o foco principal hoje é reduzir peso, desinchar e melhorar a forma como a roupa veste, certo?"
    )
    repetitive = "Faz muito sentido investigar. Às vezes peso, inchaço, disposição e hormônios andam juntos. Você sente mais cansaço ou dificuldade de perder peso?"
    fixed = b.enforce_no_repetitive_discovery_after_declared_context(
        "5571000000000",
        "Eu também tenho que ver esse hormônios, não é possível",
        repetitive,
    )
    lower = fixed.lower()
    assert "você sente mais" not in lower and "voce sente mais" not in lower, fixed
    assert "consulta médica" in lower or "dra. daniely" in lower, fixed
    assert "bioimpedância" in lower or "bioimpedancia" in lower, fixed
    assert "esse formato de avaliação faz sentido" in lower or "esse formato de avaliacao faz sentido" in lower, fixed


if __name__ == "__main__":
    test_bare_peso_does_not_get_reflective_confirmation_loop()
    test_weight_plus_hormone_context_advances_to_journey_not_more_spin()
    print("rc86_no_repetitive_spin_ok")
