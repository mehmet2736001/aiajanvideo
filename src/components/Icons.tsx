import React from 'react';
import { Img, staticFile } from 'remotion';

interface IconProps {
  name: string;
  color?: string;
  size?: number;
  style?: React.CSSProperties;
}

export const Icon: React.FC<IconProps> = ({
  name = 'fingerprint',
  color = '#facc15',
  size = 64,
  style,
}) => {
  const cleanName = (name || 'fingerprint').toLowerCase().replace(/[^a-z0-9_]/g, '_');

  switch (cleanName) {
    case 'crescent':
    case 'moon':
    case 'hilal':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" style={style}>
          <path d="M 68 15 C 40 22 24 50 34 78 C 42 92 58 98 72 90 C 48 88 38 66 46 44 C 52 28 62 18 68 15 Z" fill={color} fillOpacity="0.25"/>
          <circle cx="72" cy="40" r="5" fill={color}/>
        </svg>
      );

    case 'kaaba':
    case 'kabe':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="3" strokeLinejoin="round" style={style}>
          <polygon points="50 18, 86 34, 50 50, 14 34" fill={color} fillOpacity="0.3"/>
          <polygon points="14 34, 50 50, 50 88, 14 72" fill={color} fillOpacity="0.5"/>
          <polygon points="50 50, 86 34, 86 72, 50 88" fill={color} fillOpacity="0.7"/>
          <line x1="14" y1="44" x2="50" y2="60" stroke="#facc15" strokeWidth="4"/>
          <line x1="50" y1="60" x2="86" y2="44" stroke="#facc15" strokeWidth="4"/>
        </svg>
      );

    case 'islamic_star':
    case 'star8':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="3.5" style={style}>
          <rect x="25" y="25" width="50" height="50" rx="3" fill={color} fillOpacity="0.15"/>
          <rect x="25" y="25" width="50" height="50" rx="3" transform="rotate(45 50 50)" fill={color} fillOpacity="0.15"/>
          <circle cx="50" cy="50" r="12" fill={color} fillOpacity="0.4"/>
        </svg>
      );

    case 'fingerprint':
    case 'parmak_izi':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="3.5" strokeLinecap="round" style={style}>
          <path d="M 50 15 C 32 15 20 30 20 50 C 20 80 32 92 50 95" />
          <path d="M 50 25 C 38 25 30 36 30 50 C 30 74 38 86 50 88" />
          <path d="M 50 35 C 44 35 40 42 40 50 C 40 68 44 76 50 80" />
          <path d="M 50 15 C 68 15 80 30 80 50 C 80 80 68 92 50 95" />
          <path d="M 50 25 C 62 25 70 36 70 50 C 70 74 62 86 50 88" />
          <path d="M 50 35 C 56 35 60 42 60 50 C 60 68 56 76 50 80" />
          <circle cx="50" cy="50" r="3.5" fill={color} />
        </svg>
      );

    case 'dna':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="4" strokeLinecap="round" style={style}>
          <path d="M 28 15 C 72 38 72 62 28 85" />
          <path d="M 72 15 C 28 38 28 62 72 85" />
          <line x1="38" y1="28" x2="62" y2="28" strokeWidth="3" />
          <line x1="46" y1="50" x2="54" y2="50" strokeWidth="3" />
          <line x1="38" y1="72" x2="62" y2="72" strokeWidth="3" />
          <circle cx="38" cy="28" r="3" fill={color}/>
          <circle cx="62" cy="28" r="3" fill={color}/>
          <circle cx="38" cy="72" r="3" fill={color}/>
          <circle cx="62" cy="72" r="3" fill={color}/>
        </svg>
      );

    case 'atom':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="3.5" style={style}>
          <ellipse cx="50" cy="50" rx="42" ry="16" transform="rotate(30 50 50)" />
          <ellipse cx="50" cy="50" rx="42" ry="16" transform="rotate(-30 50 50)" />
          <circle cx="50" cy="50" r="9" fill={color} />
          <circle cx="20" cy="35" r="3.5" fill={color} />
          <circle cx="80" cy="65" r="3.5" fill={color} />
        </svg>
      );

    case 'brain':
    case 'beyin':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" style={style}>
          <path d="M 48 20 C 40 20 30 26 30 36 C 24 38 20 46 22 54 C 20 62 25 72 34 76 C 36 82 42 86 48 86" />
          <path d="M 52 20 C 60 20 70 26 70 36 C 76 38 80 46 78 54 C 80 62 75 72 66 76 C 64 82 58 86 52 86" />
          <line x1="50" y1="20" x2="50" y2="86" strokeWidth="2.5" strokeDasharray="4 3"/>
          <path d="M 34 44 C 40 46 44 40 48 42" />
          <path d="M 66 44 C 60 46 56 40 52 42" />
          <path d="M 32 62 C 40 60 42 68 48 66" />
          <path d="M 68 62 C 60 60 58 68 52 66" />
        </svg>
      );

    case 'heart':
    case 'kalp':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill={color} style={style}>
          <path d="M 50 86 L 44 80 C 22 60 12 48 12 34 C 12 22 22 14 34 14 C 41 14 47 17 50 22 C 53 17 59 14 66 14 C 78 14 88 22 88 34 C 88 48 78 60 56 80 Z" />
        </svg>
      );

    case 'eye':
    case 'goz':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="4" strokeLinecap="round" style={style}>
          <path d="M 12 50 Q 50 16 88 50 Q 50 84 12 50 Z" />
          <circle cx="50" cy="50" r="16" fill={color} fillOpacity="0.25" strokeWidth="3" />
          <circle cx="50" cy="50" r="8" fill={color} />
          <circle cx="46" cy="46" r="3" fill="#ffffff" />
        </svg>
      );

    case 'scale':
    case 'terazi':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="3.5" strokeLinecap="round" style={style}>
          <line x1="50" y1="16" x2="50" y2="86" strokeWidth="4"/>
          <line x1="30" y1="86" x2="70" y2="86" strokeWidth="5"/>
          <line x1="18" y1="28" x2="82" y2="28" strokeWidth="4"/>
          <circle cx="50" cy="20" r="4" fill={color}/>
          <line x1="20" y1="28" x2="12" y2="52"/>
          <line x1="20" y1="28" x2="28" y2="52"/>
          <path d="M 10 52 Q 20 62 30 52 Z" fill={color} fillOpacity="0.3"/>
          <line x1="80" y1="28" x2="72" y2="52"/>
          <line x1="80" y1="28" x2="88" y2="52"/>
          <path d="M 70 52 Q 80 62 90 52 Z" fill={color} fillOpacity="0.3"/>
        </svg>
      );

    case 'hourglass':
    case 'kum_saati':
    case 'clock':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="3.5" strokeLinecap="round" style={style}>
          <line x1="24" y1="18" x2="76" y2="18" strokeWidth="5"/>
          <line x1="24" y1="82" x2="76" y2="82" strokeWidth="5"/>
          <path d="M 30 18 L 70 18 L 54 48 C 52 50 52 50 54 52 L 70 82 L 30 82 L 46 52 C 48 50 48 50 46 48 Z" fill={color} fillOpacity="0.2"/>
          <polygon points="40 76, 60 76, 50 64" fill={color}/>
          <circle cx="50" cy="54" r="2" fill={color}/>
        </svg>
      );

    case 'book':
    case 'kitap':
    case 'quran':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" style={style}>
          <path d="M 50 26 C 38 18 20 18 14 22 L 14 78 C 20 74 38 74 50 82 C 62 74 80 74 86 78 L 86 22 C 80 18 62 18 50 26 Z" fill={color} fillOpacity="0.25"/>
          <line x1="50" y1="26" x2="50" y2="82" strokeWidth="4"/>
          <line x1="24" y1="38" x2="42" y2="38" strokeWidth="2.5"/>
          <line x1="24" y1="50" x2="42" y2="50" strokeWidth="2.5"/>
          <line x1="58" y1="38" x2="76" y2="38" strokeWidth="2.5"/>
          <line x1="58" y1="50" x2="76" y2="50" strokeWidth="2.5"/>
        </svg>
      );

    case 'lightbulb':
    case 'ampul':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="3.5" strokeLinecap="round" style={style}>
          <path d="M 34 38 C 34 24 66 24 66 38 C 66 48 58 54 58 64 L 42 64 C 42 54 34 48 34 38 Z" fill={color} fillOpacity="0.25"/>
          <line x1="42" y1="70" x2="58" y2="70" strokeWidth="4"/>
          <line x1="45" y1="76" x2="55" y2="76" strokeWidth="4"/>
          <path d="M 50 14 L 50 8" strokeWidth="3"/>
          <path d="M 22 24 L 17 19" strokeWidth="3"/>
          <path d="M 78 24 L 83 19" strokeWidth="3"/>
        </svg>
      );

    case 'compass':
    case 'pusula':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="3.5" style={style}>
          <circle cx="50" cy="50" r="38" strokeWidth="4"/>
          <polygon points="50 20, 58 46, 50 50, 42 46" fill="#ef4444" stroke="#ef4444"/>
          <polygon points="50 80, 58 54, 50 50, 42 54" fill={color} fillOpacity="0.4"/>
          <circle cx="50" cy="50" r="4" fill="#ffffff" stroke={color} strokeWidth="2"/>
        </svg>
      );

    case 'shield':
    case 'kalkan':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="3.5" strokeLinecap="round" style={style}>
          <path d="M 50 16 L 82 26 C 82 58 68 78 50 88 C 32 78 18 58 18 26 Z" fill={color} fillOpacity="0.25"/>
          <path d="M 50 32 L 68 38 C 68 56 60 70 50 76 C 40 70 32 56 32 38 Z" fill={color} fillOpacity="0.35"/>
        </svg>
      );

    case 'infinity':
    case 'sonsuzluk':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="5" strokeLinecap="round" style={style}>
          <path d="M 32 36 C 18 36 14 50 14 50 C 14 50 18 64 32 64 C 46 64 54 50 54 50 C 54 50 62 36 76 36 C 90 36 94 50 94 50 C 94 50 90 64 76 64 C 62 64 54 50 54 50 C 54 50 46 36 32 36 Z" />
        </svg>
      );

    case 'galaxy':
    case 'star':
    case 'yildiz':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="3.5" strokeLinecap="round" style={style}>
          <path d="M 50 50 C 45 40, 35 45, 35 55 C 35 68, 55 70, 65 60 C 75 50, 72 35, 55 30 C 35 25, 20 45, 25 68 C 30 85, 60 90, 78 78 C 88 70, 90 50, 80 35" strokeDasharray="4 2"/>
          <circle cx="50" cy="50" r="6" fill="#f59e0b" stroke="#d97706" strokeWidth="2" />
        </svg>
      );

    case 'embryo':
    case 'hucre':
      return (
        <svg width={size} height={size} viewBox="0 0 140 100" fill="none" stroke={color} strokeWidth="3" style={style}>
          <circle cx="20" cy="50" r="10" stroke={color} strokeWidth="3" fill={color} fillOpacity="0.2"/>
          <circle cx="50" cy="50" r="16" stroke={color} strokeWidth="3" fill={color} fillOpacity="0.3"/>
          <circle cx="85" cy="50" r="22" stroke={color} strokeWidth="3" fill={color} fillOpacity="0.4"/>
          <circle cx="115" cy="50" r="26" stroke={color} strokeWidth="3" fill={color} fillOpacity="0.5"/>
        </svg>
      );

    case 'sprout':
    case 'tohum':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" stroke={color} strokeWidth="4" strokeLinecap="round" style={style}>
          <path d="M 50 85 L 50 45"/>
          <path d="M 50 55 C 35 45, 25 60, 48 65" fill={color} fillOpacity="0.3"/>
          <path d="M 50 45 C 65 30, 80 48, 52 50" fill={color} fillOpacity="0.3"/>
          <path d="M 30 85 Q 50 82 70 85"/>
        </svg>
      );

    default:
      // Fallback: render from assets/icons/{cleanName}.svg via Remotion Img
      return (
        <div style={{ width: size, height: size, display: 'flex', alignItems: 'center', justifyContent: 'center', color, ...style }}>
          <Img
            src={staticFile(`assets/icons/${cleanName}.svg`)}
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
            onError={(e) => {
              e.currentTarget.style.display = 'none';
            }}
          />
        </div>
      );
  }
};
