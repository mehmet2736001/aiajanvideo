import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { TimelineData } from '../types';

interface TimelineViewProps {
  timeline: TimelineData;
  startFrame?: number;
}

export const TimelineView: React.FC<TimelineViewProps> = ({ timeline, startFrame = 15 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const currentLocal = Math.max(0, frame - startFrame);

  // Line drawing animation
  const lineProgress = interpolate(currentLocal, [0, 25], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const cardSpring = spring({
    frame: currentLocal - 15,
    fps,
    config: { damping: 14, mass: 0.8 },
  });

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        paddingLeft: 60,
        paddingRight: 60,
        marginTop: 40,
        fontFamily: '"Caveat", "Kalam", cursive, sans-serif',
      }}
    >
      {/* Title */}
      <div
        style={{
          fontSize: 64,
          fontWeight: 800,
          color: '#1e3a8a',
          fontStyle: 'italic',
          marginBottom: 30,
        }}
      >
        {timeline.title}
      </div>

      {/* Timeline Ruler */}
      <div
        style={{
          width: '100%',
          maxWidth: 900,
          position: 'relative',
          paddingTop: 40,
          paddingBottom: 40,
        }}
      >
        {/* Duration Label above line */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: '50%',
            transform: 'translateX(-50%)',
            fontSize: 48,
            fontWeight: 800,
            color: '#854d0e',
          }}
        >
          {timeline.durationLabel}
        </div>

        {/* The horizontal ruler SVG with tick marks */}
        <svg width="100%" height="60" viewBox="0 0 800 60" style={{ overflow: 'visible' }}>
          {/* Main Axis Line */}
          <line
            x1="50"
            y1="30"
            x2={50 + 7 * lineProgress}
            y2="30"
            stroke="#854d0e"
            strokeWidth="4"
            strokeLinecap="round"
          />

          {/* Start and end tick marks */}
          {lineProgress > 5 && (
            <line x1="50" y1="10" x2="50" y2="50" stroke="#854d0e" strokeWidth="4" />
          )}
          {lineProgress > 90 && (
            <line x1="750" y1="10" x2="750" y2="50" stroke="#854d0e" strokeWidth="4" />
          )}

          {/* Intermediate ticks */}
          {[150, 250, 350, 450, 550, 650].map((x, idx) => {
            const threshold = (idx + 1) * 14;
            return lineProgress > threshold ? (
              <line key={x} x1={x} y1="20" x2={x} y2="40" stroke="#854d0e" strokeWidth="2.5" />
            ) : null;
          })}
        </svg>

        {/* Labels below line: 610 and 632 */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            paddingLeft: 30,
            paddingRight: 30,
            fontSize: 42,
            fontWeight: 800,
            color: '#0f172a',
          }}
        >
          <span>{timeline.startYear}</span>
          <span>{timeline.endYear}</span>
        </div>
      </div>

      {/* Quote / Ayah Card */}
      {timeline.ayahArabic && (
        <div
          style={{
            position: 'relative',
            width: '100%',
            maxWidth: 920,
            marginTop: 40,
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            border: '3.5px solid #854d0e',
            borderRadius: 24,
            padding: '30px 40px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            boxShadow: '0 8px 18px rgba(0, 0, 0, 0.04)',
            transform: `scale(${Math.max(0, cardSpring)})`,
            opacity: Math.max(0, cardSpring),
          }}
        >
          {/* Translation */}
          <div
            style={{
              fontSize: 42,
              fontWeight: 700,
              fontStyle: 'italic',
              color: '#0f172a',
              flex: 1,
            }}
          >
            "{timeline.ayahTranslation}"
          </div>

          {/* Arabic Calligraphy */}
          <div
            style={{
              fontSize: 54,
              fontWeight: 700,
              color: '#0f172a',
              fontFamily: '"Amiri", "Traditional Arabic", serif',
              textAlign: 'right',
              paddingLeft: 30,
            }}
          >
            {timeline.ayahArabic}
          </div>

          {/* Yellow Post-it badge in corner */}
          {timeline.ayahRef && (
            <div
              style={{
                position: 'absolute',
                right: 30,
                bottom: -22,
                backgroundColor: '#fef08a',
                padding: '6px 20px',
                borderRadius: 8,
                fontSize: 32,
                fontWeight: 800,
                color: '#713f12',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                border: '1px solid #fde047',
              }}
            >
              {timeline.ayahRef}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
