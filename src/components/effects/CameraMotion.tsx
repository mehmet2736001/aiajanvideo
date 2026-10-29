import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';

export type CameraMotionMode = 'static' | 'handheld' | 'cinematic_drift';

interface CameraMotionProps {
  mode?: CameraMotionMode;
  children: React.ReactNode;
}

export const CameraMotion: React.FC<CameraMotionProps> = ({
  mode = 'handheld',
  children,
}) => {
  const frame = useCurrentFrame();

  if (mode === 'static') {
    return <div style={{ width: '100%', height: '100%', position: 'relative' }}>{children}</div>;
  }

  const isCinematic = mode === 'cinematic_drift';

  // Multi-frequency smooth organic movement
  const t = frame / 30;

  // Handheld: slight tremor + sway. Cinematic: slow majestic drift
  const freq1 = isCinematic ? 0.3 : 1.1;
  const freq2 = isCinematic ? 0.45 : 1.7;

  const ampX = isCinematic ? 6 : 4;
  const ampY = isCinematic ? 8 : 5;
  const ampRot = isCinematic ? 0.25 : 0.4;

  const x = Math.sin(t * freq1) * ampX + Math.sin(t * freq2 * 0.7) * (ampX * 0.4);
  const y = Math.cos(t * freq2) * ampY + Math.cos(t * freq1 * 0.8) * (ampY * 0.3);
  const rot = Math.sin(t * freq1 * 0.9) * ampRot;
  const scale = interpolate(Math.sin(t * 0.2), [-1, 1], [1.01, 1.025]);

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        position: 'relative',
        transform: `translate3d(${x}px, ${y}px, 0px) rotate(${rot}deg) scale(${scale})`,
        transformOrigin: 'center center',
      }}
    >
      {children}
    </div>
  );
};
