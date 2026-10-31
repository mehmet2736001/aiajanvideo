import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { QuoteSpotlightData } from '../types';

interface QuoteSpotlightViewProps {
  quoteSpotlight: QuoteSpotlightData;
  theme?: string;
  startFrame?: number;
}

export const QuoteSpotlightView: React.FC<QuoteSpotlightViewProps> = ({
  quoteSpotlight,
  theme = 'notebook',
  startFrame = 10,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const isChalkboard = theme === 'chalkboard';
  const isBlueprint = theme === 'blueprint';
  const isParchment = theme === 'parchment';
  const isKraft = theme === 'kraft';

  const paperScale = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 13, mass: 0.9 },
  });

  const sealSpring = spring({
    frame: frame - (startFrame + 25),
    fps,
    config: { damping: 10, mass: 0.7 },
  });

  const paperBg = isChalkboard
    ? 'rgba(20, 36, 28, 0.95)'
    : isBlueprint
    ? 'rgba(12, 40, 70, 0.95)'
    : isParchment
    ? '#faf1dc'
    : isKraft
    ? '#ede0c8'
    : '#ffffff';

  const borderColor = isChalkboard
    ? '#86efac'
    : isBlueprint
    ? '#38bdf8'
    : isParchment
    ? '#92400e'
    : '#1e3a8a';

  const textPrimary = isChalkboard || isBlueprint ? '#ffffff' : '#0f172a';
  const textMuted = isChalkboard ? '#cbd5e1' : isBlueprint ? '#93c5fd' : '#475569';

  const isVerse = (quoteSpotlight as any).isVerse || (quoteSpotlight.title && (quoteSpotlight.title.toLowerCase().includes('ayet') || quoteSpotlight.title.toLowerCase().includes('sure') || quoteSpotlight.title.toLowerCase().includes('hadis')));
  const badgeText = (quoteSpotlight as any).verseBadge || (isVerse ? 'AYET-İ KERİME' : (quoteSpotlight.title || 'HİKMETLİ SÖZ'));
  const rawText = quoteSpotlight.quoteText || (quoteSpotlight as any).quote || (quoteSpotlight as any).text || '';

  // Typewriter calculation
  const elapsedFrames = Math.max(0, frame - (startFrame + 12));
  const charsToShow = Math.min(rawText.length, Math.floor(elapsedFrames * 1.6));
  const currentText = rawText.slice(0, charsToShow);
  const isFinished = charsToShow >= rawText.length;

  const targetWords = (((quoteSpotlight as any).underlinedWords) || ['adalet', 'ilim', 'sabır', 'allah', 'huzur', 'hakikat']).map((w: string) => w.toLowerCase());

  const words = currentText.split(' ');
  const renderedWords = words.map((w: string, idx: number) => {
    const clean = w.replace(/[.,/#!$%^&*;:{}=\-_`~()"“”!?’]/g, '').toLowerCase();
    const shouldUnderline = targetWords.some((tw: string) => clean.includes(tw) || tw.includes(clean));
    if (shouldUnderline && clean.length > 2) {
      return (
        <span
          key={idx}
          style={{
            display: 'inline-block',
            position: 'relative',
            color: '#d97706',
            fontWeight: 900,
            borderBottom: '4px solid #f59e0b',
            paddingBottom: 2,
            marginRight: 8,
            textShadow: '0 0 12px rgba(245, 158, 11, 0.5)',
          }}
        >
          {w}
        </span>
      );
    }
    return (
      <span key={idx} style={{ marginRight: 8 }}>
        {w}
      </span>
    );
  });

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '0 40px',
        width: '100%',
        position: 'relative',
      }}
    >
      {/* Pinned Note Container */}
      <div
        style={{
          width: '100%',
          maxWidth: 820,
          backgroundColor: paperBg,
          border: `4px solid ${borderColor}`,
          borderRadius: 32,
          padding: '44px 36px 36px',
          boxShadow: '0 20px 45px rgba(0,0,0,0.15)',
          transform: `scale(${Math.max(0, paperScale)}) rotate(-1deg)`,
          position: 'relative',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
        }}
      >
        {/* Washi Masking Tape on Top */}
        <div
          style={{
            position: 'absolute',
            top: -16,
            left: '50%',
            transform: 'translateX(-50%) rotate(2deg)',
            width: 140,
            height: 32,
            backgroundColor: 'rgba(251, 191, 36, 0.85)',
            borderLeft: '3px dashed rgba(217, 119, 6, 0.5)',
            borderRight: '3px dashed rgba(217, 119, 6, 0.5)',
            boxShadow: '0 4px 10px rgba(0,0,0,0.1)',
          }}
        />

        {/* Big Decorative Quotation Marks */}
        <div
          style={{
            fontSize: 72,
            lineHeight: 0.6,
            color: borderColor,
            opacity: 0.35,
            fontWeight: 900,
            marginBottom: 10,
          }}
        >
          “
        </div>

        {/* Subtitle / Category / Verse Badge */}
        <div
          style={{
            fontSize: isVerse ? 28 : 24,
            fontWeight: 900,
            color: isVerse ? '#d97706' : borderColor,
            letterSpacing: 3,
            textTransform: 'uppercase',
            marginBottom: 14,
            padding: isVerse ? '4px 20px' : '0',
            borderRadius: 20,
            backgroundColor: isVerse ? 'rgba(217, 119, 6, 0.12)' : 'transparent',
            border: isVerse ? '2px solid rgba(217, 119, 6, 0.4)' : 'none',
          }}
        >
          {badgeText}
        </div>

        {/* The Giant Quote Text with Typewriter & Gold Underline */}
        <div
          style={{
            fontSize: 38,
            fontWeight: 900,
            color: textPrimary,
            lineHeight: 1.4,
            padding: '0 20px',
            marginBottom: 26,
            fontStyle: 'italic',
            minHeight: 110,
          }}
        >
          “{renderedWords}
          {!isFinished && (
            <span
              style={{
                display: 'inline-block',
                width: 12,
                height: 34,
                backgroundColor: '#f59e0b',
                marginLeft: 6,
                verticalAlign: 'middle',
                opacity: (frame % 20 < 10) ? 1 : 0.2,
                boxShadow: '0 0 10px #f59e0b',
              }}
            />
          )}”
        </div>

        {/* Speaker & Source */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            width: '100%',
            borderTop: `2px dashed ${isChalkboard ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.12)'}`,
            paddingTop: 18,
            marginTop: 'auto',
          }}
        >
          <div style={{ textAlign: 'left' }}>
            <div style={{ fontSize: 30, fontWeight: 900, color: textPrimary }}>
              — {quoteSpotlight.speaker || (quoteSpotlight as any).author || 'Ses Kaydı'}
            </div>
            {quoteSpotlight.sourceRef && (
              <div style={{ fontSize: 22, fontWeight: 600, color: textMuted, marginTop: 2 }}>
                {quoteSpotlight.sourceRef}
              </div>
            )}
          </div>

          {/* Wax Seal / Stamp */}
          <div
            style={{
              width: 72,
              height: 72,
              borderRadius: '50%',
              backgroundColor: '#dc2626',
              border: '3px solid #b91c1c',
              boxShadow: '0 6px 15px rgba(220, 38, 38, 0.4)',
              transform: `scale(${Math.max(0, sealSpring)}) rotate(12deg)`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              fontSize: 28,
              fontWeight: 900,
            }}
          >
            ★
          </div>
        </div>
      </div>
    </div>
  );
};
