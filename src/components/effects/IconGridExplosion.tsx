import React from 'react';
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { Icon } from '../Icons';

interface IconGridProps {
  title?: string;
  subtitle?: string;
  iconType?: 'fingerprint' | 'star' | 'dna' | 'atom' | 'human';
  itemCount?: number;
  accentColor?: string;
  badgeText?: string;
}

export const IconGridExplosion: React.FC<IconGridProps> = ({
  title = 'MİLYARLARCA İNSAN',
  subtitle = 'HİÇBİRİNİN PARMAK İZİ AYNI DEĞİL',
  iconType = 'fingerprint',
  itemCount = 12,
  accentColor = '#facc15',
  badgeText,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const items = Array.from({ length: Math.min(16, itemCount) });

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '10px 30px',
        width: '100%',
      }}
    >
      {/* Top Badge */}
      {Boolean(badgeText) && (
        <div
          style={{
            fontSize: 24,
            fontWeight: 800,
            color: accentColor,
            border: `2px solid ${accentColor}60`,
            borderRadius: 30,
            padding: '6px 24px',
            marginBottom: 16,
            letterSpacing: 2,
            backgroundColor: `${accentColor}15`,
            textTransform: 'uppercase',
          }}
        >
          {badgeText}
        </div>
      )}

      {/* Main Title */}
      <h2
        style={{
          fontSize: 64,
          fontWeight: 900,
          color: '#ffffff',
          letterSpacing: 2,
          textAlign: 'center',
          marginBottom: 32,
          lineHeight: 1.1,
          textShadow: '0 4px 20px rgba(0,0,0,0.8)',
        }}
      >
        {title.split(' ')[0]}{' '}
        <span style={{ color: accentColor, textShadow: `0 0 24px ${accentColor}80` }}>
          {title.split(' ').slice(1).join(' ')}
        </span>
      </h2>

      {/* 3x4 Icon Matrix */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: 22,
          width: '100%',
          maxWidth: 720,
          marginBottom: 36,
        }}
      >
        {items.map((_, i) => {
          // Staggered spring entrance
          const delay = i * 2;
          const scale = spring({
            frame: frame - delay,
            fps,
            config: { damping: 12, mass: 0.6 },
          });

          // Gentle ambient pulse
          const pulse = Math.sin((frame + i * 15) * 0.08) * 0.06;

          return (
            <div
              key={i}
              style={{
                transform: `scale(${Math.max(0, scale + pulse)})`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'radial-gradient(circle, rgba(250, 204, 21, 0.12) 0%, rgba(10, 16, 26, 0.6) 80%)',
                border: `1.5px solid ${accentColor}40`,
                borderRadius: 20,
                padding: 16,
                boxShadow: `0 8px 24px rgba(0,0,0,0.4), inset 0 0 16px ${accentColor}15`,
              }}
            >
                <Icon name={iconType} size={64} color={accentColor} />
            </div>
          );
        })}
      </div>

      {/* Subtitle / Takeaway */}
      {subtitle && (
        <p
          style={{
            fontSize: 42,
            fontWeight: 800,
            color: '#ffffff',
            letterSpacing: 1.5,
            textAlign: 'center',
            maxWidth: 820,
            lineHeight: 1.25,
            textShadow: '0 2px 12px rgba(0,0,0,0.8)',
          }}
        >
          {subtitle}
        </p>
      )}
    </div>
  );
};
