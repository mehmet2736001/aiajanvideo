import React from 'react';
import { useCurrentFrame } from 'remotion';

export type FilmGrainMode = 'none' | 'subtle' | 'vintage' | 'heavy';

interface FilmGrainOverlayProps {
  mode?: FilmGrainMode;
  opacity?: number;
}

export const FilmGrainOverlay: React.FC<FilmGrainOverlayProps> = ({
  mode = 'subtle',
  opacity,
}) => {
  const frame = useCurrentFrame();

  if (mode === 'none') return null;

  // Change noise seed every 2 frames for realistic 24-30fps analog film grain flutter
  const seed = Math.floor(frame / 2) % 100;

  const baseOpacity =
    opacity !== undefined
      ? opacity
      : mode === 'vintage'
      ? 0.18
      : mode === 'heavy'
      ? 0.28
      : 0.09; // subtle

  const baseFrequency = mode === 'vintage' ? '0.75' : '0.9';

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
        zIndex: 40,
        opacity: baseOpacity,
        mixBlendMode: 'overlay',
      }}
    >
      <svg
        style={{
          width: '100%',
          height: '100%',
        }}
        xmlns="http://www.w3.org/2000/svg"
      >
        <filter id={`film-grain-filter-${seed}`}>
          <feTurbulence
            type="fractalNoise"
            baseFrequency={baseFrequency}
            numOctaves="3"
            seed={seed}
            stitchTiles="stitch"
          />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect
          width="100%"
          height="100%"
          filter={`url(#film-grain-filter-${seed})`}
        />
      </svg>
    </div>
  );
};
