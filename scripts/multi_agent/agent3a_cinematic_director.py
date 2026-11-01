# -*- coding: utf-8 -*-
"""
Agent 3A: Sinematik Sanat Yönetmeni & Prompt Mühendisi (Art Director & Prompt Engineer)
Görevi:
  1. Sahne metinlerini 3-5 saniyelik görsel beat'lere böler veya optimize eder.
  2. Her sahne için fotogerçekçi, 35mm film estetiğinde İngilizce video promptları yazar.
     (Örn: 'Cinematic macro shot, 35mm anamorphic lens, 8k, shallow depth of field, volumetric light, --ar 9:16')
"""
from typing import Optional, Callable, List
from .base_agent import BaseAgent
from .state import (
    ProjectState, PipelinePhase, ScenePrompt, ArtDirectionData
)
from scripts.animation_engine import craft_cinematic_documentary_prompt


class CinematicArtDirectorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id=3,
            name="Sinematik Sanat Yönetmeni & Prompt Mühendisi (Ajan 3A)",
            required_phase=PipelinePhase.PHASE_2_BRANCH_SELECTED,
            target_phase=PipelinePhase.PHASE_3A_PROMPTS_COMPOSED
        )

    def can_execute(self, state: ProjectState):
        if state.selected_track != "cinematic":
            return False, f"Seçilen dal '{state.selected_track}'. Ajan 3A (Sinematik) yalnızca 'cinematic' dalında çalışabilir."
        return super().can_execute(state)

    def _process(
        self,
        state: ProjectState,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        if on_progress:
            on_progress(self.agent_id, "running", {
                "message": "35mm fotogerçekçi kamera ve ışık promptları yapılandırılıyor..."
            })

        from scripts.key_pool import pool
        scenes = state.storyboard.scenes
        prompts: List[ScenePrompt] = []

        for idx, sc in enumerate(scenes):
            cam = "slow_push_in" if idx % 2 == 0 else "slow_pan_dolly"
            # Craft detailed 35mm prompt
            english_prompt = craft_cinematic_documentary_prompt(
                scene_text=sc.spoken_text or sc.concept,
                style="cinematic_photoreal",
                pool=pool
            )

            continuity = (
                f"Sahne {idx} son karesinden kesintisiz 35mm kamera hareketiyle devam eder."
                if idx > 0 else "Açılış anahtar karesi."
            )

            prompts.append(
                ScenePrompt(
                    scene_id=sc.scene_id,
                    visual_prompt=english_prompt,
                    negative_prompt=(
                        "cartoon, anime, 3d render, illustration, drawing, flat vector, "
                        "blurry, distorted, watermark, signature, low quality, oversaturated"
                    ),
                    aspect_ratio=state.aspect_ratio,
                    camera_movement=cam,
                    style="cinematic_photoreal",
                    continuity_notes=continuity
                )
            )

        state.art_direction = ArtDirectionData(
            prompts=prompts,
            global_style="cinematic_photoreal",
            color_palette="ARRI Alexa 65, 35mm natural tones, volumetric golden god rays, organic film grain"
        )

        return state

    def _validate_contract(self, state: ProjectState) -> None:
        if not state.art_direction or not state.art_direction.prompts:
            raise ValueError("CinematicArtDirectorAgent kontrat hatası: prompts listesi boş!")
