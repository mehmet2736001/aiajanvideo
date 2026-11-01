# -*- coding: utf-8 -*-
"""
Agent 2: Senaryo & Sahne Yönetmeni Ajanı (Storyboarder / Director)
Görevi: Metnin anlamsal derinliğini, vurgu noktalarını ve ritmini analiz ederek
konuşmayı 2 ila 8 saniyelik görsel sahnelere (beat'lere) bölmek.
Girdi: 1. Ajan'dan gelen TranscriptionData.
Çıktı: Sahne listesi JSON'ı (SceneBeat listesi).
"""
import json
import math
from typing import Optional, Callable, List
from .base_agent import BaseAgent
from .state import ProjectState, PipelinePhase, StoryboardData, SceneBeat


class StoryboardDirectorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id=2,
            name="Senaryo & Sahne Yönetmeni Ajanı",
            required_phase=PipelinePhase.PHASE_1_TRANSCRIBED,
            target_phase=PipelinePhase.PHASE_2_STORYBOARDED
        )

    def _process(
        self,
        state: ProjectState,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        transcription = state.transcription
        total_duration = transcription.duration
        clean_text = transcription.clean_text
        words = transcription.words

        if on_progress:
            on_progress(self.agent_id, "running", {
                "message": f"Konuşma ritmi ve anlamsal vuruşlar (beats) analiz ediliyor ({total_duration:.1f}s)..."
            })

        # Calculate target number of scenes:
        # Ideal scene duration is 5-10 seconds per scene
        if total_duration <= 14.0:
            target_scene_count = max(1, math.ceil(total_duration / 6.0))
        elif total_duration <= 35.0:
            target_scene_count = 3  # Standard 3-act structure (0-10, 10-20, 20-30s)
        else:
            target_scene_count = max(3, math.ceil(total_duration / 10.0))

        # Try AI Director with Gemini
        scenes = self._generate_ai_storyboard(clean_text, total_duration, target_scene_count, words)

        state.storyboard = StoryboardData(
            scenes=scenes,
            total_scenes=len(scenes),
            total_duration=total_duration,
            emotional_arc="inspiring"
        )

        return state

    def _generate_ai_storyboard(
        self,
        text: str,
        total_duration: float,
        target_scene_count: int,
        words: list
    ) -> List[SceneBeat]:
        from scripts.key_pool import pool

        system_instruction = (
            "Sen uzman bir Sinematik Sahne ve Senaryo Yönetmenisin. "
            "Verilen konuşma metnini ve toplam video süresini analiz et. "
            f"Metni tam olarak {target_scene_count} adet ardışık sahneye (beat'e) böl. "
            "Her sahnenin başlangıç ve bitiş zamanı ardışık ve kesintisiz olmalıdır (0'dan başlayıp toplam süreye kadar). "
            "Son sahne hikmetli söz / ayet veya vurucu mesaj sahnesi olmalıdır. "
            "ÇIKTIYI SADECE GEÇERLİ JSON OLARAK VER."
        )

        prompt = f"""
Konuşma Metni:
"{text[:1200]}"

Toplam Süre: {total_duration:.1f} saniye
Hedef Sahne Sayısı: {target_scene_count}

Lütfen şu JSON formatında yanıt ver:
{{
  "scenes": [
    {{
      "scene_id": 1,
      "start": 0.0,
      "end": {min(10.0, total_duration / target_scene_count):.1f},
      "spoken_text": "İlk kısımda söylenen sözler...",
      "concept": "1. sahne görsel konsepti (ör. Dağ patikasında asasıyla yürüyen derviş)",
      "mood": "mistik, derin tefekkür",
      "camera_movement": "slow_zoom_in",
      "emphasis_keywords": ["ilmi", "hikmet"]
    }}
  ]
}}
"""
        try:
            raw_res, _ = pool.query_with_rotation(prompt, system_instruction=system_instruction, model="gemini-2.5-flash")
            cleaned = raw_res.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            parsed = json.loads(cleaned)
            ai_scenes = parsed.get("scenes", [])
            if ai_scenes and len(ai_scenes) >= 1:
                result_scenes = []
                cur_time = 0.0
                slice_dur = total_duration / len(ai_scenes)
                for idx, sc in enumerate(ai_scenes):
                    s_id = idx + 1
                    st = round(cur_time, 2)
                    cur_time += slice_dur
                    en = round(min(total_duration, cur_time) if idx < len(ai_scenes) - 1 else total_duration, 2)
                    dur = round(en - st, 2)

                    # Extract spoken text from word timestamps if possible
                    words_in_window = [w.word for w in words if (w.start >= st - 0.4 and w.end <= en + 0.4)]
                    scene_spoken = " ".join(words_in_window) or sc.get("spoken_text") or f"Sahne {s_id}"

                    layout = "quote_spotlight" if idx == len(ai_scenes) - 1 else "cinematic_ambient"
                    result_scenes.append(
                        SceneBeat(
                            scene_id=s_id,
                            start=st,
                            end=en,
                            duration=dur,
                            spoken_text=scene_spoken,
                            concept=sc.get("concept") or f"Sahne {s_id} görsel konsepti",
                            mood=sc.get("mood") or "derin",
                            camera_movement=sc.get("camera_movement") or "slow_zoom_in",
                            emphasis_keywords=sc.get("emphasis_keywords") or [],
                            layout_type=layout
                        )
                    )
                return result_scenes
        except Exception as e:
            print(f"[Storyboard Agent] Gemini fallback triggered: {e}")

        # Heuristic fallback if AI call fails
        slice_dur = total_duration / target_scene_count
        fallback_scenes = []
        cur = 0.0
        words_all = text.split()
        words_per_slice = max(1, len(words_all) // target_scene_count)

        for i in range(target_scene_count):
            st = round(cur, 2)
            cur += slice_dur
            en = round(min(total_duration, cur) if i < target_scene_count - 1 else total_duration, 2)
            dur = round(en - st, 2)

            sub_words = words_all[i * words_per_slice: (i + 1) * words_per_slice]
            scene_text = " ".join(sub_words) or f"Sahne {i+1}"

            if i == 0:
                concept = "Mistik gün doğumu, dağ patikasında asasıyla yürüyen derviş, altın ışık huzmeleri"
                mood = "tefekkür ve huşu"
                cam = "slow_zoom_in"
            elif i == target_scene_count - 1:
                concept = "Aydınlanan kadim el yazması defter ve altın varaklı ayet çerçevesi"
                mood = "derin hakikat"
                cam = "cinematic_push"
            else:
                concept = "Doğanın dinginliği, rüzgarda dalgalanan cübbe, asırlık kütüphane ve kitaplar"
                mood = "manevi yükseliş"
                cam = "slow_pan_right"

            layout = "quote_spotlight" if i == target_scene_count - 1 else "cinematic_ambient"
            fallback_scenes.append(
                SceneBeat(
                    scene_id=i + 1,
                    start=st,
                    end=en,
                    duration=dur,
                    spoken_text=scene_text,
                    concept=concept,
                    mood=mood,
                    camera_movement=cam,
                    emphasis_keywords=[w for w in sub_words[:2] if len(w) > 3],
                    layout_type=layout
                )
            )

        return fallback_scenes

    def _validate_contract(self, state: ProjectState) -> None:
        if not state.storyboard:
            raise ValueError("2. Ajan Kontrat Hatası: 'storyboard' verisi oluşturulmadı!")
        if not state.storyboard.scenes or len(state.storyboard.scenes) == 0:
            raise ValueError("2. Ajan Kontrat Hatası: Sahne listesi boş olamaz!")
        # Validate sequential non-overlapping timestamps
        for i, sc in enumerate(state.storyboard.scenes):
            if sc.end <= sc.start:
                raise ValueError(f"2. Ajan Kontrat Hatası: Sahne {sc.scene_id} başlangıç zamanı bitişten büyük/eşit ({sc.start} >= {sc.end})!")
            if i > 0:
                prev = state.storyboard.scenes[i - 1]
                if abs(sc.start - prev.end) > 0.5:
                    print(f"[Storyboard Warning] Sahne {sc.scene_id} ile {prev.scene_id} arasında boşluk/örtüşme var.")
