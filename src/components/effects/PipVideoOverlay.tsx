import React from 'react';
import { interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Video } from 'remotion';
import { PipVideoItem } from '../../types';

export interface PipVideoOverlayProps {
  pipVideos?: PipVideoItem[];
}

export const PipVideoOverlay: React.FC<PipVideoOverlayProps> = ({ pipVideos = [] }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const currentTimeSec = frame / fps;

  if (!pipVideos || pipVideos.length === 0) return null;

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 45,
      }}
    >
      {pipVideos.map((pip) => {
        const startSec = pip.startTime ?? 0;
        const endSec = pip.endTime ?? 9999;

        if (currentTimeSec < startSec || currentTimeSec > endSec) {
          return null;
        }

        const startFrame = Math.round(startSec * fps);
        const endFrame = Math.round(endSec * fps);
        const localFrame = frame - startFrame;

        // Spring entrance animation
        const enterSpring = spring({
          frame: localFrame,
          fps,
          config: { damping: 13, stiffness: 90 },
        });

        // Fade out at end
        const exitOpacity = interpolate(
          frame,
          [endFrame - 15, endFrame],
          [1, 0],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
        );

        const overallScale = enterSpring;
        const overallOpacity = (pip.opacity ?? 1.0) * exitOpacity;

        // Dimensions
        const pipW = pip.width || 340;
        const pipH = pip.height || (pip.shape === 'circle' ? pipW : Math.round(pipW * 1.35));

        // Position coordinates
        let posStyle: React.CSSProperties = {};
        const pos = pip.position || 'top-right';

        if (pip.x !== undefined || pip.y !== undefined) {
          posStyle = {
            left: pip.x !== undefined ? `${pip.x}px` : undefined,
            top: pip.y !== undefined ? `${pip.y}px` : undefined,
          };
        } else {
          switch (pos) {
            case 'top-left':
              posStyle = { top: 120, left: 40 };
              break;
            case 'bottom-left':
              posStyle = { bottom: 220, left: 40 };
              break;
            case 'bottom-right':
              posStyle = { bottom: 220, right: 40 };
              break;
            case 'center':
              posStyle = { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' };
              break;
            case 'top-right':
            default:
              posStyle = { top: 120, right: 40 };
              break;
          }
        }

        // Shape styling
        let shapeRadius = 24;
        let isCircle = false;
        let isPhone = false;

        if (pip.shape === 'circle') {
          shapeRadius = 9999;
          isCircle = true;
        } else if (pip.shape === 'phone') {
          shapeRadius = 36;
          isPhone = true;
        } else if (pip.shape === 'rectangle') {
          shapeRadius = 8;
        }

        const borderColor = pip.borderColor || '#38bdf8';
        const borderWidth = pip.borderWidth ?? (isPhone ? 6 : 4);

        // Resolve src
        let resolvedSrc = pip.videoUrl;
        if (
          !resolvedSrc.startsWith('http://') &&
          !resolvedSrc.startsWith('https://') &&
          !resolvedSrc.startsWith('blob:') &&
          !resolvedSrc.startsWith('data:')
        ) {
          const cleanPath = resolvedSrc.replace(/^\/?(public\/)?/, '');
          resolvedSrc = staticFile(cleanPath);
        }

        return (
          <div
            key={pip.id || `${startSec}_${pip.videoUrl}`}
            style={{
              position: 'absolute',
              ...posStyle,
              width: pipW,
              height: pipH,
              transform: `${posStyle.transform || ''} scale(${overallScale})`,
              opacity: overallOpacity,
              borderRadius: shapeRadius,
              overflow: 'hidden',
              boxShadow: isCircle
                ? '0 12px 35px rgba(0, 0, 0, 0.7), 0 0 25px rgba(56, 189, 248, 0.35)'
                : '0 20px 50px rgba(0, 0, 0, 0.8), 0 0 30px rgba(0, 0, 0, 0.5)',
              border: `${borderWidth}px solid ${borderColor}`,
              backgroundColor: '#020617',
              zIndex: 50,
            }}
          >
            {/* Phone Speaker Notch if shape is phone */}
            {isPhone && (
              <div
                style={{
                  position: 'absolute',
                  top: 8,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  width: 70,
                  height: 10,
                  borderRadius: 20,
                  backgroundColor: '#0f172a',
                  zIndex: 2,
                  border: '1px solid #334155',
                }}
              />
            )}

            <Video
              src={resolvedSrc}
              volume={pip.muted ? 0 : (pip.volume ?? 1.0)}
              muted={pip.muted ?? false}
              loop
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
            />

            {/* Glowing Accent Ring */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                borderRadius: shapeRadius,
                boxShadow: 'inset 0 0 15px rgba(0, 0, 0, 0.6)',
                pointerEvents: 'none',
              }}
            />
          </div>
        );
      })}
    </div>
  );
};
