import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { PenCursor } from './PenCursor';

interface HeaderProps {
  subtitle?: string;
  title1?: string;
  title2?: string;
  circledWord?: string;
  highlightedText?: string;
  theme?: 'notebook' | 'kraft' | 'chalkboard' | 'parchment' | 'blueprint' | 'dark_minimalist' | 'neon_cyber' | 'gold_luxury';
  isRTL?: boolean;
}

export const HanddrawnHeader: React.FC<HeaderProps> = ({
  subtitle = 'Kısa Kıssa',
  title1 = '',
  title2 = '',
  circledWord = '',
  highlightedText = '',
  theme = 'notebook',
  isRTL = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const isChalkboard = theme === 'chalkboard';
  const isBlueprint = theme === 'blueprint';
  const isParchment = theme === 'parchment';
  const isKraft = theme === 'kraft';
  const isDarkMotion = theme === 'dark_minimalist' || theme === 'gold_luxury' || theme === 'neon_cyber';
  const isGold = theme === 'gold_luxury';
  const isNeon = theme === 'neon_cyber';

  const subtitleColor = isNeon
    ? '#38bdf8'
    : isDarkMotion || isGold
    ? '#facc15'
    : isChalkboard
    ? '#86efac'
    : isBlueprint
    ? '#38bdf8'
    : isParchment
    ? '#92400e'
    : isKraft
    ? '#15803d'
    : '#16a34a';

  const titleColor = isDarkMotion
    ? '#ffffff'
    : isChalkboard
    ? '#f8fafc'
    : isBlueprint
    ? '#ffffff'
    : isParchment
    ? '#451a03'
    : isKraft
    ? '#292524'
    : '#1e3a8a';

  const circleColor = isNeon
    ? '#38bdf8'
    : isDarkMotion || isGold
    ? '#facc15'
    : isChalkboard
    ? '#f87171'
    : isBlueprint
    ? '#38bdf8'
    : isParchment
    ? '#991b1b'
    : '#dc2626';

  const highlightTextColor = isDarkMotion ? '#030712' : isChalkboard ? '#0f172a' : isBlueprint ? '#041c32' : isParchment ? '#78350f' : '#991b1b';
  const highlightBg = isNeon ? '#38bdf8' : isDarkMotion || isGold ? '#facc15' : isChalkboard ? '#fef08a' : isBlueprint ? '#38bdf8' : isParchment ? '#fde68a' : '#fef08a';

  // Entrance scale
  const scale = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8 },
  });

  // Red circle drawing animation
  const circleProgress = interpolate(frame, [15, 35], [350, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Pen cursor position
  const circleAngle = interpolate(frame, [15, 35], [-Math.PI * 0.5, Math.PI * 1.5], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const penX = 75 + 85 * Math.cos(circleAngle);
  const penY = 32 + 28 * Math.sin(circleAngle);

  // Yellow highlighter sweep animation
  const highlightWidth = interpolate(frame, [25, 45], [0, 105], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const markerX = isRTL
    ? interpolate(frame, [25, 45], [480, 20], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })
    : interpolate(frame, [25, 45], [20, 480], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <div
      style={{
        transform: `scale(${scale})`,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        paddingTop: 10,
        position: 'relative',
        zIndex: 10,
        direction: isRTL ? 'rtl' : 'ltr',
      }}
    >
      {/* Subtitle */}
      {subtitle && (
        <div
          style={{
            fontSize: 44,
            fontWeight: 700,
            color: subtitleColor,
            letterSpacing: 1,
            marginBottom: 4,
            textShadow: isChalkboard ? '0 0 8px rgba(134, 239, 172, 0.4)' : isBlueprint ? '0 0 10px rgba(56, 189, 248, 0.5)' : undefined,
          }}
        >
          {subtitle}
        </div>
      )}

      {/* Line 1: Main hook word */}
      {title1 && (
        <div
          style={{
            fontSize: 78,
            fontWeight: 900,
            color: titleColor,
            lineHeight: 1.1,
            letterSpacing: 2,
            textShadow: isChalkboard ? '0 0 10px rgba(255,255,255,0.4)' : isBlueprint ? '0 0 12px rgba(255,255,255,0.6)' : undefined,
          }}
        >
          {title1}
        </div>
      )}

      {/* Line 2: Circled Word + Optional Title2 */}
      {(circledWord || title2) && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 16,
            fontSize: 64,
            fontWeight: 800,
            color: titleColor,
            position: 'relative',
            marginTop: 4,
            textShadow: isChalkboard ? '0 0 10px rgba(255,255,255,0.4)' : undefined,
          }}
        >
          {/* Circled Word */}
          {circledWord && (
            <div style={{ position: 'relative', display: 'inline-block', padding: '0 12px' }}>
              <span>{circledWord}</span>
              <svg
                style={{
                  position: 'absolute',
                  top: -12,
                  left: -12,
                  width: 'calc(100% + 24px)',
                  height: 'calc(100% + 24px)',
                  pointerEvents: 'none',
                  overflow: 'visible',
                }}
                viewBox="0 0 200 80"
              >
                <path
                  d="M 25 40 C 20 15, 175 12, 185 38 C 195 65, 30 70, 20 45 C 15 32, 70 20, 110 22"
                  fill="none"
                  stroke={circleColor}
                  strokeWidth="5"
                  strokeLinecap="round"
                  strokeDasharray="350"
                  strokeDashoffset={circleProgress}
                />
              </svg>

              {/* Physical Pen Cursor */}
              <PenCursor
                x={penX}
                y={penY}
                visible={frame >= 15 && frame <= 36}
                type="pen"
                rotation={-15 + 10 * Math.sin(frame)}
              />
            </div>
          )}

          {title2 && <span>{title2}</span>}
        </div>
      )}

      {/* Line 3: Highlighted Text */}
      {highlightedText && (
        <div
          style={{
            position: 'relative',
            display: 'inline-block',
            marginTop: 8,
            padding: '2px 14px',
          }}
        >
          {/* Highlighter Stroke */}
          <div
            style={{
              position: 'absolute',
              left: isRTL ? undefined : -12,
              right: isRTL ? -12 : undefined,
              bottom: 4,
              height: 64,
              width: `${highlightWidth}%`,
              backgroundColor: highlightBg,
              opacity: 0.92,
              borderRadius: 6,
              transform: isRTL ? 'rotate(0.8deg)' : 'rotate(-0.8deg)',
              zIndex: 0,
              boxShadow: isBlueprint ? '0 0 12px rgba(56, 189, 248, 0.4)' : undefined,
            }}
          />

          <span
            style={{
              position: 'relative',
              zIndex: 1,
              fontSize: 74,
              fontWeight: 900,
              color: highlightTextColor,
              fontStyle: 'italic',
              letterSpacing: 2,
            }}
          >
            {highlightedText}
          </span>

          {/* Marker Cursor */}
          <PenCursor
            x={markerX}
            y={20}
            visible={frame >= 25 && frame <= 46}
            type="highlighter"
            rotation={-35}
          />
        </div>
      )}
    </div>
  );
};
