export type LayoutType =
  | 'cards'
  | 'vs_split'
  | 'flowchart'
  | 'quote_spotlight'
  | 'metric_impact'
  | 'grid_explosion'
  | 'tri_concept'
  | 'pip_split'
  | 'cinematic_ambient';

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

export type PipPosition = 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'center';
export type PipShape = 'circle' | 'rounded' | 'rectangle' | 'phone';

export interface PipVideoItem {
  id: string;
  videoUrl: string;
  startTime: number; // in seconds
  endTime: number; // in seconds
  position?: PipPosition;
  shape?: PipShape;
  width?: number; // width in px
  height?: number; // height in px
  x?: number;
  y?: number;
  volume?: number; // 0.0 to 1.0
  muted?: boolean;
  opacity?: number;
  borderColor?: string;
  borderWidth?: number;
}

export type OverlayPosition = 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'center' | 'top-banner' | 'bottom-banner';
export type OverlayAnimation = 'fade' | 'bounce' | 'slide_up' | 'spin' | 'none';

export interface OverlayImageItem {
  id: string;
  imageUrl: string;
  startTime: number;
  endTime: number;
  position?: OverlayPosition;
  width?: number;
  height?: number;
  x?: number;
  y?: number;
  opacity?: number;
  rotation?: number;
  animation?: OverlayAnimation;
}

export interface AudioTrackItem {
  id: string;
  audioUrl: string;
  startTime: number;
  endTime: number;
  volume: number;
  muted: boolean;
  type?: 'voiceover' | 'music' | 'sfx' | 'extracted';
  label?: string;
}

export type QuoteFrameTheme =
  | 'red_alert'       // 🚨 Kırmızı Alarm & Yanıltıcı İçerik Uyarısı (Glow Kırmızı Çerçeve)
  | 'social_phone'    // 📱 Sosyal Medya Telefonu (iPhone Mockup, Reels/TikTok stili)
  | 'news_broadcast'  // 📺 Haber Kanalı / Arşiv TV Çerçevesi ("İDDİA EDİLEN BİLGİ")
  | 'court_evidence'  // ⚖️ Hukuki / Bilimsel Delil Dosyası ("DELİL #1")
  | 'minimal_card';   // 💬 Şık Eleştiri Kartı (Tırnak işaretli modern kart)

export type QuoteStampType = 'yalan' | 'iddia' | 'carpitma' | 'dikkat' | 'none';

export interface QuoteVideoItem {
  id: string;
  videoUrl: string;             // Orijinal video dosya yolu
  trimStart: number;            // Kırpma başlangıç zamanı (video içindeki saniye)
  trimEnd: number;              // Kırpma bitiş zamanı (video içindeki saniye)
  timelineStart: number;        // Proje zaman tüneline giriş saniyesi
  duration: number;             // Gösterim süresi (trimEnd - trimStart)
  timelineEnd?: number;         // timelineStart + duration
  theme: QuoteFrameTheme;       // Çerçeve teması
  headerText: string;           // Üst afiş: "Arkadaşlar bu videoyu iyi izleyin..."
  subHeaderText?: string;       // İkinci satır / İddia başlığı: "Sosyal medyada yayılan iddia"
  authorTag?: string;           // Kaynak hesabı: "@orijinal_hesap"
  stamp?: QuoteStampType;       // Damga efekti ('yalan', 'iddia', 'carpitma', 'dikkat', 'none')
  volume?: number;              // Alıntı video ses düzeyi (0.0 - 1.0, varsayılan 1.0)
  muted?: boolean;              // Sessize alma
  freezeAtEnd?: boolean;        // Klip bitiminde son kareyi dondurup filtre uygula
  width?: number;               // Özel genişlik (px)
  height?: number;              // Özel yükseklik (px)
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
  brollType?: 'none' | 'cosmic' | 'ink' | 'clouds' | 'waves' | 'gold_dust' | string;
  brollOpacity?: number;
  pipData?: { title?: string; subtitle?: string; caption?: string; badge?: string };
  videoUrl?: string;
  animationVideoUrl?: string;
  animationPrompt?: string;
  animationStyle?: string;
  pipVideos?: PipVideoItem[];
  overlayImages?: OverlayImageItem[];
  quoteVideos?: QuoteVideoItem[];
  aiKurguStartOffset?: number;
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
  brollType?: 'none' | 'cosmic' | 'ink' | 'clouds' | 'waves' | 'gold_dust' | string;
  brollOpacity?: number;
  pipData?: { title?: string; subtitle?: string; caption?: string; badge?: string };
  narration?: string;
  words?: Array<any>;
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
  videoUrl?: string;
  animationVideoUrl?: string;
  animationPrompt?: string;
  animationStyle?: string;
  audioMuted?: boolean;
  audioVolume?: number;
  pipVideos?: PipVideoItem[];
  overlayImages?: OverlayImageItem[];
  quoteVideos?: QuoteVideoItem[];
  audioTracks?: AudioTrackItem[];
  scenes?: VideoScene[];
  language?: LanguageCode;
  direction?: TextDirection;
  isRTL?: boolean;
}
