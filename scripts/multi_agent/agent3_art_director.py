# -*- coding: utf-8 -*-
"""
Agent 3: Görsel Sanat Yönetmeni Ajanı (Art Director & Prompt Engineer)
Görevi: Sahne konseptlerini video üretim modellerinin (Runway, Kling, Flux, Gemini Omni)
en iyi anlayacağı İngilizce sinematik prompt'lara çevirmek ve görsel devamlılığı sağlamak.
Girdi: 2. Ajan'dan gelen StoryboardData ve seçilen görsel tarz.
Çıktı: Sahne bazlı İngilizce video üretim promptları (ArtDirectionData).
"""
import json
from typing import Optional, Callable, List
from .base_agent import BaseAgent
from .state import ProjectState, PipelinePhase, ArtDirectionData, ScenePrompt


class ArtDirectorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id=3,
            name="Görsel Sanat Yönetmeni Ajanı",
            required_phase=PipelinePhase.PHASE_2_STORYBOARDED,
            target_phase=PipelinePhase.PHASE_3_ART_DIRECTED
        )

    def _process(
        self,
        state: ProjectState,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        storyboard = state.storyboard
        style = state.visual_style or "2d_anime"
        aspect_ratio = state.aspect_ratio or "9:16"

        if on_progress:
            on_progress(self.agent_id, "running", {
                "message": f"Sanat yönetimi başlatıldı: '{style}' estetiğinde {len(storyboard.scenes)} sahne için promptlar hazırlanıyor..."
            })

        prompts = self._craft_prompts(storyboard.scenes, style, aspect_ratio)

        state.art_direction = ArtDirectionData(
            prompts=prompts,
            global_style=style,
            color_palette="divine gold, emerald robes, natural misty earth tones"
        )

        return state

    def _craft_prompts(
        self,
        scenes: list,
        style: str,
        aspect_ratio: str
    ) -> List[ScenePrompt]:
        from scripts.key_pool import pool

        style_descriptions = {
            "2d_anime": "Studio Ghibli 2D anime aesthetic, hand-drawn anime background, vibrant natural colors, soft volumetric lighting, Makoto Shinkai sky",
            "2d_dervish_miniature": "Traditional Ottoman Persian Islamic miniature art style, intricate gold foil leaf tezhib motifs, mystical spiritual depth",
            "cinematic_photoreal": "Hyper-realistic cinematic 8k, RED Komodo 6K shot, photorealistic volumetric sunbeams, shallow depth of field, anamorphic bokeh",
            "2d_watercolor": "Artistic lyrical watercolor painting, flowing ink splashes, pastel tones, divine light wash"
        }
        style_prompt_core = style_descriptions.get(style, style_descriptions["2d_anime"])

        prompts_result = []

        system_instruction = (
            "You are a World-Class Art Director & Cinematic AI Prompt Engineer. "
            "Convert each scene beat into a hyper-detailed English video generation prompt. "
            "CRITICAL: Maintain absolute character and environmental continuity between sequential scenes. "
            "Scene 2 must visually pick up from Scene 1's closing frame. Scene 3 continues to the climactic wisdom/ayah frame. "
            "OUTPUT STRICT VALID JSON ONLY."
        )

        user_input_scenes = [
            {
                "scene_id": s.scene_id,
                "duration": s.duration,
                "concept": s.concept,
                "spoken_text": s.spoken_text,
                "camera": s.camera_movement
            }
            for s in scenes
        ]

        query = f"""
Visual Style Core: {style_prompt_core}
Aspect Ratio: {aspect_ratio}

Scenes to engineer:
{json.dumps(user_input_scenes, ensure_ascii=False, indent=2)}

Please return this JSON format:
{{
  "prompts": [
    {{
      "scene_id": 1,
      "visual_prompt": "Ultra-detailed English prompt describing characters, lighting, environment, camera angle...",
      "negative_prompt": "blurry, low quality, distorted, watermark, deformed limbs, text",
      "camera_movement": "slow zoom in"
    }}
  ]
}}
"""
        try:
            raw_res, _ = pool.query_with_rotation(query, system_instruction=system_instruction, model="gemini-2.5-flash")
            cleaned = raw_res.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            parsed = json.loads(cleaned)
            ai_prompts = parsed.get("prompts", [])

            if ai_prompts and len(ai_prompts) >= len(scenes):
                for idx, ap in enumerate(ai_prompts):
                    s_id = idx + 1
                    cont_note = "Establishing opening scene" if idx == 0 else f"Continuity from scene {idx}"
                    prompts_result.append(
                        ScenePrompt(
                            scene_id=s_id,
                            visual_prompt=f"{ap.get('visual_prompt', '')}, {style_prompt_core}, {aspect_ratio}",
                            negative_prompt=ap.get("negative_prompt", "blurry, distorted, low quality, watermark, text"),
                            aspect_ratio=aspect_ratio,
                            camera_movement=ap.get("camera_movement", scenes[idx].camera_movement),
                            style=style,
                            continuity_notes=cont_note
                        )
                    )
                return prompts_result
        except Exception as e:
            print(f"[Art Director Agent] Gemini prompt engineering fallback: {e}")

        # High-End Heuristic Fallback
        for idx, s in enumerate(scenes):
            s_id = s.scene_id
            if idx == 0:
                p_text = (
                    f"A humble Sufi dervish with green robe and wooden staff walking along a winding mountain path "
                    f"on a bright sunny day, majestic mountain vistas, streaming golden sunbeams, gentle mountain breeze. "
                    f"Establishing wide shot, {style_prompt_core}, aspect ratio {aspect_ratio}"
                )
                cont = "Establishing opening scene"
            elif idx == len(scenes) - 1:
                p_text = (
                    f"Ancient illuminated golden manuscript open on a rustic wooden stand in a tranquil sacred library, "
                    f"soft celestial light illuminating gold-leaf calligraphy and intricate tezhib floral borders, particles of light floating. "
                    f"Slow cinematic push, {style_prompt_core}, aspect ratio {aspect_ratio}"
                )
                cont = f"Seamless continuation from scene {idx} ending into sacred revelation"
            else:
                p_text = (
                    f"The same Sufi dervish continuing his contemplative journey on a stone bridge overlooking a cascading mountain stream, "
                    f"same emerald robe, serene expression, warm atmospheric sunset lighting, continuous sequential shot from previous scene {idx}. "
                    f"Slow pan camera movement, {style_prompt_core}, aspect ratio {aspect_ratio}"
                )
                cont = f"Continuous sequential motion matching character and colors from scene {idx}"

            prompts_result.append(
                ScenePrompt(
                    scene_id=s_id,
                    visual_prompt=p_text,
                    negative_prompt="blurry, distorted, low quality, watermark, extra fingers, text overlay",
                    aspect_ratio=aspect_ratio,
                    camera_movement=s.camera_movement,
                    style=style,
                    continuity_notes=cont
                )
            )

        return prompts_result

    def _validate_contract(self, state: ProjectState) -> None:
        if not state.art_direction:
            raise ValueError("3. Ajan Kontrat Hatası: 'art_direction' verisi oluşturulmadı!")
        if not state.art_direction.prompts or len(state.art_direction.prompts) == 0:
            raise ValueError("3. Ajan Kontrat Hatası: Sahne promptları boş olamaz!")
        for p in state.art_direction.prompts:
            if not p.visual_prompt or len(p.visual_prompt) < 15:
                raise ValueError(f"3. Ajan Kontrat Hatası: Sahne {p.scene_id} promptu yetersiz veya boş!")
