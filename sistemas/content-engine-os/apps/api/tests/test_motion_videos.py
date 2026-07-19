import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.motion_video_planner import (  # noqa: E402
    CONTENT_FORMATS,
    MOTION_PRESETS,
    SCREEN_FORMATS,
    build_motion_video_plan,
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

    def test_build_plan_rejects_unknown_content_format(self):
        with self.assertRaisesRegex(ValueError, "content_format desconhecido"):
            build_motion_video_plan({"topic": "Teste", "content_format": "lego_brick"})


if __name__ == "__main__":
    unittest.main()
