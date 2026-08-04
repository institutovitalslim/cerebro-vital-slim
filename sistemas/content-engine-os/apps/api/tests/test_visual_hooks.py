import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.motion_video_planner import (  # noqa: E402
    VISUAL_HOOKS,
    build_motion_video_plan,
    motion_video_options,
)
from app.routers.orchestrate import (  # noqa: E402
    OrchestrateRequest,
    _build_prompt,
    _modular_meta,
    _quality,
    _visual_hook_gate,
    _visual_hook_key,
)


class VisualHookLayerTests(unittest.TestCase):
    def test_visual_hook_registry_exposes_five_pdf_categories(self):
        keys = {item["key"] for item in VISUAL_HOOKS}
        self.assertEqual(len(VISUAL_HOOKS), 5)
        self.assertEqual(keys, {
            "text_slide_in",
            "match_cut",
            "jump_switch",
            "speed_ramp",
            "unusual_image",
        })
        self.assertTrue(all(item["category"] for item in VISUAL_HOOKS))
        self.assertTrue(all(item["ivs_use"] for item in VISUAL_HOOKS))
        self.assertTrue(all(item["guardrails"] for item in VISUAL_HOOKS))

    def test_motion_options_and_plan_include_visual_hook_layer(self):
        options = motion_video_options()
        self.assertIn("visual_hooks", options)
        self.assertIn("Visual Hook", " → ".join(options["workflow"]))

        plan = build_motion_video_plan({
            "topic": "Mulher 45+ que não se reconhece no espelho",
            "content_format": "historia_espelho",
            "visual_hook": "unusual_image",
            "content_strategy": "jornada_ivs",
        })
        self.assertEqual(plan["visual_hook"], "unusual_image")
        self.assertEqual(plan["visual_hook_category"], "visual_selection")
        self.assertIn("rouparia", plan["visual_hook_application"].lower())
        self.assertGreaterEqual(plan["visual_hook_gate"]["total"], 8)
        self.assertIn("VISUAL HOOK", plan["blocks"][0]["visual_prompt"])

    def test_orchestrate_request_carries_visual_hook_to_prompt_meta_and_quality(self):
        req = OrchestrateRequest(
            formato="reels",
            tema="Mulher 45+ que não se reconhece no espelho e acha que falhou de novo",
            visual_hook_mechanic="match_cut",
            objecao_alvo="ja_tentei_de_tudo",
            quebra_objecao="não é falta de força de vontade; é falta de investigação individualizada",
            content_strategy="jornada_ivs",
        )
        prompt = _build_prompt(req, None, [], None, [])
        self.assertIn("VISUAL HOOK ESCOLHIDO", prompt)
        self.assertIn("match_cut", prompt)
        self.assertIn("visual_hook_shots", prompt)

        output = {
            "title": "Não é *falta de disciplina*",
            "hook": "O prato solto vira checklist de avaliação em um match cut.",
            "script": [
                "Você olha para o espelho e pensa que falhou de novo.",
                "Mas talvez o problema não seja força de vontade.",
                "Na prática, investigar exames, rotina e fome muda o caminho.",
                "O Instituto Vital Slim entra como guia, sem julgamento.",
                "Salve para lembrar: primeiro entenda o mecanismo.",
            ],
            "caption": "Conteúdo educativo. Salve.",
            "hashtags": ["#emagrecimento"],
            "modular_blocks": {
                "visual_hook_mechanic": "match_cut",
                "visual_hook_category": "pattern_interrupt_visual_switching",
                "visual_hook_purpose": "mostrar a virada entre tentativa solta e avaliação",
                "visual_hook_shots": [
                    {"shot": 1, "duration_sec": "0-2", "visual_action": "prato solto", "reason": "interrompe o scroll"},
                    {"shot": 2, "duration_sec": "2-4", "visual_action": "checklist de avaliação", "reason": "abre payoff"},
                ],
                "cena": "espelho",
                "tensao": "não se reconhece",
                "reframe": "não é culpa",
                "guia": "Instituto Vital Slim",
                "caminho": "avaliação individualizada",
            },
        }
        meta = _modular_meta(req, output)
        self.assertEqual(meta["modular_blocks"]["visual_hook_mechanic"], "match_cut")
        self.assertEqual(meta["modular_blocks"]["visual_hook_category"], "pattern_interrupt_visual_switching")

        gate = _visual_hook_gate(output)
        self.assertEqual(gate["version"], "visual_hook_gate_ivs_v1")
        self.assertGreaterEqual(gate["total"], 8)
        score, breakdown = _quality(output, "reels", "jornada_ivs")
        self.assertIn("visual_hook_gate", breakdown)
        self.assertGreater(score, 70)

    def test_unknown_visual_hook_falls_back_safely(self):
        self.assertEqual(_visual_hook_key("efeito_milagre"), "text_slide_in")


if __name__ == "__main__":
    unittest.main()
