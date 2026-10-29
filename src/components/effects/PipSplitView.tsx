import React from 'react';
import { interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { CardItem, QuoteSpotlightData, MetricImpactData } from '../../types';
import { PolaroidCard } from './PolaroidCard';
import { TornPaperImage } from './TornPaperImage';

export interface PipSplitViewProps {
  illustrationUrl?: string;
  illustrationCaption?: string;
  illustrationStyle?: 'polaroid' | 'torn_paper' | 'clean_frame' | 'none';
  pipData?: { title?: string; subtitle?: string; caption?: string; badge?: string };
  cards?: CardItem[];
  quoteSpotlight?: QuoteSpotlightData;
  metricImpact?: MetricImpactData;
  isDarkTheme?: boolean;
  isRTL?: boolean;
}

export const PipSplitView: React.FC<PipSplitViewProps> = ({
  illustrationUrl = 'illustrations/test_sample.jpg',
  illustrationCaption,
  illustrationStyle = 'polaroid',
  pipData,
  cards,
  quoteSpotlight,
  metricImpact,
  isDarkTheme = false,
  isRTL = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Bottom content entrance
  const bottomEntrance = spring({
    frame: frame - 15,
    fps,
    config: { damping: 14, stiffness: 85 }
  });
  const bottomY = interpolate(bottomEntrance, [0, 1], [60, 0]);
  const bottomOpacity = interpolate(frame, [15, 28], [0, 1], { extrapolateRight: 'clamp' });

  const captionText = illustrationCaption || pipData?.caption || pipData?.subtitle || 'Gözlem & Hakikat';

  return (
    <div
      style={{
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'flex-start',
        paddingTop: 8,
        paddingBottom: 24,
        boxSizing: 'border-box',
        gap: 18,
        direction: isRTL ? 'rtl' : 'ltr',
      }}
    >
      {/* 1. TOP PIP VISUAL WINDOW (Polaroid or Torn Paper) */}
      <div
        style={{
          position: 'relative',
          zIndex: 10,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {pipData?.badge && (
          <div
            style={{
              marginBottom: 10,
              padding: '6px 20px',
              borderRadius: 9999,
              backgroundColor: '#facc15',
              color: '#020617',
              fontSize: 16,
              fontWeight: 900,
              letterSpacing: 2,
              textTransform: 'uppercase',
              boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
            }}
          >
            {pipData.badge}
          </div>
        )}

        {illustrationStyle === 'torn_paper' ? (
          <TornPaperImage
            imageSrc={illustrationUrl}
            caption={captionText}
            width={520}
            rotation={1.2}
            isRTL={isRTL}
          />
        ) : (
          <PolaroidCard
            imageSrc={illustrationUrl}
            caption={captionText}
            width={480}
            rotation={-2}
            isRTL={isRTL}
          />
        )}
      </div>

      {/* 2. BOTTOM NOTEBOOK EXPLAINER AREA */}
      <div
        style={{
          width: '100%',
          maxWidth: 720,
          transform: `translateY(${bottomY}px)`,
          opacity: bottomOpacity,
          zIndex: 10,
          boxSizing: 'border-box',
          padding: '0 16px',
        }}
      >
        {/* Scenario A: Metric Impact inside PiP */}
        {metricImpact ? (
          <div
            style={{
              padding: '18px 28px',
              borderRadius: 20,
              border: isDarkTheme
                ? '1px solid rgba(56, 189, 248, 0.3)'
                : '2px dashed rgba(168, 162, 158, 0.7)',
              backgroundColor: isDarkTheme
                ? 'rgba(11, 18, 32, 0.92)'
                : 'rgba(255, 255, 255, 0.92)',
              textAlign: 'center',
              boxShadow: '0 12px 28px rgba(0, 0, 0, 0.15)',
              backdropFilter: 'blur(8px)',
            }}
          >
            <div
              style={{
                fontSize: 54,
                fontWeight: 900,
                color: '#facc15',
                lineHeight: 1.1,
                fontFamily: isDarkTheme ? 'inherit' : '"Caveat", "Kalam", cursive',
              }}
            >
              {metricImpact.bigNumber}
            </div>
            <div
              style={{
                fontSize: 22,
                fontWeight: 800,
                textTransform: 'uppercase',
                letterSpacing: 2,
                marginTop: 4,
                color: isDarkTheme ? '#38bdf8' : '#1e3a8a',
              }}
            >
              {metricImpact.bigLabel}
            </div>
            <div
              style={{
                fontSize: 20,
                color: isDarkTheme ? '#cbd5e1' : '#44403c',
                marginTop: 6,
                lineHeight: 1.3,
                fontFamily: isDarkTheme ? 'inherit' : '"Kalam", cursive',
              }}
            >
              {metricImpact.keyTakeaway || metricImpact.subheading}
            </div>
          </div>
        ) : quoteSpotlight ? (
          /* Scenario B: Quote Spotlight inside PiP */
          <div
            style={{
              padding: '18px 28px',
              borderRadius: 20,
              border: isDarkTheme
                ? '1px solid rgba(250, 204, 21, 0.4)'
                : '2px solid rgba(217, 119, 6, 0.4)',
              backgroundColor: isDarkTheme
                ? 'rgba(8, 13, 26, 0.94)'
                : 'rgba(254, 243, 199, 0.94)',
              fontStyle: 'italic',
              textAlign: 'center',
              boxShadow: '0 12px 28px rgba(0, 0, 0, 0.15)',
            }}
          >
            <div
              style={{
                fontSize: 18,
                textTransform: 'uppercase',
                fontWeight: 800,
                letterSpacing: 2,
                color: '#d97706',
                marginBottom: 6,
              }}
            >
              — {quoteSpotlight.speaker || 'Kilit Söz'} —
            </div>
            <div
              style={{
                fontSize: 26,
                fontWeight: 700,
                color: isDarkTheme ? '#fef08a' : '#292524',
                lineHeight: 1.3,
                fontFamily: isDarkTheme ? 'inherit' : '"Caveat", "Kalam", cursive',
              }}
            >
              "{quoteSpotlight.quoteText}"
            </div>
          </div>
        ) : cards && cards.length > 0 ? (
          /* Scenario C: Explainer Cards inside PiP (compact) */
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {cards.slice(0, 2).map((c, idx) => (
              <div
                key={c.id || idx}
                style={{
                  padding: '14px 20px',
                  borderRadius: 16,
                  border: isDarkTheme
                    ? '1px solid rgba(51, 65, 85, 0.8)'
                    : '1px solid rgba(214, 211, 209, 0.8)',
                  backgroundColor: isDarkTheme
                    ? 'rgba(7, 11, 20, 0.92)'
                    : 'rgba(255, 255, 255, 0.94)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  boxShadow: '0 8px 18px rgba(0, 0, 0, 0.08)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: 10,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 800,
                      fontSize: 20,
                      backgroundColor: `${c.color || '#3b82f6'}25`,
                      color: c.color || '#3b82f6',
                    }}
                  >
                    {idx + 1}
                  </div>
                  <div>
                    <div
                      style={{
                        fontSize: 22,
                        fontWeight: 800,
                        color: isDarkTheme ? '#ffffff' : '#1c1917',
                      }}
                    >
                      {c.label}
                    </div>
                    <div
                      style={{
                        fontSize: 18,
                        color: isDarkTheme ? '#94a3b8' : '#78716c',
                      }}
                    >
                      {c.value}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Default Fallback Explainer Note */
          <div
            style={{
              padding: '16px 24px',
              borderRadius: 16,
              border: isDarkTheme
                ? '1px solid rgba(30, 41, 59, 0.8)'
                : '1px solid rgba(229, 231, 235, 0.8)',
              backgroundColor: isDarkTheme
                ? 'rgba(7, 11, 20, 0.85)'
                : 'rgba(255, 255, 255, 0.88)',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: 24, fontWeight: 800, color: '#facc15' }}>
              {pipData?.title || 'Hakikatin Görsel İfadesi'}
            </div>
            <div
              style={{
                fontSize: 18,
                color: isDarkTheme ? '#94a3b8' : '#57534e',
                marginTop: 4,
              }}
            >
              Her detay, anlatılan büyük fikrin görsel bir parçasını taşır.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
