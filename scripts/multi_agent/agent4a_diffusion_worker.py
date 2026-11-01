# -*- coding: utf-8 -*-
"""
Agent 4A: Sinematik Video Difüzyon Ajanı (Video Diffusion Worker)
Görevi:
  1. İki aşamalı üretim (Two-Tier Diffusion Pipeline):
     - Aşama 1: T2I Keyframe üretimi (Flux / AI Horde / Curated 8K Library)
     - Aşama 2: Image-to-Video (I2V) canlandırma (Kling 1.5 / Runway Gen-3 / Veo 2 / 35mm Ken Burns Kinematics)
  2. Video kliplerini yerel depoya (/assets/cinematic/scene_x.mp4) indirir ve doğrular.
"""
import os
import shutil
from typing import Optional, Callable, List
from .base_agent import BaseAgent
from .state import (
    ProjectState, PipelinePhase, SceneMediaAsset, MediaWorkerData
)
from scripts.animation_engine import create_cinematic_documentary_video


ASSETS_CINEMATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "cinematic")
PUBLIC_VIDEOS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "public", "videos")
os.makedirs(ASSETS_CINEMATIC_DIR, exist_ok=True)
os.makedirs(PUBLIC_VIDEOS_DIR, exist_ok=True)


class VideoDiffusionWorkerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id=4,
            name="Sinematik Video Difüzyon Ajanı (Ajan 4A)",
            required_phase=PipelinePhase.PHASE_3A_PROMPTS_COMPOSED,
            target_phase=PipelinePhase.PHASE_4A_DIFFUSION_RENDERED
        )

    def can_execute(self, state: ProjectState):
        if state.selected_track != "cinematic":
            return False, f"Seçilen dal '{state.selected_track}'. Ajan 4A yalnızca 'cinematic' dalında çalışabilir."
        return super().can_execute(state)

    def _process(
        self,
        state: ProjectState,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        prompts = state.art_direction.prompts
        scenes = state.storyboard.scenes
        assets: List[SceneMediaAsset] = []
        total_size = 0

        from scripts.key_pool import pool

        for idx, p in enumerate(prompts):
            sc = scenes[idx] if idx < len(scenes) else None
            dur = sc.duration if sc else 10.0

            if on_progress:
                on_progress(self.agent_id, "running", {
                    "message": f"Sahne {p.scene_id}/{len(prompts)} iki aşamalı (T2I -> I2V) difüzyon ile üretiliyor...",
                    "scene_index": idx + 1,
                    "total_scenes": len(prompts)
                })

            # Two-tier I2V synthesis
            res = create_cinematic_documentary_video(
                scene_text=p.visual_prompt,
                duration=dur,
                style=p.style,
                pool=pool,
                custom_prompt=p.visual_prompt,
                camera_movement=p.camera_movement
            )

            generated_abs = res.get("filePath") or os.path.join(PUBLIC_VIDEOS_DIR, os.path.basename(res.get("videoUrl", "")))
            if not generated_abs or not os.path.exists(generated_abs):
                raise FileNotFoundError(f"Difüzyon klibi oluşturulamadı: Sahne {p.scene_id}")

            # Persist to /assets/cinematic/scene_{x}.mp4
            dest_name = f"scene_{p.scene_id}.mp4"
            asset_path = os.path.join(ASSETS_CINEMATIC_DIR, dest_name)
            shutil.copyfile(generated_abs, asset_path)

            file_size = os.path.getsize(asset_path)
            total_size += file_size

            asset = SceneMediaAsset(
                scene_id=p.scene_id,
                video_file=asset_path,
                video_url=res.get("videoUrl", f"/public/videos/{os.path.basename(generated_abs)}"),
                thumbnail_file=res.get("keyframeUrl"),
                duration=dur,
                width=720,
                height=1280,
                verified=True,
                file_size_bytes=file_size
            )
            assets.append(asset)

        state.media_assets = MediaWorkerData(
            assets=assets,
            all_verified=True,
            total_size_bytes=total_size
        )

        return state

    def _validate_contract(self, state: ProjectState) -> None:
        if not state.media_assets or not state.media_assets.assets:
            raise ValueError("VideoDiffusionWorkerAgent kontrat hatası: assets listesi boş!")
        for a in state.media_assets.assets:
            if not a.verified or not os.path.exists(a.video_file):
                raise ValueError(f"Video dosyası doğrulanamadı: {a.video_file}")
