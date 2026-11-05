import React from 'react';
import { useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';

export type SilhouettePosture = 'sujood' | 'dua' | 'traveler' | 'contemplation';

interface HalalSilhouetteRigProps {
  posture?: SilhouettePosture;
  scale?: number;
  xOffset?: number;
  yOffset?: number;
  glowColor?: string;
  rimColor?: string;
  showAuraParticles?: boolean;
}

/**
 * HalalSilhouetteRig (İslami Hareketli Karakter Rig'i)
 * 
 * Tasvir adabına %100 sadık kalarak, hiçbir yüz veya şahıs tasviri içermeyen;
 * derin tefekkür, secde, dua ve yolculuk anlarını minimalist ve estetik bir
 * silüet ve altın rim-light ışığıyla canlandıran modern İslami Motion Design bileşeni.
 * (Sufariq, Visual Deen & Yaqeen Institute standartlarında)
 */
export const HalalSilhouetteRig: React.FC<HalalSilhouetteRigProps> = ({
  posture = 'sujood',
  scale = 1.0,
  xOffset = 0,
  yOffset = 0,
  glowColor = 'rgba(243, 208, 129, 0.45)',
  rimColor = '#f3d081',
  showAuraParticles = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Gentle spiritual breathing cycle
  const breath = Math.sin(frame * 0.045) * 0.025;
  const pulseAura = 0.85 + Math.sin(frame * 0.06) * 0.15;

  // Entrance spring
  const enterScale = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 60 },
  });

  // SVG Paths for different postures (minimalist, faceless, sacred contours)
  const getSilhouetteContent = () => {
    switch (posture) {
      case 'sujood':
        // Sujood (Secde): Head grounded, back arched in deep humility, arms extended
        return (
          <g transform="translate(240, 1150)">
            {/* Ground reflection glow */}
            <ellipse cx="300" cy="460" rx="420" ry="25" fill="url(#groundGlow)" opacity={0.6 * pulseAura} />
            
            {/* Sujood Body Contour */}
            <path
              d="
                M 120 450
                C 140 430, 210 400, 240 370
                C 270 340, 310 270, 370 240
                C 430 210, 520 220, 560 270
                C 590 310, 570 380, 510 430
                C 470 460, 350 465, 120 450 Z
              "
              fill="#060913"
              stroke={rimColor}
              strokeWidth="3.5"
              filter="url(#silhouetteGlow)"
            />

            {/* Head grounded in prostration (No face, pure smooth sphere) */}
            <circle
              cx="130"
              cy="410"
              r="45"
              fill="#060913"
              stroke={rimColor}
              strokeWidth="3.5"
              filter="url(#silhouetteGlow)"
            />

            {/* Forearms resting on ground */}
            <path
              d="M 170 440 C 190 410, 240 420, 270 450 Z"
              fill="#060913"
              stroke={rimColor}
              strokeWidth="2.5"
            />
          </g>
        );

      case 'dua':
        // Dua: Kneeling / sitting in tahiyyat, hands raised toward heavens
        return (
          <g transform="translate(320, 920)">
            {/* Torso & Head */}
            <circle cx="220" cy="190" r="50" fill="#060913" stroke={rimColor} strokeWidth="3.5" filter="url(#silhouetteGlow)" />
            <path
              d="
                M 170 250
                C 190 230, 250 230, 270 250
                C 290 290, 320 480, 310 650
                C 280 670, 160 670, 130 650
                C 120 480, 150 290, 170 250 Z
              "
              fill="#060913"
              stroke={rimColor}
              strokeWidth="3.5"
              filter="url(#silhouetteGlow)"
            />
            {/* Raised Hands for Supplication (Avuçlar semaya açık) */}
            <path
              d="
                M 160 360 C 120 300, 110 220, 140 180
                M 280 360 C 320 300, 330 220, 300 180
              "
              stroke={rimColor}
              strokeWidth="5"
              strokeLinecap="round"
              fill="none"
              filter="url(#silhouetteGlow)"
            />
            {/* Organic Soft Heavenly Glow (No hard cone, purely atmospheric light) */}
            <ellipse
              cx="220"
              cy="180"
              rx="180"
              ry="260"
              fill="url(#groundGlow)"
              opacity={0.25 * pulseAura}
            />
          </g>
        );

      case 'traveler':
        // Traveler in Desert: Walking alone, cloak billowing slightly
        return (
          <g transform="translate(360, 850)">
            <circle cx="180" cy="180" r="48" fill="#060913" stroke={rimColor} strokeWidth="3.5" filter="url(#silhouetteGlow)" />
            {/* Cloak & Striding Legs */}
            <path
              d="
                M 140 230
                C 160 210, 210 210, 230 230
                C 260 300, 290 520, 300 780
                C 250 780, 210 680, 190 620
                C 170 680, 130 790, 80 780
                C 90 520, 120 300, 140 230 Z
              "
              fill="#060913"
              stroke={rimColor}
              strokeWidth="3.5"
              filter="url(#silhouetteGlow)"
            />
          </g>
        );

      case 'contemplation':
      default:
        // Contemplation: Gazing into cosmic horizon, arms at side or behind back
        return (
          <g transform="translate(340, 900)">
            <circle cx="200" cy="180" r="50" fill="#060913" stroke={rimColor} strokeWidth="3.5" filter="url(#silhouetteGlow)" />
            <path
              d="
                M 150 240
                C 170 220, 230 220, 250 240
                C 280 320, 290 540, 280 750
                C 250 770, 150 770, 120 750
                C 110 540, 120 320, 150 240 Z
              "
              fill="#060913"
              stroke={rimColor}
              strokeWidth="3.5"
              filter="url(#silhouetteGlow)"
            />
          </g>
        );
    }
  };

  // Generate floating spiritual gold dust particles around the silhouette
  const particles = Array.from({ length: 16 }).map((_, i) => {
    const seed = (i * 73) % 100;
    const px = 200 + (seed * 6.8);
    const speed = 0.8 + (i % 5) * 0.3;
    const py = 1600 - ((frame * speed * 2 + i * 90) % 800);
    const pAlpha = 0.3 + Math.sin(frame * 0.05 + i) * 0.4;
    const pRadius = 1.5 + (i % 3);

    return (
      <circle
        key={i}
        cx={px}
        cy={py}
        r={pRadius}
        fill="#f3d081"
        opacity={Math.max(0, pAlpha)}
        filter="url(#particleBlur)"
      />
    );
  });

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: 1080,
        height: 1920,
        pointerEvents: 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        transform: `translate(${xOffset}px, ${yOffset}px) scale(${(scale + breath) * enterScale})`,
        transformOrigin: 'bottom center',
        zIndex: 10,
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
          {/* Intense golden rim glow for sacred silhouette borders */}
          <filter id="silhouetteGlow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur1" />
            <feGaussianBlur in="SourceGraphic" stdDeviation="18" result="blur2" />
            <feMerge>
              <feMergeNode in="blur2" />
              <feMergeNode in="blur1" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          <filter id="particleBlur" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="2" />
          </filter>

          {/* Gradients */}
          <radialGradient id="groundGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#f3d081" stopOpacity="0.45" />
            <stop offset="60%" stopColor="#d4af37" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#050814" stopOpacity="0" />
          </radialGradient>

          <linearGradient id="heavenlyNur" x1="50%" y1="0%" x2="50%" y2="100%">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.6" />
            <stop offset="60%" stopColor="#f3d081" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#f3d081" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Aura Particles */}
        {showAuraParticles && <g>{particles}</g>}

        {/* Main Silhouette Rig */}
        {getSilhouetteContent()}
      </svg>
    </div>
  );
};
