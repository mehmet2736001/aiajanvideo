import React from 'react';
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { OverlayImageItem } from '../../types';

export interface PngOverlayLayerProps {
  overlayImages?: OverlayImageItem[];
}

export const PngOverlayLayer: React.FC<PngOverlayLayerProps> = ({ overlayImages = [] }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTimeSec = frame / fps;

  if (!overlayImages || overlayImages.length === 0) return null;

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 42,
      }}
    >
      {overlayImages.map((ov) => {
        const startSec = ov.startTime ?? 0;
        const endSec = ov.endTime ?? 9999;

        if (currentTimeSec < startSec || currentTimeSec > endSec) {
          return null;
        }

        const startFrame = Math.round(startSec * fps);
        const endFrame = Math.round(endSec * fps);
        const localFrame = frame - startFrame;

        // Animations
        const anim = ov.animation || 'bounce';
        let scale = 1;
        let translateY = 0;
        let rotate = ov.rotation || 0;

        if (anim === 'bounce') {
          scale = spring({
            frame: localFrame,
            fps,
            config: { damping: 12, stiffness: 100 },
          });
        } else if (anim === 'slide_up') {
          const slideSpring = spring({
            frame: localFrame,
            fps,
            config: { damping: 14, stiffness: 80 },
          });
          translateY = interpolate(slideSpring, [0, 1], [60, 0]);
        } else if (anim === 'spin') {
          rotate += localFrame * 1.5;
        }

        // Fade in & out
        const fadeIn = interpolate(localFrame, [0, 12], [0, 1], { extrapolateRight: 'clamp' });
        const fadeOut = interpolate(frame, [endFrame - 12, endFrame], [1, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        const currentOpacity = (ov.opacity ?? 1.0) * fadeIn * fadeOut;

        // Positioning
        let posStyle: React.CSSProperties = {};
        const pos = ov.position || 'top-right';

        if (ov.x !== undefined || ov.y !== undefined) {
          posStyle = {
            left: ov.x !== undefined ? `${ov.x}px` : undefined,
            top: ov.y !== undefined ? `${ov.y}px` : undefined,
          };
        } else {
          switch (pos) {
            case 'top-left':
              posStyle = { top: 90, left: 50 };
              break;
            case 'bottom-left':
              posStyle = { bottom: 180, left: 50 };
              break;
            case 'bottom-right':
              posStyle = { bottom: 180, right: 50 };
              break;
            case 'center':
              posStyle = { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' };
              break;
            case 'top-banner':
              posStyle = { top: 40, left: '50%', transform: 'translateX(-50%)' };
              break;
            case 'bottom-banner':
              posStyle = { bottom: 120, left: '50%', transform: 'translateX(-50%)' };
              break;
            case 'top-right':
            default:
              posStyle = { top: 90, right: 50 };
              break;
          }
        }

        const width = ov.width || 180;
        const height = ov.height;

        // Resolve image URL
        let resolvedSrc = ov.imageUrl;
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
            key={ov.id || `${startSec}_${ov.imageUrl}`}
            style={{
              position: 'absolute',
              ...posStyle,
              width,
              height: height ? height : 'auto',
              transform: `${posStyle.transform || ''} translateY(${translateY}px) scale(${scale}) rotate(${rotate}deg)`,
              opacity: currentOpacity,
              filter: 'drop-shadow(0 10px 20px rgba(0,0,0,0.45))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Img
              src={resolvedSrc}
              style={{
                width: '100%',
                height: height ? '100%' : 'auto',
                objectFit: 'contain',
              }}
            />
          </div>
        );
      })}
    </div>
  );
};
