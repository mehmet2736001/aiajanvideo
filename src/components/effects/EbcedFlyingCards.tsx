import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface EbcedFlyingCardsProps {
  scaleMultiplier?: number;
}

export const EbcedFlyingCards: React.FC<EbcedFlyingCardsProps> = ({
  scaleMultiplier = 1.0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const letters = [
    { ar: 'ح', name: 'Ha', val: 8, delay: 0 },
    { ar: 'د', name: 'Dal', val: 4, delay: 6 },
    { ar: 'ي', name: 'Ya', val: 10, delay: 12 },
    { ar: 'د', name: 'Dal', val: 4, delay: 18 },
  ];

  // Staggered springs for each card flying in
  const springs = letters.map((l) =>
    spring({
      frame: frame - l.delay,
      fps,
      config: { damping: 14, stiffness: 100, mass: 0.8 },
    })
  );

  // Result equation reveal spring
  const resultSpring = spring({
    frame: frame - 28,
    fps,
    config: { damping: 14, stiffness: 100 },
  });

  // Second row (El-Hadid = 57) reveal spring
  const surahSpring = spring({
    frame: frame - 45,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  return (
    <div
      style={{
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        width: 960 * scaleMultiplier,
        margin: '0 auto',
        transform: `scale(${scaleMultiplier})`,
      }}
    >
      {/* Title Header */}
      <div
        style={{
          fontFamily: "'Cinzel', serif",
          fontSize: 22,
          fontWeight: 700,
          color: '#d4af37',
          letterSpacing: 4,
          marginBottom: 24,
          textTransform: 'uppercase',
          textAlign: 'center',
          textShadow: '0 2px 10px rgba(0,0,0,0.8)',
        }}
      >
        ✦ EBCED İLMİ & NÜKLEER MİZAN DENKLEMİ ✦
      </div>

      {/* Row of 4 Flying Letter Cards */}
      <div
        style={{
          display: 'flex',
          gap: 20,
          justifyContent: 'center',
          alignItems: 'center',
          marginBottom: 30,
        }}
      >
        {letters.map((l, i) => {
          const s = springs[i];
          const flyY = interpolate(s, [0, 1], [60, 0]);
          const rotZ = interpolate(s, [0, 1], [(i % 2 === 0 ? -12 : 12), 0]);

          return (
            <div
              key={i}
              style={{
                width: 150,
                height: 190,
                borderRadius: 20,
                background: 'linear-gradient(145deg, rgba(20, 26, 45, 0.92) 0%, rgba(8, 12, 22, 0.95) 100%)',
                border: '2px solid rgba(212, 175, 55, 0.75)',
                boxShadow: '0 12px 35px rgba(0,0,0,0.8), inset 0 0 15px rgba(212, 175, 55, 0.25)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                transform: `scale(${s}) translateY(${flyY}px) rotate(${rotZ}deg)`,
                opacity: s,
                backdropFilter: 'blur(10px)',
              }}
            >
              {/* Arabic Letter with 24K Glow */}
              <div
                style={{
                  fontFamily: "'Amiri', serif",
                  fontSize: 70,
                  color: '#ffffff',
                  lineHeight: 1,
                  textShadow: '0 0 16px #d4af37, 0 0 30px #f59e0b',
                  marginBottom: 6,
                }}
              >
                {l.ar}
              </div>

              {/* Letter Name */}
              <div
                style={{
                  fontFamily: "'Cinzel', serif",
                  fontSize: 14,
                  fontWeight: 600,
                  color: '#94a3b8',
                  letterSpacing: 2,
                }}
              >
                {l.name}
              </div>

              {/* Ebced Value Badge */}
              <div
                style={{
                  marginTop: 10,
                  padding: '4px 14px',
                  borderRadius: 12,
                  background: 'rgba(212, 175, 55, 0.25)',
                  border: '1px solid #d4af37',
                  color: '#fbbf24',
                  fontFamily: "'Cinzel', serif",
                  fontSize: 20,
                  fontWeight: 900,
                }}
              >
                {l.val}
              </div>
            </div>
          );
        })}
      </div>

      {/* Result Formula 1: 8 + 4 + 10 + 4 = 26 (ATOM NO: 26) */}
      <div
        style={{
          width: '100%',
          maxWidth: 820,
          padding: '16px 28px',
          borderRadius: 20,
          background: 'linear-gradient(90deg, rgba(8, 12, 24, 0.95) 0%, rgba(30, 41, 69, 0.95) 50%, rgba(8, 12, 24, 0.95) 100%)',
          border: '2px solid #38bdf8',
          boxShadow: '0 10px 30px rgba(56, 189, 248, 0.35)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          transform: `scale(${resultSpring})`,
          opacity: resultSpring,
          marginBottom: 16,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ color: '#94a3b8', fontSize: 22, fontFamily: "'Cinzel', serif" }}>
            8 + 4 + 10 + 4 =
          </span>
          <span
            style={{
              color: '#38bdf8',
              fontSize: 38,
              fontWeight: 900,
              fontFamily: "'Cinzel', serif",
              textShadow: '0 0 15px #38bdf8',
            }}
          >
            26
          </span>
        </div>

        <div
          style={{
            padding: '6px 20px',
            borderRadius: 12,
            background: 'rgba(56, 189, 248, 0.2)',
            border: '1px solid #38bdf8',
            color: '#ffffff',
            fontFamily: "'Cinzel', serif",
            fontSize: 18,
            fontWeight: 800,
            letterSpacing: 2,
          }}
        >
          DEMİR ATOM NUMARASI: 26
        </div>
      </div>

      {/* Result Formula 2: EL-HADÎD = 57 (SÛRE SIRASI & Fe-57 İZOTOPU) */}
      <div
        style={{
          width: '100%',
          maxWidth: 820,
          padding: '16px 28px',
          borderRadius: 20,
          background: 'linear-gradient(90deg, rgba(8, 12, 24, 0.95) 0%, rgba(55, 38, 15, 0.95) 50%, rgba(8, 12, 24, 0.95) 100%)',
          border: '2px solid #d4af37',
          boxShadow: '0 10px 30px rgba(212, 175, 55, 0.35)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          transform: `scale(${surahSpring})`,
          opacity: surahSpring,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ color: '#d4af37', fontSize: 24, fontFamily: "'Amiri', serif" }}>
            الحديد =
          </span>
          <span
            style={{
              color: '#fbbf24',
              fontSize: 38,
              fontWeight: 900,
              fontFamily: "'Cinzel', serif",
              textShadow: '0 0 15px #d4af37',
            }}
          >
            57
          </span>
        </div>

        <div
          style={{
            padding: '6px 20px',
            borderRadius: 12,
            background: 'rgba(212, 175, 55, 0.2)',
            border: '1px solid #d4af37',
            color: '#fef08a',
            fontFamily: "'Cinzel', serif",
            fontSize: 18,
            fontWeight: 800,
            letterSpacing: 2,
          }}
        >
          57. SÛRE = Fe-57 İZOTOPU
        </div>
      </div>
    </div>
  );
};
