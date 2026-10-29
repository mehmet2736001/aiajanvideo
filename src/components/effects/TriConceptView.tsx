import React from 'react';
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { TriConceptData } from '../../types';
import { Icon } from '../Icons';

interface TriConceptProps {
  data?: TriConceptData;
  theme?: string;
}

export const TriConceptView: React.FC<TriConceptProps> = ({ data, theme = 'dark_minimalist' }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const c1 = data?.concept1 || { title: 'BEYİN', subtitle: 'Hafıza & Akıl', icon: 'brain', color: '#38bdf8' };
  const c2 = data?.concept2 || { title: 'KALP', subtitle: 'Yaşam Merkezi', icon: 'heart', color: '#ef4444' };
  const c3 = data?.concept3 || { title: 'GÖZ', subtitle: 'En İnce Mercek', icon: 'eye', color: '#facc15' };

  const concepts = [c1, c2, c3];

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px 24px',
        width: '100%',
      }}
    >
      {/* Top Badge */}
      {data?.badge && (
        <div
          style={{
            fontSize: 26,
            fontWeight: 800,
            color: '#facc15',
            backgroundColor: 'rgba(250, 204, 21, 0.12)',
            border: '2px solid rgba(250, 204, 21, 0.4)',
            borderRadius: 30,
            padding: '6px 26px',
            marginBottom: 28,
            letterSpacing: 2,
            textTransform: 'uppercase',
          }}
        >
          {data.badge}
        </div>
      )}

      {/* 3 Organ / Concept Cards in Row */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: 20,
          width: '100%',
          maxWidth: 920,
          marginBottom: 36,
        }}
      >
        {concepts.map((c, i) => {
          const delay = i * 4;
          const scale = spring({
            frame: frame - delay,
            fps,
            config: { damping: 13, mass: 0.7 },
          });

          const float = Math.sin((frame + i * 20) * 0.08) * 8;

          return (
            <div
              key={i}
              style={{
                transform: `scale(${Math.max(0, scale)}) translateY(${float}px)`,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                background: 'linear-gradient(180deg, rgba(15, 23, 42, 0.85) 0%, rgba(8, 12, 20, 0.95) 100%)',
                border: `2px solid ${c.color || '#38bdf8'}60`,
                borderRadius: 24,
                padding: '32px 16px',
                boxShadow: `0 12px 32px rgba(0,0,0,0.5), 0 0 24px ${c.color || '#38bdf8'}25`,
              }}
            >
              {/* Icon Container */}
              <div
                style={{
                  width: 90,
                  height: 90,
                  borderRadius: '50%',
                  backgroundColor: `${c.color || '#38bdf8'}20`,
                  border: `2px solid ${c.color || '#38bdf8'}80`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: 18,
                  boxShadow: `0 0 20px ${c.color || '#38bdf8'}40`,
                }}
              >
                <Icon name={c.icon} size={48} color={c.color || '#38bdf8'} />
              </div>

              {/* Title */}
              <div
                style={{
                  fontSize: 38,
                  fontWeight: 900,
                  color: '#ffffff',
                  letterSpacing: 1.5,
                  marginBottom: 6,
                }}
              >
                {c.title}
              </div>

              {/* Subtitle */}
              {c.subtitle && (
                <div
                  style={{
                    fontSize: 22,
                    fontWeight: 600,
                    color: '#94a3b8',
                  }}
                >
                  {c.subtitle}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Bottom Takeaway Note */}
      {data?.bottomNote && (
        <div
          style={{
            fontSize: 34,
            fontWeight: 800,
            color: '#fbbf24',
            letterSpacing: 2,
            textAlign: 'center',
            textTransform: 'uppercase',
            textShadow: '0 2px 14px rgba(251, 191, 36, 0.4)',
          }}
        >
          {data.bottomNote}
        </div>
      )}
    </div>
  );
};
