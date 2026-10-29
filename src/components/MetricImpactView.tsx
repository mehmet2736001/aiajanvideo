import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { MetricImpactData } from '../types';

interface MetricImpactViewProps {
  metricImpact: MetricImpactData;
  theme?: string;
  startFrame?: number;
}

export const MetricImpactView: React.FC<MetricImpactViewProps> = ({
  metricImpact,
  theme = 'notebook',
  startFrame = 10,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const isChalkboard = theme === 'chalkboard';
  const isBlueprint = theme === 'blueprint';
  const isParchment = theme === 'parchment';
  const isKraft = theme === 'kraft';
  const isDarkMotion =
    theme === 'dark_minimalist' ||
    theme === 'neon_cyber' ||
    theme === 'gold_luxury';

  const circleSpring = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 11, mass: 0.8 },
  });

  const bannerSpring = spring({
    frame: frame - (startFrame + 18),
    fps,
    config: { damping: 13, mass: 0.9 },
  });

  const accentColor = metricImpact.accentColor || (theme === 'neon_cyber' ? '#38bdf8' : theme === 'gold_luxury' ? '#facc15' : isChalkboard ? '#f87171' : '#dc2626');
  const textPrimary = isChalkboard || isBlueprint || isDarkMotion ? '#ffffff' : '#0f172a';
  const textMuted = isChalkboard ? '#cbd5e1' : isBlueprint ? '#93c5fd' : isDarkMotion ? '#94a3b8' : '#475569';

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '0 40px',
        width: '100%',
        position: 'relative',
      }}
    >
      {/* Big Hand-drawn Circle with Number */}
      <div
        style={{
          position: 'relative',
          width: 380,
          height: 380,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          transform: `scale(${Math.max(0, circleSpring)})`,
          marginBottom: 30,
        }}
      >
        {/* SVG Handdrawn Double Rings */}
        <svg
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none',
          }}
          viewBox="0 0 400 400"
        >
          {/* Ring 1 */}
          <path
            d="M 200 20 C 310 15, 385 90, 380 200 C 375 310, 305 385, 200 380 C 90 375, 15 305, 20 200 C 25 90, 95 18, 200 20"
            fill="none"
            stroke={accentColor}
            strokeWidth="8"
            strokeLinecap="round"
          />
          {/* Ring 2 (Offset hand-drawn) */}
          <path
            d="M 205 30 C 300 25, 370 100, 365 200 C 360 295, 295 370, 200 365 C 105 360, 30 290, 35 200 C 40 105, 105 28, 205 30"
            fill="none"
            stroke={accentColor}
            strokeWidth="5"
            strokeDasharray="12 8"
            strokeLinecap="round"
          />
        </svg>

        {/* The Big Number */}
        <div
          style={{
            fontSize: 108,
            fontWeight: 900,
            color: accentColor,
            lineHeight: 0.9,
            letterSpacing: -2,
            textShadow: '0 4px 15px rgba(220, 38, 38, 0.25)',
          }}
        >
          {metricImpact.bigNumber || (metricImpact as any).mainMetric || '%100'}
        </div>

        {/* The Label under Number */}
        <div
          style={{
            fontSize: 34,
            fontWeight: 800,
            color: textPrimary,
            marginTop: 8,
            letterSpacing: 2,
            textTransform: 'uppercase',
          }}
        >
          {metricImpact.bigLabel || (metricImpact as any).label || 'ETKİ'}
        </div>
      </div>

      {/* Explanatory Banner Below */}
      <div
        style={{
          width: '100%',
          maxWidth: 820,
          backgroundColor: isDarkMotion
            ? 'rgba(10, 16, 28, 0.95)'
            : isChalkboard
            ? 'rgba(15, 30, 22, 0.9)'
            : isBlueprint
            ? 'rgba(10, 35, 60, 0.9)'
            : '#ffffff',
          border: `3px solid ${isDarkMotion ? (theme === 'neon_cyber' ? '#38bdf8' : '#facc15') : isChalkboard ? '#86efac' : isBlueprint ? '#38bdf8' : '#1e3a8a'}`,
          borderRadius: 24,
          padding: '24px 30px',
          textAlign: 'center',
          boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
          transform: `scale(${Math.max(0, bannerSpring)}) rotate(-0.5deg)`,
        }}
      >
        <div
          style={{
            fontSize: 32,
            fontWeight: 900,
            color: textPrimary,
            marginBottom: 8,
          }}
        >
          {metricImpact.subheading || (metricImpact as any).description || ''}
        </div>
        <div
          style={{
            fontSize: 26,
            fontWeight: 600,
            color: textMuted,
            lineHeight: 1.3,
          }}
        >
          {metricImpact.keyTakeaway || (metricImpact as any).keyTakeaway || ''}
        </div>
      </div>
    </div>
  );
};
