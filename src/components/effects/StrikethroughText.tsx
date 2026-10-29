import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface StrikethroughTextProps {
  prefixText?: string;
  strikeText: string;
  suffixText?: string;
  startFrame?: number;
  strikeDuration?: number;
  textColor?: string;
  strikeColor?: string;
  fontSize?: number;
  theme?: string;
}

export const StrikethroughText: React.FC<StrikethroughTextProps> = ({
  prefixText = 'SIRADAN BİR FİİL DEĞİL',
  strikeText = '"YARATMAK"',
  suffixText = '',
  startFrame = 25,
  strikeDuration = 20,
  textColor = '#ffffff',
  strikeColor = '#ef4444',
  fontSize = 68,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const scale = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8 },
  });

  // Animated strike line width progress (0% to 105%)
  const strikeProgress = interpolate(
    frame,
    [startFrame, startFrame + strikeDuration],
    [0, 105],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        transform: `scale(${scale})`,
        margin: '12px 0 8px 0',
      }}
    >
      {Boolean(prefixText) && (
        <div
          style={{
            fontSize: fontSize * 0.45,
            fontWeight: 800,
            color: '#fbbf24',
            letterSpacing: 2,
            textTransform: 'uppercase',
            marginBottom: 6,
          }}
        >
          {prefixText}
        </div>
      )}

      {/* Word to be crossed out */}
      <div
        style={{
          position: 'relative',
          display: 'inline-block',
          padding: '4px 16px',
        }}
      >
        <span
          style={{
            fontSize,
            fontWeight: 900,
            color: strikeProgress >= 80 ? 'rgba(255, 255, 255, 0.45)' : textColor,
            letterSpacing: 3,
            transition: 'color 0.2s ease',
          }}
        >
          {strikeText}
        </span>

        {/* The Animated Red Strike Line */}
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: '52%',
            height: 7,
            width: `${strikeProgress}%`,
            backgroundColor: strikeColor,
            borderRadius: 4,
            transform: 'translateY(-50%) rotate(-1.5deg)',
            boxShadow: `0 0 16px ${strikeColor}`,
          }}
        />
      </div>

      {suffixText && (
        <div
          style={{
            fontSize: fontSize * 0.5,
            fontWeight: 700,
            color: '#94a3b8',
            marginTop: 8,
          }}
        >
          {suffixText}
        </div>
      )}
    </div>
  );
};
