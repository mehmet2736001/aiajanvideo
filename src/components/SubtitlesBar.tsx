import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { SubtitleWord } from '../types';

// Turkish clitics that must NEVER wrap alone or be separated from their host word
const TURKISH_CLITICS = new Set([
  'mi', 'mı', 'mu', 'mü',
  'misin', 'mısın', 'musun', 'müsün',
  'miyiz', 'mıyız', 'muyuz', 'müyüz',
  'miydi', 'mıydı', 'muydu', 'müydü',
  'miymiş', 'mıymış', 'muymuş', 'müymüş',
  'midir', 'mıdır', 'mudur', 'müdür',
  'miyim', 'mıyım',
  'misiniz', 'mısınız', 'musunuz', 'müsünüz',
  'miler', 'mılar',
  'de', 'da', 'ki', 'ise', 'bile', 'dahi'
]);

const isCliticToken = (token: string): boolean => {
  if (!token) return false;
  const clean = token.toLowerCase().replace(/[^a-zçğıöşü]/g, '');
  return TURKISH_CLITICS.has(clean);
};

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
  const { fps, width, height } = useVideoConfig();
  const isHorizontal = width > height;


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

  // CapCut viral spring entrance for the whole phrase
  const pillScale = activeWord
    ? spring({
        frame: Math.max(0, frame - Math.floor(activeWord.start * fps)),
        fps,
        config: { damping: 10, mass: 0.45, stiffness: 220 },
      })
    : 1;

  // Sweep progress for highlighter marker under the words (0% -> 100%)
  const chunkDuration = activeWord ? Math.max(0.2, activeWord.end - activeWord.start) : 1;
  const elapsed = activeWord ? Math.max(0, currentTime - activeWord.start) : 0;
  const sweepProgress = interpolate(elapsed, [0, chunkDuration * 0.88], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const pillBg = isDarkMotion
    ? 'rgba(6, 10, 18, 0.94)'
    : isChalkboard
    ? 'rgba(15, 30, 22, 0.96)'
    : isBlueprint
    ? 'rgba(10, 35, 60, 0.96)'
    : isParchment
    ? '#faf1dc'
    : isKraft
    ? '#ede0c8'
    : 'rgba(255, 255, 255, 0.96)';

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

  const defaultTextColor = isDarkMotion
    ? '#ffffff'
    : isChalkboard
    ? '#f8fafc'
    : isBlueprint
    ? '#ffffff'
    : isParchment
    ? '#451a03'
    : isKraft
    ? '#292524'
    : '#1e3a8a';

  const highlightColor = isDarkMotion
    ? theme === 'neon_cyber'
      ? '#38bdf8'
      : '#facc15'
    : isChalkboard
    ? '#86efac'
    : isBlueprint
    ? '#38bdf8'
    : '#eab308';

  const highlighterStrokeColor = isDarkMotion
    ? theme === 'neon_cyber'
      ? 'rgba(56, 189, 248, 0.4)'
      : 'rgba(250, 204, 21, 0.35)'
    : isChalkboard
    ? 'rgba(134, 239, 172, 0.35)'
    : isBlueprint
    ? 'rgba(56, 189, 248, 0.35)'
    : 'rgba(254, 240, 138, 0.85)';

  const effectiveFont = isRTL
    ? '"Cairo", "Amiri", -apple-system, sans-serif'
    : isDarkMotion
    ? '"Montserrat", "Inter", -apple-system, sans-serif'
    : '"Caveat", "Kalam", cursive, sans-serif';

  // Words list for word-by-word karaoke progression with apostrophe stitching
  const cleanActiveText = activeWord
    ? activeWord.text
        .replace(/([A-Za-zÇĞİÖŞÜçğıöşü]+)\s*['’‘ʼ`´]\s*([A-Za-zÇĞİÖŞÜçğıöşü]+)/g, "$1'$2")
        .replace(/\bKur\s+an\b/gi, "Kur'an")
        .replace(/\bKur\s+an'([a-zçğıöşü]+)\b/gi, "Kur'an'$1")
        .replace(/Kur'an[\s\-]+ı\s+Kerim/gi, "Kur'an-ı Kerim")
        .replace(/\s+/g, ' ')
        .trim()
    : '';
  const words = cleanActiveText ? cleanActiveText.split(/\s+/) : [];
  const wordsCount = Math.max(1, words.length);
  const activeWordIndex = Math.min(
    wordsCount - 1,
    Math.floor((elapsed / chunkDuration) * wordsCount)
  );

  // Group clitic words with their preceding host word into visual nowrap groups
  // e.g. ["Sen", "de"] -> group, ["gördün", "mü?"] -> group
  const visualGroups: Array<Array<{ word: string; wIdx: number }>> = [];
  for (let i = 0; i < words.length; i++) {
    const w = words[i];
    if (i > 0 && isCliticToken(w) && visualGroups.length > 0) {
      visualGroups[visualGroups.length - 1].push({ word: w, wIdx: i });
    } else {
      visualGroups.push([{ word: w, wIdx: i }]);
    }
  }

  return (
    <div
      style={{
        position: 'absolute',
        bottom: isHorizontal ? 35 : 110,
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
      {/* CapCut Viral Subtitle Pill with Dynamic Word Highlight & Sweep */}
      {activeWord && (
        <div
          style={{
            position: 'relative',
            backgroundColor: pillBg,
            border: pillBorder,
            borderRadius: isDarkMotion ? 20 : 24,
            padding: isDarkMotion ? '12px 36px' : '12px 40px',
            boxShadow: isDarkMotion
              ? '0 12px 32px rgba(0, 0, 0, 0.75), 0 0 24px rgba(250, 204, 21, 0.2)'
              : '0 10px 24px rgba(0, 0, 0, 0.12)',
            marginBottom: 16,
            transform: `scale(${Math.max(0.85, Math.min(1.14, pillScale))})`,
            transition: 'transform 0.08s cubic-bezier(0.34, 1.56, 0.64, 1)',
            backdropFilter: isDarkMotion ? 'blur(12px)' : undefined,
          }}
        >
          {/* Animated SVG Marker Sweep Stroke Under the Phrase */}
          <div
            style={{
              position: 'absolute',
              bottom: 8,
              left: isRTL ? undefined : 20,
              right: isRTL ? 20 : undefined,
              width: `calc(${sweepProgress}% - 40px)`,
              height: 12,
              backgroundColor: highlighterStrokeColor,
              borderRadius: 6,
              transform: 'rotate(-0.5deg)',
              pointerEvents: 'none',
              zIndex: 0,
              transition: 'width 0.06s linear',
            }}
          />

          {/* Karaoke Words Container */}
          <div
            style={{
              position: 'relative',
              zIndex: 1,
              display: 'flex',
              flexDirection: 'row',
              alignItems: 'center',
              justifyContent: 'center',
              gap: isDarkMotion ? 12 : 14,
              flexWrap: 'wrap',
            }}
          >
            {visualGroups.map((group, gIdx) => (
              <span
                key={`group-${gIdx}`}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: isDarkMotion ? 10 : 12,
                  whiteSpace: 'nowrap',
                }}
              >
                {group.map(({ word, wIdx }) => {
                  const isWordActive = wIdx === activeWordIndex;
                  const hasBeenSpoken = wIdx <= activeWordIndex;

                  return (
                    <span
                      key={`${word}-${wIdx}`}
                      style={{
                        fontSize: isDarkMotion ? (isWordActive ? 48 : 44) : (isWordActive ? 56 : 52),
                        fontWeight: 900,
                        color: isWordActive
                          ? highlightColor
                          : hasBeenSpoken
                          ? defaultTextColor
                          : isDarkMotion
                          ? 'rgba(255,255,255,0.6)'
                          : '#64748b',
                        letterSpacing: isDarkMotion ? 2 : 1.5,
                        textTransform: isDarkMotion ? 'uppercase' : 'none',
                        transform: isWordActive ? 'scale(1.12)' : 'scale(1)',
                        transition: 'transform 0.1s ease, color 0.1s ease',
                        textShadow: isWordActive
                          ? isDarkMotion
                            ? `0 2px 10px rgba(0,0,0,0.9), 0 0 16px ${highlightColor}`
                            : isChalkboard
                            ? '0 0 12px rgba(134, 239, 172, 0.7)'
                            : isBlueprint
                            ? '0 0 14px rgba(56, 189, 248, 0.7)'
                            : '0 2px 4px rgba(0,0,0,0.2)'
                          : undefined,
                      }}
                    >
                      {word}
                    </span>
                  );
                })}
              </span>
            ))}
          </div>
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
            fontSize: isDarkMotion ? 24 : 30,
            fontWeight: 700,
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
