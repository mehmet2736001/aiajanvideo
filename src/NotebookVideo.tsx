import React from 'react';
import { loadFont } from '@remotion/google-fonts/Kalam';
import { loadFont as loadAmiri } from '@remotion/google-fonts/Amiri';
import { loadFont as loadCairo } from '@remotion/google-fonts/Cairo';
import { Audio, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { CardGrid } from './components/CardGrid';
import { DoodleDecorations } from './components/DoodleDecorations';
import { FlowchartView } from './components/FlowchartView';
import { HanddrawnDoodle, DoodleType } from './components/HanddrawnDoodle';
import { HanddrawnHeader } from './components/HanddrawnHeader';
import { MetricImpactView } from './components/MetricImpactView';
import { NotebookBackground } from './components/NotebookBackground';
import { QuoteSpotlightView } from './components/QuoteSpotlightView';
import { SceneBlock } from './components/SceneBlock';
import { SubtitlesBar } from './components/SubtitlesBar';
import { TimelineView } from './components/TimelineView';
import { VsSplitView } from './components/VsSplitView';
import { BackgroundWatermark } from './components/effects/BackgroundWatermark';
import { IconGridExplosion } from './components/effects/IconGridExplosion';
import { ParticleField } from './components/effects/ParticleField';
import { StrikethroughText } from './components/effects/StrikethroughText';
import { TriConceptView } from './components/effects/TriConceptView';
import { CameraMotion } from './components/effects/CameraMotion';
import { FilmGrainOverlay } from './components/effects/FilmGrainOverlay';
import { LightLeaksOverlay } from './components/effects/LightLeaksOverlay';
import { HanddrawnAccents } from './components/effects/HanddrawnAccents';
import { BRollOverlay } from './components/effects/BRollOverlay';
import { PipSplitView } from './components/effects/PipSplitView';
import { PipVideoOverlay } from './components/effects/PipVideoOverlay';
import { PngOverlayLayer } from './components/effects/PngOverlayLayer';
import { QuoteVideoFrame } from './components/effects/QuoteVideoFrame';
import { PipVideoItem, OverlayImageItem, QuoteVideoItem } from './types';
import { VideoData } from './types';

export const NotebookVideo: React.FC<VideoData> = (props) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps, width, height } = useVideoConfig();
  const currentTimeSec = frame / fps;

  const isHorizontal = width > height;
  const isSquare = width === height;

  const isRTL = props.isRTL || props.direction === 'rtl' || props.language === 'ar';


  // Collect all PIP videos & PNG overlays from props and individual scenes
  const allPipVideos = React.useMemo(() => {
    const list: PipVideoItem[] = [...(props.pipVideos || [])];
    if (props.scenes) {
      for (const sc of props.scenes) {
        if (sc.pipVideos) list.push(...sc.pipVideos);
      }
    }
    return list;
  }, [props.pipVideos, props.scenes]);

  const allOverlayImages = React.useMemo(() => {
    const list: OverlayImageItem[] = [...(props.overlayImages || [])];
    if (props.scenes) {
      for (const sc of props.scenes) {
        if (sc.overlayImages) list.push(...sc.overlayImages);
      }
    }
    return list;
  }, [props.overlayImages, props.scenes]);

  const allQuoteVideos = React.useMemo(() => {
    const list: QuoteVideoItem[] = [...(props.quoteVideos || [])];
    if (props.scenes) {
      for (const sc of props.scenes) {
        if (sc.quoteVideos) list.push(...sc.quoteVideos);
      }
    }
    return list;
  }, [props.quoteVideos, props.scenes]);

  // Load fonts
  const { fontFamily } = loadFont();
  if (isRTL) {
    try {
      loadAmiri();
      loadCairo();
    } catch (e) {
      // Font fallback
    }
  }

  // Pre-calculate active speech intervals in seconds for Dynamic Music Ducking 2.0 (Faz 7)
  const speechIntervals = React.useMemo(() => {
    const intervals: { start: number; end: number }[] = [];
    if (props.subtitles && props.subtitles.length > 0) {
      for (const sub of props.subtitles) {
        if (typeof sub.start === 'number' && typeof sub.end === 'number') {
          intervals.push({ start: sub.start - 0.1, end: sub.end + 0.15 });
        }
      }
    } else if ((props as any).words && (props as any).words.length > 0) {
      for (const w of (props as any).words) {
        if (typeof w.start === 'number' && typeof w.end === 'number') {
          intervals.push({ start: w.start - 0.05, end: w.end + 0.1 });
        }
      }
    }
    return intervals;
  }, [props.subtitles, (props as any).words]);

  // Subtle 2.5D camera zoom to break visual monotony
  const cameraZoom = interpolate(frame, [0, durationInFrames], [1.0, 1.035], {
    extrapolateRight: 'clamp',
  });

  const activeTheme = props.theme || 'notebook';
  const layout = props.layoutType || 'cards';

  // Determine dynamic hand-drawn doodle sketch based on topic (Faz 2)
  let doodleType: DoodleType = props.doodleType || 'galaxy';
  const textCorpus = (
    (props.headerLine1 || '') +
    ' ' +
    (props.circledWord || '') +
    ' ' +
    (props.highlightedText || '') +
    ' ' +
    (props.narration || '')
  ).toLowerCase();

  if (textCorpus.includes('zaman') || textCorpus.includes('saat') || textCorpus.includes('yÄ±l') || textCorpus.includes('gÃ¼n')) {
    doodleType = 'hourglass';
  } else if (textCorpus.includes('kitap') || textCorpus.includes('aristo') || textCorpus.includes('farabi') || textCorpus.includes('alim') || textCorpus.includes('oku') || textCorpus.includes('sina')) {
    doodleType = 'book';
  } else if (textCorpus.includes('fikir') || textCorpus.includes('akÄ±l') || textCorpus.includes('beyin') || textCorpus.includes('dÃ¼ÅŸÃ¼n') || textCorpus.includes('Ä±ÅŸÄ±k')) {
    doodleType = 'lightbulb';
  } else if (textCorpus.includes('kainat') || textCorpus.includes('galaksi') || textCorpus.includes('evren') || textCorpus.includes('kara') || textCorpus.includes('yÄ±ldÄ±z') || textCorpus.includes('delik')) {
    doodleType = 'galaxy';
  } else if (textCorpus.includes('yÃ¶n') || textCorpus.includes('pusula') || textCorpus.includes('yol') || textCorpus.includes('hedef')) {
    doodleType = 'compass';
  }

  const isDarkMotion =
    activeTheme === 'dark_minimalist' ||
    activeTheme === 'neon_cyber' ||
    activeTheme === 'gold_luxury';

  const effectiveFont = isRTL
    ? '"Amiri", "Cairo", "Scheherazade New", serif'
    : isDarkMotion
    ? '"Montserrat", "Inter", "Poppins", -apple-system, sans-serif'
    : fontFamily;

  // Determine dynamic header lines
  const title1 = props.headerLine1 || (props.headerMain ? props.headerMain.split(' ')[0] : 'NEDEN');
  const title2 = props.headerLine2 || '';

  return (
    <div
      style={{
        width,
        height,
        position: 'relative',
        overflow: 'hidden',

        fontFamily: effectiveFont,
        direction: isRTL ? 'rtl' : 'ltr',
        transform: `scale(${cameraZoom})`,
        transformOrigin: 'center center',
      }}
    >
      <CameraMotion mode={props.cameraMotion || 'handheld'}>
        {/* 1. Themed Background (Notebook / Kraft / Dark Minimalist / Gold Luxury / Neon Cyber) */}
        <NotebookBackground theme={activeTheme} isRTL={isRTL} />

      {/* 2. Ambient Watermarks (Fingerprint / DNA / Cosmic for Dark Motion) */}
      <BackgroundWatermark
        pattern={props.ambientPattern || (isDarkMotion ? 'fingerprint' : 'none')}
        theme={activeTheme}
      />

      {/* 3. Floating Ambient Particles */}
      <ParticleField
        type={props.particles || (isDarkMotion ? 'dust' : 'none')}
        count={35}
        color={activeTheme === 'gold_luxury' ? '#facc15' : activeTheme === 'neon_cyber' ? '#38bdf8' : '#fef08a'}
      />

      {/* 3.5 Sinematik B-Roll Stok Medya KatmanÄ± (Faz 8) */}
      {/* 3.5 Sinematik Canli B-Roll Arkaplan Video Katmani */}
      <BRollOverlay
        type={props.brollType && props.brollType !== 'none' ? props.brollType : (isDarkMotion ? (activeTheme === 'gold_luxury' ? 'gold_dust' : 'cosmic') : 'cosmic')}
        brollUrl={props.brollUrl}
        opacity={props.brollOpacity ?? 0.8}
        blendMode="normal"
      />

      {/* Decorative Doodles (Only for Notebook / Kraft / Blueprint) */}
      {!isDarkMotion && <DoodleDecorations theme={activeTheme} />}

      {/* Main Content Layout Container */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 1,
        }}
      >
        {/* MULTI-SCENE CHAINED NARRATIVE (10-14s INTERVALS) */}
        {props.scenes && props.scenes.length > 0 ? (
          props.scenes.map((scene, idx) => {
            const startF = Math.floor(scene.startTime * 30);
            const endF = Math.floor(scene.endTime * 30);
            const durF = Math.max(30, endF - startF);
            return (
              <Sequence key={scene.id || idx} from={startF} durationInFrames={durF}>
                <SceneBlock
                  scene={scene}
                  theme={activeTheme}
                  isDarkMotion={isDarkMotion}
                  sceneIndex={idx}
                  totalScenes={props.scenes!.length}
                  isRTL={isRTL}
                />
              </Sequence>
            );
          })
        ) : (
          /* Classic Single-Scene Layout */
          <>
            {/* Top Spacer for spiral wire */}
            <div style={{ height: activeTheme === 'chalkboard' ? 30 : 60 }} />

            {/* 2. Top Handdrawn Header with Pen & Marker Cursor Animation */}
            <HanddrawnHeader
              subtitle={props.headerSubtitle || 'KÄ±sa KÄ±ssa'}
              title1={title1}
              title2={title2}
              circledWord={props.circledWord || ''}
              highlightedText={props.highlightedText || ''}
              theme={activeTheme}
              isRTL={isRTL}
            />

            {/* Hand-drawn Organic Doodle Sketch (Faz 2) - For Notebook, Kraft & Chalkboard */}
            {!isDarkMotion && (
              <div
                style={{
                  position: 'absolute',
                  top: activeTheme === 'chalkboard' ? 35 : 65,
                  right: isRTL ? undefined : 48,
                  left: isRTL ? 48 : undefined,
                  zIndex: 12,
                  pointerEvents: 'none',
                }}
              >
                <HanddrawnDoodle
                  type={doodleType}
                  size={135}
                  theme={activeTheme}
                  startFrame={25}
                  durationInFrames={40}
                />
              </div>
            )}

            {/* Optional Animated Strikethrough Effect */}
            {props.strikeWord && (
              <StrikethroughText
                strikeText={props.strikeWord}
                prefixText=""
                strikeColor="#ef4444"
              />
            )}

            {/* 3. Middle Dynamic Multi-Scene Interactive Area */}
            <div style={{ position: 'relative', width: '100%', minHeight: 640, marginTop: props.strikeWord ? 0 : 20 }}>
              {layout === 'grid_explosion' ? (
                <Sequence from={0} durationInFrames={props.timeline ? 180 : durationInFrames}>
                  <IconGridExplosion
                    title={props.gridExplosion?.title || (title1 + ' ' + (props.circledWord || '') + ' ' + (props.highlightedText || ''))}
                    subtitle={props.gridExplosion?.subtitle || (props.metricImpact?.subheading || 'Milyarlarca Ä°nsan, Benzersiz MÃ¼hÃ¼r')}
                    iconType={props.gridExplosion?.iconType || 'fingerprint'}
                    itemCount={props.gridExplosion?.itemCount || 12}
                    accentColor={activeTheme === 'neon_cyber' ? '#38bdf8' : '#facc15'}
                    badgeText={props.strikeWord ? undefined : (props.gridExplosion?.badgeText || 'EÅSÄ°Z BÄ°YOLOJÄ°K MÃœHÃœR')}
                  />
                </Sequence>
              ) : layout === 'pip_split' ? (
                <Sequence from={0} durationInFrames={props.timeline ? 180 : durationInFrames}>
                  <PipSplitView
                    illustrationUrl={props.illustrationUrl || 'illustrations/test_sample.jpg'}
                    illustrationCaption={props.illustrationCaption}
                    illustrationStyle={props.illustrationStyle || 'polaroid'}
                    pipData={props.pipData}
                    cards={props.cards}
                    quoteSpotlight={props.quoteSpotlight}
                    metricImpact={props.metricImpact}
                    isDarkTheme={isDarkMotion}
                    isRTL={isRTL}
                  />
                </Sequence>
              ) : layout === 'tri_concept' ? (
                <Sequence from={0} durationInFrames={props.timeline ? 180 : durationInFrames}>
                  <TriConceptView data={props.triConcept} theme={activeTheme} />
                </Sequence>
              ) : layout === 'vs_split' && props.vsData ? (
                <Sequence from={0} durationInFrames={props.timeline ? 180 : durationInFrames}>
                  <VsSplitView vsData={props.vsData} theme={activeTheme} startFrame={15} />
                </Sequence>
              ) : layout === 'flowchart' && props.flowchartSteps ? (
                <Sequence from={0} durationInFrames={props.timeline ? 180 : durationInFrames}>
                  <FlowchartView steps={props.flowchartSteps} theme={activeTheme} startFrame={15} />
                </Sequence>
              ) : layout === 'quote_spotlight' && props.quoteSpotlight ? (
                <Sequence from={0} durationInFrames={props.timeline ? 180 : durationInFrames}>
                  <QuoteSpotlightView quoteSpotlight={props.quoteSpotlight} theme={activeTheme} startFrame={15} />
                </Sequence>
              ) : layout === 'metric_impact' && props.metricImpact ? (
                <Sequence from={0} durationInFrames={props.timeline ? 180 : durationInFrames}>
                  <MetricImpactView metricImpact={props.metricImpact} theme={activeTheme} startFrame={15} />
                </Sequence>
              ) : (
                <Sequence from={0} durationInFrames={props.timeline ? Math.floor(durationInFrames / 2) : durationInFrames}>
                  <CardGrid cards={props.cards || []} startFrame={15} theme={activeTheme} />
                </Sequence>
              )}

              {/* Scene 2: Timeline View (if present) */}
              {props.timeline && (
                <Sequence from={Math.floor(durationInFrames / 2)} durationInFrames={Math.ceil(durationInFrames / 2)}>
                  <TimelineView timeline={props.timeline} startFrame={10} />
                </Sequence>
              )}
            </div>
          </>
        )}

        {/* 4. Subtitles Bar & Social Handle at bottom */}
        <SubtitlesBar
          subtitles={props.subtitles || []}
          socialHandle={props.socialHandle || '@birkissa'}
          theme={activeTheme}
          isRTL={isRTL}
        />

        {/* 4.5. Floating PIP Video Katmanı & PNG Sticker / Watermark Katmanı */}
        <PipVideoOverlay pipVideos={allPipVideos} />
        <PngOverlayLayer overlayImages={allOverlayImages} />
      </div>

      {/* 4.8. Debunk / Reaction Quote Video Frame (Full-Screen Studio Stage Overlay) */}
      <QuoteVideoFrame quoteVideos={allQuoteVideos} />

      {/* 5. Cinematic Light Leaks (Faz 6) */}
      <LightLeaksOverlay
        type={props.lightLeaks || 'auto'}
        theme={activeTheme}
      />

      {/* 6. Analog 35mm Film Grain Layer (Faz 6) */}
      <FilmGrainOverlay
        mode={props.filmGrain || 'subtle'}
      />
    </CameraMotion>

      {/* ================= AUDIO & ASMR SFX LAYERS ================= */}
      {/* 0. Multi-Scene Page Turn Rustle SFX on each scene transition */}
      {props.scenes && props.scenes.length > 1 &&
        props.scenes.slice(1).map((s, idx) => {
          const sFrame = Math.max(0, Math.floor(s.startTime * 30) - 2);
          return (
            <Sequence key={`sfx_${s.id || idx}`} from={sFrame} durationInFrames={25}>
              <Audio src={staticFile('sfx/page_turn.wav')} volume={0.65} />
            </Sequence>
          );
        })}

      {/* 1. Primary Spoken Voiceover (With smart auto-ducking and AI Kurgu start offset sync) */}
      {props.audioUrl && !props.audioMuted && (() => {
        const isAudibleQuoteActive = allQuoteVideos.some((qv) => {
          if (qv.muted) return false;
          const startSec = qv.timelineStart ?? 0;
          const dur = qv.duration || Math.max(1, (qv.trimEnd || 6) - (qv.trimStart || 0));
          return currentTimeSec >= startSec && currentTimeSec <= (startSec + dur);
        });
        const effectiveVol = isAudibleQuoteActive ? 0.0 : (props.audioVolume ?? 1.0);
        const firstSceneStart = (props.scenes && props.scenes.length > 0) ? (props.scenes[0].startTime || 0) : 0;
        const audioOffsetSec = props.aiKurguStartOffset ?? firstSceneStart;

        // If video is currently before the AI kurgu start, do not play voiceover yet
        if (currentTimeSec < audioOffsetSec) return null;

        return (
          <Sequence from={Math.floor(audioOffsetSec * 30)}>
            <Audio
              src={
                props.audioUrl.startsWith('http://') || props.audioUrl.startsWith('https://')
                  ? props.audioUrl
                  : staticFile(props.audioUrl.replace(/^\/?(public\/)?/, ''))
              }
              volume={effectiveVol}
            />
          </Sequence>
        );
      })()}

      {/* 1.5 Additional Audio Tracks (Extracted / Multi-track) */}
      {props.audioTracks && props.audioTracks.map((trk) => {
        if (trk.muted) return null;
        const fromFrame = Math.round((trk.startTime || 0) * fps);
        const durFrame = Math.max(1, Math.round(((trk.endTime || (durationInFrames / fps)) - (trk.startTime || 0)) * fps));
        return (
          <Sequence key={trk.id} from={fromFrame} durationInFrames={durFrame}>
            <Audio
              src={
                trk.audioUrl.startsWith('http://') || trk.audioUrl.startsWith('https://')
                  ? trk.audioUrl
                  : staticFile(trk.audioUrl.replace(/^\/?(public\/)?/, ''))
              }
              volume={trk.volume ?? 1.0}
            />
          </Sequence>
        );
      })}

      {/* 2. Background Ambient Music Bed with Smart Auto-Ducking 2.0 (Faz 7) */}
      <Audio
        src={staticFile(
          props.musicTrack
            ? (props.musicTrack.startsWith('sfx/') ? props.musicTrack : `sfx/${props.musicTrack}`)
            : 'sfx/ambient_music.wav'
        )}
        loop
        volume={(f) => {
          const time = f / fps;

          // 1. First 0.6s smooth intro fade-in
          if (f < 20) {
            return interpolate(f, [0, 20], [0, 0.08]);
          }

          // 2. Final 2.5s outro swell (Faz 7: swells to 48% for strong closing impact)
          const outroStartFrame = durationInFrames - 75;
          if (f > outroStartFrame) {
            return interpolate(f, [outroStartFrame, durationInFrames - 5], [0.10, 0.48], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            });
          }

          // 3. Dynamic Speech Detection & Adaptive Ducking
          let isSpeaking = false;
          let minDist = 999;
          for (const interval of speechIntervals) {
            if (time >= interval.start && time <= interval.end) {
              isSpeaking = true;
              minDist = 0;
              break;
            }
            const d = Math.min(Math.abs(time - interval.start), Math.abs(time - interval.end));
            if (d < minDist) {
              minDist = d;
            }
          }

          if (isSpeaking) {
            // Active speech: duck down to 8% so voiceover is crisp & broadcast-grade
            return 0.08;
          }

          // Gap / pause between sentences (> 0.5s): swell smoothly up to 26%
          if (minDist > 0.15) {
            const swellFactor = Math.min(1.0, (minDist - 0.15) / 0.35);
            return 0.08 + (0.26 - 0.08) * swellFactor;
          }

          return 0.09;
        }}
      />

      {/* 3. Pen Drawing Circle Scratch SFX (frame 15) */}
      <Sequence from={15} durationInFrames={30}>
        <Audio src={staticFile('sfx/pen_draw.wav')} volume={0.7} />
      </Sequence>

      {/* 4. Marker Highlighter Squeak SFX (frame 25) */}
      <Sequence from={25} durationInFrames={28}>
        <Audio src={staticFile('sfx/marker_sweep.wav')} volume={0.65} />
      </Sequence>

      {/* 5. Card Pop SFX (staggered) */}
      <Sequence from={15} durationInFrames={10}>
        <Audio src={staticFile('sfx/pop.wav')} volume={0.35} />
      </Sequence>
      <Sequence from={23} durationInFrames={10}>
        <Audio src={staticFile('sfx/pop.wav')} volume={0.35} />
      </Sequence>
      <Sequence from={31} durationInFrames={10}>
        <Audio src={staticFile('sfx/pop.wav')} volume={0.35} />
      </Sequence>

      {/* 6. Page Turn Rustle SFX on Scene Change (frame 180) */}
      {props.timeline && (
        <Sequence from={178} durationInFrames={25}>
          <Audio src={staticFile('sfx/page_turn.wav')} volume={0.75} />
        </Sequence>
      )}
    </div>
  );
};
