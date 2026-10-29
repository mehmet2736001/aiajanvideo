import React from 'react';

interface PenCursorProps {
  x: number;
  y: number;
  visible: boolean;
  type?: 'pen' | 'highlighter';
  rotation?: number;
}

export const PenCursor: React.FC<PenCursorProps> = ({
  x,
  y,
  visible,
  type = 'pen',
  rotation = -25,
}) => {
  if (!visible) return null;

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        transform: `translate(-12px, -70px) rotate(${rotation}deg)`,
        pointerEvents: 'none',
        zIndex: 50,
        filter: 'drop-shadow(2px 6px 8px rgba(0,0,0,0.25))',
        transition: 'transform 0.05s ease-out',
      }}
    >
      {type === 'pen' ? (
        // Red ballpoint pen tip
        <svg width="44" height="88" viewBox="0 0 44 88" fill="none">
          {/* Pen body */}
          <rect x="14" y="0" width="16" height="52" rx="3" fill="#dc2626" stroke="#991b1b" strokeWidth="2" />
          <line x1="22" y1="0" x2="22" y2="52" stroke="#fca5a5" strokeWidth="2" />
          {/* Silver grip / connector */}
          <rect x="15" y="52" width="14" height="12" fill="#cbd5e1" stroke="#64748b" strokeWidth="1.5" />
          {/* Metal cone tip */}
          <polygon points="15,64 29,64 22,84" fill="#94a3b8" stroke="#475569" strokeWidth="1.5" />
          {/* Ballpoint nib */}
          <circle cx="22" cy="85" r="2.5" fill="#ef4444" />
        </svg>
      ) : (
        // Fluorescent yellow highlighter
        <svg width="48" height="84" viewBox="0 0 48 84" fill="none">
          {/* Wide marker body */}
          <rect x="10" y="0" width="28" height="48" rx="4" fill="#eab308" stroke="#ca8a04" strokeWidth="2" />
          {/* Chisel tip collar */}
          <rect x="14" y="48" width="20" height="12" fill="#1e293b" />
          {/* Angled chisel tip */}
          <polygon points="16,60 32,60 28,78 18,74" fill="#facc15" stroke="#eab308" strokeWidth="1.5" />
        </svg>
      )}
    </div>
  );
};
