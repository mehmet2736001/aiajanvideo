import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface EarthShieldTelemetryHUDProps {
  scaleMultiplier?: number;
}

export const EarthShieldTelemetryHUD: React.FC<EarthShieldTelemetryHUDProps> = ({
  scaleMultiplier = 1.0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 95 },
  });

  const shieldPulse = 0.85 + Math.sin(frame * 0.15) * 0.15;
  const solarWaveOffset = (frame * 4) % 180;

  return (
    <div
      style={{
        position: 'relative',
        width: 860 * scaleMultiplier,
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        opacity: entrance,
        transform: `scale(${entrance * scaleMultiplier})`,
        pointerEvents: 'none',
      }}
    >
      {/* Top Telemetry Header */}
      <div
        style={{
          width: '100%',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 24px',
          background: 'rgba(6, 12, 28, 0.85)',
          border: '1px solid rgba(16, 185, 129, 0.6)',
          borderRadius: 16,
          boxShadow: '0 0 25px rgba(16, 185, 129, 0.25)',
          marginBottom: 20,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              backgroundColor: '#10b981',
              boxShadow: '0 0 10px #10b981',
            }}
          />
          <span
            style={{
              color: '#f8fafc',
              fontFamily: "'Cinzel', serif",
              fontSize: 16,
              fontWeight: 800,
              letterSpacing: 2,
            }}
          >
            DİNAMO MOTORU: ERİMİŞ DEMİR ÇEKİRDEK
          </span>
        </div>

        <div
          style={{
            color: '#10b981',
            fontFamily: "'Cinzel', serif",
            fontSize: 16,
            fontWeight: 800,
            letterSpacing: 1,
          }}
        >
          KALKAN: %100 AKTİF
        </div>
      </div>

      {/* SVG Solar Wind Deflection Waves */}
      <svg width="780" height="240" viewBox="0 0 780 240">
        <defs>
          <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#10b981" stopOpacity="0.8" />
            <stop offset="50%" stopColor="#38bdf8" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#d4af37" stopOpacity="0.1" />
          </linearGradient>
        </defs>

        {/* Curved Magnetosphere Arc */}
        <path
          d="M 140 20 Q 390 120 140 220"
          fill="none"
          stroke="url(#shieldGrad)"
          strokeWidth="6"
          filter="drop-shadow(0 0 12px #10b981)"
          transform={`scale(${shieldPulse})`}
          transformOrigin="390 120"
        />

        <path
          d="M 180 35 Q 430 120 180 205"
          fill="none"
          stroke="rgba(56, 189, 248, 0.6)"
          strokeWidth="3"
          strokeDasharray="10 15"
        />

        {/* Incoming Solar Wind Arrows Deflecting */}
        {[-40, 0, 40].map((dy, i) => (
          <g key={i} transform={`translate(${solarWaveOffset}, ${dy})`}>
            <line
              x1="680"
              y1={120 + dy}
              x2="480"
              y2={120 + dy}
              stroke="#fbbf24"
              strokeWidth="3"
              strokeDasharray="15 10"
            />
            <path
              d={`M 480 ${120 + dy} Q 400 ${120 + dy} 340 ${60 + dy * 2}`}
              fill="none"
              stroke="#f59e0b"
              strokeWidth="2.5"
            />
          </g>
        ))}
      </svg>
    </div>
  );
};
