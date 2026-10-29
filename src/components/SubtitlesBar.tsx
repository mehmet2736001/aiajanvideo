import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { SubtitleWord } from '../types';

interface SubtitlesBarProps {
  subtitles?: SubtitleWord[];
  socialHandle?: string;
  theme?: string;
  isRTL?: boolean;
}

export const SubtitlesBar: React.FC<SubtitlesBarProps> = ({
  subtitles = [],
  socialHandle = '@birkissa',
  theme = 'notebook',
  isRTL = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const currentTime = frame / fps;

  const isChalkboard = theme === 'chalkboard';
  const isBlueprint = theme === 'blueprint';
  const isParchment = theme === 'parchment';
  const isKraft = theme === 'kraft';
  const isDarkMotion =
    theme === 'dark_minimalist' ||
    theme === 'neon_cyber' ||
    theme === 'gold_luxury';

  // Find currently active subtitle chunk with smooth persistence between pauses
  let activeWord: SubtitleWord | null = null;
  for (let i = 0; i < subtitles.length; i++) {
    const sub = subtitles[i];
    const nextStart = i + 1 < subtitles.length ? subtitles[i + 1].start : sub.end + 0.5;
    const holdUntil = Math.min(nextStart, sub.end + 0.45);
    if (currentTime >= sub.start && currentTime <= holdUntil) {
      activeWord = sub;
      break;
    }
  }

  // Spring entrance for subtitle pill
  const pillScale = activeWord
    ? spring({
        frame: frame - Math.floor(activeWord.start * fps),
        fps,
        config: { damping: 14, mass: 0.7 },
      })
    : 1;

  const pillBg = isDarkMotion
    ? 'rgba(6, 10, 18, 0.92)'
    : isChalkboard
    ? 'rgba(15, 30, 22, 0.95)'
    : isBlueprint
    ? 'rgba(10, 35, 60, 0.95)'
    : isParchment
    ? '#faf1dc'
    : isKraft
    ? '#ede0c8'
    : 'rgba(255, 255, 255, 0.95)';

  const pillBorder = isDarkMotion
    ? theme === 'neon_cyber'
      ? '2px solid rgba(56, 189, 248, 0.85)'
      : '2px solid rgba(250, 204, 21, 0.85)'
    : isChalkboard
    ? '3px solid #86efac'
    : isBlueprint
    ? '3px solid #38bdf8'
    : isParchment
    ? '3px solid #92400e'
    : '3px solid #1e3a8a';

  const textColor = isDarkMotion
    ? theme === 'neon_cyber'
      ? '#38bdf8'
      : '#facc15'
    : isChalkboard
    ? '#f8fafc'
    : isBlueprint
    ? '#ffffff'
    : isParchment
    ? '#451a03'
    : isKraft
    ? '#292524'
    : '#1e3a8a';

  const effectiveFont = isRTL
    ? '"Cairo", "Amiri", -apple-system, sans-serif'
    : isDarkMotion
    ? '"Montserrat", "Inter", -apple-system, sans-serif'
    : '"Caveat", "Kalam", cursive, sans-serif';

  return (
    <div
      style={{
        position: 'absolute',
        bottom: 110,
        left: 0,
        right: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: effectiveFont,
        direction: isRTL ? 'rtl' : 'ltr',
        zIndex: 20,
      }}
    >
      {/* Dynamic Word Pill with Whisper millisecond sync */}
      {activeWord && (
        <div
          style={{
            backgroundColor: pillBg,
            border: pillBorder,
            borderRadius: isDarkMotion ? 20 : 24,
            padding: isDarkMotion ? '12px 38px' : '14px 42px',
            boxShadow: isDarkMotion
              ? '0 12px 32px rgba(0, 0, 0, 0.7), 0 0 24px rgba(250, 204, 21, 0.15)'
              : '0 10px 24px rgba(0, 0, 0, 0.12)',
            marginBottom: 16,
            transform: `scale(${Math.max(0.85, Math.min(1.05, pillScale))})`,
            transition: 'transform 0.1s ease',
            backdropFilter: isDarkMotion ? 'blur(12px)' : undefined,
          }}
        >
          <span
            style={{
              fontSize: isDarkMotion ? 44 : 54,
              fontWeight: 900,
              color: textColor,
              letterSpacing: isDarkMotion ? 2 : 1.5,
              textTransform: isDarkMotion ? 'uppercase' : 'none',
              textShadow: isDarkMotion
                ? '0 2px 10px rgba(0,0,0,0.8)'
                : isChalkboard
                ? '0 0 10px rgba(134, 239, 172, 0.4)'
                : isBlueprint
                ? '0 0 12px rgba(56, 189, 248, 0.5)'
                : undefined,
            }}
          >
            {activeWord.text}
          </span>
        </div>
      )}

      {/* Social Handle */}
      {socialHandle && (
        <div
          style={{
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            gap: 16,
            fontSize: isDarkMotion ? 24 : 32,
            fontWeight: isDarkMotion ? 700 : 700,
            color: isDarkMotion
              ? 'rgba(255, 255, 255, 0.55)'
              : isChalkboard
              ? '#94a3b8'
              : isBlueprint
              ? '#93c5fd'
              : '#64748b',
            fontStyle: isDarkMotion ? 'normal' : 'italic',
            letterSpacing: isDarkMotion ? 1 : 0.5,
          }}
        >
          <div>Instagram: {socialHandle}</div>
          <div>•</div>
          <div>YouTube: {socialHandle}</div>
        </div>
      )}
    </div>
  );
};
