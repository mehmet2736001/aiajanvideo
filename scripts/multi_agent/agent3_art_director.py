# -*- coding: utf-8 -*-
"""
Agent 3: Görsel Sanat Yönetmeni Ajanı (Art Director & Cinematic Prompt Engineer)
Görevi: Sahne konseptlerini video difüzyon modellerinin (Google Veo 2, Kling 1.5, Runway Gen-3, Flux.1)
en iyi anlayacağı sinematik, fotogerçekçi teknik İngilizce kamera ve ışık promptlarına dönüştürmek.
Girdi: 2. Ajan'dan gelen StoryboardData ve seçilen sinematik görsel tarz.
Çıktı: Sahne bazlı İngilizce sinematik video üretim promptları (ArtDirectionData).
"""
import json
from typing import Optional, Callable, List
from .base_agent import BaseAgent
from .state import ProjectState, PipelinePhase, ArtDirectionData, ScenePrompt
from scripts.animation_engine import CINEMATIC_STYLES, NEGATIVE_PROMPT_CINEMATIC, normalize_style_key


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
        raw_style = state.visual_style or "cinematic_photoreal"
        clean_style = normalize_style_key(raw_style)
        aspect_ratio = state.aspect_ratio or "9:16"

        if on_progress:
            on_progress(self.agent_id, "running", {
                "message": f"Sinematik sanat yönetimi devrede: '{clean_style}' fotogerçekçi formatında {len(storyboard.scenes)} sahne promptu hazırlanıyor..."
            })

        prompts = self._craft_prompts(storyboard.scenes, clean_style, aspect_ratio)

        state.art_direction = ArtDirectionData(
            prompts=prompts,
            global_style=clean_style,
            color_palette="cinematic 35mm tones, warm volumetric golden light, deep organic contrast"
        )

        return state

    def _craft_prompts(
        self,
        scenes: list,
        style: str,
        aspect_ratio: str
    ) -> List[ScenePrompt]:
        from scripts.key_pool import pool

        clean_style = normalize_style_key(style)
        style_prompt_core = CINEMATIC_STYLES[clean_style]

        prompts_result = []

        system_instruction = (
            "You are a World-Class National Geographic & BBC Earth Cinematographer and AI Prompt Director "
            "for high-end Video Diffusion Engines (Google Veo 2, Kling 1.5, Runway Gen-3, Flux.1). "
            "Convert each scene beat into a hyper-detailed, photorealistic English video generation prompt for documentary B-roll. "
            "Include technical camera specs: 35mm anamorphic or macro lens, f/1.4 aperture, cinematic lighting, "
            "volumetric god rays, shallow depth of field, natural motion blur, authentic film grain, and subtle camera movement. "
            "CRITICAL: Maintain absolute character, tone, and environmental continuity between sequential scenes. "
            "Scene 2 must visually pick up from Scene 1's closing frame. "
            "CRITICAL: NEVER use cartoon, anime, 3d render, illustration, drawing, flat vector, or painting terms. "
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

Scenes to engineer for 35mm photorealistic documentary video:
{json.dumps(user_input_scenes, ensure_ascii=False, indent=2)}

Please return this JSON format:
{{
  "prompts": [
    {{
      "scene_id": 1,
      "visual_prompt": "Ultra-detailed photorealistic English prompt describing subject, ARRI Alexa 65 camera, 35mm lens, volumetric lighting, authentic textures...",
      "negative_prompt": "cartoon, anime, 3d render, illustration, drawing, flat vector, blurry, distorted, watermark, text",
      "camera_movement": "slow cinematic push in"
    }}
  ]
}}
"""
        try:
            raw_res, _ = pool.query_with_rotation(query, system_instruction=system_instruction, model="gemini-3.5-flash-lite")
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
                    cont_note = "Establishing opening scene" if idx == 0 else f"Photoreal continuity from scene {idx}"
                    prompts_result.append(
                        ScenePrompt(
                            scene_id=s_id,
                            visual_prompt=f"{ap.get('visual_prompt', '')}, {style_prompt_core}, {aspect_ratio}",
                            negative_prompt=NEGATIVE_PROMPT_CINEMATIC,
                            aspect_ratio=aspect_ratio,
                            camera_movement=ap.get("camera_movement", scenes[idx].camera_movement),
                            style=clean_style,
                            continuity_notes=cont_note
                        )
                    )
                return prompts_result
        except Exception as e:
            print(f"[Art Director Agent] Gemini prompt engineering fallback: {e}")

        # High-End Heuristic Fallback matching the selected cinematic documentary style
        for idx, s in enumerate(scenes):
            s_id = s.scene_id
            if clean_style == "historical_documentary":
                if idx == 0:
                    p_text = (
                        f"Macro cinematic 35mm documentary shot of ancient illuminated parchment manuscripts, "
                        f"antique quill pen on a dark aged wooden lectern, divine golden light rays streaming from high windows, "
                        f"dust motes floating in chiaroscuro lighting, shallow depth of field, photorealistic 8k, aspect ratio {aspect_ratio}"
                    )
                elif idx == len(scenes) - 1:
                    p_text = (
                        f"Extreme close-up macro shot of gold-leaf calligraphy and intricate tezhib floral borders on aged parchment, "
                        f"warm celestial illumination, particles of light floating, sacred reverent atmosphere, "
                        f"photorealistic 8k, aspect ratio {aspect_ratio}"
                    )
                else:
                    p_text = (
                        f"Continuous sequential macro shot of ancient leather-bound manuscripts stacked in a tranquil sacred library, "
                        f"same warm golden illumination, slow cinematic pan, shallow depth of field, "
                        f"photorealistic 8k, aspect ratio {aspect_ratio}"
                    )
            elif clean_style == "macro_biometrics":
                if idx == 0:
                    p_text = (
                        f"Ultra-macro 8k scientific documentary footage of human biometric fingerprint ridges, "
                        f"delicate skin texture, organic micro-details, shallow depth of field, cinematic lighting, aspect ratio {aspect_ratio}"
                    )
                elif idx == len(scenes) - 1:
                    p_text = (
                        f"Extreme macro close-up of human iris with intricate crystalline patterns and glowing depth, "
                        f"biological wonder, shallow depth of field, 8k photorealistic, aspect ratio {aspect_ratio}"
                    )
                else:
                    p_text = (
                        f"Pulsing microscopic cellular structures and glowing neural synapses, "
                        f"complex biological symmetry, scientific documentary b-roll, 8k photorealistic, aspect ratio {aspect_ratio}"
                    )
            elif clean_style == "dramatic_tefekkur":
                if idx == 0:
                    p_text = (
                        f"Moody dramatic documentary shot of a contemplative solitary silhouette on a dark mountain ridge, "
                        f"gazing into majestic deep space cosmos with drifting stardust, volumetric rays, 8k, aspect ratio {aspect_ratio}"
                    )
                elif idx == len(scenes) - 1:
                    p_text = (
                        f"Luminous celestial nebulae and glowing stardust floating in infinite dark space, "
                        f"spiritual reverence, awe-inspiring cosmological documentary shot, 35mm film grain, 8k, aspect ratio {aspect_ratio}"
                    )
                else:
                    p_text = (
                        f"Atmospheric volumetric god rays piercing through dramatic misty clouds at dusk, "
                        f"epic natural horizon, contemplative spiritual depth, cinematic 35mm, aspect ratio {aspect_ratio}"
                    )
            else: # Default cinematic_photoreal
                if idx == 0:
                    p_text = (
                        f"Cinematic photorealistic 35mm shot of a humble traveler with earth-tone cloak walking along a misty mountain path, "
                        f"volumetric morning sunbeams filtering through ancient trees, shallow depth of field, ARRI Alexa 65, 8k, aspect ratio {aspect_ratio}"
                    )
                elif idx == len(scenes) - 1:
                    p_text = (
                        f"Macro cinematic shot of an ancient open book with sacred verse, warm golden illumination falling on aged paper, "
                        f"floating dust particles, peaceful contemplation, photorealistic 8k, aspect ratio {aspect_ratio}"
                    )
                else:
                    p_text = (
                        f"Continuous sequential shot of the traveler pausing by a cascading mountain stream, "
                        f"natural cinematic lighting, atmospheric mist, shallow depth of field, 8k, aspect ratio {aspect_ratio}"
                    )

            cont = "Establishing opening scene" if idx == 0 else f"Seamless sequential continuity from scene {idx}"
            prompts_result.append(
                ScenePrompt(
                    scene_id=s_id,
                    visual_prompt=p_text,
                    negative_prompt=NEGATIVE_PROMPT_CINEMATIC,
                    aspect_ratio=aspect_ratio,
                    camera_movement=s.camera_movement,
                    style=clean_style,
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
