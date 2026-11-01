# -*- coding: utf-8 -*-
"""
Agent 0: Orkestratör Ajan (Master Orchestrator / Yapımcı)
Görevi: Tüm boru hattının (pipeline) durumunu yönetir.
Her ajanın bir önceki ajan görevini eksiksiz tamamlamadan sonraki ajanın çalışamayacağı
katı durum kuralını (State Gatekeeper) uygular.
"""
import os
import time
import json
import uuid
from typing import Optional, Callable, Dict, Any, List

from .state import ProjectState, PipelinePhase, AgentStatus, AgentStepLog
from .base_agent import StateTransitionError
from .agent1_transcriber import TranscribeAlignAgent
from .agent2_storyboarder import StoryboardDirectorAgent
from .agent3_art_director import ArtDirectorAgent
from .agent4_media_worker import MediaWorkerAgent
from .agent5_typography import TypographyAgent
from .agent6_audio_designer import AudioDesignAgent
from .agent7_assembler import AssemblyAgent


JOBS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "multi_agent")
os.makedirs(JOBS_DIR, exist_ok=True)


class MasterOrchestrator:
    def __init__(self):
        # Register the 7 specialized agents strictly in sequential order
        self.agents = [
            TranscribeAlignAgent(),       # 1: Speech & Timing
            StoryboardDirectorAgent(),    # 2: Storyboard & Scenes
            ArtDirectorAgent(),           # 3: Art & Prompts
            MediaWorkerAgent(),           # 4: Video Generation & Asset Dispatch
            TypographyAgent(),            # 5: Motion Subtitles (.ass)
            AudioDesignAgent(),           # 6: Audio Ducking & SFX
            AssemblyAgent()               # 7: FFmpeg Final Concat & Render
        ]
        self._active_jobs: Dict[str, ProjectState] = {}

    def get_job_state(self, job_id: str) -> Optional[ProjectState]:
        if job_id in self._active_jobs:
            return self._active_jobs[job_id]
        job_file = os.path.join(JOBS_DIR, f"job_{job_id}.json")
        if os.path.exists(job_file):
            try:
                with open(job_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return ProjectState(**data)
            except Exception:
                pass
        return None

    def execute_pipeline(
        self,
        audio_file: str,
        project_id: Optional[str] = None,
        aspect_ratio: str = "9:16",
        visual_style: str = "2d_anime",
        custom_transcript: Optional[str] = None,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        """
        Executes the entire 7-agent pipeline sequentially with ironclad state checks.
        NO AGENT CAN RUN UNLESS THE PREVIOUS AGENT HAS REACHED SUCCESS!
        """
        job_id = project_id or str(uuid.uuid4())[:8]

        # Initialize Master Project State at PHASE_0_IDLE
        state = ProjectState(
            project_id=job_id,
            audio_file=audio_file,
            aspect_ratio=aspect_ratio,
            visual_style=visual_style,
            custom_transcript=custom_transcript,
            current_phase=PipelinePhase.PHASE_0_IDLE
        )
        self._active_jobs[job_id] = state
        self._persist_state(state)

        print(f"\n=======================================================")
        print(f"[Orkestratör Ajan] Video Üretim Boru Hattı Başlatıldı! (İş ID: {job_id})")
        print(f"Toplam Ajan Sayısı: {len(self.agents)} Uzman Ajan")
        print(f"Girdi Sesi: {audio_file}")
        print(f"Görsel Tarz: {visual_style} | En Boy Oranı: {aspect_ratio}")
        print(f"=======================================================\n")

        def handle_progress(aid, status, payload):
            self._persist_state(state)
            if on_progress:
                try:
                    on_progress(aid, status, payload)
                except Exception:
                    pass

        for agent in self.agents:
            print(f"[Orkestratör] Sıradaki Ajan Denetleniyor: [{agent.agent_id}. {agent.name}]")

            # 1. STRICT GATEKEEPER CHECK:
            # Verify that the state is precisely at this agent's required prerequisite phase
            can_run, reason = agent.can_execute(state)
            if not can_run:
                error_msg = f"[Kritik Hata] {reason}"
                print(error_msg)
                state.errors.append(error_msg)
                self._persist_state(state)
                raise StateTransitionError(error_msg)

            print(f"[Orkestratör] Ön Koşul Doğrulandı: Mevcut Aşama='{state.current_phase.value}'. Ajan başlatılıyor...")

            # 2. RUN AGENT WITH RETRY POLICY (Up to 2 attempts on transient network issues)
            max_retries = 2
            attempt = 0
            agent_success = False

            while attempt < max_retries and not agent_success:
                attempt += 1
                try:
                    state = agent.run(state, handle_progress)
                    agent_success = True
                    print(f"[Orkestratör] [{agent.agent_id}. {agent.name}] Başarıyla Tamamlandı -> Yeni Aşama: '{state.current_phase.value}'\n")
                    self._persist_state(state)
                except Exception as e:
                    print(f"[Orkestratör] [{agent.agent_id}. {agent.name}] Deneme {attempt}/{max_retries} Hatası: {e}")
                    if attempt >= max_retries:
                        self._persist_state(state)
                        raise RuntimeError(f"Ajan {agent.agent_id} ({agent.name}) {max_retries} denemeden sonra başarısız oldu: {e}")
                    time.sleep(1.5)

        print(f"\n=======================================================")
        print(f"[Orkestrator Ajan] TUM 7 AJAN GOREVINI KUSURSUZ TAMAMLADI!")
        print(f"Final Video: {state.assembly.final_video_file}")
        print(f"Sure: {state.assembly.duration:.1f}s | Dosya Boyutu: {state.assembly.file_size_bytes} bytes")
        print(f"=======================================================\n")

        self._persist_state(state)
        return state

    def _persist_state(self, state: ProjectState) -> None:
        """Saves JSON snapshot of the project state after every agent transition."""
        state.updated_at = time.strftime("%Y-%m-%d %H:%M:%S")
        job_file = os.path.join(JOBS_DIR, f"job_{state.project_id}.json")
        try:
            with open(job_file, "w", encoding="utf-8") as f:
                json_data = json.dumps(state.dict(), ensure_ascii=False, indent=2)
                f.write(json_data)
        except Exception as e:
            print(f"[Orkestratör] Durum kaydetme uyarısı: {e}")
