import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface QuranMatrixTableProps {
  title?: string;
  mode?: 'scroll' | 'grid';
  subtitle?: string;
}

// Sample representative dataset of Quranic Suras (Name, Sura No, Ayah Count)
const SURA_SAMPLE = [
  { no: 1, name: 'الفاتحة (Fâtiha)', ayahs: 7, sum: 8, isEven: true },
  { no: 2, name: 'البقرة (Bakara)', ayahs: 286, sum: 288, isEven: true },
  { no: 3, name: 'آل عمران (Âl-i İmrân)', ayahs: 200, sum: 203, isEven: false },
  { no: 4, name: 'النساء (Nisâ)', ayahs: 176, sum: 180, isEven: true },
  { no: 5, name: 'المائدة (Mâide)', ayahs: 120, sum: 125, isEven: false },
  { no: 6, name: 'الأنعام (En’âm)', ayahs: 165, sum: 171, isEven: false },
  { no: 7, name: 'الأعراف (A’râf)', ayahs: 206, sum: 213, isEven: false },
  { no: 8, name: 'الأنفال (Enfâl)', ayahs: 75, sum: 83, isEven: false },
  { no: 9, name: 'التوبة (Tevbe)', ayahs: 129, sum: 138, isEven: true },
  { no: 10, name: 'يونس (Yûnus)', ayahs: 109, sum: 119, isEven: false },
  { no: 67, name: 'الملك (Mülk)', ayahs: 30, sum: 97, isEven: false },
  { no: 68, name: 'القلم (Kalem)', ayahs: 52, sum: 120, isEven: true },
  { no: 112, name: 'الإخلاص (İhlâs)', ayahs: 4, sum: 116, isEven: true },
  { no: 113, name: 'الفلق (Felak)', ayahs: 5, sum: 118, isEven: true },
  { no: 114, name: 'الناس (Nâs)', ayahs: 6, sum: 120, isEven: true },
];

export const QuranMatrixTable: React.FC<QuranMatrixTableProps> = ({
  title = 'SÛRELERİN DİZİLİŞ VE AYET MATRİSİ',
  mode = 'scroll',
  subtitle = 'SIRA NUMARASI + ÂYET SAYISI = ŞEF’ VE VETİR',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 16, stiffness: 85, mass: 0.9 },
  });

  const fadeIn = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });
  const scrollOffsetY = interpolate(frame, [0, 120], [0, -180], { extrapolateRight: 'clamp' });

  return (
    <div
      style={{
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        opacity: fadeIn,
        transform: `scale(${entrance})`,
        padding: '24px 32px',
        borderRadius: 28,
        backgroundColor: 'rgba(3, 18, 12, 0.85)',
        border: '1.5px solid rgba(16, 185, 129, 0.45)',
        boxShadow: '0 16px 45px rgba(0, 0, 0, 0.9), 0 0 35px rgba(16, 185, 129, 0.25)',
        backdropFilter: 'blur(24px)',
        maxWidth: 900,
        margin: '16px auto',
        zIndex: 10,
        overflow: 'hidden',
      }}
    >
      {/* 1. Table Title */}
      {title && (
        <div
          style={{
            fontFamily: '"Cinzel", "Amiri", serif',
            fontSize: 22,
            fontWeight: 800,
            letterSpacing: '3px',
            color: '#a7f3d0',
            textTransform: 'uppercase',
            textAlign: 'center',
            marginBottom: 6,
            textShadow: '0 0 15px rgba(16, 185, 129, 0.6)',
          }}
        >
          {title}
        </div>
      )}

      {subtitle && (
        <div
          style={{
            fontSize: 14,
            fontWeight: 800,
            letterSpacing: '2px',
            color: '#facc15',
            textTransform: 'uppercase',
            marginBottom: 16,
            textAlign: 'center',
          }}
        >
          {subtitle}
        </div>
      )}

      {/* 2. Mode: Grid vs Scroll */}
      {mode === 'grid' ? (
        /* 114 Sura Number Grid (1 to 114 summing to 6,555) */
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(10, 1fr)',
              gap: 6,
              maxWidth: 620,
              padding: '16px',
              borderRadius: 16,
              backgroundColor: 'rgba(2, 44, 34, 0.6)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
            }}
          >
            {Array.from({ length: 114 }, (_, i) => i + 1).map((num) => {
              const isHighlighted = (num + Math.floor(frame / 4)) % 12 === 0;
              return (
                <div
                  key={`grid_num_${num}`}
                  style={{
                    width: 48,
                    height: 32,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 13,
                    fontWeight: 700,
                    borderRadius: 6,
                    backgroundColor: isHighlighted ? 'rgba(250, 204, 21, 0.3)' : 'rgba(15, 23, 42, 0.6)',
                    color: isHighlighted ? '#fef08a' : '#94a3b8',
                    border: isHighlighted ? '1px solid #facc15' : '1px solid rgba(255,255,255,0.08)',
                    transition: 'all 0.1s ease',
                  }}
                >
                  {num}
                </div>
              );
            })}
          </div>
          <div
            style={{
              marginTop: 14,
              fontSize: 18,
              fontWeight: 800,
              color: '#fde047',
              letterSpacing: '2px',
            }}
          >
            1 + 2 + 3 + ... + 114 = <span style={{ fontSize: 24, fontWeight: 900 }}>6.555</span>
          </div>
        </div>
      ) : (
        /* Scrolling Matrix Table */
        <div style={{ width: '100%', maxWidth: 720 }}>
          {/* Table Header Row */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '2.5fr 1fr 1fr 1.2fr',
              padding: '10px 16px',
              borderRadius: 12,
              backgroundColor: 'rgba(16, 185, 129, 0.25)',
              border: '1px solid rgba(16, 185, 129, 0.5)',
              fontSize: 15,
              fontWeight: 800,
              color: '#ffffff',
              letterSpacing: '1px',
              textAlign: 'center',
              marginBottom: 8,
            }}
          >
            <span style={{ textAlign: 'left' }}>SÛRE ADI</span>
            <span>SIRA (A)</span>
            <span>ÂYET (B)</span>
            <span>TOPLAM (A+B)</span>
          </div>

          {/* Scrolling Rows Container */}
          <div
            style={{
              position: 'relative',
              height: 240,
              overflow: 'hidden',
              borderRadius: 12,
              backgroundColor: 'rgba(2, 24, 18, 0.5)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 6,
                padding: '8px',
                transform: `translateY(${scrollOffsetY}px)`,
              }}
            >
              {SURA_SAMPLE.map((row, idx) => (
                <div
                  key={`sura_row_${idx}`}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '2.5fr 1fr 1fr 1.2fr',
                    padding: '8px 14px',
                    borderRadius: 8,
                    backgroundColor: row.isEven ? 'rgba(245, 158, 11, 0.12)' : 'rgba(16, 185, 129, 0.12)',
                    border: `1px solid ${row.isEven ? 'rgba(245, 158, 11, 0.35)' : 'rgba(16, 185, 129, 0.35)'}`,
                    fontSize: 16,
                    fontWeight: 700,
                    alignItems: 'center',
                    textAlign: 'center',
                  }}
                >
                  <span style={{ textAlign: 'left', color: '#f8fafc', fontWeight: 800 }}>{row.name}</span>
                  <span style={{ color: '#cbd5e1' }}>{row.no}</span>
                  <span style={{ color: '#cbd5e1' }}>{row.ayahs}</span>
                  <span
                    style={{
                      color: row.isEven ? '#fde047' : '#6ee7b7',
                      fontWeight: 900,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 4,
                    }}
                  >
                    {row.sum}
                    <span style={{ fontSize: 11, padding: '2px 6px', borderRadius: 4, backgroundColor: 'rgba(0,0,0,0.4)' }}>
                      {row.isEven ? 'ÇİFT' : 'TEK'}
                    </span>
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
