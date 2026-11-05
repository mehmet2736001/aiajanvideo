import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface AtomFe26HoloModelProps {
  scaleMultiplier?: number;
}

export const AtomFe26HoloModel: React.FC<AtomFe26HoloModelProps> = ({
  scaleMultiplier = 1.0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Spring entrance from bottom with slight tilt
  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 90, mass: 0.8 },
  });

  const fadeIn = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const pulse = 1 + Math.sin(frame * 0.12) * 0.05;

  // 3D rotation angles
  const rotZ1 = (frame * 1.8) % 360;
  const rotZ2 = (-frame * 2.2) % 360;
  const rotZ3 = (frame * 1.4) % 360;
  const rotZ4 = (-frame * 2.6) % 360;

  // Number counter for protons and electrons
  const protonCount = Math.round(
    interpolate(frame, [10, 40], [1, 26], { extrapolateRight: 'clamp' })
  );

  return (
    <div
      style={{
        position: 'relative',
        width: 640 * scaleMultiplier,
        height: 640 * scaleMultiplier,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        opacity: fadeIn,
        transform: `scale(${entrance * scaleMultiplier})`,
        perspective: 1000,
        margin: '0 auto',
      }}
    >
      {/* Outer Holographic HUD Radar Ring */}
      <svg
        width="620"
        height="620"
        viewBox="0 0 620 620"
        style={{
          position: 'absolute',
          transform: `rotate(${frame * 0.4}deg)`,
        }}
      >
        <circle
          cx="310"
          cy="310"
          r="300"
          fill="none"
          stroke="rgba(212, 175, 55, 0.3)"
          strokeWidth="2"
          strokeDasharray="8 12"
        />
        <circle
          cx="310"
          cy="310"
          r="285"
          fill="none"
          stroke="rgba(56, 189, 248, 0.4)"
          strokeWidth="1.5"
          strokeDasharray="40 180"
        />
        <circle
          cx="310"
          cy="310"
          r="260"
          fill="none"
          stroke="rgba(212, 175, 55, 0.2)"
          strokeWidth="1"
        />
        {/* Cardinal Ticks */}
        {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
          <line
            key={deg}
            x1="310"
            y1="10"
            x2="310"
            y2="28"
            stroke="#d4af37"
            strokeWidth="2.5"
            transform={`rotate(${deg} 310 310)`}
          />
        ))}
      </svg>

      {/* Orbit 1: Tilted X 65deg, Z rot1 */}
      <div
        style={{
          position: 'absolute',
          width: 460,
          height: 460,
          borderRadius: '50%',
          border: '2px solid rgba(212, 175, 55, 0.65)',
          boxShadow: '0 0 15px rgba(212, 175, 55, 0.4)',
          transform: `rotateX(68deg) rotateY(15deg) rotateZ(${rotZ1}deg)`,
          transformStyle: 'preserve-3d',
        }}
      >
        {/* Orbiting Electron */}
        <div
          style={{
            position: 'absolute',
            top: -8,
            left: '50%',
            width: 16,
            height: 16,
            borderRadius: '50%',
            backgroundColor: '#ffffff',
            boxShadow: '0 0 12px #38bdf8, 0 0 24px #38bdf8',
          }}
        />
      </div>

      {/* Orbit 2: Tilted X -65deg, Z rot2 */}
      <div
        style={{
          position: 'absolute',
          width: 480,
          height: 480,
          borderRadius: '50%',
          border: '2px dashed rgba(56, 189, 248, 0.7)',
          boxShadow: '0 0 20px rgba(56, 189, 248, 0.35)',
          transform: `rotateX(-65deg) rotateY(-20deg) rotateZ(${rotZ2}deg)`,
          transformStyle: 'preserve-3d',
        }}
      >
        <div
          style={{
            position: 'absolute',
            bottom: -8,
            left: '50%',
            width: 18,
            height: 18,
            borderRadius: '50%',
            backgroundColor: '#fbbf24',
            boxShadow: '0 0 15px #f59e0b, 0 0 30px #d4af37',
          }}
        />
      </div>

      {/* Orbit 3: Tilted Y 70deg */}
      <div
        style={{
          position: 'absolute',
          width: 500,
          height: 500,
          borderRadius: '50%',
          border: '2px solid rgba(245, 158, 11, 0.6)',
          boxShadow: '0 0 25px rgba(245, 158, 11, 0.35)',
          transform: `rotateY(72deg) rotateX(25deg) rotateZ(${rotZ3}deg)`,
          transformStyle: 'preserve-3d',
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: -8,
            width: 16,
            height: 16,
            borderRadius: '50%',
            backgroundColor: '#ffffff',
            boxShadow: '0 0 14px #e0e7ff',
          }}
        />
      </div>

      {/* Orbit 4: Horizontal oblique */}
      <div
        style={{
          position: 'absolute',
          width: 520,
          height: 520,
          borderRadius: '50%',
          border: '1.5px solid rgba(167, 139, 250, 0.6)',
          transform: `rotateX(40deg) rotateY(60deg) rotateZ(${rotZ4}deg)`,
          transformStyle: 'preserve-3d',
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: '50%',
            right: -8,
            width: 16,
            height: 16,
            borderRadius: '50%',
            backgroundColor: '#38bdf8',
            boxShadow: '0 0 14px #38bdf8',
          }}
        />
      </div>

      {/* Radiant Glowing Nucleus (Fe-26 Protons & Neutrons) */}
      <div
        style={{
          position: 'relative',
          width: 170,
          height: 170,
          borderRadius: '50%',
          background: 'radial-gradient(circle at 35% 35%, #fff7ed 0%, #fbbf24 45%, #b45309 85%, #451a03 100%)',
          boxShadow: '0 0 40px #f59e0b, 0 0 80px rgba(212, 175, 55, 0.6), inset 0 0 20px #ffffff',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          transform: `scale(${pulse})`,
          zIndex: 10,
        }}
      >
        <div
          style={{
            fontFamily: "'Cinzel', serif",
            fontSize: 48,
            fontWeight: 900,
            color: '#1e1b4b',
            lineHeight: 1,
            letterSpacing: 2,
            textShadow: '0 2px 8px rgba(255,255,255,0.8)',
          }}
        >
          Fe
        </div>
        <div
          style={{
            fontFamily: "'Cinzel', serif",
            fontSize: 22,
            fontWeight: 800,
            color: '#78350f',
            marginTop: 4,
            letterSpacing: 1,
          }}
        >
          {protonCount} P+
        </div>
      </div>

      {/* Holographic Data Telemetry Badges Flying on Left & Right */}
      <div
        style={{
          position: 'absolute',
          left: -40,
          top: 80,
          padding: '8px 18px',
          background: 'rgba(5, 10, 24, 0.85)',
          border: '1px solid rgba(56, 189, 248, 0.6)',
          borderRadius: 8,
          backdropFilter: 'blur(8px)',
          boxShadow: '0 0 18px rgba(56, 189, 248, 0.3)',
        }}
      >
        <div style={{ color: '#38bdf8', fontSize: 13, fontWeight: 700, letterSpacing: 2 }}>
          ATOM NUMARASI
        </div>
        <div style={{ color: '#f8fafc', fontSize: 24, fontWeight: 900, fontFamily: "'Cinzel', serif" }}>
          26
        </div>
      </div>

      <div
        style={{
          position: 'absolute',
          right: -40,
          bottom: 80,
          padding: '8px 18px',
          background: 'rgba(5, 10, 24, 0.85)',
          border: '1px solid rgba(212, 175, 55, 0.6)',
          borderRadius: 8,
          backdropFilter: 'blur(8px)',
          boxShadow: '0 0 18px rgba(212, 175, 55, 0.3)',
          textAlign: 'right',
        }}
      >
        <div style={{ color: '#d4af37', fontSize: 13, fontWeight: 700, letterSpacing: 2 }}>
          ATOM AĞIRLIĞI
        </div>
        <div style={{ color: '#f8fafc', fontSize: 24, fontWeight: 900, fontFamily: "'Cinzel', serif" }}>
          55.845 u
        </div>
      </div>
    </div>
  );
};
