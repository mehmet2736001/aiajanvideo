import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';

interface DoodleProps {
  theme?: string;
}

export const DoodleDecorations: React.FC<DoodleProps> = ({ theme = 'notebook' }) => {
  const frame = useCurrentFrame();

  const isChalkboard = theme === 'chalkboard';
  const isBlueprint = theme === 'blueprint';
  const isParchment = theme === 'parchment';

  const tapeColor = isChalkboard
    ? 'rgba(255, 255, 255, 0.15)'
    : isBlueprint
    ? 'rgba(56, 189, 248, 0.25)'
    : 'rgba(251, 191, 36, 0.65)';

  const starColor = isChalkboard ? '#fef08a' : isBlueprint ? '#38bdf8' : isParchment ? '#b45309' : '#f59e0b';

  const starPulse = interpolate(frame % 30, [0, 15, 30], [0.85, 1.15, 0.85]);

  return (
    <>
      {/* Top Left Washi Tape */}
      <div
        style={{
          position: 'absolute',
          top: 35,
          left: 50,
          width: 110,
          height: 28,
          backgroundColor: tapeColor,
          transform: 'rotate(-25deg)',
          zIndex: 5,
          pointerEvents: 'none',
          boxShadow: '0 2px 6px rgba(0,0,0,0.08)',
        }}
      />

      {/* Top Right Washi Tape */}
      <div
        style={{
          position: 'absolute',
          top: 35,
          right: 50,
          width: 110,
          height: 28,
          backgroundColor: tapeColor,
          transform: 'rotate(25deg)',
          zIndex: 5,
          pointerEvents: 'none',
          boxShadow: '0 2px 6px rgba(0,0,0,0.08)',
        }}
      />

      {/* Sparkle Star 1 (Near Header) */}
      <div
        style={{
          position: 'absolute',
          top: 140,
          right: 80,
          transform: `scale(${starPulse})`,
          zIndex: 5,
          pointerEvents: 'none',
        }}
      >
        <svg width="44" height="44" viewBox="0 0 40 40" fill={starColor}>
          <path d="M 20 0 L 23 15 L 38 20 L 23 25 L 20 40 L 17 25 L 2 20 L 17 15 Z" />
        </svg>
      </div>

      {/* Sparkle Star 2 (Near Left Middle) */}
      <div
        style={{
          position: 'absolute',
          top: 340,
          left: 60,
          transform: `scale(${starPulse}) rotate(15deg)`,
          zIndex: 5,
          pointerEvents: 'none',
        }}
      >
        <svg width="32" height="32" viewBox="0 0 40 40" fill={starColor} opacity={0.8}>
          <path d="M 20 0 L 23 15 L 38 20 L 23 25 L 20 40 L 17 25 L 2 20 L 17 15 Z" />
        </svg>
      </div>
    </>
  );
};
