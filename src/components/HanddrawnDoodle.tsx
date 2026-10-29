import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { PenCursor } from './PenCursor';

export type DoodleType = 'galaxy' | 'hourglass' | 'book' | 'lightbulb' | 'compass';

interface HanddrawnDoodleProps {
  type: DoodleType;
  startFrame?: number;
  durationInFrames?: number;
  size?: number;
  theme?: 'notebook' | 'kraft' | 'chalkboard' | 'parchment' | 'blueprint';
  style?: React.CSSProperties;
}

export const HanddrawnDoodle: React.FC<HanddrawnDoodleProps> = ({
  type = 'galaxy',
  startFrame = 20,
  durationInFrames = 40,
  size = 200,
  theme = 'notebook',
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const isChalkboard = theme === 'chalkboard';
  const isBlueprint = theme === 'blueprint';
  const isParchment = theme === 'parchment';
  const isKraft = theme === 'kraft';

  const strokeColor = isChalkboard
    ? '#86efac'
    : isBlueprint
    ? '#38bdf8'
    : isParchment
    ? '#92400e'
    : isKraft
    ? '#451a03'
    : '#1e3a8a';

  const accentColor = isChalkboard
    ? '#fef08a'
    : isBlueprint
    ? '#e0f2fe'
    : isParchment
    ? '#b45309'
    : isKraft
    ? '#78350f'
    : '#dc2626';

  // Overall scale spring
  const scale = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 15, mass: 0.8 },
  });

  // Stroke drawing progress (0 to 1)
  const drawProgress = interpolate(
    frame,
    [startFrame, startFrame + durationInFrames],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  // Pen cursor visibility: visible only during active drawing
  const penVisible = frame >= startFrame && frame <= startFrame + durationInFrames;

  // Approximate pen tip position based on type and progress
  const getPenCoords = () => {
    const p = drawProgress;
    if (type === 'galaxy') {
      const angle = p * Math.PI * 4;
      const r = (1 - p * 0.7) * (size * 0.4);
      return {
        x: size / 2 + r * Math.cos(angle),
        y: size / 2 + r * Math.sin(angle),
      };
    }
    if (type === 'hourglass') {
      return {
        x: size * (0.2 + p * 0.6),
        y: size * (0.15 + p * 0.7),
      };
    }
    if (type === 'lightbulb') {
      return {
        x: size / 2 + Math.sin(p * Math.PI * 2) * (size * 0.3),
        y: size * (0.2 + p * 0.6),
      };
    }
    // Default book / compass
    return {
      x: size * (0.2 + p * 0.6),
      y: size * (0.3 + Math.sin(p * Math.PI) * 0.3),
    };
  };

  const penCoords = getPenCoords();

  // Stroke dash calculations
  const pathLength = 600;
  const strokeDashoffset = pathLength * (1 - drawProgress);

  return (
    <div
      style={{
        position: 'relative',
        width: size,
        height: size,
        transform: `scale(${Math.max(0, scale)})`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        ...style,
      }}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 200 200"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{
          filter: isChalkboard
            ? 'drop-shadow(0 0 6px rgba(134,239,172,0.4))'
            : isBlueprint
            ? 'drop-shadow(0 0 8px rgba(56,189,248,0.5))'
            : 'drop-shadow(1px 2px 3px rgba(0,0,0,0.15))',
        }}
      >
        {type === 'galaxy' && (
          <g>
            {/* Core spiral */}
            <path
              d="M 100 100 
                 m -65 0 
                 a 65 65 0 1 0 130 0 
                 a 50 50 0 1 0 -100 0 
                 a 35 35 0 1 0 70 0 
                 a 20 20 0 1 0 -40 0 
                 a 8 8 0 1 0 16 0"
              stroke={strokeColor}
              strokeWidth="4"
              strokeDasharray={pathLength}
              strokeDashoffset={strokeDashoffset}
            />
            {/* Orbit sparkles */}
            {drawProgress > 0.6 && (
              <>
                <circle cx="45" cy="65" r="3" fill={accentColor} />
                <circle cx="155" cy="135" r="3.5" fill={accentColor} />
                <circle cx="140" cy="50" r="2.5" fill={strokeColor} />
                <circle cx="55" cy="140" r="2.5" fill={strokeColor} />
                {/* Cross twinkle */}
                <line x1="165" y1="80" x2="175" y2="80" stroke={accentColor} strokeWidth="2" />
                <line x1="170" y1="75" x2="170" y2="85" stroke={accentColor} strokeWidth="2" />
              </>
            )}
          </g>
        )}

        {type === 'hourglass' && (
          <g>
            {/* Top plate & bottom plate */}
            <line x1="45" y1="35" x2="155" y2="35" stroke={strokeColor} strokeWidth="5" />
            <line x1="45" y1="165" x2="155" y2="165" stroke={strokeColor} strokeWidth="5" />
            {/* Hourglass body glass curves */}
            <path
              d="M 55 38 Q 65 95 100 100 Q 135 95 145 38 Z"
              stroke={strokeColor}
              strokeWidth="4"
              strokeDasharray="300"
              strokeDashoffset={300 * (1 - drawProgress)}
            />
            <path
              d="M 55 162 Q 65 105 100 100 Q 135 105 145 162 Z"
              stroke={strokeColor}
              strokeWidth="4"
              strokeDasharray="300"
              strokeDashoffset={300 * (1 - drawProgress)}
            />
            {/* Sand falling & accumulation */}
            {drawProgress > 0.4 && (
              <>
                <line x1="100" y1="100" x2="100" y2="148" stroke={accentColor} strokeWidth="2" strokeDasharray="4 3" />
                <path d="M 75 160 Q 100 142 125 160 Z" fill={accentColor} opacity={0.8} />
              </>
            )}
          </g>
        )}

        {type === 'book' && (
          <g>
            {/* Book spine & open pages */}
            <path
              d="M 100 155 L 100 70 M 100 70 C 120 58 150 62 170 70 L 170 150 C 150 142 120 140 100 155 C 80 140 50 142 30 150 L 30 70 C 50 62 80 58 100 70"
              stroke={strokeColor}
              strokeWidth="4"
              strokeDasharray="500"
              strokeDashoffset={500 * (1 - drawProgress)}
            />
            {/* Page text lines sketch */}
            {drawProgress > 0.5 && (
              <>
                <line x1="45" y1="90" x2="85" y2="86" stroke={accentColor} strokeWidth="2.5" />
                <line x1="45" y1="108" x2="85" y2="104" stroke={accentColor} strokeWidth="2.5" />
                <line x1="45" y1="126" x2="80" y2="122" stroke={accentColor} strokeWidth="2.5" />
                <line x1="115" y1="86" x2="155" y2="90" stroke={accentColor} strokeWidth="2.5" />
                <line x1="115" y1="104" x2="155" y2="108" stroke={accentColor} strokeWidth="2.5" />
                <line x1="115" y1="122" x2="150" y2="126" stroke={accentColor} strokeWidth="2.5" />
              </>
            )}
            {/* Wisdom rays radiating from top */}
            {drawProgress > 0.7 && (
              <>
                <line x1="100" y1="52" x2="100" y2="38" stroke={accentColor} strokeWidth="3" />
                <line x1="82" y1="56" x2="72" y2="44" stroke={accentColor} strokeWidth="2.5" />
                <line x1="118" y1="56" x2="128" y2="44" stroke={accentColor} strokeWidth="2.5" />
              </>
            )}
          </g>
        )}

        {type === 'lightbulb' && (
          <g>
            {/* Bulb glass outline */}
            <path
              d="M 75 125 C 55 105 50 70 72 45 C 90 25 115 25 130 45 C 150 70 145 105 125 125 L 125 142 L 75 142 Z"
              stroke={strokeColor}
              strokeWidth="4"
              strokeDasharray="450"
              strokeDashoffset={450 * (1 - drawProgress)}
            />
            {/* Screw base & contact point */}
            <line x1="80" y1="150" x2="120" y2="150" stroke={strokeColor} strokeWidth="3.5" />
            <line x1="85" y1="158" x2="115" y2="158" stroke={strokeColor} strokeWidth="3.5" />
            <path d="M 92 158 Q 100 166 108 158" stroke={strokeColor} strokeWidth="3" />
            {/* Filament */}
            <path
              d="M 90 125 L 90 95 L 96 85 L 104 85 L 110 95 L 110 125"
              stroke={accentColor}
              strokeWidth="2.5"
            />
            {/* Glow sparks */}
            {drawProgress > 0.6 && (
              <>
                <line x1="100" y1="20" x2="100" y2="8" stroke={accentColor} strokeWidth="3" />
                <line x1="48" y1="42" x2="36" y2="34" stroke={accentColor} strokeWidth="3" />
                <line x1="152" y1="42" x2="164" y2="34" stroke={accentColor} strokeWidth="3" />
                <line x1="38" y1="92" x2="24" y2="92" stroke={accentColor} strokeWidth="3" />
                <line x1="162" y1="92" x2="176" y2="92" stroke={accentColor} strokeWidth="3" />
              </>
            )}
          </g>
        )}

        {type === 'compass' && (
          <g>
            {/* Outer dial ring */}
            <circle
              cx="100"
              cy="100"
              r="68"
              stroke={strokeColor}
              strokeWidth="4"
              strokeDasharray="450"
              strokeDashoffset={450 * (1 - drawProgress)}
            />
            {/* Inner ring */}
            <circle cx="100" cy="100" r="58" stroke={strokeColor} strokeWidth="1.5" strokeDasharray="3 3" />
            {/* Compass Star Points */}
            <polygon points="100,42 108,92 100,100 92,92" fill={accentColor} stroke={accentColor} strokeWidth="1" />
            <polygon points="100,158 108,108 100,100 92,108" fill={strokeColor} stroke={strokeColor} strokeWidth="1" />
            <polygon points="158,100 108,108 100,100 108,92" fill={strokeColor} stroke={strokeColor} strokeWidth="1" />
            <polygon points="42,100 92,108 100,100 92,92" fill={strokeColor} stroke={strokeColor} strokeWidth="1" />
            {/* Center pin */}
            <circle cx="100" cy="100" r="5" fill="#f8fafc" stroke={strokeColor} strokeWidth="2.5" />
          </g>
        )}
      </svg>

      {/* Red Pen cursor following the active drawing */}
      <PenCursor
        x={penCoords.x}
        y={penCoords.y}
        visible={penVisible}
        type="pen"
        rotation={-18}
      />
    </div>
  );
};
