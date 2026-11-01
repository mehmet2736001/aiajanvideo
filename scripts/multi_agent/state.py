# -*- coding: utf-8 -*-
"""
Multi-Agent Video Production System - State & Schema Definitions
Dual-Track Architecture: Cinematic Documentary (Diffusion) & 2D Vector Infographic (Remotion/Code-as-Video)
Interactive Checkpoint: AWAIT_USER_SELECTION
"""
from enum import Enum
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
import time


class TrackType(str, Enum):
    CINEMATIC = "cinematic"
    VECTOR_INFOGRAPHIC = "vector_infographic"


class PipelinePhase(str, Enum):
    PHASE_0_IDLE = "phase_0_idle"
    PHASE_1_TRANSCRIBED = "phase_1_transcribed"
    PHASE_1_AWAITING_USER_SELECTION = "phase_1_awaiting_user_selection"
    PHASE_2_BRANCH_SELECTED = "phase_2_branch_selected"

    # Branch A: Cinematic Track (Diffusion)
    PHASE_3A_PROMPTS_COMPOSED = "phase_3a_prompts_composed"
    PHASE_4A_DIFFUSION_RENDERED = "phase_4a_diffusion_rendered"

    # Branch B: 2D Vector Infographic Track (Code-as-Video)
    PHASE_3B_METAPHORS_COMPOSED = "phase_3b_metaphors_composed"
    PHASE_4B_REMOTION_RENDERED = "phase_4b_remotion_rendered"

    # Common Post-Production
    PHASE_5_SUBTITLES_COMPOSED = "phase_5_subtitles_composed"
    PHASE_6_AUDIO_DESIGNED = "phase_6_audio_designed"
    PHASE_7_ASSEMBLED = "phase_7_assembled"

    # Backward compatibility aliases
    PHASE_2_STORYBOARDED = "phase_2_storyboarded"
    PHASE_3_ART_DIRECTED = "phase_3_art_directed"
    PHASE_4_ASSETS_GENERATED = "phase_4_assets_generated"


class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_INPUT = "awaiting_input"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


# ==========================================
# 1. TRANSCRIBE AGENT SCHEMAS (DUAL INPUT)
# ==========================================
class WordTiming(BaseModel):
    word: str
    start: float
    end: float
    confidence: float = 1.0


class SentenceBeat(BaseModel):
    sentence_id: int
    text: str
    start: float
    end: float
    duration: float
    emphasis_words: List[str] = Field(default_factory=list)


class TranscriptionData(BaseModel):
    input_type: str = "audio"  # "audio" or "text"
    raw_text: str
    clean_text: str
    duration: float
    words: List[WordTiming] = Field(default_factory=list)
    sentence_beats: List[SentenceBeat] = Field(default_factory=list)
    language: str = "tr"
    created_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))


# ==========================================
# 2. STYLE RECOMMENDER & CHECKPOINT SCHEMAS
# ==========================================
class TrackOption(BaseModel):
    id: TrackType
    title: str
    subtitle: str
    badge: str
    description: str
    engine: str
    pros: List[str] = Field(default_factory=list)


class RecommendationCard(BaseModel):
    recommended_track: TrackType
    confidence: float = 0.95
    analysis_summary: str
    recommendation_reason: str
    semantic_features: List[str] = Field(default_factory=list)
    options: List[TrackOption] = Field(default_factory=list)
    user_prompt_text: str = (
        "İçerik analizi tamamlandı. Bu konsept için önerilen stili onaylayabilir "
        "veya dilediğiniz motoru seçebilirsiniz."
    )
    selected_track: Optional[TrackType] = None
    selected_at: Optional[str] = None


# ==========================================
# BRANCH A: CINEMATIC DOCUMENTARY SCHEMAS
# ==========================================
class SceneBeat(BaseModel):
    scene_id: int
    start: float
    end: float
    duration: float
    spoken_text: str
    concept: str
    mood: str
    camera_movement: str = "slow_push_in"
    emphasis_keywords: List[str] = Field(default_factory=list)
    layout_type: str = "cinematic_ambient"


class StoryboardData(BaseModel):
    scenes: List[SceneBeat]
    total_scenes: int
    total_duration: float
    emotional_arc: str = "inspiring"


class ScenePrompt(BaseModel):
    scene_id: int
    visual_prompt: str
    negative_prompt: str = (
        "cartoon, anime, 3d render, illustration, drawing, flat vector, blurry, distorted, watermark, text"
    )
    aspect_ratio: str = "9:16"
    camera_movement: str = "slow_push_in"
    style: str = "cinematic_photoreal"
    continuity_notes: str = ""


class ArtDirectionData(BaseModel):
    prompts: List[ScenePrompt]
    global_style: str = "cinematic_photoreal"
    color_palette: str = "35mm natural tones, volumetric golden light, organic depth"


class SceneMediaAsset(BaseModel):
    scene_id: int
    video_file: str
    video_url: str
    thumbnail_file: Optional[str] = None
    duration: float
    width: int = 720
    height: int = 1280
    verified: bool = False
    file_size_bytes: int = 0


class MediaWorkerData(BaseModel):
    assets: List[SceneMediaAsset]
    all_verified: bool = False
    total_size_bytes: int = 0


# ==========================================
# BRANCH B: 2D VECTOR INFOGRAPHIC SCHEMAS
# ==========================================
class SvgIconDefinition(BaseModel):
    icon_id: str
    name: str
    view_box: str = "0 0 100 100"
    svg_body: str
    stroke_width: float = 2.5
    stroke_color: str = "#f59e0b"
    fill_color: str = "none"


class MetaphorMapping(BaseModel):
    scene_id: int
    concept: str
    symbol_name: str
    metaphor_explanation: str
    icon: SvgIconDefinition
    animation_type: Literal["spring_pop", "path_draw", "scale_fade", "counter_spin"] = "spring_pop"
    spring_damping: float = 12.0
    spring_stiffness: float = 120.0


class VectorDirectorData(BaseModel):
    metaphors: List[MetaphorMapping]
    primary_color: str = "#0f172a"
    accent_gold: str = "#f59e0b"
    accent_cyan: str = "#06b6d4"
    bg_style: str = "minimal_grid_canvas"


class RemotionSceneAsset(BaseModel):
    scene_id: int
    video_file: str
    video_url: str
    component_name: str
    jsx_file: Optional[str] = None
    duration: float
    width: int = 720
    height: int = 1280
    verified: bool = False
    file_size_bytes: int = 0


class RemotionWorkerData(BaseModel):
    assets: List[RemotionSceneAsset]
    all_verified: bool = False
    total_size_bytes: int = 0


# ==========================================
# COMMON POST-PRODUCTION SCHEMAS
# ==========================================
class TypographyData(BaseModel):
    ass_file_path: str
    ass_url: str
    subtitle_chunks: List[Dict[str, Any]] = Field(default_factory=list)
    style_name: str = "TikTok_Gold_Pop"
    font_name: str = "Arial"
    primary_color: str = "&H00FFFFFF"
    highlight_color: str = "&H00D7FF"  # Vivid gold/yellow
    category_badge_text: str = ""


class SfxEvent(BaseModel):
    timestamp: float
    sfx_file: str
    volume: float = 0.6
    description: str = "transition"


class AudioDesignData(BaseModel):
    mixed_audio_file: str
    mixed_audio_url: str
    bgm_file: str
    bgm_volume_ducked_db: float = -18.0
    sfx_events: List[SfxEvent] = Field(default_factory=list)
    total_duration: float


class AssemblyData(BaseModel):
    final_video_file: str
    final_video_url: str
    duration: float
    file_size_bytes: int
    resolution: str = "720x1280"
    render_time_sec: float = 0.0


# ==========================================
# MASTER PROJECT STATE
# ==========================================
class AgentStepLog(BaseModel):
    agent_id: int
    agent_name: str
    status: AgentStatus = AgentStatus.PENDING
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    duration_sec: float = 0.0
    error: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class ProjectState(BaseModel):
    project_id: str
    input_type: str = "audio"  # "audio" or "text"
    raw_input_text: Optional[str] = None
    audio_file: Optional[str] = None
    aspect_ratio: str = "9:16"
    visual_style: str = "cinematic_photoreal"
    custom_transcript: Optional[str] = None

    # Track Decision & Branching
    selected_track: Optional[TrackType] = None
    recommendation_card: Optional[RecommendationCard] = None

    current_phase: PipelinePhase = PipelinePhase.PHASE_0_IDLE
    agent_logs: Dict[int, AgentStepLog] = Field(default_factory=dict)

    # Data Containers
    transcription: Optional[TranscriptionData] = None
    storyboard: Optional[StoryboardData] = None

    # Branch A: Cinematic
    art_direction: Optional[ArtDirectionData] = None
    media_assets: Optional[MediaWorkerData] = None

    # Branch B: Vector Infographic
    vector_direction: Optional[VectorDirectorData] = None
    vector_assets: Optional[RemotionWorkerData] = None

    # Common Post-Production
    typography: Optional[TypographyData] = None
    audio_design: Optional[AudioDesignData] = None
    assembly: Optional[AssemblyData] = None

    errors: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
