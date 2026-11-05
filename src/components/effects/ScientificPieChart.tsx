import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface ScientificPieChartProps {
  primaryPercentage?: number;
  primaryLabel?: string;
  secondaryLabel?: string;
  title?: string;
  subtitle?: string;
  primaryColor?: string;
  secondaryColor?: string;
}

export const ScientificPieChart: React.FC<ScientificPieChartProps> = ({
  primaryPercentage = 80,
  primaryLabel = 'OKYANUS TABANI',
  secondaryLabel = 'KARALAR',
  title = 'TÜM VOLKANİK PATLAMALARIN',
  subtitle = "YÜZDE 80'DEN FAZLASI DENİZ ALTINDA",
  primaryColor = '#f97316', // Magma Orange
  secondaryColor = '#475569', // Cool Slate
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Spring entrance for container scale & opacity
  const entrance = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 90, mass: 0.85 },
  });

  const fadeIn = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });
  const gentleFloat = Math.sin(frame * 0.05) * 5;

  // Animated percentage counter from 0 to primaryPercentage
  const currentPercent = Math.round(
    interpolate(frame, [10, 45], [0, primaryPercentage], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  // SVG Circle stroke parameters (Radius = 120, Circumference = 2 * PI * 120 ≈ 753.98)
  const radius = 120;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (currentPercent / 100) * circumference;

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
        padding: '24px 36px',
        borderRadius: 28,
        backgroundColor: 'rgba(3, 7, 18, 0.82)',
        border: '1.5px solid rgba(249, 115, 22, 0.45)',
        boxShadow: '0 16px 45px rgba(0, 0, 0, 0.9), 0 0 35px rgba(249, 115, 22, 0.25)',
        backdropFilter: 'blur(24px)',
        maxWidth: 880,
        margin: '16px auto',
        zIndex: 10,
      }}
    >
      {/* 1. Header Title */}
      {title && (
        <div
          style={{
            fontFamily: '"Cinzel", "Montserrat", sans-serif',
            fontSize: 24,
            fontWeight: 800,
            letterSpacing: '3px',
            color: '#f8fafc',
            textTransform: 'uppercase',
            textAlign: 'center',
            marginBottom: 20,
            textShadow: '0 2px 12px rgba(0,0,0,0.8)',
          }}
        >
          {title}
        </div>
      )}

      {/* 2. SVG Donut Chart with Dynamic Glowing Magma Arc */}
      <div style={{ position: 'relative', width: 300, height: 300 }}>
        <svg viewBox="0 0 300 300" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
          <defs>
            {/* Magma Arc Glow Filter */}
            <filter id="magmaGlow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur1" />
              <feGaussianBlur in="SourceGraphic" stdDeviation="14" result="blur2" />
              <feMerge>
                <feMergeNode in="blur2" />
                <feMergeNode in="blur1" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>

            <linearGradient id="magmaGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#fef08a" />
              <stop offset="45%" stopColor="#f97316" />
              <stop offset="100%" stopColor="#dc2626" />
            </linearGradient>
          </defs>

          {/* Background Ring (Secondary Slice - Land 20%) */}
          <circle
            cx="150"
            cy="150"
            r={radius}
            fill="transparent"
            stroke={secondaryColor}
            strokeWidth="32"
            opacity={0.35}
          />

          {/* Active Animated Magma Arc (Primary Slice - Ocean 80%) */}
          <circle
            cx="150"
            cy="150"
            r={radius}
            fill="transparent"
            stroke="url(#magmaGradient)"
            strokeWidth="34"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            filter="url(#magmaGlow)"
          />
        </svg>

        {/* Center Text: Dynamic Percentage Counter */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            pointerEvents: 'none',
          }}
        >
          <div
            style={{
              fontFamily: '"Cinzel", "Montserrat", sans-serif',
              fontSize: 64,
              fontWeight: 900,
              color: '#ffffff',
              lineHeight: 1,
              textShadow: '0 0 25px rgba(249, 115, 22, 0.7), 0 4px 15px rgba(0,0,0,0.95)',
            }}
          >
            %{currentPercent}
          </div>
          <div
            style={{
              fontSize: 16,
              fontWeight: 800,
              letterSpacing: '2px',
              color: '#fbbf24',
              textTransform: 'uppercase',
              marginTop: 6,
            }}
          >
            {primaryLabel}
          </div>
        </div>
      </div>

      {/* 3. Legend & Comparative Callout */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 36,
          marginTop: 22,
          padding: '12px 28px',
          borderRadius: 9999,
          backgroundColor: 'rgba(5, 10, 22, 0.65)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 14, height: 14, borderRadius: '50%', backgroundColor: primaryColor, boxShadow: `0 0 10px ${primaryColor}` }} />
          <span style={{ fontSize: 18, fontWeight: 700, color: '#fef08a' }}>{primaryLabel} (%{primaryPercentage})</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 14, height: 14, borderRadius: '50%', backgroundColor: secondaryColor }} />
          <span style={{ fontSize: 18, fontWeight: 700, color: '#94a3b8' }}>{secondaryLabel} (%{100 - primaryPercentage})</span>
        </div>
      </div>

      {/* 4. Subtitle / Revelation Conclusion */}
      {subtitle && (
        <div
          style={{
            fontFamily: '"Cormorant Garamond", Georgia, serif',
            fontSize: 26,
            fontWeight: 700,
            fontStyle: 'italic',
            color: '#fef08a',
            textAlign: 'center',
            marginTop: 18,
            textShadow: '0 2px 10px rgba(0,0,0,0.85)',
          }}
        >
          «{subtitle}»
        </div>
      )}
    </div>
  );
};
