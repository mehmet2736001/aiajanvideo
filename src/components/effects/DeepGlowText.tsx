import React from 'react';
import { useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';

interface DeepGlowTextProps {
  arabicText?: string;
  turkishMeal?: string;
  keywordHighlight?: string;
  subtext?: string;
  glowColor?: string;
  primaryColor?: string;
  yPosition?: number;
}

/**
 * DeepGlowText (İslami Hareketli Tipografi ve Derin Parlama Bileşeni)
 * 
 * Sufariq, Yaqeen ve Visual Deen ekolünün en belirgin özelliği olan
 * Uthmani Mushaf hattı ve Türkçe mealin içten dışa 3 kademeli altın
 * ışımasıyla (Deep Glow) parıldamasını sağlayan sinematik tipografi motoru.
 */
export const DeepGlowText: React.FC<DeepGlowTextProps> = ({
  arabicText,
  turkishMeal,
  keywordHighlight,
  subtext,
  glowColor = '#f3d081',
  primaryColor = '#f8fafc',
  yPosition = 500,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring animation
  const enterScale = spring({
    frame,
    fps,
    config: { damping: 16, stiffness: 80 },
  });

  const enterOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Breathing spiritual luminescence
  const glowIntensity = 1 + Math.sin(frame * 0.05) * 0.25;

  return (
    <div
      style={{
        position: 'absolute',
        top: yPosition,
        left: 0,
        width: 1080,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '0 60px',
        textAlign: 'center',
        zIndex: 25,
        opacity: enterOpacity,
        transform: `scale(${enterScale})`,
        pointerEvents: 'none',
      }}
    >
      {/* Arabic Calligraphy with 3-Layer Deep Glow */}
      {arabicText && (
        <div
          style={{
            fontFamily: "'Amiri', 'Traditional Arabic', 'Scheherazade New', serif",
            fontSize: '56px',
            lineHeight: '1.6',
            color: '#ffffff',
            direction: 'rtl',
            marginBottom: '24px',
            textShadow: `
              0 0 10px ${glowColor},
              0 0 25px ${glowColor},
              0 0 60px ${glowColor}aa,
              0 0 100px ${glowColor}44
            `,
            transform: `scale(${glowIntensity})`,
            transition: 'transform 0.1s ease',
          }}
        >
          {arabicText}
        </div>
      )}

      {/* Turkish Meaning with Accent Highlight */}
      {turkishMeal && (
        <div
          style={{
            fontFamily: "'Cinzel', 'Cormorant Garamond', Georgia, serif",
            fontSize: '32px',
            lineHeight: '1.5',
            color: primaryColor,
            maxWidth: '960px',
            letterSpacing: '0.5px',
            textShadow: '0 4px 16px rgba(0, 0, 0, 0.9)',
          }}
        >
          {keywordHighlight ? (
            <span>
              {turkishMeal.split(keywordHighlight).map((part, i, arr) => (
                <React.Fragment key={i}>
                  {part}
                  {i < arr.length - 1 && (
                    <span
                      style={{
                        color: glowColor,
                        fontWeight: 700,
                        textShadow: `0 0 16px ${glowColor}, 0 0 35px ${glowColor}88`,
                        padding: '0 6px',
                      }}
                    >
                      {keywordHighlight}
                    </span>
                  )}
                </React.Fragment>
              ))}
            </span>
          ) : (
            turkishMeal
          )}
        </div>
      )}

      {/* Surah Citation & Reference Badge */}
      {subtext && (
        <div
          style={{
            marginTop: '20px',
            padding: '6px 20px',
            borderRadius: '9999px',
            border: `1px solid ${glowColor}44`,
            background: 'rgba(5, 8, 20, 0.75)',
            backdropFilter: 'blur(8px)',
            fontFamily: "'Cinzel', sans-serif",
            fontSize: '18px',
            letterSpacing: '2px',
            color: glowColor,
            textTransform: 'uppercase',
            boxShadow: `0 0 20px ${glowColor}22`,
          }}
        >
          {subtext}
        </div>
      )}
    </div>
  );
};
