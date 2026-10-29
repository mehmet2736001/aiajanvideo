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
import { PolaroidCard } from './effects/PolaroidCard';
import { TornPaperImage } from './effects/TornPaperImage';

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
  const sceneTranslateY = interpolate(frame, [0, 12], [28, 0], {
    extrapolateRight: 'clamp',
  });
  const sceneScale = interpolate(frame, [0, 12], [0.97, 1.0], {
    extrapolateRight: 'clamp',
  });

  const layout = scene.layoutType || 'cards';
  const title1 = scene.headerLine1 || 'NEDEN';
  const title2 = scene.headerLine2 || '';

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
      {/* Top Spacer for spiral wire */}
      <div style={{ height: theme === 'chalkboard' ? 30 : 60 }} />

      {/* Chapter indicator badge if multi-scene */}
      {totalScenes > 1 && (
        <div
          style={{
            position: 'absolute',
            top: theme === 'chalkboard' ? 32 : 62,
            left: activeRTL ? undefined : 54,
            right: activeRTL ? 54 : undefined,
            zIndex: 15,
            fontSize: 18,
            fontWeight: 800,
            letterSpacing: '1px',
            textTransform: 'uppercase',
            color: isDarkMotion ? '#38bdf8' : '#1e3a8a',
            opacity: 0.85,
          }}
        >
          {sceneIndex + 1} / {totalScenes} • BÖLÜM
        </div>
      )}

      {/* 1. Scene Header */}
      <HanddrawnHeader
        subtitle={scene.headerSubtitle || (totalScenes > 1 ? `Bölüm ${sceneIndex + 1}` : 'Kısa Kıssa')}
        title1={title1}
        title2={title2}
        circledWord={scene.circledWord || ''}
        highlightedText={scene.highlightedText || ''}
        theme={theme as any}
        isRTL={activeRTL}
      />

      {/* Optional Doodle sketch (for non-dark themes) */}
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

      {/* Optional Animated Strikethrough */}
      {scene.strikeWord && (
        <StrikethroughText
          strikeText={scene.strikeWord}
          prefixText=""
          strikeColor="#ef4444"
        />
      )}

      {/* 2. Scene Middle Dynamic Layout */}
      <div style={{ position: 'relative', width: '100%', minHeight: 640, marginTop: scene.strikeWord ? 0 : 20 }}>
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
        ) : layout === 'quote_spotlight' && scene.quoteSpotlight ? (
          <QuoteSpotlightView quoteSpotlight={scene.quoteSpotlight} theme={theme} startFrame={10} />
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
    </div>
  );
};
