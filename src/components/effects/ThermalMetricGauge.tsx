import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface ThermalMetricGaugeProps {
  currentTemp?: number; // Target temperature in °C (e.g. 1200)
  title?: string;
  subtitle?: string;
}

export const ThermalMetricGauge: React.FC<ThermalMetricGaugeProps> = ({
  currentTemp = 1200,
  title = 'OKYANUS TABANINDAKİ MAGMA SICAKLIĞI',
  subtitle = 'MİLYARLARCA TON SUYUN SÖNDÜREMEDİĞİ İLAHİ ATEŞ',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 85, mass: 0.9 },
  });

  const fadeIn = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });
  const gentleFloat = Math.sin(frame * 0.06) * 4;

  // Animated temperature counter (from 0 to currentTemp)
  const animatedTemp = Math.round(
    interpolate(frame, [8, 45], [0, currentTemp], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  // Gauge bar progress (0% to 100%)
  const gaugeProgress = interpolate(frame, [8, 45], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

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
        backgroundColor: 'rgba(3, 7, 18, 0.85)',
        border: '1.5px solid rgba(239, 68, 68, 0.55)',
        boxShadow: '0 16px 45px rgba(0, 0, 0, 0.9), 0 0 35px rgba(239, 68, 68, 0.3)',
        backdropFilter: 'blur(24px)',
        maxWidth: 880,
        margin: '16px auto',
        zIndex: 10,
      }}
    >
      {/* 1. Gauge Title */}
      {title && (
        <div
          style={{
            fontFamily: '"Cinzel", "Montserrat", sans-serif',
            fontSize: 22,
            fontWeight: 800,
            letterSpacing: '3px',
            color: '#fca5a5',
            textTransform: 'uppercase',
            textAlign: 'center',
            marginBottom: 16,
            textShadow: '0 0 15px rgba(239, 68, 68, 0.6)',
          }}
        >
          {title}
        </div>
      )}

      {/* 2. Hero Metric: Animated 1200°C Display */}
      <div
        style={{
          display: 'flex',
          alignItems: 'baseline',
          justifyContent: 'center',
          gap: 8,
          marginBottom: 16,
        }}
      >
        <span
          style={{
            fontFamily: '"Cinzel", "Montserrat", sans-serif',
            fontSize: 84,
            fontWeight: 900,
            color: '#ffffff',
            lineHeight: 1,
            textShadow: '0 0 25px rgba(239, 68, 68, 0.85), 0 0 50px rgba(249, 115, 22, 0.5)',
            background: 'linear-gradient(180deg, #ffffff 0%, #fef08a 40%, #f97316 75%, #ef4444 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          {animatedTemp}°C
        </span>
        <span
          style={{
            fontSize: 22,
            fontWeight: 800,
            letterSpacing: '3px',
            color: '#f97316',
            textTransform: 'uppercase',
          }}
        >
          ERİMİŞ MAGMA
        </span>
      </div>

      {/* 3. Horizontal Thermal Gradient Bar */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: 620,
          height: 24,
          borderRadius: 12,
          backgroundColor: 'rgba(15, 23, 42, 0.85)',
          border: '1.5px solid rgba(255, 255, 255, 0.15)',
          overflow: 'hidden',
          marginBottom: 12,
        }}
      >
        <div
          style={{
            width: `${gaugeProgress}%`,
            height: '100%',
            borderRadius: 12,
            background: 'linear-gradient(90deg, #0284c7 0%, #eab308 35%, #f97316 70%, #ef4444 100%)',
            boxShadow: '0 0 20px rgba(239, 68, 68, 0.8)',
            transition: 'width 0.1s linear',
          }}
        />
      </div>

      {/* 4. Thermal Scale Reference Markers */}
      <div
        style={{
          width: '100%',
          maxWidth: 620,
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: 14,
          fontWeight: 700,
          color: '#94a3b8',
          letterSpacing: '1px',
          marginBottom: 16,
        }}
      >
        <span>2°C (Dip Suyu)</span>
        <span>100°C (Kaynama)</span>
        <span>400°C (Bacalar)</span>
        <span style={{ color: '#ef4444', fontWeight: 900 }}>1200°C (Magma)</span>
      </div>

      {/* 5. Subtitle & Spiritual Contemplation */}
      {subtitle && (
        <div
          style={{
            fontFamily: '"Cormorant Garamond", Georgia, serif',
            fontSize: 24,
            fontWeight: 700,
            fontStyle: 'italic',
            color: '#fef08a',
            textAlign: 'center',
            textShadow: '0 2px 10px rgba(0,0,0,0.85)',
            paddingTop: 10,
            borderTop: '1px solid rgba(255, 255, 255, 0.1)',
            width: '100%',
          }}
        >
          «{subtitle}»
        </div>
      )}
    </div>
  );
};
