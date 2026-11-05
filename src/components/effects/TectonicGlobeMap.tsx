import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface TectonicGlobeMapProps {
  title?: string;
  metricNumber?: string;
  metricLabel?: string;
  glowColor?: string;
}

export const TectonicGlobeMap: React.FC<TectonicGlobeMapProps> = ({
  title = 'OKYANUS TABANINDAKİ DEV YARIKLAR',
  metricNumber = '65.000 KM',
  metricLabel = 'DÜNYAYI SARAN OKYANUS SIRTI FAY HATTI',
  glowColor = '#f97316',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 16, stiffness: 85, mass: 0.9 },
  });

  const fadeIn = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const pulseRift = 0.8 + Math.sin(frame * 0.08) * 0.2;
  const globeRotate = frame * 0.15;

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
        padding: '26px 36px',
        borderRadius: 28,
        backgroundColor: 'rgba(3, 7, 18, 0.82)',
        border: '1.5px solid rgba(56, 189, 248, 0.45)',
        boxShadow: '0 16px 45px rgba(0, 0, 0, 0.9), 0 0 35px rgba(56, 189, 248, 0.25)',
        backdropFilter: 'blur(24px)',
        maxWidth: 880,
        margin: '16px auto',
        zIndex: 10,
      }}
    >
      {/* 1. Section Title */}
      {title && (
        <div
          style={{
            fontFamily: '"Cinzel", "Montserrat", sans-serif',
            fontSize: 22,
            fontWeight: 800,
            letterSpacing: '3px',
            color: '#38bdf8',
            textTransform: 'uppercase',
            textAlign: 'center',
            marginBottom: 18,
            textShadow: '0 0 15px rgba(56, 189, 248, 0.6)',
          }}
        >
          {title}
        </div>
      )}

      {/* 2. Stylized Globe with Glowing Tectonic Rift Network */}
      <div style={{ position: 'relative', width: 320, height: 320 }}>
        <svg viewBox="0 0 320 320" style={{ width: '100%', height: '100%' }}>
          <defs>
            {/* Fault Line Neon Heat Glow Filter */}
            <filter id="riftGlow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur1" />
              <feGaussianBlur in="SourceGraphic" stdDeviation="12" result="blur2" />
              <feMerge>
                <feMergeNode in="blur2" />
                <feMergeNode in="blur1" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>

            {/* Atmosphere Halo Gradient */}
            <radialGradient id="atmoGlow" cx="50%" cy="50%" r="50%">
              <stop offset="75%" stopColor="#0284c7" stopOpacity="0.4" />
              <stop offset="98%" stopColor="#38bdf8" stopOpacity="0.95" />
              <stop offset="100%" stopColor="#38bdf8" stopOpacity="0" />
            </radialGradient>

            {/* Ocean Sphere Gradient */}
            <radialGradient id="oceanSphere" cx="40%" cy="35%" r="65%">
              <stop offset="0%" stopColor="#0369a1" />
              <stop offset="60%" stopColor="#0c4a6e" />
              <stop offset="100%" stopColor="#082f49" />
            </radialGradient>
          </defs>

          {/* Outer Atmospheric Aura */}
          <circle cx="160" cy="160" r="148" fill="url(#atmoGlow)" />

          {/* Main Earth Globe */}
          <circle cx="160" cy="160" r="135" fill="url(#oceanSphere)" stroke="#38bdf8" strokeWidth="2.5" />

          {/* Stylized Continents (Greenish Earth masses) */}
          <g opacity={0.65}>
            {/* Africa / Eurasia shape */}
            <path
              d="M 175 75 Q 195 90 190 125 Q 210 145 200 195 Q 170 215 155 185 Q 145 135 155 105 Z"
              fill="#15803d"
            />
            {/* Americas shape */}
            <path
              d="M 115 85 Q 130 115 110 145 Q 125 185 105 225 Q 90 205 95 155 Q 85 115 100 95 Z"
              fill="#15803d"
            />
          </g>

          {/* Glowing Mid-Ocean Tectonic Rift Network (65,000 km oceanic fault) */}
          <g filter="url(#riftGlow)" opacity={pulseRift}>
            {/* Mid-Atlantic Ridge */}
            <path
              d="M 148 35 Q 140 85 145 135 Q 135 195 148 275"
              fill="none"
              stroke="#f97316"
              strokeWidth="4.5"
              strokeLinecap="round"
            />
            {/* Pacific Ring fault branch */}
            <path
              d="M 65 95 Q 75 160 85 235"
              fill="none"
              stroke="#fbbf24"
              strokeWidth="3.5"
              strokeLinecap="round"
            />
            {/* Indian Ocean Triple Junction branch */}
            <path
              d="M 145 155 Q 185 185 235 210"
              fill="none"
              stroke="#f97316"
              strokeWidth="4"
              strokeLinecap="round"
            />
            {/* Magma hot spot nodes */}
            <circle cx="145" cy="135" r="5" fill="#fef08a" />
            <circle cx="140" cy="85" r="4" fill="#fef08a" />
            <circle cx="145" cy="195" r="4.5" fill="#fef08a" />
            <circle cx="195" cy="190" r="4" fill="#fef08a" />
          </g>

          {/* Coordinate Latitude & Longitude Grid Rings */}
          <ellipse cx="160" cy="160" rx="135" ry="55" fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth="1" strokeDasharray="4 6" />
          <line x1="160" y1="25" x2="160" y2="295" stroke="rgba(255,255,255,0.18)" strokeWidth="1" strokeDasharray="4 6" />
        </svg>
      </div>

      {/* 3. Metric Badge */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          marginTop: 18,
          padding: '10px 32px',
          borderRadius: 20,
          backgroundColor: 'rgba(249, 115, 22, 0.18)',
          border: '1.5px solid rgba(249, 115, 22, 0.65)',
          boxShadow: '0 8px 24px rgba(0,0,0,0.6), 0 0 20px rgba(249, 115, 22, 0.3)',
        }}
      >
        <div
          style={{
            fontFamily: '"Cinzel", "Montserrat", sans-serif',
            fontSize: 48,
            fontWeight: 900,
            color: '#fef08a',
            lineHeight: 1,
            textShadow: '0 0 20px rgba(249, 115, 22, 0.75)',
          }}
        >
          {metricNumber}
        </div>
        <div
          style={{
            fontSize: 16,
            fontWeight: 800,
            letterSpacing: '2.5px',
            color: '#ffffff',
            textTransform: 'uppercase',
            marginTop: 6,
            textAlign: 'center',
          }}
        >
          {metricLabel}
        </div>
      </div>
    </div>
  );
};
