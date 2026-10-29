import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';

interface WatermarkProps {
  pattern?: 'fingerprint' | 'dna' | 'cosmic' | 'grid' | 'none';
  theme?: string;
}

export const BackgroundWatermark: React.FC<WatermarkProps> = ({
  pattern = 'fingerprint',
  theme = 'dark_minimalist',
}) => {
  const frame = useCurrentFrame();

  if (pattern === 'none') return null;

  // Slow subtle rotation for hypnotic motion
  const rotation = interpolate(frame, [0, 900], [0, 18], {
    extrapolateRight: 'extend',
  });

  const strokeColor =
    theme === 'neon_cyber'
      ? '#38bdf8'
      : theme === 'gold_luxury'
      ? '#d97706'
      : '#94a3b8';

  const opacity =
    theme === 'dark_minimalist' || theme === 'gold_luxury' || theme === 'neon_cyber'
      ? 0.08
      : 0.05;

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: 1080,
        height: 1920,
        pointerEvents: 'none',
        overflow: 'hidden',
        zIndex: 1,
        opacity,
      }}
    >
      {pattern === 'fingerprint' && (
        <>
          {/* Top-Right Fingerprint Loop */}
          <div
            style={{
              position: 'absolute',
              top: -80,
              right: -100,
              width: 600,
              height: 750,
              transform: `rotate(${rotation * 0.5}deg)`,
            }}
          >
            <svg viewBox="0 0 400 500" fill="none" stroke={strokeColor} strokeWidth="3.5" strokeLinecap="round">
              <path d="M 200 120 C 140 120 100 180 100 250 C 100 350 140 430 200 450" />
              <path d="M 200 150 C 160 150 130 195 130 250 C 130 330 160 395 200 420" />
              <path d="M 200 180 C 180 180 160 210 160 250 C 160 310 180 360 200 390" />
              <path d="M 200 90 C 120 90 70 165 70 250 C 70 370 120 460 200 480" />
              <path d="M 200 120 C 260 120 300 180 300 250 C 300 350 260 430 200 450" />
              <path d="M 200 150 C 240 150 270 195 270 250 C 270 330 240 395 200 420" />
              <path d="M 200 180 C 220 180 240 210 240 250 C 240 310 220 360 200 390" />
              <path d="M 200 90 C 280 90 330 165 330 250 C 330 370 280 460 200 480" />
              <circle cx="200" cy="250" r="18" />
            </svg>
          </div>

          {/* Bottom-Left Fingerprint Loop */}
          <div
            style={{
              position: 'absolute',
              bottom: 80,
              left: -120,
              width: 650,
              height: 800,
              transform: `rotate(${-rotation * 0.4}deg)`,
            }}
          >
            <svg viewBox="0 0 400 500" fill="none" stroke={strokeColor} strokeWidth="3.5" strokeLinecap="round">
              <path d="M 200 120 C 140 120 100 180 100 250 C 100 350 140 430 200 450" />
              <path d="M 200 150 C 160 150 130 195 130 250 C 130 330 160 395 200 420" />
              <path d="M 200 180 C 180 180 160 210 160 250 C 160 310 180 360 200 390" />
              <path d="M 200 90 C 120 90 70 165 70 250 C 70 370 120 460 200 480" />
              <path d="M 200 120 C 260 120 300 180 300 250 C 300 350 260 430 200 450" />
              <path d="M 200 150 C 240 150 270 195 270 250 C 270 330 240 395 200 420" />
              <path d="M 200 180 C 220 180 240 210 240 250 C 240 310 220 360 200 390" />
              <path d="M 200 90 C 280 90 330 165 330 250 C 330 370 280 460 200 480" />
            </svg>
          </div>
        </>
      )}

      {pattern === 'islamic_geometric' && (
        <div
          style={{
            position: 'absolute',
            top: 250,
            left: -100,
            width: 1280,
            height: 1280,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transform: `rotate(${rotation * 0.4}deg)`,
          }}
        >
          <svg width="1000" height="1000" viewBox="0 0 400 400" fill="none" stroke={strokeColor} strokeWidth="2.5">
            <g transform="translate(200, 200)">
              <circle cx="0" cy="0" r="170" strokeDasharray="10 6" />
              <circle cx="0" cy="0" r="120" />
              <circle cx="0" cy="0" r="70" />
              <rect x="-85" y="-85" width="170" height="170" />
              <rect x="-85" y="-85" width="170" height="170" transform="rotate(45)" />
              <rect x="-85" y="-85" width="170" height="170" transform="rotate(22.5)" />
              <rect x="-85" y="-85" width="170" height="170" transform="rotate(67.5)" />
            </g>
          </svg>
        </div>
      )}

      {pattern === 'cosmic' && (
        <div
          style={{
            position: 'absolute',
            top: 200,
            left: 40,
            width: 1000,
            height: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transform: `rotate(${rotation * 0.3}deg)`,
          }}
        >
          <svg width="900" height="900" viewBox="0 0 400 400" fill="none" stroke={strokeColor} strokeWidth="2">
            <circle cx="200" cy="200" r="180" strokeDasharray="8 6"/>
            <circle cx="200" cy="200" r="130"/>
            <circle cx="200" cy="200" r="80" strokeDasharray="4 4"/>
            <line x1="20" y1="200" x2="380" y2="200"/>
            <line x1="200" y1="20" x2="200" y2="380"/>
          </svg>
        </div>
      )}

      {pattern === 'dna' && (
        <div
          style={{
            position: 'absolute',
            top: 200,
            left: 100,
            width: 880,
            height: 1500,
            display: 'flex',
            justifyContent: 'center',
          }}
        >
          <svg width="400" height="1400" viewBox="0 0 200 700" fill="none" stroke={strokeColor} strokeWidth="3">
            {Array.from({ length: 14 }).map((_, i) => {
              const y = 30 + i * 48;
              const w = 40 + Math.sin(i * 0.7 + frame * 0.04) * 35;
              return (
                <g key={i}>
                  <line x1={100 - w} y1={y} x2={100 + w} y2={y} strokeWidth="2.5" />
                  <circle cx={100 - w} cy={y} r="5" fill={strokeColor} />
                  <circle cx={100 + w} cy={y} r="5" fill={strokeColor} />
                </g>
              );
            })}
          </svg>
        </div>
      )}
    </div>
  );
};
