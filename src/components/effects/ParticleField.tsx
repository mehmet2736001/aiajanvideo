import React from 'react';
import { useCurrentFrame } from 'remotion';

interface ParticleFieldProps {
  type?: 'dust' | 'stars' | 'fireflies' | 'none';
  count?: number;
  color?: string;
}

// 40 deterministic pseudo-random particle initial states
const PARTICLES = Array.from({ length: 42 }).map((_, i) => ({
  x: ((i * 137.5) % 1080),
  y: ((i * 223.7) % 1920),
  size: 2 + (i % 5) * 1.5,
  speed: 0.6 + (i % 4) * 0.4,
  driftPhase: (i * 0.4) % (Math.PI * 2),
  baseOpacity: 0.25 + (i % 6) * 0.12,
}));

export const ParticleField: React.FC<ParticleFieldProps> = ({
  type = 'dust',
  count = 35,
  color = '#fef08a',
}) => {
  const frame = useCurrentFrame();

  if (type === 'none') return null;

  const activeParticles = PARTICLES.slice(0, count);

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
        zIndex: 2,
      }}
    >
      {activeParticles.map((p, idx) => {
        // Vertical upward float with wrap-around
        const currentY = (p.y - frame * p.speed + 1920 * 10) % 1920;
        // Horizontal gentle drift
        const currentX = (p.x + Math.sin(frame * 0.03 + p.driftPhase) * 28 + 1080) % 1080;
        // Twinkle pulse
        const opacity = Math.min(1, Math.max(0.1, p.baseOpacity + Math.sin(frame * 0.05 + idx) * 0.35));

        const glowSize = type === 'fireflies' ? p.size * 3.5 : p.size * 2;
        const particleColor = type === 'fireflies' ? '#fde047' : type === 'stars' ? '#38bdf8' : color;

        return (
          <div
            key={idx}
            style={{
              position: 'absolute',
              left: currentX,
              top: currentY,
              width: p.size,
              height: p.size,
              borderRadius: '50%',
              backgroundColor: particleColor,
              opacity,
              boxShadow: `0 0 ${glowSize}px ${particleColor}`,
            }}
          />
        );
      })}
    </div>
  );
};
