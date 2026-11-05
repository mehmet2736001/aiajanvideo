import React from 'react';
import { useCurrentFrame } from 'remotion';

interface AstrolabeGoldenMandalaProps {
  size?: number;
  opacity?: number;
}

export const AstrolabeGoldenMandala: React.FC<AstrolabeGoldenMandalaProps> = ({
  size = 600,
  opacity = 0.35,
}) => {
  const frame = useCurrentFrame();

  const rotClockwise = (frame * 0.4) % 360;
  const rotCounter = (-frame * 0.3) % 360;
  const rotSlow = (frame * 0.15) % 360;

  return (
    <div
      style={{
        position: 'absolute',
        width: size,
        height: size,
        pointerEvents: 'none',
        opacity,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* Outer Ring 1 (Degree Scale - Rotating Clockwise) */}
      <svg
        width={size}
        height={size}
        viewBox="0 0 600 600"
        style={{
          position: 'absolute',
          transform: `rotate(${rotClockwise}deg)`,
        }}
      >
        <circle cx="300" cy="300" r="280" fill="none" stroke="#d4af37" strokeWidth="2" />
        <circle
          cx="300"
          cy="300"
          r="268"
          fill="none"
          stroke="#d4af37"
          strokeWidth="1"
          strokeDasharray="4 8"
        />
        {/* 24 Degree Ticks */}
        {[...Array(24)].map((_, i) => (
          <line
            key={i}
            x1="300"
            y1="20"
            x2="300"
            y2="34"
            stroke="#d4af37"
            strokeWidth="2"
            transform={`rotate(${i * 15} 300 300)`}
          />
        ))}
      </svg>

      {/* Middle Ring 2 (12-Pointed Islamic Star Geometric Mandala - Counter Clockwise) */}
      <svg
        width={size * 0.82}
        height={size * 0.82}
        viewBox="0 0 500 500"
        style={{
          position: 'absolute',
          transform: `rotate(${rotCounter}deg)`,
        }}
      >
        <circle cx="250" cy="250" r="230" fill="none" stroke="#f59e0b" strokeWidth="1.5" />
        {/* 3 Intersecting Squares (12-Pointed Star) */}
        <rect
          x="70"
          y="70"
          width="360"
          height="360"
          fill="none"
          stroke="rgba(212, 175, 55, 0.45)"
          strokeWidth="2"
        />
        <rect
          x="70"
          y="70"
          width="360"
          height="360"
          fill="none"
          stroke="rgba(212, 175, 55, 0.45)"
          strokeWidth="2"
          transform="rotate(30 250 250)"
        />
        <rect
          x="70"
          y="70"
          width="360"
          height="360"
          fill="none"
          stroke="rgba(212, 175, 55, 0.45)"
          strokeWidth="2"
          transform="rotate(60 250 250)"
        />
      </svg>

      {/* Inner Core Ring (Slow Rotation) */}
      <svg
        width={size * 0.55}
        height={size * 0.55}
        viewBox="0 0 300 300"
        style={{
          position: 'absolute',
          transform: `rotate(${rotSlow}deg)`,
        }}
      >
        <circle
          cx="150"
          cy="150"
          r="130"
          fill="none"
          stroke="#fef08a"
          strokeWidth="2"
          strokeDasharray="20 40"
        />
        <circle
          cx="150"
          cy="150"
          r="90"
          fill="none"
          stroke="#d4af37"
          strokeWidth="1.5"
        />
        <circle cx="150" cy="150" r="15" fill="#d4af37" />
      </svg>
    </div>
  );
};
