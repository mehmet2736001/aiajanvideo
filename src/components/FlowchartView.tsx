import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { FlowchartStep } from '../types';

interface FlowchartViewProps {
  steps: FlowchartStep[];
  theme?: string;
  startFrame?: number;
}

export const FlowchartView: React.FC<FlowchartViewProps> = ({
  steps,
  theme = 'notebook',
  startFrame = 10,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const isChalkboard = theme === 'chalkboard';
  const isBlueprint = theme === 'blueprint';
  const isParchment = theme === 'parchment';
  const isKraft = theme === 'kraft';

  const cardBg = isChalkboard
    ? 'rgba(15, 30, 22, 0.9)'
    : isBlueprint
    ? 'rgba(10, 35, 60, 0.9)'
    : isParchment
    ? 'rgba(255, 248, 235, 0.95)'
    : isKraft
    ? 'rgba(245, 230, 205, 0.95)'
    : 'rgba(255, 255, 255, 0.96)';

  const strokeColor = isChalkboard
    ? '#fef08a'
    : isBlueprint
    ? '#38bdf8'
    : isParchment
    ? '#78350f'
    : isKraft
    ? '#78350f'
    : '#dc2626';

  const textPrimary = isChalkboard || isBlueprint ? '#ffffff' : '#0f172a';
  const textMuted = isChalkboard ? '#cbd5e1' : isBlueprint ? '#93c5fd' : '#475569';

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '0 40px',
        width: '100%',
        gap: 16,
      }}
    >
      {steps.map((st, idx) => {
        const stepDelay = startFrame + idx * 24;
        const scale = spring({
          frame: frame - stepDelay,
          fps,
          config: { damping: 13, mass: 0.8 },
        });

        // Arrow drawing animation
        const arrowProgress = interpolate(frame, [stepDelay - 10, stepDelay], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });

        return (
          <React.Fragment key={idx}>
            {/* Step Card */}
            <div
              style={{
                width: '100%',
                maxWidth: 820,
                backgroundColor: cardBg,
                border: `3px solid ${st.color || strokeColor}`,
                borderRadius: 24,
                padding: '20px 28px',
                display: 'flex',
                alignItems: 'center',
                gap: 24,
                boxShadow: '0 10px 24px rgba(0,0,0,0.08)',
                transform: `scale(${Math.max(0, scale)}) rotate(${idx % 2 === 0 ? '-1deg' : '1deg'})`,
              }}
            >
              {/* Step Circle Badge */}
              <div
                style={{
                  minWidth: 64,
                  height: 64,
                  borderRadius: '50%',
                  backgroundColor: st.color || strokeColor,
                  color: '#ffffff',
                  fontSize: 32,
                  fontWeight: 900,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                }}
              >
                {st.stepNumber || idx + 1}
              </div>

              {/* Text Content */}
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 4 }}>
                  <span
                    style={{
                      fontSize: 20,
                      fontWeight: 800,
                      color: st.color || strokeColor,
                      textTransform: 'uppercase',
                      letterSpacing: 1,
                    }}
                  >
                    {st.badge}
                  </span>
                </div>
                <div
                  style={{
                    fontSize: 32,
                    fontWeight: 900,
                    color: textPrimary,
                    lineHeight: 1.2,
                  }}
                >
                  {st.title}
                </div>
                <div
                  style={{
                    fontSize: 24,
                    fontWeight: 600,
                    color: textMuted,
                    marginTop: 4,
                  }}
                >
                  {st.desc}
                </div>
              </div>
            </div>

            {/* Handdrawn Arrow connecting to next step */}
            {idx < steps.length - 1 && (
              <div
                style={{
                  height: 48,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  opacity: arrowProgress,
                  transform: `scale(${arrowProgress})`,
                }}
              >
                <svg width="40" height="48" viewBox="0 0 40 48" fill="none">
                  <path
                    d="M 20 4 C 18 16, 22 30, 20 42"
                    stroke={strokeColor}
                    strokeWidth="5"
                    strokeLinecap="round"
                    strokeDasharray="6 4"
                  />
                  <path
                    d="M 12 34 L 20 44 L 28 34"
                    stroke={strokeColor}
                    strokeWidth="5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
