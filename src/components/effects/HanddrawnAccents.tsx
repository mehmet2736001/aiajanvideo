import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

export type AccentType =
  | 'none'
  | 'curved_arrow'
  | 'highlighter'
  | 'burst'
  | 'double_wave'
  | 'zigzag'
  | 'bracket'
  | 'exclamation';

interface HanddrawnAccentsProps {
  type?: AccentType;
  color?: string;
  theme?: string;
  startFrame?: number;
  width?: number;
  height?: number;
}

export const HanddrawnAccents: React.FC<HanddrawnAccentsProps> = ({
  type = 'curved_arrow',
  color,
  theme = 'notebook',
  startFrame = 15,
  width = 160,
  height = 100,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (type === 'none') return null;

  const isDark =
    theme === 'dark_minimalist' ||
    theme === 'neon_cyber' ||
    theme === 'gold_luxury';

  const defaultColor = color
    ? color
    : theme === 'neon_cyber'
    ? '#38bdf8'
    : theme === 'gold_luxury'
    ? '#facc15'
    : isDark
    ? '#f59e0b'
    : theme === 'blueprint'
    ? '#38bdf8'
    : '#dc2626';

  const animProgress = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 12, mass: 0.8 },
  });

  const strokeDash = interpolate(animProgress, [0, 1], [300, 0]);

  if (type === 'highlighter') {
    const hlColor = isDark ? 'rgba(250, 204, 21, 0.35)' : 'rgba(254, 240, 138, 0.85)';
    return (
      <div
        style={{
          position: 'absolute',
          width: '100%',
          height: 38,
          pointerEvents: 'none',
          zIndex: 1,
          transform: `scaleX(${animProgress})`,
          transformOrigin: 'left center',
        }}
      >
        <svg
          viewBox="0 0 400 40"
          style={{ width: '100%', height: '100%' }}
          preserveAspectRatio="none"
        >
          <path
            d="M 5 22 Q 100 15, 200 24 T 395 20"
            fill="none"
            stroke={hlColor}
            strokeWidth="32"
            strokeLinecap="round"
            opacity={0.8}
          />
        </svg>
      </div>
    );
  }

  if (type === 'curved_arrow') {
    return (
      <div
        style={{
          width,
          height,
          position: 'relative',
          pointerEvents: 'none',
          transform: `scale(${Math.max(0, animProgress)}) rotate(-5deg)`,
          transformOrigin: 'top left',
        }}
      >
        <svg
          viewBox="0 0 120 90"
          style={{ width: '100%', height: '100%', overflow: 'visible' }}
        >
          {/* Main Curved Shaft */}
          <path
            d="M 15 15 Q 60 10, 85 45 T 95 75"
            fill="none"
            stroke={defaultColor}
            strokeWidth="4"
            strokeLinecap="round"
            strokeDasharray="300"
            strokeDashoffset={strokeDash}
          />
          {/* Arrow Head */}
          <path
            d="M 80 65 L 95 78 L 105 60"
            fill="none"
            stroke={defaultColor}
            strokeWidth="4"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ opacity: animProgress > 0.8 ? 1 : 0 }}
          />
        </svg>
      </div>
    );
  }

  if (type === 'burst') {
    return (
      <div
        style={{
          width: 80,
          height: 80,
          position: 'relative',
          pointerEvents: 'none',
          transform: `scale(${Math.max(0, animProgress)}) rotate(${animProgress * 15}deg)`,
          transformOrigin: 'center center',
        }}
      >
        <svg viewBox="0 0 100 100" style={{ width: '100%', height: '100%' }}>
          <path
            d="M 50 5 L 62 35 L 95 38 L 70 60 L 78 92 L 50 74 L 22 92 L 30 60 L 5 38 L 38 35 Z"
            fill="none"
            stroke={defaultColor}
            strokeWidth="3.5"
            strokeLinejoin="round"
            strokeDasharray="300"
            strokeDashoffset={strokeDash}
          />
        </svg>
      </div>
    );
  }

  if (type === 'double_wave' || type === 'zigzag') {
    return (
      <div
        style={{
          width: '100%',
          height: 24,
          position: 'relative',
          pointerEvents: 'none',
          transform: `scaleX(${animProgress})`,
          transformOrigin: 'left center',
        }}
      >
        <svg
          viewBox="0 0 300 20"
          style={{ width: '100%', height: '100%' }}
          preserveAspectRatio="none"
        >
          <path
            d={
              type === 'zigzag'
                ? 'M 5 10 L 25 18 L 45 6 L 65 18 L 85 6 L 105 18 L 125 6 L 145 18 L 165 6 L 185 18 L 205 6 L 225 18 L 245 6 L 265 18 L 285 6 L 295 12'
                : 'M 5 10 Q 35 2, 65 10 T 125 10 T 185 10 T 245 10 T 295 10'
            }
            fill="none"
            stroke={defaultColor}
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeDasharray="300"
            strokeDashoffset={strokeDash}
          />
        </svg>
      </div>
    );
  }

  if (type === 'bracket') {
    return (
      <div
        style={{
          width: 30,
          height: '100%',
          position: 'relative',
          pointerEvents: 'none',
          transform: `scaleY(${animProgress})`,
          transformOrigin: 'center center',
        }}
      >
        <svg viewBox="0 0 30 100" style={{ width: '100%', height: '100%' }}>
          <path
            d="M 25 5 Q 8 10, 8 40 L 4 50 L 8 60 Q 8 90, 25 95"
            fill="none"
            stroke={defaultColor}
            strokeWidth="4"
            strokeLinecap="round"
          />
        </svg>
      </div>
    );
  }

  return null;
};
