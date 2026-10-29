import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { VsItem } from '../types';

interface VsSplitViewProps {
  vsData: VsItem;
  theme?: string;
  startFrame?: number;
}

export const VsSplitView: React.FC<VsSplitViewProps> = ({
  vsData,
  theme = 'notebook',
  startFrame = 10,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const isChalkboard = theme === 'chalkboard';
  const isBlueprint = theme === 'blueprint';
  const isParchment = theme === 'parchment';
  const isKraft = theme === 'kraft';

  const leftSpring = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 14, mass: 0.9 },
  });

  const rightSpring = spring({
    frame: frame - (startFrame + 12),
    fps,
    config: { damping: 14, mass: 0.9 },
  });

  const vsBadgeSpring = spring({
    frame: frame - (startFrame + 22),
    fps,
    config: { damping: 10, mass: 0.7 },
  });

  const verdictSpring = spring({
    frame: frame - (startFrame + 34),
    fps,
    config: { damping: 12, mass: 0.8 },
  });

  const cardBg = isChalkboard
    ? 'rgba(15, 30, 22, 0.85)'
    : isBlueprint
    ? 'rgba(10, 35, 60, 0.85)'
    : isParchment
    ? 'rgba(255, 248, 235, 0.92)'
    : isKraft
    ? 'rgba(245, 230, 205, 0.92)'
    : 'rgba(255, 255, 255, 0.95)';

  const cardBorder = isChalkboard
    ? '3px solid rgba(255, 255, 255, 0.3)'
    : isBlueprint
    ? '3px solid #38bdf8'
    : isParchment
    ? '3px solid #78350f'
    : isKraft
    ? '3px solid #78350f'
    : '3px solid #1e3a8a';

  const textPrimary = isChalkboard || isBlueprint ? '#ffffff' : '#0f172a';
  const textMuted = isChalkboard ? '#cbd5e1' : isBlueprint ? '#93c5fd' : '#475569';

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
      {/* Cards Container */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'stretch',
          width: '100%',
          gap: 30,
          position: 'relative',
        }}
      >
        {/* Left Side: Side A */}
        <div
          style={{
            flex: 1,
            backgroundColor: cardBg,
            border: cardBorder,
            borderRadius: 28,
            padding: '28px 24px',
            boxShadow: '0 12px 30px rgba(0,0,0,0.1)',
            transform: `scale(${Math.max(0, leftSpring)}) rotate(-1.5deg)`,
            transformOrigin: 'bottom center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
          }}
        >
          {/* Badge */}
          <div
            style={{
              backgroundColor: vsData.leftColor || '#dc2626',
              color: '#ffffff',
              padding: '6px 20px',
              borderRadius: 20,
              fontSize: 26,
              fontWeight: 800,
              marginBottom: 14,
            }}
          >
            {vsData.leftTitle}
          </div>
          <div
            style={{
              fontSize: 34,
              fontWeight: 900,
              color: textPrimary,
              marginBottom: 16,
              lineHeight: 1.2,
            }}
          >
            {vsData.leftSubtitle}
          </div>
          <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 10, marginTop: 'auto' }}>
            {vsData.leftPoints?.map((pt, i) => (
              <div
                key={i}
                style={{
                  fontSize: 26,
                  fontWeight: 600,
                  color: textMuted,
                  backgroundColor: 'rgba(0,0,0,0.03)',
                  padding: '8px 12px',
                  borderRadius: 14,
                }}
              >
                • {pt}
              </div>
            ))}
          </div>
        </div>

        {/* Center: Animated VS Badge */}
        <div
          style={{
            position: 'absolute',
            left: '50%',
            top: '40%',
            transform: `translate(-50%, -50%) scale(${Math.max(0, vsBadgeSpring)}) rotate(8deg)`,
            zIndex: 10,
            width: 90,
            height: 90,
            borderRadius: '50%',
            backgroundColor: '#f59e0b',
            border: '5px solid #ffffff',
            boxShadow: '0 8px 25px rgba(245, 158, 11, 0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
            fontWeight: 900,
            fontSize: 36,
            letterSpacing: 1,
          }}
        >
          VS
        </div>

        {/* Right Side: Side B */}
        <div
          style={{
            flex: 1,
            backgroundColor: cardBg,
            border: cardBorder,
            borderRadius: 28,
            padding: '28px 24px',
            boxShadow: '0 12px 30px rgba(0,0,0,0.1)',
            transform: `scale(${Math.max(0, rightSpring)}) rotate(1.5deg)`,
            transformOrigin: 'bottom center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
          }}
        >
          {/* Badge */}
          <div
            style={{
              backgroundColor: vsData.rightColor || '#16a34a',
              color: '#ffffff',
              padding: '6px 20px',
              borderRadius: 20,
              fontSize: 26,
              fontWeight: 800,
              marginBottom: 14,
            }}
          >
            {vsData.rightTitle}
          </div>
          <div
            style={{
              fontSize: 34,
              fontWeight: 900,
              color: textPrimary,
              marginBottom: 16,
              lineHeight: 1.2,
            }}
          >
            {vsData.rightSubtitle}
          </div>
          <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 10, marginTop: 'auto' }}>
            {vsData.rightPoints?.map((pt, i) => (
              <div
                key={i}
                style={{
                  fontSize: 26,
                  fontWeight: 600,
                  color: textMuted,
                  backgroundColor: 'rgba(0,0,0,0.03)',
                  padding: '8px 12px',
                  borderRadius: 14,
                }}
              >
                ✓ {pt}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Verdict Banner */}
      {vsData.verdict && (
        <div
          style={{
            marginTop: 35,
            width: '90%',
            backgroundColor: isChalkboard ? '#15803d' : '#fef08a',
            border: '3px dashed #b45309',
            borderRadius: 20,
            padding: '16px 24px',
            textAlign: 'center',
            fontSize: 30,
            fontWeight: 800,
            color: isChalkboard ? '#ffffff' : '#78350f',
            boxShadow: '0 6px 18px rgba(0,0,0,0.08)',
            transform: `scale(${Math.max(0, verdictSpring)}) rotate(-0.5deg)`,
          }}
        >
          💡 {vsData.verdict}
        </div>
      )}
    </div>
  );
};
