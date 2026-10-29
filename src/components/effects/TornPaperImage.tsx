import React from 'react';
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';

export interface TornPaperImageProps {
  imageSrc: string;
  caption?: string;
  rotation?: number;
  width?: number;
  style?: React.CSSProperties;
  isRTL?: boolean;
}

export const TornPaperImage: React.FC<TornPaperImageProps> = ({
  imageSrc,
  caption,
  rotation = 1.8,
  width = 620,
  style = {},
  isRTL = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 13, stiffness: 95 }
  });

  const scale = interpolate(entrance, [0, 1], [0.92, 1.0]);
  const opacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });
  const subtleFloat = Math.sin(frame / 28) * 3;

  const fullSrc = imageSrc.startsWith('http')
    ? imageSrc
    : staticFile(imageSrc.startsWith('/') ? imageSrc.slice(1) : imageSrc);

  return (
    <div
      style={{
        position: 'relative',
        display: 'inline-block',
        userSelect: 'none',
        transform: `translateY(${subtleFloat}px) scale(${scale}) rotate(${rotation}deg)`,
        opacity,
        filter: 'drop-shadow(0 20px 30px rgba(0,0,0,0.6))',
        ...style
      }}
    >
      {/* Tape Strip across the center top */}
      <div
        style={{
          position: 'absolute',
          top: -12,
          left: '50%',
          transform: 'translateX(-50%) rotate(-2deg)',
          zIndex: 20,
          pointerEvents: 'none',
          width: 140,
          height: 32,
          backgroundColor: 'rgba(235, 220, 190, 0.7)',
          borderLeft: '2px dashed rgba(180, 160, 120, 0.5)',
          borderRight: '2px dashed rgba(180, 160, 120, 0.5)',
          boxShadow: '0 4px 6px rgba(0,0,0,0.15)'
        }}
      />

      {/* Torn Paper Body */}
      <div
        style={{
          width,
          padding: 12,
          backgroundColor: '#fdfbf7',
          border: '2px solid rgba(168, 162, 158, 0.7)',
          clipPath: 'polygon(0% 2%, 3% 0%, 97% 1%, 100% 3%, 99% 97%, 97% 100%, 3% 99%, 0% 97%)',
          boxShadow: 'inset 0 0 15px rgba(0,0,0,0.06)',
          boxSizing: 'border-box'
        }}
      >
        <div
          style={{
            position: 'relative',
            overflow: 'hidden',
            width: '100%',
            height: Math.round(width * 0.75),
            borderRadius: 2,
            backgroundColor: '#000000'
          }}
        >
          <Img
            src={fullSrc}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover'
            }}
          />
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              pointerEvents: 'none',
              background: 'linear-gradient(to bottom, rgba(0,0,0,0.15) 0%, transparent 20%, transparent 80%, rgba(0,0,0,0.3) 100%)'
            }}
          />
        </div>

        {caption && (
          <div
            style={{
              paddingTop: 10,
              paddingBottom: 4,
              textAlign: 'center',
              fontWeight: 700,
              color: '#292524',
              fontSize: isRTL ? 28 : 26,
              fontFamily: isRTL ? '"Amiri", "Cairo", serif' : '"Caveat", "Kalam", cursive',
              letterSpacing: isRTL ? 'normal' : '0.04em'
            }}
          >
            {caption}
          </div>
        )}
      </div>
    </div>
  );
};
