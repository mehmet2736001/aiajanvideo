import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';

interface EtymologyRootCardProps {
  arabicWord?: string;
  transliteration?: string;
  rootWord?: string;
  definition?: string;
  significance?: string;
}

export const EtymologyRootCard: React.FC<EtymologyRootCardProps> = ({
  arabicWord = 'الْمَسْجُورِ',
  transliteration = 'el-Bahru’l-Mescûr',
  rootWord = 'س - ج - ر  (SECR)',
  definition = 'Tandır veya fırını harlı ateşle doldurup kızdırmak.',
  significance = '7. yüzyılda serin bir su kütlesi olarak bilinen okyanusun altına Kur’an’ın «kızgın fırın» teşhisi koyması...',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 16, stiffness: 85, mass: 0.9 },
  });

  const fadeIn = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: 'clamp' });
  const gentleFloat = Math.sin(frame * 0.05) * 5;
  const flamePulse = 0.85 + Math.sin(frame * 0.12) * 0.15;

  return (
    <div
      style={{
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        opacity: fadeIn,
        transform: `scale(${entrance}) translateY(${gentleFloat}px)`,
        padding: '28px 40px',
        borderRadius: 28,
        backgroundColor: 'rgba(4, 8, 20, 0.85)',
        border: '1.5px solid rgba(245, 158, 11, 0.55)',
        boxShadow: '0 16px 45px rgba(0, 0, 0, 0.9), 0 0 35px rgba(245, 158, 11, 0.25)',
        backdropFilter: 'blur(24px)',
        maxWidth: 900,
        margin: '16px auto',
        zIndex: 10,
      }}
    >
      {/* 1. Category Tag */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          padding: '6px 22px',
          borderRadius: 9999,
          backgroundColor: 'rgba(245, 158, 11, 0.15)',
          border: '1px solid rgba(245, 158, 11, 0.45)',
          color: '#facc15',
          fontSize: 16,
          fontWeight: 800,
          letterSpacing: '2px',
          textTransform: 'uppercase',
          marginBottom: 16,
        }}
      >
        <span>۞</span>
        <span>İLÂHİ KELİME TAHKÎKİ</span>
        <span>۞</span>
      </div>

      {/* 2. Golden Celi Sülüs Arabic Calligraphy */}
      <div
        style={{
          fontFamily: '"Amiri", "Scheherazade New", serif',
          fontSize: 68,
          fontWeight: 700,
          direction: 'rtl',
          color: '#fef08a',
          lineHeight: 1.25,
          textShadow: '0 0 25px rgba(245, 158, 11, 0.75), 0 4px 18px rgba(0,0,0,0.95)',
          marginBottom: 8,
        }}
      >
        {arabicWord}
      </div>

      {/* 3. Transliteration & Latin Phonetics */}
      <div
        style={{
          fontFamily: '"Cinzel", "Montserrat", sans-serif',
          fontSize: 26,
          fontWeight: 800,
          letterSpacing: '3px',
          color: '#38bdf8',
          textShadow: '0 0 15px rgba(56, 189, 248, 0.6)',
          marginBottom: 16,
        }}
      >
        {transliteration}
      </div>

      {/* 4. Root Word Pill */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '8px 24px',
          borderRadius: 14,
          backgroundColor: 'rgba(220, 38, 38, 0.2)',
          border: '1.5px solid rgba(239, 68, 68, 0.6)',
          color: '#fca5a5',
          fontSize: 19,
          fontWeight: 800,
          letterSpacing: '2px',
          marginBottom: 18,
        }}
      >
        <span style={{ fontSize: 20, opacity: flamePulse }}>🔥</span>
        <span>KÖKÜ: {rootWord}</span>
        <span style={{ fontSize: 20, opacity: flamePulse }}>🔥</span>
      </div>

      {/* 5. Classical Dictionary Definition */}
      <div
        style={{
          fontFamily: '"Cormorant Garamond", Georgia, serif',
          fontSize: 28,
          fontWeight: 700,
          color: '#f8fafc',
          textAlign: 'center',
          lineHeight: 1.45,
          maxWidth: 780,
          marginBottom: 12,
        }}
      >
        “{definition}”
      </div>

      {/* 6. Theological / Scientific Significance */}
      {significance && (
        <div
          style={{
            fontSize: 17,
            fontWeight: 600,
            fontStyle: 'italic',
            color: '#94a3b8',
            textAlign: 'center',
            lineHeight: 1.5,
            maxWidth: 780,
            paddingTop: 12,
            borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          {significance}
        </div>
      )}
    </div>
  );
};
