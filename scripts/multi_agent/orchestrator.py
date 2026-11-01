# -*- coding: utf-8 -*-
"""
Agent 0: Orkestratör Ajan (Master Orchestrator / Producer)
Çift Hatlı (Dual-Track) Otonom Video Üretim Mimarisi:
  - Faz 1: Transcribe & Style Recommendation (Giriş & Çözümleme)
  - Interactive Checkpoint: AWAIT_USER_SELECTION (Kullanıcı Onay Döngüsü)
  - Faz 2: Branşlaşma (Branching Pipeline)
      * Dal A: Sinematik Belgesel Motoru (Ajan 3A + Ajan 4A)
      * Dal B: 2D Vektörel İnfografik Motoru (Ajan 3B + Ajan 4B)
  - Faz 3: Ortak Tamamlama & Post-Production (Ajan 5 + Ajan 6 + Ajan 7)
"""
import os
import time
import json
import uuid
from typing import Optional, Callable, Dict, Any, List

from .state import (
    ProjectState, PipelinePhase, AgentStatus, AgentStepLog, TrackType
)
from .base_agent import BaseAgent, StateTransitionError
from .agent1_transcriber import TranscribeAlignAgent
from .agent2_style_recommender import StyleRecommenderAgent
from .agent3a_cinematic_director import CinematicArtDirectorAgent
from .agent4a_diffusion_worker import VideoDiffusionWorkerAgent
from .agent3b_vector_director import VectorMetaphorDirectorAgent
from .agent4b_remotion_worker import RemotionMotionGraphicsAgent
from .agent5_typography import TypographyAgent
from .agent6_audio_designer import AudioDesignAgent
from .agent7_assembler import AssemblyAgent


JOBS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "multi_agent")
os.makedirs(JOBS_DIR, exist_ok=True)


class MasterOrchestrator:
    def __init__(self):
        # Instantiate all specialized agents across both tracks
        self.agent1_transcribe = TranscribeAlignAgent()
        self.agent2_recommender = StyleRecommenderAgent()

        # Branch A: Cinematic
        self.agent3a_cinematic_art = CinematicArtDirectorAgent()
        self.agent4a_diffusion_worker = VideoDiffusionWorkerAgent()

        # Branch B: Vector Infographic
        self.agent3b_vector_director = VectorMetaphorDirectorAgent()
        self.agent4b_remotion_worker = RemotionMotionGraphicsAgent()

        # Shared Post-Production
        self.agent5_typography = TypographyAgent()
        self.agent6_audio = AudioDesignAgent()
        self.agent7_assembly = AssemblyAgent()

        self._active_jobs: Dict[str, ProjectState] = {}

    def get_job_state(self, job_id: str) -> Optional[ProjectState]:
        if job_id in self._active_jobs:
            return self._active_jobs[job_id]
        job_file = os.path.join(JOBS_DIR, f"job_{job_id}.json")
        if os.path.exists(job_file):
            try:
                with open(job_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    state = ProjectState(**data)
                    self._active_jobs[job_id] = state
                    return state
            except Exception as e:
                print(f"[Orchestrator] State loading error: {e}")
        return None

    def _persist_state(self, state: ProjectState) -> None:
        state.updated_at = time.strftime("%Y-%m-%d %H:%M:%S")
        job_file = os.path.join(JOBS_DIR, f"job_{state.project_id}.json")
        try:
            with open(job_file, "w", encoding="utf-8") as f:
                json_data = json.dumps(state.dict(), ensure_ascii=False, indent=2)
                f.write(json_data)
        except Exception as e:
            print(f"[Orchestrator] State persistence notice: {e}")

    def _run_agent_safely(
        self,
        agent: BaseAgent,
        state: ProjectState,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        """Executes an agent with state verification and retry handling."""
        can_run, reason = agent.can_execute(state)
        if not can_run:
            msg = f"[Kritik Kapı Hatası] {reason}"
            print(msg)
            state.errors.append(msg)
            self._persist_state(state)
            raise StateTransitionError(msg)

        print(f"[Orkestratör] [{agent.agent_id}. {agent.name}] Başlatılıyor (Aşama: {state.current_phase.value})...")
        max_retries = 2
        for attempt in range(1, max_retries + 1):
            try:
                state = agent.run(state, on_progress)
                self._persist_state(state)
                return state
            except Exception as e:
                print(f"[Orkestratör] [{agent.agent_id}. {agent.name}] Deneme {attempt}/{max_retries} Hatası: {e}")
                if attempt >= max_retries:
                    state.errors.append(str(e))
                    self._persist_state(state)
                    raise e
                time.sleep(1.0)
        return state

    # =========================================================================
    # FAZ 1: GİRİŞ, ÇÖZÜMLEME & INTERACTIVE CHECKPOINT (AWAIT_USER_SELECTION)
    # =========================================================================
    def start_pipeline(
        self,
        audio_file: Optional[str] = None,
        text: Optional[str] = None,
        project_id: Optional[str] = None,
        aspect_ratio: str = "9:16",
        custom_transcript: Optional[str] = None,
        auto_approve: bool = False,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        """
        Runs Phase 1:
          1. Transcribe & Text Beat Segmentation
          2. Semantic Style Recommendation & Prompt Card Building
          3. Enters AWAIT_USER_SELECTION interactive checkpoint unless auto_approve=True.
        """
        job_id = project_id or str(uuid.uuid4())[:8]

        state = ProjectState(
            project_id=job_id,
            input_type="audio" if audio_file else "text",
            raw_input_text=text,
            audio_file=audio_file,
            aspect_ratio=aspect_ratio,
            custom_transcript=custom_transcript,
            current_phase=PipelinePhase.PHASE_0_IDLE
        )
        self._active_jobs[job_id] = state
        self._persist_state(state)

        print(f"\n=======================================================")
        print(f"[Orkestratör Ajan] Çift Hatlı Hibrit Video Üretim Hattı Başlatıldı! (İş: {job_id})")
        print(f"Girdi Türü: {state.input_type.upper()} | En Boy Oranı: {aspect_ratio}")
        print(f"=======================================================\n")

        # 1. Run Agent 1: Transcribe & Text Parsing
        state = self._run_agent_safely(self.agent1_transcribe, state, on_progress)

        # 2. Run Agent 2: Style Recommender
        state = self._run_agent_safely(self.agent2_recommender, state, on_progress)

        # 3. Interactive Checkpoint Evaluation
        rec_track = state.recommendation_card.recommended_track
        print(f"[Orkestratör] İnteraktif Onay Kapısına Ulaşıldı (AWAIT_USER_SELECTION).")
        print(f"Ajan Önerisi: {rec_track.value.upper()}")
        print(f"Gerekçe: {state.recommendation_card.recommendation_reason}")

        if auto_approve:
            print("[Orkestratör] Oto-Mod Aktif: Önerilen stil otomatik onaylandı. Faz 2'ye geçiliyor...")
            return self.resume_with_selection(job_id, rec_track.value, on_progress)

        # Halted at AWAIT_USER_SELECTION, awaiting user interaction via API
        return state

    # =========================================================================
    # FAZ 2 & FAZ 3: BRANŞLAŞMA & POST-PRODUCTION RENDER
    # =========================================================================
    def resume_with_selection(
        self,
        job_id: str,
        selected_track: str,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        """
        Resumes the pipeline from AWAIT_USER_SELECTION with the user's chosen track.
        Executes Branch A or Branch B, followed by shared Post-Production (Agents 5, 6, 7).
        """
        state = self.get_job_state(job_id)
        if not state:
            raise ValueError(f"İş ID bulunamadı: {job_id}")

        if state.current_phase != PipelinePhase.PHASE_1_AWAITING_USER_SELECTION:
            raise StateTransitionError(
                f"Boru hattı kullanıcı onayı bekleme aşamasında değil! Mevcut Aşama: '{state.current_phase.value}'"
            )

        # Validate selection
        if selected_track not in ["cinematic", "vector_infographic"]:
            raise ValueError(f"Geçersiz dal seçimi: '{selected_track}'. 'cinematic' veya 'vector_infographic' olmalıdır.")

        chosen_track = TrackType(selected_track)
        state.selected_track = chosen_track
        if state.recommendation_card:
            state.recommendation_card.selected_track = chosen_track
            state.recommendation_card.selected_at = time.strftime("%Y-%m-%d %H:%M:%S")

        # Advance to Branch Selected Phase
        state.current_phase = PipelinePhase.PHASE_2_BRANCH_SELECTED
        self._persist_state(state)

        print(f"\n[Orkestratör] Kullanıcı Onayı Alındı: Seçilen Dal -> [{chosen_track.value.upper()}]")

        if on_progress:
            on_progress(2, "success", {
                "message": f"Kullanıcı seçimi onaylandı: {chosen_track.value.upper()}. Motor branşlaşması başlatılıyor...",
                "selected_track": chosen_track.value
            })

        # ==========================================
        # BRANCH A: SINEMATIK BELGESEL (DIFFUSION)
        # ==========================================
        if chosen_track == TrackType.CINEMATIC:
            print("[Orkestratör] Branş A Tetiklendi: Sinematik Difüzyon Hattı (Veo / Kling / Flux)...")
            state = self._run_agent_safely(self.agent3a_cinematic_art, state, on_progress)
            state = self._run_agent_safely(self.agent4a_diffusion_worker, state, on_progress)

        # ==========================================
        # BRANCH B: 2D VEKTOREL INFOGRAFIK (REMOTION)
        # ==========================================
        else:
            print("[Orkestratör] Branş B Tetiklendi: 2D Vektörel İnfografik Hattı (Remotion / Motion Graphics)...")
            state = self._run_agent_safely(self.agent3b_vector_director, state, on_progress)
            state = self._run_agent_safely(self.agent4b_remotion_worker, state, on_progress)

        # ==========================================
        # FAZ 3: ORTAK POST-PRODUCTION & FINAL ASSEMBLY
        # ==========================================
        print("\n[Orkestratör] Faz 3 Başlatılıyor: Dinamik Tipografi, Ses Tasarımı ve FFmpeg Render...")
        state = self._run_agent_safely(self.agent5_typography, state, on_progress)
        state = self._run_agent_safely(self.agent6_audio, state, on_progress)
        state = self._run_agent_safely(self.agent7_assembly, state, on_progress)

        print(f"\n=======================================================")
        print(f"[Orkestratör Ajan] ÇİFT HATLI HİBRİT VİDEO KURGUSU TAMAMLANDI!")
        print(f"Seçilen Dal: {chosen_track.value.upper()}")
        print(f"Nihai Video Dosyası: {state.assembly.final_video_file}")
        print(f"Toplam Süre: {state.assembly.duration:.1f}s | Boyut: {state.assembly.file_size_bytes} bytes")
        print(f"=======================================================\n")

        self._persist_state(state)
        return state

    # Backward compatibility wrapper for old single-shot pipeline
    def execute_pipeline(
        self,
        audio_file: str,
        project_id: Optional[str] = None,
        aspect_ratio: str = "9:16",
        visual_style: str = "cinematic_photoreal",
        custom_transcript: Optional[str] = None,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        return self.start_pipeline(
            audio_file=audio_file,
            project_id=project_id,
            aspect_ratio=aspect_ratio,
            custom_transcript=custom_transcript,
            auto_approve=True,
            on_progress=on_progress
        )
