import React from 'react';
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { CardItem } from '../types';
import { Icon } from './Icons';

interface CardGridProps {
  cards: CardItem[];
  startFrame?: number;
  theme?: 'notebook' | 'kraft' | 'chalkboard' | 'parchment' | 'blueprint';
}

export const CardGrid: React.FC<CardGridProps> = ({
  cards,
  startFrame = 15,
  theme = 'notebook',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const isChalkboard = theme === 'chalkboard';
  const isBlueprint = theme === 'blueprint';
  const isParchment = theme === 'parchment';
  const isKraft = theme === 'kraft';

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 24,
        paddingLeft: 40,
        paddingRight: 40,
        marginTop: 40,
        width: '100%',
        boxSizing: 'border-box',
      }}
    >
      {cards.map((card, index) => {
        const delay = startFrame + index * 8;
        const currentLocalFrame = Math.max(0, frame - delay);

        const cardSpring = spring({
          frame: currentLocalFrame,
          fps,
          config: { damping: 14, mass: 0.7, stiffness: 120 },
        });

        // Theme adaptive card colors
        const cardBg = isChalkboard
          ? 'rgba(15, 32, 23, 0.88)'
          : isBlueprint
          ? 'rgba(12, 36, 60, 0.92)'
          : isParchment
          ? 'rgba(254, 250, 240, 0.92)'
          : isKraft
          ? 'rgba(254, 252, 245, 0.90)'
          : 'rgba(255, 255, 255, 0.92)';

        const borderColor = isChalkboard
          ? card.color === '#1e3a8a' ? '#38bdf8' : card.color
          : isBlueprint
          ? '#38bdf8'
          : isParchment
          ? '#b45309'
          : card.color || '#1e3a8a';

        const valueColor = isChalkboard || isBlueprint ? '#f8fafc' : isParchment ? '#451a03' : '#0f172a';

        return (
          <div
            key={card.id || index}
            style={{
              width: 290,
              height: 480,
              backgroundColor: cardBg,
              borderRadius: 24,
              border: `3.5px solid ${borderColor}`,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '30px 16px',
              boxSizing: 'border-box',
              boxShadow: isChalkboard
                ? `0 0 15px ${borderColor}30`
                : isBlueprint
                ? '0 0 20px rgba(56, 189, 248, 0.3)'
                : isParchment
                ? '0 8px 18px rgba(120, 53, 15, 0.12)'
                : '0 8px 18px rgba(0, 0, 0, 0.04)',
              transform: `scale(${cardSpring}) translateY(${(1 - cardSpring) * 30}px)`,
              opacity: cardSpring,
            }}
          >
            {/* Top Icon */}
            <div
              style={{
                height: 140,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                filter: isChalkboard || isBlueprint ? 'drop-shadow(0 0 8px rgba(56, 189, 248, 0.4))' : undefined,
              }}
            >
              <Icon name={card.icon} color={borderColor} size={110} />
            </div>

            {/* Label */}
            <div
              style={{
                fontSize: 42,
                fontWeight: 700,
                color: borderColor,
                fontStyle: 'italic',
                textAlign: 'center',
              }}
            >
              {card.label}
            </div>

            {/* Value */}
            <div
              style={{
                fontSize: 54,
                fontWeight: 900,
                color: valueColor,
                textAlign: 'center',
                letterSpacing: 1,
                marginBottom: 8,
                textShadow: isChalkboard || isBlueprint ? '0 0 8px rgba(255,255,255,0.4)' : undefined,
              }}
            >
              {card.value}
            </div>
          </div>
        );
      })}
    </div>
  );
};
