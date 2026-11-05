import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface DopplerExpansionHUDProps {
  scaleMultiplier?: number;
  mode?: 'spectrum' | 'etymology' | 'hubble';
}

export const DopplerExpansionHUD: React.FC<DopplerExpansionHUDProps> = ({
  scaleMultiplier = 1.0,
  mode = 'spectrum',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 90 },
  });

  // Animated wave frequency (stretches from tight blue waves to wide red waves)
  const waveStretch = interpolate(frame, [0, 90], [1.0, 2.4], {
    extrapolateRight: 'clamp',
  });
  const waveShift = (frame * 5) % 120;

  if (mode === 'etymology') {
    return (
      <div
        style={{
          position: 'relative',
          width: 880 * scaleMultiplier,
          padding: '24px 36px',
          background: 'linear-gradient(135deg, rgba(8, 14, 30, 0.92) 0%, rgba(20, 10, 35, 0.95) 100%)',
          border: '2px solid rgba(212, 175, 55, 0.75)',
          borderRadius: 24,
          boxShadow: '0 16px 45px rgba(0,0,0,0.85), inset 0 0 20px rgba(212, 175, 55, 0.25)',
          backdropFilter: 'blur(12px)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          transform: `scale(${entrance * scaleMultiplier})`,
          opacity: entrance,
          margin: '0 auto',
        }}
      >
        <div
          style={{
            fontFamily: "'Cinzel', serif",
            fontSize: 20,
            fontWeight: 800,
            color: '#d4af37',
            letterSpacing: 3,
            marginBottom: 16,
            textTransform: 'uppercase',
          }}
        >
          ✦ KUR'AN'IN LİSAN MUCİZESİ · İSM-İ FÂİL ✦
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 30, marginBottom: 16 }}>
          <div
            style={{
              fontFamily: "'Amiri', serif",
              fontSize: 64,
              color: '#ffffff',
              textShadow: '0 0 20px #d4af37, 0 0 40px #f59e0b',
            }}
          >
            مُوسِعُونَ
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <span style={{ color: '#38bdf8', fontSize: 16, fontWeight: 700, fontFamily: "'Cinzel', serif" }}>
              KÖK: [ و - س - ع ] (V-S-A)
            </span>
            <span style={{ color: '#e2e8f0', fontSize: 22, fontWeight: 700 }}>
              "Genişleticiyiz / Aralıksız Genişletmekteyiz"
            </span>
          </div>
        </div>

        <div
          style={{
            padding: '10px 24px',
            borderRadius: 14,
            background: 'rgba(56, 189, 248, 0.15)',
            border: '1px solid #38bdf8',
            color: '#f8fafc',
            fontSize: 18,
            fontWeight: 600,
            textAlign: 'center',
          }}
        >
          Arapçada mazi (geçmiş) değil; <span style={{ color: '#fbbf24', fontWeight: 800 }}>Şu anda ve sürekli devam eden</span> bir eylemi bildirir!
        </div>
      </div>
    );
  }

  // Spectrum / Hubble mode
  return (
    <div
      style={{
        position: 'relative',
        width: 880 * scaleMultiplier,
        padding: '20px 32px',
        background: 'rgba(5, 10, 24, 0.9)',
        border: '1.5px solid rgba(56, 189, 248, 0.65)',
        borderRadius: 24,
        boxShadow: '0 16px 45px rgba(0,0,0,0.85), 0 0 25px rgba(56, 189, 248, 0.25)',
        backdropFilter: 'blur(12px)',
        transform: `scale(${entrance * scaleMultiplier})`,
        opacity: entrance,
        margin: '0 auto',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 14,
        }}
      >
        <span
          style={{
            color: '#38bdf8',
            fontFamily: "'Cinzel', serif",
            fontSize: 18,
            fontWeight: 800,
            letterSpacing: 2,
          }}
        >
          DOPPLER KIRMIZIYA KAYMA (REDSHIFT)
        </span>
        <span
          style={{
            color: '#ef4444',
            fontFamily: "'Cinzel', serif",
            fontSize: 16,
            fontWeight: 800,
            letterSpacing: 1,
          }}
        >
          z = Δλ / λ ➔ GENİŞLEME AKTİF
        </span>
      </div>

      {/* SVG Light Wave Stretching from Cyan to Crimson Red */}
      <svg width="816" height="90" viewBox="0 0 816 90">
        <defs>
          <linearGradient id="dopplerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#38bdf8" />
            <stop offset="40%" stopColor="#fbbf24" />
            <stop offset="100%" stopColor="#ef4444" />
          </linearGradient>
        </defs>

        {/* Sinusoidal Wave */}
        <path
          d={`M 0 45 Q ${40 * waveStretch} ${45 - 35} ${80 * waveStretch} 45 T ${160 * waveStretch} 45 T ${240 * waveStretch} 45 T ${320 * waveStretch} 45 T ${400 * waveStretch} 45 T ${480 * waveStretch} 45 T ${560 * waveStretch} 45 T ${640 * waveStretch} 45 T ${720 * waveStretch} 45 T ${800 * waveStretch} 45`}
          fill="none"
          stroke="url(#dopplerGrad)"
          strokeWidth="4"
          filter="drop-shadow(0 0 10px rgba(239, 68, 68, 0.6))"
          transform={`translate(${-waveShift}, 0)`}
        />
      </svg>

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginTop: 10,
          color: '#94a3b8',
          fontSize: 14,
          fontFamily: "'Cinzel', serif",
        }}
      >
        <span>YÜKSEK FREKANS (YAKLAŞMA)</span>
        <span style={{ color: '#ef4444', fontWeight: 800 }}>UZAY KUMAŞININ GENİŞLEMESİ (UZAKLAŞMA)</span>
      </div>
    </div>
  );
};
