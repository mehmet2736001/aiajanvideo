import React from 'react';
import { interpolate, staticFile, useCurrentFrame, useVideoConfig, Video } from 'remotion';

export interface BRollOverlayProps {
  type?: 'none' | 'cosmic' | 'clouds' | 'waves' | 'ink';
  brollUrl?: string;
  opacity?: number;
  blendMode?: 'screen' | 'overlay' | 'soft-light' | 'normal';
}

export const BRollOverlay: React.FC<BRollOverlayProps> = ({
  type = 'none',
  brollUrl,
  opacity = 0.18,
  blendMode = 'screen'
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // If no broll requested, render nothing
  if ((!type || type === 'none') && !brollUrl) {
    return null;
  }

  // Resolve video path
  let videoPath = brollUrl;
  if (!videoPath && type && type !== 'none') {
    videoPath = `broll/${type}.mp4`;
  }

  if (!videoPath) return null;

  const resolvedSrc = staticFile(
    videoPath.startsWith('/') ? videoPath.slice(1) : videoPath
  );

  // Subtle slow cinematic drift/zoom
  const zoom = interpolate(frame, [0, durationInFrames], [1.0, 1.08], {
    extrapolateRight: 'clamp'
  });

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: 1080,
        height: 1920,
        zIndex: 6,
        pointerEvents: 'none',
        overflow: 'hidden',
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
          filter: 'contrast(1.1) saturate(1.15)',
        }}
      />
    </div>
  );
};
