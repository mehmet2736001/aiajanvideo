/**
 * Dual-Track Autonomous Video Production State Machine & Agent Interfaces
 * Supports both "Cinematic Documentary" (Diffusion Pipeline) and "2D Vector Infographic" (Code-as-Video Pipeline)
 * Enforces the AWAIT_USER_SELECTION interactive checkpoint event loop.
 */

// ==========================================
// 1. PIPELINE PHASES & TYPES
// ==========================================
export type TrackType = 'cinematic' | 'vector_infographic';

export enum PipelinePhase {
  PHASE_0_IDLE = 'phase_0_idle',
  PHASE_1_TRANSCRIBED = 'phase_1_transcribed',
  PHASE_1_AWAITING_USER_SELECTION = 'phase_1_awaiting_user_selection',
  PHASE_2_BRANCH_SELECTED = 'phase_2_branch_selected',

  // Branch A: Cinematic Track (Diffusion)
  PHASE_3A_PROMPTS_COMPOSED = 'phase_3a_prompts_composed',
  PHASE_4A_DIFFUSION_RENDERED = 'phase_4a_diffusion_rendered',

  // Branch B: 2D Vector Infographic Track (Remotion / Code-as-Video)
  PHASE_3B_METAPHORS_COMPOSED = 'phase_3b_metaphors_composed',
  PHASE_4B_REMOTION_RENDERED = 'phase_4b_remotion_rendered',

  // Common Post-Production
  PHASE_5_SUBTITLES_COMPOSED = 'phase_5_subtitles_composed',
  PHASE_6_AUDIO_DESIGNED = 'phase_6_audio_designed',
  PHASE_7_ASSEMBLED = 'phase_7_assembled'
}

export type AgentStatus = 'pending' | 'running' | 'awaiting_input' | 'success' | 'failed' | 'skipped';

// ==========================================
// 2. DATA SCHEMAS
// ==========================================
export interface WordTiming {
  word: string;
  start: number;
  end: number;
  confidence?: number;
}

export interface SentenceBeat {
  sentence_id: number;
  text: string;
  start: number;
  end: number;
  duration: number;
  emphasis_words: string[];
}

export interface TranscriptionData {
  input_type: 'audio' | 'text';
  raw_text: string;
  clean_text: string;
  duration: number;
  words: WordTiming[];
  sentence_beats: SentenceBeat[];
  language: string;
}

export interface TrackOption {
  id: TrackType;
  title: string;
  subtitle: string;
  badge: string;
  description: string;
  engine: string;
  pros: string[];
}

export interface RecommendationCard {
  recommended_track: TrackType;
  confidence: number;
  analysis_summary: string;
  recommendation_reason: string;
  semantic_features: string[];
  options: TrackOption[];
  user_prompt_text: string;
  selected_track?: TrackType | null;
  selected_at?: string | null;
}

// Branch A: Cinematic
export interface SceneBeat {
  scene_id: number;
  start: number;
  end: number;
  duration: number;
  spoken_text: string;
  concept: string;
  mood: string;
  camera_movement: 'slow_push_in' | 'slow_pan_dolly' | 'orbital_drift';
  emphasis_keywords: string[];
  layout_type?: string;
}

export interface StoryboardData {
  scenes: SceneBeat[];
  total_scenes: number;
  total_duration: number;
  emotional_arc: string;
}

export interface ScenePrompt {
  scene_id: number;
  visual_prompt: string;
  negative_prompt: string;
  aspect_ratio: '9:16' | '16:9' | '1:1';
  camera_movement: string;
  style: string;
  continuity_notes?: string;
}

export interface ArtDirectionData {
  prompts: ScenePrompt[];
  global_style: string;
  color_palette: string;
}

export interface SceneMediaAsset {
  scene_id: number;
  video_file: string;
  video_url: string;
  thumbnail_file?: string;
  duration: number;
  width: number;
  height: number;
  verified: boolean;
  file_size_bytes: number;
}

export interface MediaWorkerData {
  assets: SceneMediaAsset[];
  all_verified: boolean;
  total_size_bytes: number;
}

// Branch B: 2D Vector Infographic
export interface SvgIconDefinition {
  icon_id: string;
  name: string;
  view_box: string;
  svg_body: string;
  stroke_width: number;
  stroke_color: string;
  fill_color: string;
}

export interface MetaphorMapping {
  scene_id: number;
  concept: string;
  symbol_name: string;
  metaphor_explanation: string;
  icon: SvgIconDefinition;
  animation_type: 'spring_pop' | 'path_draw' | 'scale_fade' | 'counter_spin';
  spring_damping: number;
  spring_stiffness: number;
}

export interface VectorDirectorData {
  metaphors: MetaphorMapping[];
  primary_color: string;
  accent_gold: string;
  accent_cyan: string;
  bg_style: string;
}

export interface RemotionSceneAsset {
  scene_id: number;
  video_file: string;
  video_url: string;
  component_name: string;
  jsx_file?: string;
  duration: number;
  width: number;
  height: number;
  verified: boolean;
  file_size_bytes: number;
}

export interface RemotionWorkerData {
  assets: RemotionSceneAsset[];
  all_verified: boolean;
  total_size_bytes: number;
}

// Common Post-Production
export interface TypographyData {
  ass_file_path: string;
  ass_url: string;
  subtitle_chunks: Array<{ text: string; start: number; end: number }>;
  style_name: string;
  font_name: string;
  primary_color: string;
  highlight_color: string;
}

export interface SfxEvent {
  timestamp: number;
  sfx_file: string;
  volume: number;
  description: string;
}

export interface AudioDesignData {
  mixed_audio_file: string;
  mixed_audio_url: string;
  bgm_file: string;
  bgm_volume_ducked_db: number;
  sfx_events: SfxEvent[];
  total_duration: number;
}

export interface AssemblyData {
  final_video_file: string;
  final_video_url: string;
  duration: number;
  file_size_bytes: number;
  resolution: string;
  render_time_sec: number;
}

export interface AgentStepLog {
  agent_id: number;
  agent_name: string;
  status: AgentStatus;
  started_at?: string;
  finished_at?: string;
  duration_sec?: number;
  error?: string;
  details?: Record<string, any>;
}

export interface DualTrackProjectState {
  project_id: string;
  input_type: 'audio' | 'text';
  raw_input_text?: string;
  audio_file?: string;
  aspect_ratio: '9:16' | '16:9';
  custom_transcript?: string;

  // Selected Track & Checkpoint
  selected_track?: TrackType | null;
  recommendation_card?: RecommendationCard | null;

  current_phase: PipelinePhase;
  agent_logs: Record<number, AgentStepLog>;

  // Data Containers
  transcription?: TranscriptionData | null;
  storyboard?: StoryboardData | null;

  // Branch A: Cinematic
  art_direction?: ArtDirectionData | null;
  media_assets?: MediaWorkerData | null;

  // Branch B: Vector Infographic
  vector_direction?: VectorDirectorData | null;
  vector_assets?: RemotionWorkerData | null;

  // Post-Production
  typography?: TypographyData | null;
  audio_design?: AudioDesignData | null;
  assembly?: AssemblyData | null;

  errors: string[];
  created_at: string;
  updated_at: string;
}

// ==========================================
// 3. AGENT CLASS INTERFACES
// ==========================================
export interface IAgent<TContext, TOutput> {
  readonly agentId: number;
  readonly name: string;
  readonly requiredPhase: PipelinePhase;
  readonly targetPhase: PipelinePhase;

  canExecute(state: DualTrackProjectState): { canRun: boolean; reason?: string };
  execute(state: DualTrackProjectState, onProgress?: (msg: string) => void): Promise<DualTrackProjectState>;
}

export interface ITranscribeAgent extends IAgent<void, TranscriptionData> {}
export interface IStyleRecommenderAgent extends IAgent<TranscriptionData, RecommendationCard> {}

// Branch A
export interface ICinematicArtDirectorAgent extends IAgent<StoryboardData, ArtDirectionData> {}
export interface IVideoDiffusionWorkerAgent extends IAgent<ArtDirectionData, MediaWorkerData> {}

// Branch B
export interface IVectorMetaphorDirectorAgent extends IAgent<StoryboardData, VectorDirectorData> {}
export interface IRemotionMotionGraphicsAgent extends IAgent<VectorDirectorData, RemotionWorkerData> {}

// Common Post-Production
export interface ITypographyAgent extends IAgent<TranscriptionData, TypographyData> {}
export interface IAudioDesignAgent extends IAgent<TranscriptionData, AudioDesignData> {}
export interface IAssemblyAgent extends IAgent<DualTrackProjectState, AssemblyData> {}

// ==========================================
// 4. AWAIT_USER_SELECTION EVENT LOOP & STATE MACHINE
// ==========================================
export type StateMachineEvent =
  | { type: 'START'; payload: { input_type: 'audio' | 'text'; audio_file?: string; text?: string; aspect_ratio?: '9:16' | '16:9' } }
  | { type: 'TRANSCRIBE_COMPLETE'; payload: TranscriptionData }
  | { type: 'RECOMMENDATION_READY'; payload: RecommendationCard }
  | { type: 'SELECT_TRACK'; payload: { selected_track: TrackType } }
  | { type: 'PROMPTS_COMPOSED'; payload: ArtDirectionData }
  | { type: 'DIFFUSION_COMPLETE'; payload: MediaWorkerData }
  | { type: 'METAPHORS_COMPOSED'; payload: VectorDirectorData }
  | { type: 'REMOTION_COMPLETE'; payload: RemotionWorkerData }
  | { type: 'SUBTITLES_COMPOSED'; payload: TypographyData }
  | { type: 'AUDIO_DESIGN_COMPLETE'; payload: AudioDesignData }
  | { type: 'ASSEMBLY_COMPLETE'; payload: AssemblyData }
  | { type: 'ERROR'; payload: { error: string } }
  | { type: 'RESET' };

export class DualTrackStateMachine {
  private state: DualTrackProjectState;
  private listeners: Array<(state: DualTrackProjectState) => void> = [];

  constructor(initialState?: Partial<DualTrackProjectState>) {
    this.state = {
      project_id: initialState?.project_id || Math.random().toString(36).substring(2, 10),
      input_type: initialState?.input_type || 'audio',
      aspect_ratio: initialState?.aspect_ratio || '9:16',
      current_phase: PipelinePhase.PHASE_0_IDLE,
      agent_logs: {},
      errors: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      ...initialState
    };
  }

  public getState(): DualTrackProjectState {
    return { ...this.state };
  }

  public subscribe(listener: (state: DualTrackProjectState) => void): () => void {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notify(): void {
    this.state.updated_at = new Date().toISOString();
    const snapshot = this.getState();
    this.listeners.forEach(fn => fn(snapshot));
  }

  /**
   * Atomic transition dispatch with strict validation.
   */
  public dispatch(event: StateMachineEvent): void {
    switch (event.type) {
      case 'START':
        if (this.state.current_phase !== PipelinePhase.PHASE_0_IDLE) {
          throw new Error(`Cannot START from phase: ${this.state.current_phase}`);
        }
        this.state.input_type = event.payload.input_type;
        this.state.audio_file = event.payload.audio_file;
        this.state.raw_input_text = event.payload.text;
        if (event.payload.aspect_ratio) this.state.aspect_ratio = event.payload.aspect_ratio;
        this.notify();
        break;

      case 'TRANSCRIBE_COMPLETE':
        this.state.transcription = event.payload;
        this.state.current_phase = PipelinePhase.PHASE_1_TRANSCRIBED;
        this.notify();
        break;

      case 'RECOMMENDATION_READY':
        this.state.recommendation_card = event.payload;
        // ENTER INTERACTIVE CHECKPOINT: Execution halts here waiting for SELECT_TRACK!
        this.state.current_phase = PipelinePhase.PHASE_1_AWAITING_USER_SELECTION;
        this.notify();
        break;

      case 'SELECT_TRACK':
        if (this.state.current_phase !== PipelinePhase.PHASE_1_AWAITING_USER_SELECTION) {
          throw new Error(`Cannot SELECT_TRACK when phase is ${this.state.current_phase}. Expected: PHASE_1_AWAITING_USER_SELECTION.`);
        }
        this.state.selected_track = event.payload.selected_track;
        if (this.state.recommendation_card) {
          this.state.recommendation_card.selected_track = event.payload.selected_track;
          this.state.recommendation_card.selected_at = new Date().toISOString();
        }
        // Resumes pipeline towards chosen branch
        this.state.current_phase = PipelinePhase.PHASE_2_BRANCH_SELECTED;
        this.notify();
        break;

      // Branch A Transitions
      case 'PROMPTS_COMPOSED':
        if (this.state.selected_track !== 'cinematic') {
          throw new Error('PROMPTS_COMPOSED is only valid for cinematic track');
        }
        this.state.art_direction = event.payload;
        this.state.current_phase = PipelinePhase.PHASE_3A_PROMPTS_COMPOSED;
        this.notify();
        break;

      case 'DIFFUSION_COMPLETE':
        this.state.media_assets = event.payload;
        this.state.current_phase = PipelinePhase.PHASE_4A_DIFFUSION_RENDERED;
        this.notify();
        break;

      // Branch B Transitions
      case 'METAPHORS_COMPOSED':
        if (this.state.selected_track !== 'vector_infographic') {
          throw new Error('METAPHORS_COMPOSED is only valid for vector_infographic track');
        }
        this.state.vector_direction = event.payload;
        this.state.current_phase = PipelinePhase.PHASE_3B_METAPHORS_COMPOSED;
        this.notify();
        break;

      case 'REMOTION_COMPLETE':
        this.state.vector_assets = event.payload;
        this.state.current_phase = PipelinePhase.PHASE_4B_REMOTION_RENDERED;
        this.notify();
        break;

      // Common Post-Production Transitions
      case 'SUBTITLES_COMPOSED':
        this.state.typography = event.payload;
        this.state.current_phase = PipelinePhase.PHASE_5_SUBTITLES_COMPOSED;
        this.notify();
        break;

      case 'AUDIO_DESIGN_COMPLETE':
        this.state.audio_design = event.payload;
        this.state.current_phase = PipelinePhase.PHASE_6_AUDIO_DESIGNED;
        this.notify();
        break;

      case 'ASSEMBLY_COMPLETE':
        this.state.assembly = event.payload;
        this.state.current_phase = PipelinePhase.PHASE_7_ASSEMBLED;
        this.notify();
        break;

      case 'ERROR':
        this.state.errors.push(event.payload.error);
        this.notify();
        break;

      case 'RESET':
        this.state.current_phase = PipelinePhase.PHASE_0_IDLE;
        this.state.selected_track = null;
        this.state.recommendation_card = null;
        this.state.errors = [];
        this.notify();
        break;
    }
  }
}
