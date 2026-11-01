import React from 'react';
import { interpolate, useCurrentFrame, useVideoConfig } from 'remotion';
import { VideoScene } from '../types';
import { CardGrid } from './CardGrid';
import { FlowchartView } from './FlowchartView';
import { HanddrawnDoodle } from './HanddrawnDoodle';
import { HanddrawnHeader } from './HanddrawnHeader';
import { MetricImpactView } from './MetricImpactView';
import { QuoteSpotlightView } from './QuoteSpotlightView';
import { TimelineView } from './TimelineView';
import { VsSplitView } from './VsSplitView';
import { IconGridExplosion } from './effects/IconGridExplosion';
import { StrikethroughText } from './effects/StrikethroughText';
import { TriConceptView } from './effects/TriConceptView';
import { HanddrawnAccents } from './effects/HanddrawnAccents';
import { PipSplitView } from './effects/PipSplitView';

interface SceneBlockProps {
  scene: VideoScene;
  theme: string;
  isDarkMotion: boolean;
  sceneIndex: number;
  totalScenes: number;
  isRTL?: boolean;
}

export const SceneBlock: React.FC<SceneBlockProps> = ({
  scene,
  theme,
  isDarkMotion,
  sceneIndex,
  totalScenes,
  isRTL = false,
}) => {
  const activeRTL = isRTL || scene.isRTL || scene.direction === 'rtl' || scene.language === 'ar';
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Smooth entrance transition from previous scene (frame 0-12)
  const sceneOpacity = interpolate(frame, [0, 9], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const sceneTranslateY = interpolate(frame, [0, 12], [24, 0], {
    extrapolateRight: 'clamp',
  });
  const sceneScale = interpolate(frame, [0, 12], [0.98, 1.0], {
    extrapolateRight: 'clamp',
  });

  const layout = scene.layoutType || 'cards';
  const title1 = scene.headerLine1 || '';
  const title2 = scene.headerLine2 || '';

  const isQuoteLayout = layout === 'quote_spotlight';
  const isCinematicAmbient = layout === 'cinematic_ambient';

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        opacity: sceneOpacity,
        transform: `translateY(${sceneTranslateY}px) scale(${sceneScale})`,
        transformOrigin: 'top center',
        zIndex: 2,
        direction: activeRTL ? 'rtl' : 'ltr',
      }}
    >
      {/* Top Spacer */}
      <div style={{ height: theme === 'chalkboard' ? 30 : isQuoteLayout ? 35 : 55 }} />

      {/* Chapter indicator badge if multi-scene */}
      {totalScenes > 1 && (
        <div
          style={{
            position: 'absolute',
            top: theme === 'chalkboard' ? 32 : isQuoteLayout ? 36 : 56,
            left: activeRTL ? undefined : 54,
            right: activeRTL ? 54 : undefined,
            zIndex: 15,
            fontSize: 16,
            fontWeight: 800,
            letterSpacing: '1.5px',
            textTransform: 'uppercase',
            color: isDarkMotion ? '#38bdf8' : '#1e3a8a',
            opacity: 0.85,
          }}
        >
          {sceneIndex + 1} / {totalScenes} • BÖLÜM
        </div>
      )}

      {/* 1. SCENE HEADER (SADE, FERAH & DİNAMİK) */}
      {isQuoteLayout ? (
        /* Minimalist floating category pill for Quote Spotlight */
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: 15, marginBottom: 20 }}>
          <div
            style={{
              padding: '8px 28px',
              borderRadius: 9999,
              backgroundColor: isDarkMotion ? 'rgba(245, 158, 11, 0.16)' : 'rgba(30, 58, 138, 0.1)',
              border: `1.5px solid ${isDarkMotion ? 'rgba(245, 158, 11, 0.45)' : 'rgba(30, 58, 138, 0.3)'}`,
              color: isDarkMotion ? '#facc15' : '#1e3a8a',
              fontSize: 22,
              fontWeight: 800,
              letterSpacing: '2.5px',
              textTransform: 'uppercase',
              backdropFilter: 'blur(12px)',
              boxShadow: '0 4px 20px rgba(0,0,0,0.35)',
            }}
          >
            {scene.headerSubtitle || 'HİKMET VE MANEVİYAT'}
          </div>
        </div>
      ) : isCinematicAmbient ? (
        /* Cinematic ambient layout - Breathing room, no heavy banners */
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            flex: 1,
            padding: '0 60px',
            textAlign: 'center',
            marginTop: 60,
          }}
        >
          {scene.headerSubtitle && (
            <div
              style={{
                padding: '6px 22px',
                borderRadius: 9999,
                backgroundColor: 'rgba(245, 158, 11, 0.18)',
                border: '1px solid rgba(245, 158, 11, 0.45)',
                color: '#facc15',
                fontSize: 22,
                fontWeight: 800,
                letterSpacing: '2.5px',
                textTransform: 'uppercase',
                marginBottom: 24,
                backdropFilter: 'blur(10px)',
              }}
            >
              {scene.headerSubtitle}
            </div>
          )}
          <div
            style={{
              fontSize: 58,
              fontWeight: 900,
              color: '#ffffff',
              lineHeight: 1.25,
              textShadow: '0 4px 30px rgba(0,0,0,0.9), 0 0 35px rgba(245, 158, 11, 0.3)',
              maxWidth: 860,
            }}
          >
            {title1 || scene.headerSubtitle || ''}
          </div>
          {scene.highlightedText && (
            <div
              style={{
                marginTop: 28,
                padding: '10px 30px',
                borderRadius: 20,
                backgroundColor: 'rgba(245, 158, 11, 0.22)',
                border: '1.5px solid rgba(245, 158, 11, 0.55)',
                color: '#fef08a',
                fontSize: 30,
                fontWeight: 800,
                boxShadow: '0 8px 30px rgba(245, 158, 11, 0.35)',
              }}
            >
              {scene.highlightedText}
            </div>
          )}
        </div>
      ) : isDarkMotion ? (
        /* Clean minimalist header for dark themes (no 5 stacked banners!) */
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
            marginTop: 10,
            marginBottom: 16,
            padding: '0 40px',
          }}
        >
          {scene.headerSubtitle && (
            <div
              style={{
                fontSize: 19,
                fontWeight: 800,
                letterSpacing: '2px',
                textTransform: 'uppercase',
                color: '#facc15',
                marginBottom: 6,
              }}
            >
              {scene.headerSubtitle}
            </div>
          )}
          {title1 && (
            <div
              style={{
                fontSize: 44,
                fontWeight: 900,
                color: '#ffffff',
                lineHeight: 1.15,
                textShadow: '0 4px 20px rgba(0,0,0,0.7)',
              }}
            >
              {title1} {title2 ? <span style={{ color: '#93c5fd' }}>{title2}</span> : null}
            </div>
          )}
          {scene.highlightedText && (
            <div
              style={{
                marginTop: 8,
                display: 'inline-block',
                padding: '4px 16px',
                borderRadius: 10,
                backgroundColor: 'rgba(245, 158, 11, 0.2)',
                border: '1px solid rgba(245, 158, 11, 0.4)',
                color: '#fef08a',
                fontSize: 20,
                fontWeight: 800,
              }}
            >
              {scene.highlightedText}
            </div>
          )}
        </div>
      ) : (
        /* Classic Handdrawn Header for Notebook / Kraft / Blueprint themes */
        <>
          <HanddrawnHeader
            subtitle={scene.headerSubtitle || (totalScenes > 1 ? `Bölüm ${sceneIndex + 1}` : 'Kısa Kıssa')}
            title1={title1 || 'NEDEN'}
            title2={title2}
            circledWord={scene.circledWord || ''}
            highlightedText={scene.highlightedText || ''}
            theme={theme as any}
            isRTL={activeRTL}
          />
          {!isDarkMotion && scene.doodleType && scene.doodleType !== 'none' && (
            <div
              style={{
                position: 'absolute',
                top: theme === 'chalkboard' ? 35 : 65,
                right: activeRTL ? undefined : 48,
                left: activeRTL ? 48 : undefined,
                zIndex: 12,
                pointerEvents: 'none',
              }}
            >
              <HanddrawnDoodle
                type={scene.doodleType as any}
                size={135}
                theme={theme}
                startFrame={10}
                durationInFrames={35}
              />
            </div>
          )}
        </>
      )}

      {/* Optional Animated Strikethrough (only for non-quote layouts) */}
      {!isQuoteLayout && !isCinematicAmbient && scene.strikeWord && (
        <StrikethroughText
          strikeText={scene.strikeWord}
          prefixText=""
          strikeColor="#ef4444"
        />
      )}

      {/* 2. Scene Middle Dynamic Layout */}
      {!isCinematicAmbient && (
        <div style={{ position: 'relative', width: '100%', minHeight: isQuoteLayout ? 540 : 600, marginTop: scene.strikeWord ? 0 : 10 }}>
          {layout === 'grid_explosion' ? (
            <IconGridExplosion
              title={scene.gridExplosion?.title || (title1 + ' ' + (scene.circledWord || '') + ' ' + (scene.highlightedText || ''))}
              subtitle={scene.gridExplosion?.subtitle || 'Benzersiz Mühür'}
              iconType={scene.gridExplosion?.iconType || 'fingerprint'}
              itemCount={scene.gridExplosion?.itemCount || 12}
              accentColor={theme === 'neon_cyber' ? '#38bdf8' : '#facc15'}
              badgeText={scene.strikeWord ? undefined : (scene.gridExplosion?.badgeText || 'EŞSİZ BİYOLOJİK MÜHÜR')}
            />
          ) : layout === 'pip_split' ? (
            <PipSplitView
              illustrationUrl={scene.illustrationUrl || 'illustrations/test_sample.jpg'}
              illustrationCaption={scene.illustrationCaption}
              illustrationStyle={scene.illustrationStyle || 'polaroid'}
              pipData={scene.pipData}
              cards={scene.cards}
              quoteSpotlight={scene.quoteSpotlight}
              metricImpact={scene.metricImpact}
              isDarkTheme={isDarkMotion}
              isRTL={activeRTL}
            />
          ) : layout === 'tri_concept' ? (
            <TriConceptView data={scene.triConcept} theme={theme} />
          ) : layout === 'vs_split' && scene.vsData ? (
            <VsSplitView vsData={scene.vsData} theme={theme} startFrame={10} />
          ) : layout === 'flowchart' && scene.flowchartSteps ? (
            <FlowchartView steps={scene.flowchartSteps} theme={theme} startFrame={10} />
          ) : layout === 'quote_spotlight' ? (
            <QuoteSpotlightView quoteSpotlight={scene.quoteSpotlight || { speaker: 'HİKMET', quoteText: scene.narration || '' }} theme={theme} startFrame={10} />
          ) : layout === 'metric_impact' && scene.metricImpact ? (
            <MetricImpactView metricImpact={scene.metricImpact} theme={theme} startFrame={10} />
          ) : layout === 'timeline' && scene.timeline ? (
            <TimelineView timeline={scene.timeline} startFrame={10} />
          ) : (
            <CardGrid cards={scene.cards || []} startFrame={10} theme={theme} />
          )}

          {/* Optional Handdrawn Accent (curved arrow, highlighter, burst, zigzag) */}
          {scene.accentType && scene.accentType !== 'none' && (
            <div
              style={{
                position: 'absolute',
                bottom: 25,
                right: 35,
                zIndex: 20,
                pointerEvents: 'none',
              }}
            >
              <HanddrawnAccents
                type={scene.accentType}
                theme={theme}
                startFrame={14}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};
