import React from 'react';
import { useCurrentFrame } from 'remotion';

interface CaveSilhouetteFrameProps {
  glowColor?: string;
  theme?: string;
}

export const CaveSilhouetteFrame: React.FC<CaveSilhouetteFrameProps> = ({
  glowColor = 'rgba(245, 158, 11, 0.55)',
  theme = 'gold_luxury',
}) => {
  const frame = useCurrentFrame();

  // Subtle organic breathing animation for the rim lighting
  const rimPulse = 0.82 + Math.sin(frame * 0.045) * 0.18;
  const cyanPulse = 0.75 + Math.cos(frame * 0.05) * 0.2;

  // Organic cave cutout path (starts at top center, traces natural craggy cavern edges)
  const cavePath = `
    M 540 60
    C 740 68, 920 140, 990 320
    C 1045 460, 1020 720, 1050 980
    C 1070 1220, 1030 1480, 980 1680
    C 940 1810, 780 1875, 540 1880
    C 300 1875, 140 1810, 100 1680
    C 50 1480, 10 1220, 30 980
    C 60 720, 35 460, 90 320
    C 160 140, 340 68, 540 60 Z
  `;

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: 1080,
        height: 1920,
        zIndex: 5,
        pointerEvents: 'none',
        overflow: 'hidden',
      }}
    >
      <svg
        viewBox="0 0 1080 1920"
        style={{
          width: '100%',
          height: '100%',
        }}
      >
        <defs>
          {/* Luminous Gaussian blur filters for intense rim glow */}
          <filter id="caveRimGlow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur1" />
            <feGaussianBlur in="SourceGraphic" stdDeviation="24" result="blur2" />
            <feGaussianBlur in="SourceGraphic" stdDeviation="45" result="blur3" />
            <feMerge>
              <feMergeNode in="blur3" />
              <feMergeNode in="blur2" />
              <feMergeNode in="blur1" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Mask that cuts out the cavern center opening */}
          <mask id="organicCaveMask">
            {/* White base reveals the dark rock surround */}
            <rect x="0" y="0" width="1080" height="1920" fill="#ffffff" />
            {/* Black silhouette path punches out the transparent center window */}
            <path d={cavePath} fill="#000000" />
          </mask>

          {/* Vignette Gradient for deep craggy rock borders */}
          <radialGradient id="cavernVignette" cx="50%" cy="50%" r="62%">
            <stop offset="68%" stopColor="#04070d" stopOpacity="0.88" />
            <stop offset="90%" stopColor="#020306" stopOpacity="0.97" />
            <stop offset="100%" stopColor="#010103" stopOpacity="0.99" />
          </radialGradient>
        </defs>

        {/* 1. Deep Cavern Rock Border Frame */}
        <rect
          x="0"
          y="0"
          width="1080"
          height="1920"
          fill="url(#cavernVignette)"
          mask="url(#organicCaveMask)"
        />

        {/* 2. Primary Luminous Golden Rim Contour */}
        <path
          d={cavePath}
          stroke="rgba(245, 158, 11, 0.72)"
          strokeWidth="3.5"
          fill="none"
          filter="url(#caveRimGlow)"
          opacity={rimPulse}
        />

        {/* 3. Secondary Ethereal Cyan / Sky Blue Inner Rim Filament */}
        <path
          d={cavePath}
          stroke="rgba(56, 189, 248, 0.45)"
          strokeWidth="1.5"
          fill="none"
          opacity={cyanPulse}
        />
      </svg>
    </div>
  );
};
