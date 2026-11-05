import React from 'react';
import { useCurrentFrame, interpolate, useVideoConfig } from 'remotion';

interface ParallaxAtmosphereLayerProps {
  children?: React.ReactNode;
  backgroundContent?: React.ReactNode;
  midgroundContent?: React.ReactNode;
  zoomSpeed?: number; // Zoom percentage, e.g. 0.08 for 8% zoom over duration
  panDirection?: 'up' | 'down' | 'left' | 'right' | 'none';
  showGoldDust?: boolean;
}

/**
 * ParallaxAtmosphereLayer (2.5D Parallax ve Atmosferik Derinlik Motoru)
 * 
 * İslami Motion Design ekolünde durağan görselleri büyüleyici bir sinemaya
 * dönüştüren; arka plan, orta plan ve ön planı 3 farklı hızda hareket ettirerek
 * derinlik ve 3D kamera hissi veren katman yöneticisi.
 */
export const ParallaxAtmosphereLayer: React.FC<ParallaxAtmosphereLayerProps> = ({
  children,
  backgroundContent,
  midgroundContent,
  zoomSpeed = 0.06,
  panDirection = 'up',
  showGoldDust = true,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Slow, smooth cinematic push-in (Zoom-In)
  const currentProgress = frame / (durationInFrames || 180);
  const cameraZoom = 1.0 + currentProgress * zoomSpeed;

  // Parallax offsets
  const bgPan = interpolate(currentProgress, [0, 1], [0, panDirection === 'up' ? -25 : 25]);
  const midPan = interpolate(currentProgress, [0, 1], [0, panDirection === 'up' ? -60 : 60]);
  const fgPan = interpolate(currentProgress, [0, 1], [0, panDirection === 'up' ? -120 : 120]);

  // Floating gold dust particles for the foreground layer
  const dustParticles = Array.from({ length: 24 }).map((_, i) => {
    const seedX = (i * 97) % 1080;
    const speed = 0.5 + (i % 6) * 0.25;
    const posY = 1920 - ((frame * speed * 2 + i * 80) % 1920);
    const alpha = 0.2 + Math.sin(frame * 0.04 + i) * 0.3;
    const r = 1.5 + (i % 3);

    return (
      <div
        key={i}
        style={{
          position: 'absolute',
          left: seedX,
          top: posY,
          width: r * 2,
          height: r * 2,
          borderRadius: '50%',
          backgroundColor: '#f3d081',
          boxShadow: '0 0 8px #f3d081',
          opacity: Math.max(0, alpha),
          pointerEvents: 'none',
        }}
      />
    );
  });

  return (
    <div
      style={{
        position: 'relative',
        width: 1080,
        height: 1920,
        overflow: 'hidden',
        backgroundColor: '#050814',
      }}
    >
      {/* 1. LAYER: Background (Deep Cosmos / Architecture / Landscape) */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          transform: `scale(${cameraZoom * 1.02}) translateY(${bgPan}px)`,
          transformOrigin: 'center center',
          zIndex: 1,
        }}
      >
        {backgroundContent}
      </div>

      {/* 2. LAYER: Midground (Halal Silhouette / Quran Calligraphy) */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          transform: `scale(${cameraZoom * 1.05}) translateY(${midPan}px)`,
          transformOrigin: 'bottom center',
          zIndex: 5,
        }}
      >
        {midgroundContent}
      </div>

      {/* 3. LAYER: Children (Interactive Remotion Elements / Text) */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          zIndex: 10,
        }}
      >
        {children}
      </div>

      {/* 4. LAYER: Foreground Atmospheric Gold Dust & Light Leaks */}
      {showGoldDust && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            transform: `translateY(${fgPan}px)`,
            pointerEvents: 'none',
            zIndex: 30,
          }}
        >
          {dustParticles}
        </div>
      )}
    </div>
  );
};
