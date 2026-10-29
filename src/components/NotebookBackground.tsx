import React from 'react';

interface BackgroundProps {
  theme?:
    | 'notebook'
    | 'kraft'
    | 'chalkboard'
    | 'parchment'
    | 'blueprint'
    | 'dark_minimalist'
    | 'neon_cyber'
    | 'gold_luxury';
  isRTL?: boolean;
}

export const NotebookBackground: React.FC<BackgroundProps> = ({ theme = 'notebook', isRTL = false }) => {
  const holeCount = 13;
  const holes = Array.from({ length: holeCount });

  // 1. Dark Minimalist Theme (Ashab-ı Suffe / Deep Motion Explainer)
  if (theme === 'dark_minimalist') {
    return (
      <div
        style={{
          position: 'absolute',
          width: 1080,
          height: 1920,
          backgroundColor: '#06090e',
          backgroundImage: `
            radial-gradient(ellipse at 50% 40%, rgba(14, 165, 233, 0.08) 0%, transparent 75%),
            linear-gradient(180deg, #070b10 0%, #0d1522 50%, #05070a 100%)
          `,
          overflow: 'hidden',
          boxSizing: 'border-box',
        }}
      >
        {/* Subtle cinematic vignette */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            boxShadow: 'inset 0 0 160px rgba(0,0,0,0.85)',
            pointerEvents: 'none',
          }}
        />
      </div>
    );
  }

  // 2. Gold Luxury Theme
  if (theme === 'gold_luxury') {
    return (
      <div
        style={{
          position: 'absolute',
          width: 1080,
          height: 1920,
          backgroundColor: '#050505',
          backgroundImage: `
            radial-gradient(circle at 50% 35%, rgba(217, 119, 6, 0.15) 0%, transparent 65%),
            linear-gradient(180deg, #0a0805 0%, #171108 50%, #050402 100%)
          `,
          overflow: 'hidden',
          border: '1px solid rgba(217, 119, 6, 0.2)',
          boxSizing: 'border-box',
        }}
      >
        <div
          style={{
            position: 'absolute',
            inset: 0,
            boxShadow: 'inset 0 0 140px rgba(0,0,0,0.9)',
            pointerEvents: 'none',
          }}
        />
      </div>
    );
  }

  // 3. Neon Cyber Theme
  if (theme === 'neon_cyber') {
    return (
      <div
        style={{
          position: 'absolute',
          width: 1080,
          height: 1920,
          backgroundColor: '#030712',
          backgroundImage: `
            radial-gradient(circle at 50% 45%, rgba(6, 182, 212, 0.12) 0%, transparent 65%),
            linear-gradient(to right, rgba(56, 189, 248, 0.06) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(56, 189, 248, 0.06) 1px, transparent 1px)
          `,
          backgroundSize: '100% 100%, 48px 48px, 48px 48px',
          overflow: 'hidden',
          boxSizing: 'border-box',
        }}
      >
        <div
          style={{
            position: 'absolute',
            inset: 0,
            boxShadow: 'inset 0 0 120px rgba(3, 7, 18, 0.9)',
            pointerEvents: 'none',
          }}
        />
      </div>
    );
  }

  // 1. Chalkboard Theme
  if (theme === 'chalkboard') {
    return (
      <div
        style={{
          position: 'absolute',
          width: 1080,
          height: 1920,
          backgroundColor: '#1b2d24',
          backgroundImage: `
            radial-gradient(circle at 50% 40%, rgba(255, 255, 255, 0.05) 0%, transparent 60%),
            linear-gradient(to right, rgba(255, 255, 255, 0.07) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.07) 1px, transparent 1px)
          `,
          backgroundSize: '100% 100%, 48px 48px, 48px 48px',
          overflow: 'hidden',
          border: '18px solid #5c3a21',
          boxSizing: 'border-box',
        }}
      >
        <div
          style={{
            position: 'absolute',
            inset: 0,
            boxShadow: 'inset 0 0 100px rgba(0,0,0,0.6)',
            pointerEvents: 'none',
          }}
        />
      </div>
    );
  }

  // 2. Blueprint Theme (Engineering / Deep Science)
  if (theme === 'blueprint') {
    return (
      <div
        style={{
          position: 'absolute',
          width: 1080,
          height: 1920,
          backgroundColor: '#0c243c',
          backgroundImage: `
            linear-gradient(to right, rgba(255, 255, 255, 0.12) 1.5px, transparent 1.5px),
            linear-gradient(to bottom, rgba(255, 255, 255, 0.12) 1.5px, transparent 1.5px),
            linear-gradient(to right, rgba(56, 189, 248, 0.25) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(56, 189, 248, 0.25) 1px, transparent 1px)
          `,
          backgroundSize: '144px 144px, 144px 144px, 24px 24px, 24px 24px',
          overflow: 'hidden',
          border: '12px solid #08192b',
          boxSizing: 'border-box',
        }}
      >
        {/* Technical title block outline in corner */}
        <div
          style={{
            position: 'absolute',
            bottom: 30,
            right: 40,
            border: '2px solid rgba(56, 189, 248, 0.4)',
            padding: '8px 18px',
            fontSize: 20,
            fontFamily: 'monospace',
            color: '#38bdf8',
            letterSpacing: 2,
            opacity: 0.7,
          }}
        >
          DWG NO. AI-SHORTS-01 // SCALE 1:1
        </div>
      </div>
    );
  }

  // 3. Antique Parchment Theme
  if (theme === 'parchment') {
    return (
      <div
        style={{
          position: 'absolute',
          width: 1080,
          height: 1920,
          backgroundColor: '#f3e6cd',
          backgroundImage: `
            radial-gradient(ellipse at center, rgba(255, 255, 255, 0.4) 0%, rgba(180, 130, 80, 0.3) 100%),
            linear-gradient(to right, rgba(146, 64, 14, 0.15) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(146, 64, 14, 0.15) 1px, transparent 1px)
          `,
          backgroundSize: '100% 100%, 40px 40px, 40px 40px',
          overflow: 'hidden',
          boxShadow: 'inset 0 0 120px rgba(90, 40, 10, 0.45)',
        }}
      >
        <div
          style={{
            position: 'absolute',
            left: isRTL ? undefined : 76,
            right: isRTL ? 76 : undefined,
            top: 0,
            bottom: 0,
            width: 2,
            backgroundColor: '#b45309',
            opacity: 0.6,
          }}
        />
      </div>
    );
  }

  // 4. Kraft & Modern Notebook Themes
  const isKraft = theme === 'kraft';
  const bgColor = isKraft ? '#e2cfb0' : '#fbf8f2';
  const gridColor = isKraft ? 'rgba(120, 53, 15, 0.25)' : 'rgba(203, 213, 225, 0.45)';
  const marginColor = isKraft ? '#9a3412' : '#ef4444';

  return (
    <div
      style={{
        position: 'absolute',
        width: 1080,
        height: 1920,
        backgroundColor: bgColor,
        backgroundImage: `
          linear-gradient(to right, ${gridColor} 1.5px, transparent 1.5px),
          linear-gradient(to bottom, ${gridColor} 1.5px, transparent 1.5px)
        `,
        backgroundSize: '36px 36px',
        overflow: 'hidden',
      }}
    >
      {/* Margin line */}
      <div
        style={{
          position: 'absolute',
          left: isRTL ? undefined : 72,
          right: isRTL ? 72 : undefined,
          top: 0,
          bottom: 0,
          width: 2,
          backgroundColor: marginColor,
          opacity: 0.65,
        }}
      />

      {/* Top Spiral Wire Binding Holes */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 80,
          display: 'flex',
          justifyContent: 'space-around',
          paddingLeft: 30,
          paddingRight: 30,
          alignItems: 'flex-start',
        }}
      >
        {holes.map((_, i) => (
          <div
            key={i}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            <svg width="24" height="60" viewBox="0 0 24 60" style={{ marginTop: -8 }}>
              <path
                d="M 6 0 C 6 25, 18 25, 18 45"
                stroke="rgba(0,0,0,0.15)"
                strokeWidth="4"
                fill="none"
              />
              <path
                d="M 8 0 C 8 24, 16 24, 16 42"
                stroke={isKraft ? '#78350f' : '#64748b'}
                strokeWidth="4.5"
                strokeLinecap="round"
                fill="none"
              />
              <path
                d="M 9 0 C 9 24, 17 24, 17 42"
                stroke={isKraft ? '#d97706' : '#cbd5e1'}
                strokeWidth="2"
                strokeLinecap="round"
                fill="none"
              />
            </svg>
            <div
              style={{
                width: 20,
                height: 20,
                borderRadius: '50%',
                backgroundColor: isKraft ? '#451a03' : '#1e293b',
                marginTop: -10,
                boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.7)',
                border: '1.5px solid rgba(255,255,255,0.4)',
              }}
            />
          </div>
        ))}
      </div>
    </div>
  );
};
