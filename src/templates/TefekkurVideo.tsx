import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { SERIF } from '../fonts';

export type Kelime = { w: string; s: number; e: number; c: number };

export type TefekkurProps = {
  /** public/<slug>/ses.mp3 dosyasının klasörü */
  slug: string;
  title: string;
  words: Kelime[];
  /** Sesin gerçek süresi (sn). Verilmezse son kelimenin bitişinden hesaplanır. */
  audioDurationSec?: number;
};

export const TAIL_SEC = 1.0;

export const computeDurationFrames = (p: Pick<TefekkurProps, 'words' | 'audioDurationSec'>, fps: number): number => {
  const lastEnd = p.words.length ? p.words[p.words.length - 1].e : 0;
  const sec = p.audioDurationSec && p.audioDurationSec > 0 ? p.audioDurationSec + TAIL_SEC : lastEnd + 2.4;
  return Math.max(fps * 3, Math.ceil(sec * fps));
};

// ---- Deterministik rastgelelik (render'lar arası titreme olmaması için) ----
const mulberry32 = (seed: number) => () => {
  seed |= 0;
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const GOLD = '#F5D061';
const GOLD_SOFT = '#D4AF37';

const ease = Easing.bezier(0.45, 0, 0.55, 1);

type Particle = { x: number; y: number; r: number; speed: number; phase: number };
const makeParticles = (n: number): Particle[] => {
  const rnd = mulberry32(112);
  return Array.from({ length: n }, () => ({
    x: rnd() * 1080,
    y: rnd() * 1920,
    r: 1 + rnd() * 2.6,
    speed: 14 + rnd() * 30,
    phase: rnd() * Math.PI * 2,
  }));
};
const PARTICLES = makeParticles(46);

// Sekiz köşeli yıldız (iki üst üste binen kare) noktaları
const starPoints = (cx: number, cy: number, r: number, rot: number): string => {
  const pts: string[] = [];
  for (let i = 0; i < 16; i++) {
    const a = rot + (Math.PI * 2 * i) / 16;
    const rr = i % 2 === 0 ? r : r * 0.62;
    pts.push(`${(cx + Math.cos(a) * rr).toFixed(2)},${(cy + Math.sin(a) * rr).toFixed(2)}`);
  }
  return pts.join(' ');
};

const Background: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const t = frame / fps;
  const pulse = 1 + Math.sin(t * 0.9) * 0.025;
  return (
    <AbsoluteFill>
      <svg viewBox="0 0 1080 1920" style={{ width: '100%', height: '100%', position: 'absolute' }}>
        <defs>
          <radialGradient id="tv-bg" cx="50%" cy="42%" r="70%">
            <stop offset="0%" stopColor="#0E1A33" />
            <stop offset="55%" stopColor="#060C1A" />
            <stop offset="100%" stopColor="#02040A" />
          </radialGradient>
          <radialGradient id="tv-halo" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={GOLD} stopOpacity="0.20" />
            <stop offset="100%" stopColor={GOLD} stopOpacity="0" />
          </radialGradient>
        </defs>
        <rect width="1080" height="1920" fill="url(#tv-bg)" />
        <circle cx="540" cy="820" r={520 * pulse} fill="url(#tv-halo)" />

        {/* yavaş dönen geometrik desen */}
        <g opacity={0.32} fill="none" stroke={GOLD_SOFT} strokeWidth={1.6}>
          <polygon points={starPoints(540, 820, 420, t * 0.05)} />
          <polygon points={starPoints(540, 820, 300, -t * 0.07)} />
          <polygon points={starPoints(540, 820, 190, t * 0.09)} />
          <circle cx={540} cy={820} r={460} strokeOpacity={0.5} />
          <circle cx={540} cy={820} r={112} strokeOpacity={0.7} />
        </g>

        {/* yükselen tozlar */}
        {PARTICLES.map((p, i) => {
          const y = (((p.y - t * p.speed) % 1920) + 1920) % 1920;
          const tw = 0.35 + 0.35 * Math.sin(t * 1.6 + p.phase);
          return <circle key={i} cx={p.x + Math.sin(t * 0.5 + p.phase) * 14} cy={y} r={p.r} fill={GOLD} opacity={tw} />;
        })}

        {/* üst ve alt altın çizgiler */}
        <line x1={140} y1={200} x2={940} y2={200} stroke={GOLD_SOFT} strokeOpacity={0.5} strokeWidth={2} />
        <line x1={140} y1={1700} x2={940} y2={1700} stroke={GOLD_SOFT} strokeOpacity={0.5} strokeWidth={2} />
      </svg>
    </AbsoluteFill>
  );
};

type Line = { idx: number; words: Kelime[]; start: number; end: number };

const groupLines = (words: Kelime[]): Line[] => {
  const map = new Map<number, Kelime[]>();
  for (const w of words) {
    if (!map.has(w.c)) map.set(w.c, []);
    map.get(w.c)!.push(w);
  }
  return Array.from(map.entries())
    .sort((a, b) => a[0] - b[0])
    .map(([idx, ws]) => ({ idx, words: ws, start: ws[0].s, end: ws[ws.length - 1].e }));
};

const fontSizeFor = (chars: number): number => {
  if (chars <= 28) return 92;
  if (chars <= 48) return 78;
  if (chars <= 72) return 66;
  if (chars <= 100) return 56;
  return 48;
};

const LineView: React.FC<{ line: Line; nextStart: number | null; t: number }> = ({ line, nextStart, t }) => {
  const fadeIn = interpolate(t, [line.start - 0.45, line.start + 0.15], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });
  const holdUntil = nextStart !== null ? Math.max(line.end + 0.3, nextStart - 0.35) : line.end + 0.9;
  const fadeOut = interpolate(t, [holdUntil, holdUntil + 0.45], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });
  const opacity = fadeIn * fadeOut;
  if (opacity <= 0.001) return null;

  const rise = interpolate(t, [line.start - 0.45, line.start + 0.25], [26, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });
  const chars = line.words.reduce((a, w) => a + w.w.length + 1, 0);
  const size = fontSizeFor(chars);

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', opacity }}>
      <div
        style={{
          width: 900,
          textAlign: 'center',
          fontFamily: SERIF,
          fontWeight: 700,
          fontSize: size,
          lineHeight: 1.32,
          transform: `translateY(${rise}px)`,
          marginTop: -80,
        }}
      >
        {line.words.map((w, i) => {
          const active = t >= w.s - 0.02 && t <= w.e + 0.12;
          const past = t > w.e + 0.12;
          const glow = interpolate(t, [w.s - 0.05, w.s + 0.12], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const scale = active ? 1 + 0.06 * glow : 1;
          return (
            <span
              key={i}
              style={{
                display: 'inline-block',
                margin: '0 0.18em',
                transform: `scale(${scale})`,
                color: active ? '#FFE08A' : past ? 'rgba(255,255,255,0.92)' : 'rgba(255,255,255,0.38)',
                textShadow: active
                  ? '0 0 26px rgba(255,223,115,0.85), 0 0 56px rgba(212,175,55,0.45)'
                  : '0 4px 18px rgba(0,0,0,0.6)',
              }}
            >
              {w.w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const TefekkurVideo: React.FC<TefekkurProps> = ({ slug, title, words }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const t = frame / fps;
  const lines = React.useMemo(() => groupLines(words), [words]);

  const titleOpacity = interpolate(t, [0.2, 1.0], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const progress = frame / Math.max(1, durationInFrames - 1);
  const activeLine = lines.findIndex((l, i) => t >= l.start - 0.45 && (i === lines.length - 1 || t < lines[i + 1].start - 0.45));

  return (
    <AbsoluteFill style={{ backgroundColor: '#040711', overflow: 'hidden' }}>
      <Audio src={staticFile(`${slug}/ses.mp3`)} />
      <Background frame={frame} fps={fps} />

      <div
        style={{
          position: 'absolute',
          top: 96,
          left: 90,
          right: 90,
          textAlign: 'center',
          fontFamily: SERIF,
          fontWeight: 600,
          fontSize: 38,
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
          color: GOLD,
          opacity: titleOpacity * 0.9,
        }}
      >
        {title}
      </div>

      {lines.map((line, i) => (
        <LineView key={line.idx} line={line} nextStart={i + 1 < lines.length ? lines[i + 1].start : null} t={t} />
      ))}

      {/* sahne noktaları */}
      <div style={{ position: 'absolute', bottom: 150, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 14 }}>
        {lines.map((l, i) => (
          <div
            key={l.idx}
            style={{
              width: i === activeLine ? 34 : 12,
              height: 12,
              borderRadius: 6,
              background: i <= activeLine ? GOLD : 'rgba(255,255,255,0.22)',
            }}
          />
        ))}
      </div>

      {/* ilerleme çubuğu */}
      <div style={{ position: 'absolute', left: 140, right: 140, bottom: 96, height: 4, background: 'rgba(255,255,255,0.12)', borderRadius: 2 }}>
        <div style={{ width: `${progress * 100}%`, height: '100%', background: GOLD, borderRadius: 2 }} />
      </div>
    </AbsoluteFill>
  );
};
