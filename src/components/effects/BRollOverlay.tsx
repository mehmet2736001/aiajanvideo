import React from 'react';
import { interpolate, staticFile, useCurrentFrame, useVideoConfig, Video } from 'remotion';

export interface BRollOverlayProps {
  type?: 'none' | 'cosmic' | 'clouds' | 'waves' | 'ink' | 'gold_dust' | string;
  brollUrl?: string;
  opacity?: number;
  blendMode?: 'screen' | 'overlay' | 'soft-light' | 'normal';
}

export const BRollOverlay: React.FC<BRollOverlayProps> = ({
  type = 'cosmic',
  brollUrl,
  opacity = 0.8,
  blendMode = 'normal',
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // If explicitly none and no url, render nothing
  if ((!type || type === 'none') && !brollUrl) {
    return null;
  }

  // Resolve video path
  let videoPath = brollUrl;
  const validBrollList = ['cosmic', 'clouds', 'waves', 'ink', 'gold_dust'];
  if (!videoPath) {
    if (type && validBrollList.includes(type)) {
      videoPath = 'broll/' + type + '.mp4';
    } else {
      videoPath = 'broll/gold_dust.mp4';
    }
  }

  if (!videoPath) return null;

  const resolvedSrc = staticFile(
    videoPath.startsWith('/') ? videoPath.slice(1) : videoPath
  );

  // Subtle slow cinematic drift/zoom
  const zoom = interpolate(frame, [0, durationInFrames], [1.0, 1.06], {
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: 1080,
        height: 1920,
        zIndex: 1,
        pointerEvents: 'none',
        overflow: 'hidden',
      }}
    >
      {/* Background Animated Video */}
      <div
        style={{
          width: '100%',
          height: '100%',
          position: 'absolute',
          top: 0,
          left: 0,
          opacity,
          mixBlendMode: blendMode,
        }}
      >
        <Video
          src={resolvedSrc}
          loop
          muted
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transform: `scale(${zoom})`,
            filter: 'contrast(1.08) brightness(0.95) saturate(1.15)',
          }}
        />
      </div>

      {/* Cinematic Dark Vignette & Edge Shadow Layer for Text Legibility */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background:
            'radial-gradient(ellipse at center, rgba(5,7,14,0.2) 0%, rgba(5,7,14,0.65) 70%, rgba(3,5,10,0.85) 100%)',
          pointerEvents: 'none',
        }}
      />
    </div>
  );
};
