export type LayoutType =
  | 'cards'
  | 'vs_split'
  | 'flowchart'
  | 'quote_spotlight'
  | 'metric_impact'
  | 'grid_explosion'
  | 'tri_concept'
  | 'pip_split';

export type LanguageCode = 'tr' | 'en' | 'ar' | 'es';
export type TextDirection = 'ltr' | 'rtl';

export type DoodleType = 'galaxy' | 'hourglass' | 'book' | 'lightbulb' | 'compass' | 'fingerprint' | 'dna';

export type VideoTheme =
  | 'notebook'
  | 'kraft'
  | 'chalkboard'
  | 'parchment'
  | 'blueprint'
  | 'dark_minimalist'
  | 'neon_cyber'
  | 'gold_luxury';

export interface CardItem {
  id: string;
  label: string;
  value: string;
  icon: 'galaxy' | 'embryo' | 'book' | 'clock' | 'lightbulb' | 'sprout' | 'moon' | 'heart' | 'scale' | 'fingerprint' | 'dna' | 'bone' | 'brain' | 'eye';
  color: string;
  delay?: number;
}

export interface VsItem {
  leftTitle: string;
  leftSubtitle: string;
  leftPoints: string[];
  leftColor?: string;
  rightTitle: string;
  rightSubtitle: string;
  rightPoints: string[];
  rightColor?: string;
  verdict: string;
}

export interface FlowchartStep {
  stepNumber: number;
  badge: string;
  title: string;
  desc: string;
  color?: string;
}

export interface QuoteSpotlightData {
  speaker: string;
  title: string;
  quoteText: string;
  sourceRef?: string;
  themeColor?: string;
}

export interface MetricImpactData {
  bigNumber: string;
  bigLabel: string;
  subheading: string;
  keyTakeaway: string;
  accentColor?: string;
}

export interface TimelineData {
  startYear: string;
  endYear: string;
  durationLabel: string;
  title: string;
  ayahArabic?: string;
  ayahTranslation?: string;
  ayahRef?: string;
}

export interface GridExplosionData {
  title: string;
  subtitle: string;
  iconType: 'fingerprint' | 'star' | 'dna' | 'atom' | 'human';
  itemCount: number;
  badgeText?: string;
  accentColor?: string;
}

export interface TriConceptData {
  badge?: string;
  concept1: { title: string; subtitle?: string; icon: string; color?: string };
  concept2: { title: string; subtitle?: string; icon: string; color?: string };
  concept3: { title: string; subtitle?: string; icon: string; color?: string };
  bottomNote?: string;
}

export interface SubtitleWord {
  text: string;
  start: number;
  end: number;
}

export interface VideoScene {
  id: string; // e.g. "scene_1", "scene_2"
  startTime: number; // in seconds (e.g. 0.0, 12.0)
  endTime: number; // in seconds (e.g. 12.0, 24.0)
  layoutType: LayoutType;
  headerSubtitle?: string;
  headerLine1?: string;
  circledWord?: string;
  headerLine2?: string;
  highlightedText?: string;
  strikeWord?: string;
  doodleType?: DoodleType;
  cards?: CardItem[];
  vsData?: VsItem;
  flowchartSteps?: FlowchartStep[];
  quoteSpotlight?: QuoteSpotlightData;
  metricImpact?: MetricImpactData;
  gridExplosion?: GridExplosionData;
  triConcept?: TriConceptData;
  timeline?: TimelineData;
  transition?: 'page_flip' | 'slide_left' | 'fade_morph';
  accentType?: 'none' | 'curved_arrow' | 'highlighter' | 'burst' | 'double_wave' | 'zigzag' | 'bracket';
  illustrationUrl?: string;
  illustrationCaption?: string;
  illustrationStyle?: 'polaroid' | 'torn_paper' | 'clean_frame' | 'none';
  brollUrl?: string;
  brollType?: 'none' | 'cosmic' | 'ink' | 'clouds' | 'waves';
  brollOpacity?: number;
  pipData?: { title?: string; subtitle?: string; caption?: string; badge?: string };
  language?: LanguageCode;
  direction?: TextDirection;
  isRTL?: boolean;
}

export interface ViralMetadata {
  hookScore: number;
  viralTitles: string[];
  hashtags: string[];
  loopEnding: string;
  description: string;
}

export interface VideoData {
  theme?: VideoTheme;
  layoutType?: LayoutType;
  doodleType?: DoodleType;
  headerSubtitle: string;
  headerLine1?: string;
  circledWord: string;
  headerLine2?: string;
  highlightedText: string;
  strikeWord?: string; // Word with animated red/neon strike-through (e.g. ~~YARATMAK~~)
  particles?: 'dust' | 'stars' | 'fireflies' | 'none';
  ambientPattern?: 'fingerprint' | 'dna' | 'cosmic' | 'grid' | 'none';
  filmGrain?: 'none' | 'subtle' | 'vintage' | 'heavy';
  lightLeaks?: 'none' | 'golden_hour' | 'cyan_dream' | 'anamorphic' | 'auto';
  cameraMotion?: 'static' | 'handheld' | 'cinematic_drift';
  accentType?: 'none' | 'curved_arrow' | 'highlighter' | 'burst' | 'double_wave' | 'zigzag' | 'bracket';
  headerMain?: string;
  cards?: CardItem[];
  vsData?: VsItem;
  flowchartSteps?: FlowchartStep[];
  quoteSpotlight?: QuoteSpotlightData;
  metricImpact?: MetricImpactData;
  timeline?: TimelineData;
  gridExplosion?: GridExplosionData;
  triConcept?: TriConceptData;
  illustrationUrl?: string;
  illustrationCaption?: string;
  illustrationStyle?: 'polaroid' | 'torn_paper' | 'clean_frame' | 'none';
  brollUrl?: string;
  brollType?: 'none' | 'cosmic' | 'ink' | 'clouds' | 'waves';
  brollOpacity?: number;
  pipData?: { title?: string; subtitle?: string; caption?: string; badge?: string };
  socialHandle: string;
  audioUrl?: string;
  subtitles?: SubtitleWord[];
  musicTrack?: string;
  ttsProvider?: 'edge_tts' | 'elevenlabs' | 'gtts';
  voiceId?: string;
  emotionTone?: 'documentary' | 'curiosity' | 'dramatic' | 'calm';
  viral?: ViralMetadata;
  durationMode?: 'quick' | 'deep' | 'custom_audio';
  totalDuration?: number;
  scenes?: VideoScene[];
  language?: LanguageCode;
  direction?: TextDirection;
  isRTL?: boolean;
}
