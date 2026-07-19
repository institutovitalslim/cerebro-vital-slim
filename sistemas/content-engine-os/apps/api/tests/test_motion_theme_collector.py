import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.motion_video_theme_collector import (
    build_motion_plan_payload_from_winner,
    build_theme_ingest_payload,
    build_winner_outputs,
    parse_hashtag_posts,
    select_theme_winners,
    theme_tags,
)


class MotionThemeCollectorTests(unittest.TestCase):
    def test_theme_tags_has_menopause_seed_set(self):
        tags = theme_tags("menopausa", "")
        self.assertIn("menopausa", tags)
        self.assertIn("climaterio", tags)
        self.assertLessEqual(len(tags), 12)

    def test_parse_hashtag_posts_filters_and_scores_menopause(self):
        data = {
            "posts": {
                "edges": [
                    {"node": {"shortcode": "ABC", "is_video": True, "edge_liked_by": {"count": 10}, "edge_media_to_comment": {"count": 2}, "edge_media_to_caption": {"edges": [{"node": {"text": "Menopausa, sono e fogachos precisam de avaliação."}}]}}},
                    {"node": {"shortcode": "NOISE", "edge_liked_by": {"count": 999}, "edge_media_to_caption": {"edges": [{"node": {"text": "Receita aleatória sem relação."}}]}}},
                ]
            }
        }
        items = parse_hashtag_posts("menopausa", "fogachos", data, limit=10)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["shortcode"], "ABC")
        self.assertEqual(items[0]["score"], 20)
        self.assertEqual(items[0]["format"], "reel")

    def test_build_theme_ingest_payload_is_safe_reference(self):
        payload = build_theme_ingest_payload({
            "shortcode": "ABC",
            "url": "https://www.instagram.com/reel/ABC/",
            "caption": "Menopausa não é frescura: sono, humor e metabolismo mudam.",
            "likes": 40,
            "comments": 3,
            "score": 55,
            "hashtag": "menopausa",
            "format": "reel",
        }, topic="menopausa")
        self.assertEqual(payload["external_id"], "instagram:ABC")
        self.assertEqual(payload["source_type"], "rapidapi_instagram_theme_search")
        self.assertEqual(payload["content_format"], "sinal_escondido")
        self.assertEqual(payload["compliance_risk"], "review_required")
        self.assertIn("não copiar", payload["why_this_example_works"].lower())
    def test_select_theme_winners_returns_three_output_packs(self):
        examples = [
            {"external_id": "a", "content_format": "sinal_escondido", "hook_summary": "Menopausa não é frescura", "why_this_example_works": "Abre loop", "ivs_applicability_score": 90, "metadata": {"raw_metrics": {"score": 80}}, "source_handle_or_url": "theme_search:menopausa:fogachos", "content_url": "https://www.instagram.com/p/a/"},
            {"external_id": "b", "content_format": "antes_da_decisao", "hook_summary": "Antes da terapia hormonal", "why_this_example_works": "Quebra objeção", "ivs_applicability_score": 76, "metadata": {"raw_metrics": {"score": 120}}, "source_handle_or_url": "theme_search:menopausa:terapiahormonal", "content_url": "https://www.instagram.com/p/b/"},
            {"external_id": "c", "content_format": "checklist_rapido", "hook_summary": "Sinais que merecem avaliação", "why_this_example_works": "Seguro", "ivs_applicability_score": 95, "metadata": {"raw_metrics": {"score": 20}}, "source_handle_or_url": "theme_search:menopausa:climaterio", "content_url": "https://www.instagram.com/p/c/"},
        ]
        winners = select_theme_winners(examples, topic="menopausa")
        self.assertEqual([w["winner_type"] for w in winners], ["attention", "conversion", "ivs_fit"])
        for winner in winners:
            outputs = winner["outputs"]
            self.assertEqual(len(outputs["hooks_adaptados"]), 3)
            self.assertIn("roteiro_reel", outputs)
            self.assertIn("stories", outputs)
            self.assertIn("angulo_anuncio", outputs)
            self.assertIn("hipotese_metrica", outputs)
            self.assertFalse(winner["selected_for_generation"])

    def test_build_winner_outputs_keeps_medical_guardrails(self):
        outputs = build_winner_outputs({"hook_summary": "Menopausa não é frescura", "content_format": "sinal_escondido"}, winner_type="attention", topic="menopausa")
        text = " ".join(outputs["hooks_adaptados"]).lower()
        self.assertIn("avaliação", text)
        self.assertNotIn("garante", text)
        self.assertIn("review_required", outputs["compliance_gate"])
    def test_build_motion_plan_payload_from_winner_links_source_and_guardrails(self):
        winner = {
            "winner_type": "attention",
            "external_id": "instagram:ABC",
            "content_format": "sinal_escondido",
            "hook_summary": "Menopausa não é frescura",
            "source_url": "https://www.instagram.com/p/ABC/",
            "outputs": build_winner_outputs({"hook_summary": "Menopausa não é frescura", "content_format": "sinal_escondido"}, winner_type="attention", topic="menopausa"),
        }
        payload = build_motion_plan_payload_from_winner(winner, topic="menopausa")
        self.assertEqual(payload["source_type"], "theme_winner")
        self.assertIsNone(payload["source_id"])
        self.assertEqual(payload["content_format"], "sinal_escondido")
        self.assertIn("Menopausa", payload["topic"])
        self.assertIn("instagram:ABC", payload["source_examples_summary"])
        self.assertIn("não copiar", payload["source_examples_summary"].lower())
        self.assertEqual(payload["duration_seconds"], 60)


if __name__ == "__main__":
    unittest.main()
