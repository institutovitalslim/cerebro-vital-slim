import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.motion_video_planner import (  # noqa: E402
    CONTENT_FORMATS,
    MOTION_PRESETS,
    SCREEN_FORMATS,
    build_content_format_examples,
    build_motion_video_plan,
    example_winners_for_format,
    motion_video_matrix_8x8,
)


class MotionVideoPlannerTests(unittest.TestCase):
    def test_content_format_library_uses_official_field_and_twenty_formats(self):
        keys = {item["key"] for item in CONTENT_FORMATS}
        self.assertEqual(len(CONTENT_FORMATS), 20)
        self.assertIn("mito_que_prende", keys)
        self.assertIn("mini_aula_visual", keys)
        self.assertNotIn("format_brick", keys)
        self.assertTrue(all("motion_notes" in item for item in CONTENT_FORMATS))

    def test_options_contract_exposes_formats_presets_and_screen_formats(self):
        self.assertIn("ivs_mixed_media_medico_premium", MOTION_PRESETS)
        self.assertEqual(SCREEN_FORMATS["reels"]["aspect_ratio"], "9:16")
        self.assertEqual(SCREEN_FORMATS["youtube"]["aspect_ratio"], "16:9")

    def test_build_plan_creates_six_blocks_with_higgsfield_prompt_sections(self):
        payload = {
            "topic": "Por que emagrecer não é o mesmo que manter?",
            "objective": "educacao_autoridade",
            "objection": "ja_tentei_de_tudo",
            "content_format": "mito_que_prende",
            "content_strategy": "loop_previsao",
            "screen_format": "reels",
            "duration_seconds": 60,
            "visual_preset": "ivs_mixed_media_medico_premium",
            "source_examples_summary": "Exemplos usados apenas para abstrair ritmo e mecanismo.",
        }
        plan = build_motion_video_plan(payload)
        self.assertEqual(plan["content_format"], "mito_que_prende")
        self.assertEqual(plan["aspect_ratio"], "9:16")
        self.assertEqual(plan["blocks_count"], 6)
        self.assertEqual(len(plan["blocks"]), 6)
        first_prompt = plan["blocks"][0]["visual_prompt"]
        for marker in ("STYLE REFERENCE", "NARRATION", "SCENE", "MOTION", "AUDIO", "NEGATIVE"):
            self.assertIn(marker, first_prompt)
        self.assertGreaterEqual(plan["quality_scores_estimados"]["compliance_score"], 85)
        self.assertEqual(plan["approval_status"], "plan_only")
        self.assertEqual(len(plan["source_examples"]), 3)
        self.assertEqual(plan["matrix_8x8_applied"]["rows"], 8)
        self.assertEqual(plan["matrix_8x8_applied"]["columns"], 8)
        self.assertEqual({item["winner_type"] for item in plan["batch_winners"]}, {"attention", "conversion", "ivs_fit"})

    def test_phase2_examples_matrix_and_winners_contract(self):
        examples = build_content_format_examples("mito_que_prende")
        self.assertEqual(len(examples), 3)
        self.assertTrue(all(item["copy_guardrail"] for item in examples))
        matrix = motion_video_matrix_8x8()
        self.assertEqual(len(matrix["rows"]), 8)
        self.assertEqual(len(matrix["columns"]), 8)
        winners = example_winners_for_format("mito_que_prende")
        self.assertEqual([item["winner_type"] for item in winners], ["attention", "conversion", "ivs_fit"])
        self.assertTrue(all(len(item["outputs_required"]) == 5 for item in winners))

    def test_real_example_payload_is_sanitized_and_governed(self):
        from app.services.motion_video_planner import normalize_real_content_format_example

        item = normalize_real_content_format_example({
            "content_format": "mito_que_prende",
            "source_type": "instagram_url",
            "content_url": "https://www.instagram.com/reel/ABC123/?igsh=secret",
            "source_handle_or_url": "@perfil_exemplo",
            "hook_summary": "Hook externo aqui",
            "transcript_summary": "Resumo do vídeo, sem copiar roteiro literal.",
            "why_this_example_works": "Abre loop e resolve com mecanismo.",
            "ivs_applicability_score": 91,
        })
        self.assertEqual(item["content_format"], "mito_que_prende")
        self.assertEqual(item["external_id"], "instagram:ABC123")
        self.assertEqual(item["content_url"], "https://www.instagram.com/reel/ABC123/")
        self.assertEqual(item["compliance_risk"], "review_required")
        self.assertFalse(item["selected_for_generation"])
        self.assertIn("não copiar", item["copy_guardrail"].lower())

    def test_build_plan_rejects_unknown_content_format(self):
        with self.assertRaisesRegex(ValueError, "content_format desconhecido"):
            build_motion_video_plan({"topic": "Teste", "content_format": "lego_brick"})


if __name__ == "__main__":
    unittest.main()
