import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface HydrothermalVentWindowProps {
  title?: string;
  magmaTempText?: string;
  waterTempText?: string;
}

export const HydrothermalVentWindow: React.FC<HydrothermalVentWindowProps> = ({
  title = 'OKYANUS TABANI HİDROTERMAL BACALARI',
  magmaTempText = '1200°C ERİMİŞ MAGMA',
  waterTempText = '400°C KAYNAR SULAR VE MİNERAL DUMANI',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 16, stiffness: 85, mass: 0.9 },
  });

  const fadeIn = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const pulseMagma = 0.82 + Math.sin(frame * 0.08) * 0.18;
  const smokeWave = Math.sin(frame * 0.1) * 8;

  // Rising bubble particles
  const bubbles = [
    { x: 120, speed: 2.5, size: 4, offset: 0 },
    { x: 155, speed: 3.2, size: 6, offset: 15 },
    { x: 190, speed: 2.0, size: 5, offset: 35 },
    { x: 230, speed: 2.8, size: 4, offset: 10 },
    { x: 265, speed: 3.5, size: 7, offset: 25 },
    { x: 310, speed: 2.2, size: 5, offset: 40 },
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
        transform: `scale(${entrance})`,
        padding: '24px 32px',
        borderRadius: 28,
        backgroundColor: 'rgba(3, 7, 18, 0.85)',
        border: '1.5px solid rgba(249, 115, 22, 0.45)',
        boxShadow: '0 16px 45px rgba(0, 0, 0, 0.9), 0 0 35px rgba(249, 115, 22, 0.25)',
        backdropFilter: 'blur(24px)',
        maxWidth: 880,
        margin: '16px auto',
        zIndex: 10,
      }}
    >
      {/* 1. Window Header */}
      {title && (
        <div
          style={{
            fontFamily: '"Cinzel", "Montserrat", sans-serif',
            fontSize: 22,
            fontWeight: 800,
            letterSpacing: '3px',
            color: '#fef08a',
            textTransform: 'uppercase',
            textAlign: 'center',
            marginBottom: 16,
            textShadow: '0 0 15px rgba(249, 115, 22, 0.6)',
          }}
        >
          {title}
        </div>
      )}

      {/* 2. Scientific Cross-Section SVG Canvas */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: 620,
          height: 320,
          borderRadius: 20,
          overflow: 'hidden',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          backgroundColor: '#030a16',
        }}
      >
        <svg viewBox="0 0 620 320" style={{ width: '100%', height: '100%' }}>
          <defs>
            {/* Magma Chamber Gradient */}
            <radialGradient id="magmaChamber" cx="50%" cy="85%" r="65%">
              <stop offset="0%" stopColor="#ffffff" />
              <stop offset="25%" stopColor="#fef08a" />
              <stop offset="60%" stopColor="#f97316" />
              <stop offset="90%" stopColor="#dc2626" />
              <stop offset="100%" stopColor="#7f1d1d" />
            </radialGradient>

            {/* Magma Heat Glow */}
            <filter id="chamberGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="12" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>

            {/* Ocean Water Column Gradient */}
            <linearGradient id="oceanColumn" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#020617" />
              <stop offset="65%" stopColor="#082f49" />
              <stop offset="100%" stopColor="#0f172a" />
            </linearGradient>
          </defs>

          {/* Ocean Water Background */}
          <rect x="0" y="0" width="620" height="320" fill="url(#oceanColumn)" />

          {/* Rising Deep-Sea Bubbles */}
          {bubbles.map((b, idx) => {
            const yPos = 220 - ((frame * b.speed + b.offset * 8) % 240);
            return (
              <circle
                key={idx}
                cx={b.x + Math.sin((frame + idx * 10) * 0.1) * 6}
                cy={yPos}
                r={b.size}
                fill="none"
                stroke="rgba(56, 189, 248, 0.45)"
                strokeWidth="1.2"
              />
            );
          })}

          {/* Black Smoker Chimney Smoke Plumes (Left Chimney) */}
          <g opacity={0.75}>
            <path
              d={`M 170 170 Q ${160 + smokeWave} 110 145 60 Q ${135 - smokeWave} 20 150 5`}
              stroke="#0f172a"
              strokeWidth="28"
              strokeLinecap="round"
              fill="none"
              filter="blur(5px)"
            />
            <path
              d={`M 170 170 Q ${165 - smokeWave} 115 155 65 Q ${145 + smokeWave} 25 155 10`}
              stroke="#334155"
              strokeWidth="14"
              strokeLinecap="round"
              fill="none"
            />
          </g>

          {/* Black Smoker Chimney Smoke Plumes (Right Chimney) */}
          <g opacity={0.75}>
            <path
              d={`M 450 170 Q ${460 - smokeWave} 110 475 60 Q ${485 + smokeWave} 20 470 5`}
              stroke="#0f172a"
              strokeWidth="28"
              strokeLinecap="round"
              fill="none"
              filter="blur(5px)"
            />
            <path
              d={`M 450 170 Q ${455 + smokeWave} 115 465 65 Q ${475 - smokeWave} 25 465 10`}
              stroke="#334155"
              strokeWidth="14"
              strokeLinecap="round"
              fill="none"
            />
          </g>

          {/* Central Hydrothermal Mineral Vent Eruption */}
          <g filter="url(#chamberGlow)">
            <path
              d={`M 310 200 Q ${310 + smokeWave * 0.5} 150 300 110 Q ${320 - smokeWave * 0.5} 80 310 40`}
              stroke="rgba(254, 240, 138, 0.85)"
              strokeWidth="12"
              strokeLinecap="round"
              fill="none"
            />
            <circle cx="310" cy="190" r="14" fill="#fef08a" />
          </g>

          {/* Sea Floor Rock Bed & Chimneys */}
          <path
            d="M 0 220 
               L 140 215 
               L 160 170 
               L 180 170 
               L 200 220 
               L 280 215 
               L 310 195 
               L 340 215 
               L 420 220 
               L 440 170 
               L 460 170 
               L 480 215 
               L 620 220 
               L 620 320 
               L 0 320 Z"
            fill="#1e293b"
            stroke="#334155"
            strokeWidth="2"
          />

          {/* Subterranean 1200°C Magma Reservoir */}
          <ellipse
            cx="310"
            cy="275"
            rx="240"
            ry="45"
            fill="url(#magmaChamber)"
            filter="url(#chamberGlow)"
            opacity={pulseMagma}
          />
        </svg>

        {/* Telemetry Overlays */}
        <div
          style={{
            position: 'absolute',
            bottom: 12,
            left: 16,
            padding: '4px 14px',
            borderRadius: 8,
            backgroundColor: 'rgba(220, 38, 38, 0.85)',
            color: '#ffffff',
            fontSize: 14,
            fontWeight: 800,
            letterSpacing: '1px',
          }}
        >
          {magmaTempText}
        </div>

        <div
          style={{
            position: 'absolute',
            top: 12,
            right: 16,
            padding: '4px 14px',
            borderRadius: 8,
            backgroundColor: 'rgba(3, 105, 161, 0.85)',
            color: '#ffffff',
            fontSize: 13,
            fontWeight: 800,
            letterSpacing: '1px',
          }}
        >
          {waterTempText}
        </div>
      </div>
    </div>
  );
};
