import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';

export type LightLeakType = 'none' | 'golden_hour' | 'cyan_dream' | 'anamorphic' | 'auto';

interface LightLeaksOverlayProps {
  type?: LightLeakType;
  theme?: string;
  intensity?: number;
}

export const LightLeaksOverlay: React.FC<LightLeaksOverlayProps> = ({
  type = 'auto',
  theme = 'notebook',
  intensity = 0.5,
}) => {
  const frame = useCurrentFrame();

  let effectiveType = type;
  if (effectiveType === 'auto') {
    if (theme === 'neon_cyber' || theme === 'blueprint') {
      effectiveType = 'cyan_dream';
    } else if (theme === 'gold_luxury' || theme === 'dark_minimalist' || theme === 'parchment' || theme === 'kraft') {
      effectiveType = 'golden_hour';
    } else {
      effectiveType = 'golden_hour';
    }
  }

  if (effectiveType === 'none') return null;

  // Gentle procedural breathing cycle (6-8 seconds period)
  const breath = interpolate(
    Math.sin((frame / 30) * 0.8),
    [-1, 1],
    [0.75, 1.25]
  );

  const driftX = interpolate(
    Math.sin((frame / 30) * 0.4),
    [-1, 1],
    [-25, 25]
  );

  const driftY = interpolate(
    Math.cos((frame / 30) * 0.5),
    [-1, 1],
    [-20, 20]
  );

  const isGolden = effectiveType === 'golden_hour';
  const isCyan = effectiveType === 'cyan_dream';
  const isAnamorphic = effectiveType === 'anamorphic';

  const leakColor1 = isGolden
    ? 'rgba(251, 191, 36, 0.45)'
    : isCyan
    ? 'rgba(56, 189, 248, 0.45)'
    : 'rgba(168, 85, 247, 0.45)';

  const leakColor2 = isGolden
    ? 'rgba(245, 158, 11, 0.25)'
    : isCyan
    ? 'rgba(6, 182, 212, 0.25)'
    : 'rgba(59, 130, 246, 0.25)';

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
        zIndex: 35,
        overflow: 'hidden',
        mixBlendMode: 'screen',
        opacity: intensity,
      }}
    >
      {/* Leak 1: Top-Right Radial Glow */}
      <div
        style={{
          position: 'absolute',
          top: -120 + driftY,
          right: -120 + driftX,
          width: 650 * breath,
          height: 650 * breath,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${leakColor1} 0%, ${leakColor2} 45%, transparent 70%)`,
          filter: 'blur(55px)',
          transform: `scale(${breath})`,
        }}
      />

      {/* Leak 2: Bottom-Left Subtle Fill */}
      <div
        style={{
          position: 'absolute',
          bottom: -150 - driftY,
          left: -150 - driftX,
          width: 550 * breath,
          height: 550 * breath,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${leakColor2} 0%, transparent 65%)`,
          filter: 'blur(65px)',
        }}
      />

      {/* Leak 3 (Anamorphic Streak flare across middle if selected) */}
      {isAnamorphic && (
        <div
          style={{
            position: 'absolute',
            top: '35%',
            left: '-20%',
            width: '140%',
            height: 120,
            background: `linear-gradient(90deg, transparent 0%, rgba(56, 189, 248, 0.3) 50%, transparent 100%)`,
            filter: 'blur(20px)',
            transform: `rotate(-4deg) translateY(${driftY * 0.5}px)`,
          }}
        />
      )}
    </div>
  );
};
