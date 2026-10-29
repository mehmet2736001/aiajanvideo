import React from 'react';
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';

export interface PolaroidCardProps {
  imageSrc: string;
  caption?: string;
  rotation?: number; // e.g. -3 to +3 degrees
  width?: number; // e.g. 560
  className?: string;
  style?: React.CSSProperties;
  isRTL?: boolean;
}

export const PolaroidCard: React.FC<PolaroidCardProps> = ({
  imageSrc,
  caption,
  rotation = -2.5,
  width = 560,
  className = '',
  style = {},
  isRTL = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Natural spring entrance (drop and bounce slightly)
  const springProgress = spring({
    frame,
    fps,
    config: {
      damping: 14,
      stiffness: 90,
      mass: 0.8
    }
  });

  const translateY = interpolate(springProgress, [0, 1], [-80, 0]);
  const scale = interpolate(springProgress, [0, 1], [0.88, 1.0]);
  const opacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: 'clamp'
  });

  // Micro floating drift
  const floatY = Math.sin(frame / 25) * 4;
  const floatRot = Math.cos(frame / 30) * 0.6;

  // Resolve image static file path
  const fullSrc = imageSrc.startsWith('http')
    ? imageSrc
    : staticFile(imageSrc.startsWith('/') ? imageSrc.slice(1) : imageSrc);

  return (
    <div
      style={{
        position: 'relative',
        display: 'inline-block',
        userSelect: 'none',
        transform: `translateY(${translateY + floatY}px) scale(${scale}) rotate(${rotation + floatRot}deg)`,
        opacity,
        filter: 'drop-shadow(0 25px 35px rgba(0,0,0,0.55)) drop-shadow(0 10px 15px rgba(0,0,0,0.3))',
        ...style
      }}
    >
      {/* 1. Translucent Masking Tape (Top-Left) */}
      <div
        style={{
          position: 'absolute',
          top: -16,
          left: -24,
          zIndex: 20,
          pointerEvents: 'none',
          width: 120,
          height: 34,
          backgroundColor: 'rgba(245, 235, 205, 0.65)',
          backdropFilter: 'blur(1px)',
          borderLeft: '2px dashed rgba(200, 180, 140, 0.6)',
          borderRight: '2px dashed rgba(200, 180, 140, 0.6)',
          transform: 'rotate(-24deg)',
          boxShadow: '0 4px 8px rgba(0,0,0,0.18)'
        }}
      />

      {/* 2. Translucent Masking Tape (Top-Right) */}
      <div
        style={{
          position: 'absolute',
          top: -16,
          right: -24,
          zIndex: 20,
          pointerEvents: 'none',
          width: 120,
          height: 34,
          backgroundColor: 'rgba(245, 235, 205, 0.65)',
          backdropFilter: 'blur(1px)',
          borderLeft: '2px dashed rgba(200, 180, 140, 0.6)',
          borderRight: '2px dashed rgba(200, 180, 140, 0.6)',
          transform: 'rotate(20deg)',
          boxShadow: '0 4px 8px rgba(0,0,0,0.18)'
        }}
      />

      {/* 3. Authentic Polaroid Frame Body */}
      <div
        style={{
          width,
          backgroundColor: '#f8f6f0',
          padding: '16px 16px 24px 16px',
          borderRadius: 4,
          border: '1px solid rgba(168, 162, 158, 0.6)',
          backgroundImage: 'radial-gradient(rgba(0,0,0,0.02) 1px, transparent 0)',
          backgroundSize: '16px 16px',
          boxSizing: 'border-box'
        }}
      >
        {/* Photo Container */}
        <div
          style={{
            position: 'relative',
            overflow: 'hidden',
            backgroundColor: '#000000',
            width: '100%',
            height: Math.round(width * 0.95),
            borderRadius: 2,
            border: '1px solid rgba(120, 113, 108, 0.3)'
          }}
        >
          <Img
            src={fullSrc}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              filter: 'contrast(1.05) saturate(1.1)'
            }}
          />
          {/* Subtle Vintage Vignette inside photo */}
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              pointerEvents: 'none',
              background: 'radial-gradient(circle at 50% 50%, transparent 65%, rgba(0,0,0,0.3) 100%)'
            }}
          />
        </div>

        {/* 4. Handwritten Caption Area */}
        {caption && (
          <div style={{ paddingTop: 14, textAlign: 'center' }}>
            <span
              style={{
                fontFamily: isRTL ? '"Amiri", "Cairo", serif' : '"Kalam", "Caveat", cursive',
                fontSize: isRTL ? 34 : 32,
                fontWeight: 700,
                color: '#292524',
                letterSpacing: isRTL ? 'normal' : '0.02em',
                lineHeight: 1.2
              }}
            >
              {caption}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
