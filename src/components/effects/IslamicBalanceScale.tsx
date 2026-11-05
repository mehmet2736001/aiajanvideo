import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface IslamicBalanceScaleProps {
  leftLabel?: string;
  rightLabel?: string;
  leftCount?: number;
  rightCount?: number;
  leftSubtext?: string;
  rightSubtext?: string;
  title?: string;
  isBalanced?: boolean;
  themeColor?: string;
}

export const IslamicBalanceScale: React.FC<IslamicBalanceScaleProps> = ({
  leftLabel = 'TEK (FERDÎ)',
  rightLabel = 'ÇİFT (ZEVCÎ)',
  leftCount = 57,
  rightCount = 57,
  leftSubtext = 'TOPLAM: 6.555',
  rightSubtext = 'TOPLAM: 6.236',
  title = '114 SÛRENİN KUSURSUZ MİZANI',
  isBalanced = true,
  themeColor = '#10b981', // Emerald green
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Spring entrance
  const entrance = spring({
    frame,
    fps,
    config: { damping: 16, stiffness: 85, mass: 0.9 },
  });

  const fadeIn = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const gentleFloat = Math.sin(frame * 0.05) * 4;

  // Animated numerical counters
  const currentLeft = Math.round(
    interpolate(frame, [10, 50], [0, leftCount], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  const currentRight = Math.round(
    interpolate(frame, [10, 50], [0, rightCount], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  // Dynamic scale tilt animation: starts tilting/oscillating, then settles to 0 deg balance
  const beamAngle = interpolate(
    frame,
    [0, 15, 30, 45, 60],
    [-7, 5, -3, 1.5, 0],
    { extrapolateRight: 'clamp' }
  );

  // Left and Right pan vertical displacements based on beam tilt
  // Beam length = 460px (230px each arm)
  // Displacement = 230 * sin(angle in radians)
  const angleRad = (beamAngle * Math.PI) / 180;
  const leftOffsetY = -Math.sin(angleRad) * 230;
  const rightOffsetY = Math.sin(angleRad) * 230;

  // Ambient glow pulse
  const glowPulse = 0.85 + Math.sin(frame * 0.08) * 0.15;

  return (
    <div
      style={{
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        opacity: fadeIn,
        transform: `scale(${entrance}) translateY(${gentleFloat}px)`,
        padding: '24px 32px',
        borderRadius: 28,
        backgroundColor: 'rgba(3, 18, 12, 0.85)',
        border: '1.5px solid rgba(16, 185, 129, 0.45)',
        boxShadow: '0 16px 45px rgba(0, 0, 0, 0.9), 0 0 35px rgba(16, 185, 129, 0.25)',
        backdropFilter: 'blur(24px)',
        maxWidth: 920,
        margin: '16px auto',
        zIndex: 10,
      }}
    >
      {/* 1. Header Title */}
      {title && (
        <div
          style={{
            fontFamily: '"Cinzel", "Amiri", serif',
            fontSize: 24,
            fontWeight: 800,
            letterSpacing: '3px',
            color: '#a7f3d0',
            textTransform: 'uppercase',
            textAlign: 'center',
            marginBottom: 14,
            textShadow: '0 0 15px rgba(16, 185, 129, 0.6)',
          }}
        >
          {title}
        </div>
      )}

      {/* 2. Interactive SVG Balance Scale */}
      <div style={{ position: 'relative', width: 620, height: 350 }}>
        <svg viewBox="0 0 620 350" style={{ width: '100%', height: '100%' }}>
          <defs>
            {/* Scale Gold/Emerald Glow */}
            <filter id="scaleGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="5" result="blur1" />
              <feGaussianBlur in="SourceGraphic" stdDeviation="12" result="blur2" />
              <feMerge>
                <feMergeNode in="blur2" />
                <feMergeNode in="blur1" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>

            {/* Sacred Geometry Watermark Background */}
            <radialGradient id="sacredAura" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#042f2e" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Central Sacred Halo */}
          <circle cx="310" cy="160" r="130" fill="url(#sacredAura)" />

          {/* Vertical Central Fulcrum Pillar */}
          <line x1="310" y1="45" x2="310" y2="290" stroke="#fef08a" strokeWidth="2.5" />
          <path d="M 270 290 Q 310 260 350 290" fill="none" stroke="#fef08a" strokeWidth="2.5" />

          {/* Top Decorative Diamond / Star Node */}
          <circle cx="310" cy="45" r="9" fill="#10b981" filter="url(#scaleGlow)" />
          <circle cx="310" cy="45" r="4.5" fill="#ffffff" />

          {/* Tilting Crossbeam Assembly */}
          <g transform={`rotate(${beamAngle} 310 45)`}>
            {/* Main Crossbeam Arm */}
            <line x1="80" y1="45" x2="540" y2="45" stroke="#fef08a" strokeWidth="3" filter="url(#scaleGlow)" />
            {/* Left suspension hook */}
            <circle cx="80" cy="45" r="5" fill="#fef08a" />
            {/* Right suspension hook */}
            <circle cx="540" cy="45" r="5" fill="#fef08a" />
          </g>

          {/* LEFT SUSPENDED PAN (TEK / FERDÎ) */}
          <g transform={`translate(0, ${leftOffsetY})`}>
            {/* Suspension Strings */}
            <line x1="80" y1={45 - leftOffsetY} x2="30" y2="190" stroke="rgba(167, 243, 208, 0.7)" strokeWidth="1.2" />
            <line x1="80" y1={45 - leftOffsetY} x2="130" y2="190" stroke="rgba(167, 243, 208, 0.7)" strokeWidth="1.2" />
            {/* Pan Dish */}
            <path
              d="M 25 190 Q 80 235 135 190 Z"
              fill="rgba(16, 185, 129, 0.35)"
              stroke="#6ee7b7"
              strokeWidth="2"
              filter="url(#scaleGlow)"
            />
            {/* Glowing Stardust Orbs in Pan */}
            {Array.from({ length: 12 }).map((_, i) => (
              <circle
                key={`left_orb_${i}`}
                cx={45 + i * 6.5 + Math.sin(i * 3) * 4}
                cy={198 + Math.cos(i * 2) * 6}
                r={2.5 + (i % 3)}
                fill="#a7f3d0"
                opacity={glowPulse}
              />
            ))}
          </g>

          {/* RIGHT SUSPENDED PAN (ÇİFT / ZEVCÎ) */}
          <g transform={`translate(0, ${rightOffsetY})`}>
            {/* Suspension Strings */}
            <line x1="540" y1={45 - rightOffsetY} x2="490" y2="190" stroke="rgba(254, 240, 138, 0.7)" strokeWidth="1.2" />
            <line x1="540" y1={45 - rightOffsetY} x2="590" y2="190" stroke="rgba(254, 240, 138, 0.7)" strokeWidth="1.2" />
            {/* Pan Dish */}
            <path
              d="M 485 190 Q 540 235 595 190 Z"
              fill="rgba(245, 158, 11, 0.35)"
              stroke="#fcd34d"
              strokeWidth="2"
              filter="url(#scaleGlow)"
            />
            {/* Glowing Stardust Orbs in Pan */}
            {Array.from({ length: 12 }).map((_, i) => (
              <circle
                key={`right_orb_${i}`}
                cx={505 + i * 6.5 + Math.sin(i * 3) * 4}
                cy={198 + Math.cos(i * 2) * 6}
                r={2.5 + (i % 3)}
                fill="#fef08a"
                opacity={glowPulse}
              />
            ))}
          </g>
        </svg>

        {/* Left Pan Quantitative Display */}
        <div
          style={{
            position: 'absolute',
            bottom: 15,
            left: 20,
            width: 140,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
          }}
        >
          <div
            style={{
              fontFamily: '"Cinzel", "Montserrat", sans-serif',
              fontSize: 48,
              fontWeight: 900,
              color: '#6ee7b7',
              lineHeight: 1,
              textShadow: '0 0 20px rgba(16, 185, 129, 0.8)',
            }}
          >
            {currentLeft}
          </div>
          <div
            style={{
              fontSize: 15,
              fontWeight: 800,
              letterSpacing: '1.5px',
              color: '#ffffff',
              marginTop: 4,
            }}
          >
            {leftLabel}
          </div>
          {leftSubtext && (
            <div style={{ fontSize: 12, color: '#a7f3d0', marginTop: 2, fontWeight: 700 }}>
              {leftSubtext}
            </div>
          )}
        </div>

        {/* Right Pan Quantitative Display */}
        <div
          style={{
            position: 'absolute',
            bottom: 15,
            right: 20,
            width: 140,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
          }}
        >
          <div
            style={{
              fontFamily: '"Cinzel", "Montserrat", sans-serif',
              fontSize: 48,
              fontWeight: 900,
              color: '#fde047',
              lineHeight: 1,
              textShadow: '0 0 20px rgba(245, 158, 11, 0.8)',
            }}
          >
            {currentRight}
          </div>
          <div
            style={{
              fontSize: 15,
              fontWeight: 800,
              letterSpacing: '1.5px',
              color: '#ffffff',
              marginTop: 4,
            }}
          >
            {rightLabel}
          </div>
          {rightSubtext && (
            <div style={{ fontSize: 12, color: '#fef08a', marginTop: 2, fontWeight: 700 }}>
              {rightSubtext}
            </div>
          )}
        </div>
      </div>

      {/* 3. Perfect Equilibrium Proof Badge */}
      {isBalanced && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            marginTop: 12,
            padding: '8px 26px',
            borderRadius: 9999,
            backgroundColor: 'rgba(16, 185, 129, 0.2)',
            border: '1.5px solid rgba(16, 185, 129, 0.65)',
            boxShadow: '0 8px 24px rgba(0,0,0,0.6), 0 0 20px rgba(16, 185, 129, 0.35)',
          }}
        >
          <span style={{ color: '#facc15', fontSize: 18 }}>⚖️</span>
          <span
            style={{
              fontFamily: '"Cinzel", "Montserrat", sans-serif',
              fontSize: 18,
              fontWeight: 900,
              letterSpacing: '2px',
              color: '#f8fafc',
              textTransform: 'uppercase',
            }}
          >
            {leftCount} TEK = {rightCount} ÇİFT = 114 SÛRE
          </span>
          <span style={{ color: '#facc15', fontSize: 18 }}>⚖️</span>
        </div>
      )}
    </div>
  );
};
