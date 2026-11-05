import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface StardustConstellationProps {
  primaryText: string;
  secondaryText?: string;
  accentColor?: string;
  glowColor?: string;
  symbol?: string;
}

export const StardustConstellation: React.FC<StardustConstellationProps> = ({
  primaryText,
  secondaryText,
  accentColor = '#fef08a',
  glowColor = 'rgba(245, 158, 11, 0.65)',
  symbol = '۞',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring animation
  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 90, mass: 0.8 },
  });

  const fadeIn = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const gentleFloat = Math.sin(frame * 0.06) * 6;
  const pulseGlow = 0.85 + Math.sin(frame * 0.08) * 0.18;
  const ringRotate = frame * 0.25;

  // Generate deterministic pseudo-random constellation stars
  const stars = [
    { x: -160, y: -90, size: 4, delay: 0 },
    { x: 175, y: -110, size: 5, delay: 4 },
    { x: -220, y: 40, size: 3.5, delay: 7 },
    { x: 230, y: 60, size: 4.5, delay: 2 },
    { x: -110, y: 130, size: 3, delay: 9 },
    { x: 130, y: 125, size: 4, delay: 5 },
    { x: 0, y: -140, size: 6, delay: 3 },
    { x: -260, y: -40, size: 3, delay: 8 },
    { x: 270, y: -30, size: 3.5, delay: 6 },
    { x: 0, y: 155, size: 5, delay: 1 },
  ];

  return (
    <div
      style={{
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        opacity: fadeIn,
        transform: `translateY(${gentleFloat}px)`,
        margin: '18px 0',
      }}
    >
      {/* 1. Constellation Starfield & Orbital Linking SVG */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          width: 640,
          height: 360,
          transform: 'translate(-50%, -50%)',
          pointerEvents: 'none',
          zIndex: 0,
        }}
      >
        <svg viewBox="-320 -180 640 360" style={{ width: '100%', height: '100%' }}>
          {/* Subtle Rotating Astrolabe / Celestial Ring */}
          <circle
            cx="0"
            cy="0"
            r="150"
            stroke="rgba(245, 158, 11, 0.22)"
            strokeWidth="1.2"
            strokeDasharray="4 8"
            fill="none"
            transform={`rotate(${ringRotate})`}
          />
          <circle
            cx="0"
            cy="0"
            r="165"
            stroke="rgba(56, 189, 248, 0.18)"
            strokeWidth="0.8"
            fill="none"
            transform={`rotate(${-ringRotate * 0.7})`}
          />

          {/* Faint Constellation Linking Lines */}
          <line x1="-160" y1="-90" x2="0" y2="-140" stroke="rgba(254, 240, 138, 0.25)" strokeWidth="0.8" />
          <line x1="0" y1="-140" x2="175" y2="-110" stroke="rgba(254, 240, 138, 0.25)" strokeWidth="0.8" />
          <line x1="-220" y1="40" x2="-110" y2="130" stroke="rgba(56, 189, 248, 0.22)" strokeWidth="0.8" />
          <line x1="230" y1="60" x2="130" y2="125" stroke="rgba(56, 189, 248, 0.22)" strokeWidth="0.8" />
          <line x1="-110" y1="130" x2="0" y2="155" stroke="rgba(245, 158, 11, 0.2)" strokeWidth="0.8" />
          <line x1="130" y1="125" x2="0" y2="155" stroke="rgba(245, 158, 11, 0.2)" strokeWidth="0.8" />

          {/* Sparkling Constellation Star Nodes */}
          {stars.map((s, idx) => {
            const twinkle = 0.5 + Math.sin((frame + s.delay * 8) * 0.12) * 0.5;
            return (
              <g key={idx} transform={`translate(${s.x}, ${s.y})`}>
                <circle
                  cx="0"
                  cy="0"
                  r={s.size * 2.2}
                  fill="rgba(245, 158, 11, 0.3)"
                  opacity={twinkle}
                />
                <circle
                  cx="0"
                  cy="0"
                  r={s.size}
                  fill="#ffffff"
                  opacity={twinkle}
                />
                {/* 4-point star sparkle on key nodes */}
                {s.size >= 4.5 && (
                  <path
                    d={`M 0 ${-s.size * 2.5} L 0 ${s.size * 2.5} M ${-s.size * 2.5} 0 L ${s.size * 2.5} 0`}
                    stroke="rgba(254, 240, 138, 0.75)"
                    strokeWidth="1"
                    opacity={twinkle}
                  />
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* 2. Core Focal Stardust Text / Number */}
      <div
        style={{
          position: 'relative',
          zIndex: 2,
          transform: `scale(${entrance})`,
          textAlign: 'center',
        }}
      >
        <div
          style={{
            fontFamily: '"Cinzel", "Montserrat", "Playfair Display", serif',
            fontSize: primaryText.length <= 4 ? 104 : primaryText.length <= 8 ? 72 : 56,
            fontWeight: 900,
            letterSpacing: '3px',
            color: '#ffffff',
            lineHeight: 1.05,
            textShadow: `
              0 0 20px ${glowColor},
              0 0 45px ${glowColor},
              0 4px 30px rgba(0, 0, 0, 0.95),
              0 0 70px rgba(56, 189, 248, 0.35)
            `,
            background: 'linear-gradient(180deg, #ffffff 0%, #fef08a 65%, #f59e0b 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            filter: `drop-shadow(0 4px 15px rgba(0,0,0,0.85)) drop-shadow(0 0 25px ${glowColor})`,
          }}
        >
          {primaryText}
        </div>

        {/* 3. Celestial Sub-Badge / Secondary Text */}
        {secondaryText && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 12,
              marginTop: 10,
              fontSize: 22,
              fontWeight: 800,
              letterSpacing: '5px',
              textTransform: 'uppercase',
              color: '#38bdf8',
              textShadow: '0 0 15px rgba(56, 189, 248, 0.6), 0 2px 10px rgba(0,0,0,0.9)',
            }}
          >
            <span style={{ color: '#facc15', fontSize: 16 }}>{symbol}</span>
            <span>{secondaryText}</span>
            <span style={{ color: '#facc15', fontSize: 16 }}>{symbol}</span>
          </div>
        )}
      </div>
    </div>
  );
};
