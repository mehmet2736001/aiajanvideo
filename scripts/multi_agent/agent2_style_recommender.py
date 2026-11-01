# -*- coding: utf-8 -*-
"""
Agent 2: Stil Öneri & Orkestrasyon Ajanı (Style Recommender & Orchestrator)
Görevi:
  1. Metnin anlamsal yapısını (semantik özellikler) analiz eder.
     - Vektörel İnfografik: Tarihsel anlatılar, felsefi/soyut kavramlar, eğitim, sayılar, metaforlar.
     - Sinematik: Doğa, biyoloji, makro çekimler, atmosferik tefekkür, fiziksel görsel tasvirler.
  2. Kullanıcı Onay Kartı (RecommendationCard) oluşturur.
  3. Süreci AWAIT_USER_SELECTION (phase_1_awaiting_user_selection) durumunda duraklatır.
"""
import re
import json
from typing import Optional, Callable, List
from .base_agent import BaseAgent
from .state import (
    ProjectState, PipelinePhase, TrackType, RecommendationCard,
    TrackOption, StoryboardData, SceneBeat
)


VECTOR_KEYWORDS = [
    "tarih", "sahabe", "mus'ab", "musab", "hicret", "savaş", "zafer", "ordu",
    "kavram", "felsefe", "eğitim", "ilke", "kural", "sayı", "yıl", "asır",
    "zenginlik", "para", "altın", "kasa", "kısıtlama", "hapis", "fedakarlık",
    "dava", "inanç", "şehit", "yolculuk", "rota", "harita", "adım", "aşama"
]

CINEMATIC_KEYWORDS = [
    "doğa", "orman", "deniz", "okyanus", "güneş", "ışık", "huzme", "kainat",
    "yıldız", "galaksi", "uzay", "hücre", "biyoloji", "parmak izi", "göz",
    "iris", "dna", "el yazması", "mushaf", "parşömen", "rahle", "derviş",
    "dağ", "rüzgar", "atmosfer", "tefekkür", "sukut", "sessizlik", "yağmur"
]


class StyleRecommenderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id=2,
            name="Stil Öneri & Karar Ajanı",
            required_phase=PipelinePhase.PHASE_1_TRANSCRIBED,
            target_phase=PipelinePhase.PHASE_1_AWAITING_USER_SELECTION
        )

    def _process(
        self,
        state: ProjectState,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        transcript = state.transcription.clean_text
        text_lower = transcript.lower()

        if on_progress:
            on_progress(self.agent_id, "running", {
                "message": "Metin semantik analizi yapılıyor (Vektörel İnfografik vs Sinematik Belgesel)..."
            })

        # 1. Semantic Feature Scoring
        vector_matches = [k for k in VECTOR_KEYWORDS if k in text_lower]
        cinematic_matches = [k for k in CINEMATIC_KEYWORDS if k in text_lower]

        v_score = len(vector_matches) * 1.5 + (2.0 if any(char.isdigit() for char in transcript) else 0.0)
        c_score = len(cinematic_matches) * 1.5

        # Try Gemini LLM Deep Semantic Analysis
        llm_recommendation = None
        try:
            from scripts.key_pool import pool
            system_prompt = (
                "You are an Elite Video Production Art Director and Semantic Classifier. "
                "Analyze the Turkish transcript and strictly classify into one of two tracks:\n"
                "1. 'vector_infographic': Mandatory if the text contains historical narratives, companions/sahabe stories (e.g. Mus'ab bin Umeyr), "
                "conceptual or philosophical explanations, sacrifice, migration/hicret routes, education, statistics, numbers, or symbolic metaphors.\n"
                "2. 'cinematic': Mandatory if the text contains nature, biology, macro biometrics, cells, fingerprints, atmospheric cosmos, starry skies, physical documentary lighting, or parchment/mushaf visuals.\n"
                "Output strictly JSON with format:\n"
                "{\"recommended_track\": \"vector_infographic\" | \"cinematic\", \"confidence\": 0.95, \"reason\": \"Turkish explanation...\", \"features\": [\"feature1\", \"feature2\"]}"
            )
            raw, _ = pool.query_with_rotation(f"Transcript:\n{transcript[:1000]}", system_instruction=system_prompt, model="gemini-3.5-flash-lite")
            if raw:
                cleaned = re.sub(r"```json\s*", "", raw)
                cleaned = re.sub(r"```\s*", "", cleaned).strip()
                llm_parsed = json.loads(cleaned)
                llm_recommendation = llm_parsed
        except Exception as e:
            print(f"[Style Recommender] LLM rotation notice: {e}")

        # Consolidate decision
        if llm_recommendation and llm_recommendation.get("recommended_track") in ["vector_infographic", "cinematic"]:
            rec_track = TrackType(llm_recommendation["recommended_track"])
            confidence = float(llm_recommendation.get("confidence", 0.92))
            reason = llm_recommendation.get("reason", "Metnin içerdiği kavramsal yapı analiz edildi.")
            features = llm_recommendation.get("features", vector_matches if rec_track == TrackType.VECTOR_INFOGRAPHIC else cinematic_matches)
        else:
            if v_score >= c_score:
                rec_track = TrackType.VECTOR_INFOGRAPHIC
                confidence = round(min(0.98, 0.75 + (v_score / 20.0)), 2)
                reason = (
                    "Metin tarihsel anlatı, kavramsal/felsefi açıklamalar ve sembolik metaforlar barındırıyor "
                    "(Örn: Mus'ab bin Umeyr, fedakarlık, hicret ve soyut hakikatler)."
                )
                features = vector_matches or ["kavramsal anlatım", "tarihsel bağlam", "sembolik metafor"]
            else:
                rec_track = TrackType.CINEMATIC
                confidence = round(min(0.98, 0.75 + (c_score / 20.0)), 2)
                reason = (
                    "Metin doğa, biyoloji, makro detaylar veya tefekkür odaklı derin görsel tasvirler barındırıyor "
                    "(Örn: kainat, parmak izi, el yazması mushaf, ilahi nizam)."
                )
                features = cinematic_matches or ["atmosferik tefekkür", "makro detaylar", "35mm doku"]

        # 2. Build Interactive User Approval Card Options
        options = [
            TrackOption(
                id=TrackType.CINEMATIC,
                title="Sinematik Belgesel",
                subtitle="Photorealistic B-Roll & 35mm Film",
                badge="Diffusion Pipeline",
                description="Google Veo / Kling / Flux I2V motoruyla 35mm sığ alan derinlikli, ultra gerçekçi sinematik B-roll sahneleri.",
                engine="Flux.1 (Keyframe T2I) + Veo 2 / Kling 1.5 (I2V)",
                pros=["Yüksek sinematik gerçekçilik", "Huşu ve derin atmosfer", "35mm optik kamera hareketleri"]
            ),
            TrackOption(
                id=TrackType.VECTOR_INFOGRAPHIC,
                title="2D Vektörel İnfografik",
                subtitle="Motion Graphics & Dynamic SVG",
                badge="Code-as-Video Pipeline",
                description="Soyut kavramları minimalist SVG sembollerine eşleyen, milisaniyelik spring ve path-draw animasyonlu Remotion infografik.",
                engine="React + Remotion Engine + Motion Graphics Canvas",
                pros=["Kusursuz kavramsal anlatım", "Sıfır piksel bozulması (SVG)", "Ritimle senkronize dinamik hareket"]
            )
        ]

        rec_card = RecommendationCard(
            recommended_track=rec_track,
            confidence=confidence,
            analysis_summary=f"Metin {len(state.transcription.words)} kelime ve {state.transcription.duration:.1f} saniye olarak analiz edildi.",
            recommendation_reason=reason,
            semantic_features=features[:6],
            options=options,
            user_prompt_text=(
                f"İçerik analizi tamamlandı. Bu konsept için **{options[1].title if rec_track == TrackType.VECTOR_INFOGRAPHIC else options[0].title}** "
                f"stilini öneriyorum. Hangi formatta devam edelim?"
            )
        )

        state.recommendation_card = rec_card

        # 3. Pre-create Storyboard Beats (used by both tracks)
        beats: List[SceneBeat] = []
        if state.transcription.sentence_beats:
            for sb in state.transcription.sentence_beats:
                beats.append(
                    SceneBeat(
                        scene_id=sb.sentence_id,
                        start=sb.start,
                        end=sb.end,
                        duration=sb.duration,
                        spoken_text=sb.text,
                        concept=sb.text[:60],
                        mood="contemplative",
                        camera_movement="slow_push_in",
                        emphasis_keywords=sb.emphasis_words,
                        layout_type="cinematic_ambient"
                    )
                )
        else:
            total_d = state.transcription.duration
            dur_per = 10.0
            num_s = max(1, int(total_d // dur_per))
            for i in range(num_s):
                st = round(i * dur_per, 2)
                en = round(min(total_d, (i + 1) * dur_per), 2)
                beats.append(
                    SceneBeat(
                        scene_id=i + 1,
                        start=st,
                        end=en,
                        duration=round(en - st, 2),
                        spoken_text=f"Bölüm {i+1}",
                        concept=f"Konsept {i+1}",
                        mood="inspiring",
                        camera_movement="slow_push_in"
                    )
                )

        state.storyboard = StoryboardData(
            scenes=beats,
            total_scenes=len(beats),
            total_duration=state.transcription.duration,
            emotional_arc="enlightening"
        )

        # PAUSE AT CHECKPOINT
        state.agent_logs[self.agent_id].status = "awaiting_input"
        if on_progress:
            on_progress(self.agent_id, "awaiting_input", {
                "message": f"Stil analizi tamamlandı. Öneri: {rec_track.value.upper()}. Kullanıcı seçimi bekleniyor...",
                "recommendation": rec_card.dict()
            })

        return state

    def _validate_contract(self, state: ProjectState) -> None:
        if not state.recommendation_card:
            raise ValueError("StyleRecommenderAgent kontrat hatası: recommendation_card boş!")
        if not state.storyboard:
            raise ValueError("StyleRecommenderAgent kontrat hatası: storyboard oluşturulamadı!")
