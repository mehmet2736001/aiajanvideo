import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Easing,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { SERIF } from '../fonts';
import { AstrolabeGoldenMandala } from '../components/effects/AstrolabeGoldenMandala';
import { AtomFe26HoloModel } from '../components/effects/AtomFe26HoloModel';
import { IslamicBalanceScale } from '../components/effects/IslamicBalanceScale';
import { DopplerExpansionHUD } from '../components/effects/DopplerExpansionHUD';
import { StardustConstellation } from '../components/effects/StardustConstellation';

export type Kelime = { w: string; s: number; e: number; c: number };

export type TefekkurProps = {
  /** public/<slug>/ses.mp3 dosyasının klasörü */
  slug: string;
  title: string;
  words: Kelime[];
  /** Sesin gerçek süresi (sn). Verilmezse son kelimenin bitişinden hesaplanır. */
  audioDurationSec?: number;
  /** Animasyon stili: 2d_canvas veya 3d_motion */
  animationStyle?: '2d_canvas' | '3d_motion';
};

export const TAIL_SEC = 1.2;

export const computeDurationFrames = (
  p: Pick<TefekkurProps, 'words' | 'audioDurationSec'>,
  fps: number
): number => {
  const lastEnd = p.words && p.words.length ? p.words[p.words.length - 1].e : 0;
  const sec =
    p.audioDurationSec && p.audioDurationSec > 0
      ? p.audioDurationSec + TAIL_SEC
      : lastEnd + 2.5;
  return Math.max(fps * 3, Math.ceil(sec * fps));
};

// Deterministik rastgelelik fonksiyonu
const mulberry32 = (seed: number) => () => {
  seed |= 0;
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

const GOLD = '#FFDF73';
const GOLD_SOFT = '#D4AF37';
const ease = Easing.bezier(0.45, 0, 0.55, 1);

type Particle = { x: number; y: number; r: number; speed: number; phase: number };
const makeParticles = (n: number): Particle[] => {
  const rnd = mulberry32(112);
  return Array.from({ length: n }, () => ({
    x: rnd() * 1080,
    y: rnd() * 1920,
    r: 1.2 + rnd() * 3.0,
    speed: 15 + rnd() * 35,
    phase: rnd() * Math.PI * 2,
  }));
};
const PARTICLES = makeParticles(60);

// Sekiz köşeli Selçuklu yıldızı noktaları
const starPoints = (cx: number, cy: number, r: number, rot: number): string => {
  const pts: string[] = [];
  for (let i = 0; i < 16; i++) {
    const a = rot + (Math.PI * 2 * i) / 16;
    const rr = i % 2 === 0 ? r : r * 0.62;
    pts.push(`${(cx + Math.cos(a) * rr).toFixed(2)},${(cy + Math.sin(a) * rr).toFixed(2)}`);
  }
  return pts.join(' ');
};

type Line = { idx: number; words: Kelime[]; start: number; end: number };
const groupLines = (words: Kelime[]): Line[] => {
  if (!words || !words.length) return [];
  const map = new Map<number, Kelime[]>();
  for (const w of words) {
    if (!map.has(w.c)) map.set(w.c, []);
    map.get(w.c)!.push(w);
  }
  return Array.from(map.entries())
    .sort((a, b) => a[0] - b[0])
    .map(([idx, ws]) => ({
      idx,
      words: ws,
      start: ws[0].s,
      end: ws[ws.length - 1].e,
    }));
};

/**
 * 2D Canvas & Geometri Görsel Evreni
 */
const SceneVisual2D: React.FC<{
  sceneIdx: number;
  localFrame: number;
  sceneDurationFrames: number;
  frame: number;
  fps: number;
}> = ({ sceneIdx, localFrame, sceneDurationFrames, frame, fps }) => {
  const t = frame / fps;
  const pulse = 1 + Math.sin(frame * 0.08) * 0.06;
  const rot1 = (frame * 0.25) % 360;
  const rot2 = (-frame * 0.18) % 360;

  // Sahne türüne göre dinamik 2D görsel katman
  if (sceneIdx === 0) {
    // Sahne 0: Kanca (Hook) - Şok dalgası, parlayan portal ve patlayan parçacıklar
    const shockScale = interpolate(localFrame, [0, 25], [0.3, 1.3], {
      easing: Easing.out(Easing.cubic),
      extrapolateRight: 'clamp',
    });
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
        <svg viewBox="0 0 1080 1920" style={{ width: '100%', height: '100%', position: 'absolute' }}>
          {/* Radyal Nur Patlaması */}
          <circle cx="540" cy="800" r={420 * pulse} fill="url(#goldAura)" opacity={0.65} />
          {/* Çift sekiz köşeli dönen altın portal */}
          <g
            transform={`translate(540, 800) scale(${shockScale})`}
            fill="none"
            stroke={GOLD_SOFT}
            strokeWidth="2.5"
          >
            <polygon points={starPoints(0, 0, 360, rot1 * 0.02)} strokeOpacity={0.8} />
            <polygon points={starPoints(0, 0, 240, rot2 * 0.02)} strokeOpacity={0.9} />
            <circle cx="0" cy="0" r="180" stroke="#FFF" strokeWidth="1.5" strokeOpacity={0.7} />
            <circle cx="0" cy="0" r="380" stroke={GOLD} strokeDasharray="8 12" strokeWidth="2" />
          </g>
        </svg>
      </AbsoluteFill>
    );
  }

  if (sceneIdx === 1) {
    // Sahne 1: Kutsal Geometri & Usturlap Mandalasının canlanması
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -140 }}>
        <AstrolabeGoldenMandala size={740} opacity={0.85} />
      </AbsoluteFill>
    );
  }

  if (sceneIdx === 2) {
    // Sahne 2: Mizan Adalet Terazisi ve İlahi Lazer İstikamet Hattı
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -110 }}>
        {/* Gökyüzünden inen altın lazer istikamet sütunu */}
        <div
          style={{
            position: 'absolute',
            top: 120,
            width: 4,
            height: 900,
            background: 'linear-gradient(to bottom, rgba(255,223,115,0), #FFDF73 40%, #D4AF37 80%, rgba(212,175,55,0))',
            boxShadow: '0 0 24px rgba(255,223,115,0.8), 0 0 60px rgba(212,175,55,0.4)',
            opacity: 0.75,
          }}
        />
        <IslamicBalanceScale
          title="✦ HAKİKAT VE MİZAN TERAZİSİ ✦"
          leftLabel="AMEL"
          rightLabel="İHLAS"
          leftCount={114}
          rightCount={114}
          themeColor="#f59e0b"
          isBalanced={true}
        />
      </AbsoluteFill>
    );
  }

  // Sahne 3+: Kapanış Mührü ve Dingin Nur Aurası
  const sealScale = 1 + Math.sin(frame * 0.05) * 0.03;
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -120 }}>
      <svg viewBox="0 0 1080 1920" style={{ width: '100%', height: '100%', position: 'absolute' }}>
        <circle cx="540" cy="780" r={460 * pulse} fill="url(#deepGoldAura)" opacity={0.7} />
        <g transform={`translate(540, 780) scale(${sealScale})`} fill="none" stroke={GOLD} strokeWidth="3">
          <polygon points={starPoints(0, 0, 320, rot1 * 0.015)} strokeWidth="2.5" />
          <polygon points={starPoints(0, 0, 220, rot2 * 0.02)} strokeWidth="2" strokeDasharray="6 6" />
          <circle cx="0" cy="0" r="260" stroke="#FFF" strokeWidth="1.5" strokeOpacity={0.6} />
          <circle cx="0" cy="0" r="140" fill="url(#goldGrad)" opacity={0.15} />
        </g>
        <text
          x="540"
          y="795"
          textAnchor="middle"
          fill={GOLD}
          fontFamily={SERIF}
          fontSize="72"
          fontWeight="bold"
          letterSpacing="6"
          opacity="0.85"
        >
          ۞
        </text>
      </svg>
    </AbsoluteFill>
  );
};

/**
 * 3D Motion Görsel Evreni (Hologram, Doppler HUD, Stardust)
 */
const SceneVisual3D: React.FC<{
  sceneIdx: number;
  localFrame: number;
  sceneDurationFrames: number;
  frame: number;
  fps: number;
}> = ({ sceneIdx, localFrame, sceneDurationFrames, frame, fps }) => {
  if (sceneIdx === 0) {
    // Sahne 0: Stardust Constellation & Warp Seyahati
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -140 }}>
        <StardustConstellation
          primaryText="KOZMİK ŞAHİTLİK"
          secondaryText="KÂİNATIN GİZLİ MÜHRÜ"
          accentColor="#FFDF73"
          glowColor="rgba(245, 158, 11, 0.75)"
          symbol="✦"
        />
      </AbsoluteFill>
    );
  }

  if (sceneIdx === 1) {
    // Sahne 1: Atom Fe-26 3D Holo Modeli & Kuantum Yörüngeler
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -130 }}>
        <AtomFe26HoloModel scaleMultiplier={1.15} />
      </AbsoluteFill>
    );
  }

  if (sceneIdx === 2) {
    // Sahne 2: Doppler Genişleyen Evren Spektrumu HUD
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -140 }}>
        <DopplerExpansionHUD scaleMultiplier={1.1} mode="spectrum" />
      </AbsoluteFill>
    );
  }

  // Sahne 3+: 3D Kapanış & Evren Derinliği
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -140 }}>
      <DopplerExpansionHUD scaleMultiplier={1.05} mode="etymology" />
    </AbsoluteFill>
  );
};

export const TefekkurVideo: React.FC<TefekkurProps> = ({
  slug,
  title,
  words = [],
  animationStyle = '2d_canvas',
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const t = frame / fps;

  const lines = React.useMemo(() => groupLines(words), [words]);

  // Aktif sahne tespiti
  const activeLineIdx = lines.findIndex(
    (l, i) =>
      t >= l.start - 0.35 &&
      (i === lines.length - 1 || t < lines[i + 1].start - 0.35)
  );
  const currentScene = Math.max(0, activeLineIdx);

  // Dinamik kamera süzülüşü (Ken Burns subtle zoom)
  const cameraScale = interpolate(frame, [0, durationInFrames], [1.0, 1.07], {
    easing: Easing.linear,
  });

  const progress = frame / Math.max(1, durationInFrames - 1);

  return (
    <AbsoluteFill style={{ backgroundColor: '#03060E', overflow: 'hidden' }}>
      {/* 44.1 kHz Stüdyo Master Sesi */}
      <Audio src={staticFile(`${slug}/ses.mp3`)} />

      {/* SVG Global Gradyan ve Filtre Tanımları */}
      <svg width="0" height="0" style={{ position: 'absolute' }}>
        <defs>
          <radialGradient id="cosmosBg" cx="50%" cy="45%" r="70%">
            <stop offset="0%" stopColor="#0B152A" />
            <stop offset="50%" stopColor="#050B16" />
            <stop offset="100%" stopColor="#020408" />
          </radialGradient>
          <radialGradient id="goldAura" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(255, 223, 115, 0.45)" />
            <stop offset="60%" stopColor="rgba(212, 175, 55, 0.18)" />
            <stop offset="100%" stopColor="rgba(3, 6, 14, 0)" />
          </radialGradient>
          <radialGradient id="deepGoldAura" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(255, 223, 115, 0.55)" />
            <stop offset="70%" stopColor="rgba(180, 130, 20, 0.22)" />
            <stop offset="100%" stopColor="rgba(3, 6, 14, 0)" />
          </radialGradient>
          <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FFF2B2" />
            <stop offset="35%" stopColor="#F5D061" />
            <stop offset="70%" stopColor="#D4AF37" />
            <stop offset="100%" stopColor="#8A6714" />
          </linearGradient>
        </defs>
      </svg>

      {/* 1. Katman: Canlı Kozmik Arka Plan */}
      <AbsoluteFill style={{ transform: `scale(${cameraScale})` }}>
        <svg viewBox="0 0 1080 1920" style={{ width: '100%', height: '100%', position: 'absolute' }}>
          <rect width="1080" height="1920" fill="url(#cosmosBg)" />
          {/* Yükselen altın tefekkür tozları */}
          {PARTICLES.map((p, i) => {
            const y = (((p.y - t * p.speed) % 1920) + 1920) % 1920;
            const tw = 0.35 + 0.35 * Math.sin(t * 1.5 + p.phase);
            return (
              <circle
                key={i}
                cx={p.x + Math.sin(t * 0.4 + p.phase) * 16}
                cy={y}
                r={p.r}
                fill={GOLD}
                opacity={tw}
              />
            );
          })}
        </svg>
      </AbsoluteFill>

      {/* 2. Katman: Çok Sahneli Dinamik Görsel Animasyon Katmanı */}
      <AbsoluteFill style={{ transform: `scale(${cameraScale})` }}>
        {lines.map((line, idx) => {
          const nextStart = idx + 1 < lines.length ? lines[idx + 1].start : line.end + 2.0;
          const isVisible = t >= line.start - 0.45 && t < nextStart;
          if (!isVisible) return null;

          const sceneDurationFrames = Math.max(15, Math.ceil((nextStart - line.start) * fps));
          const localFrame = Math.max(0, Math.ceil((t - line.start) * fps));

          // Yumuşak geçiş opasitesi (cross-dissolve)
          const fadeIn = interpolate(t, [line.start - 0.45, line.start + 0.25], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
            easing: ease,
          });
          const fadeOut = interpolate(t, [nextStart - 0.35, nextStart], [1, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
            easing: ease,
          });
          const sceneOpacity = fadeIn * fadeOut;

          return (
            <AbsoluteFill key={line.idx} style={{ opacity: sceneOpacity }}>
              {animationStyle === '3d_motion' ? (
                <SceneVisual3D
                  sceneIdx={idx % 4}
                  localFrame={localFrame}
                  sceneDurationFrames={sceneDurationFrames}
                  frame={frame}
                  fps={fps}
                />
              ) : (
                <SceneVisual2D
                  sceneIdx={idx % 4}
                  localFrame={localFrame}
                  sceneDurationFrames={sceneDurationFrames}
                  frame={frame}
                  fps={fps}
                />
              )}
            </AbsoluteFill>
          );
        })}
      </AbsoluteFill>

      {/* 3. Katman: Üst Başlık & Stil Rozeti */}
      <div
        style={{
          position: 'absolute',
          top: 85,
          left: 60,
          right: 60,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          zIndex: 10,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div
            style={{
              width: 10,
              height: 10,
              borderRadius: 5,
              background: '#10B981',
              boxShadow: '0 0 12px #10B981',
            }}
          />
          <span
            style={{
              fontFamily: SERIF,
              fontWeight: 700,
              fontSize: 32,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: GOLD,
              textShadow: '0 2px 14px rgba(0,0,0,0.8)',
            }}
          >
            {title}
          </span>
        </div>

        <div
          style={{
            fontFamily: "'Plus Jakarta Sans', sans-serif",
            fontSize: 18,
            fontWeight: 700,
            color: '#CBD5E1',
            background: 'rgba(255,255,255,0.06)',
            padding: '6px 16px',
            borderRadius: 20,
            border: '1px solid rgba(255,255,255,0.12)',
            backdropFilter: 'blur(8px)',
          }}
        >
          {animationStyle === '3d_motion' ? '🌌 3D Motion' : '🎨 2D Canvas'}
        </div>
      </div>

      {/* 4. Katman: Kinetik Canlı Altyazı (Alt Üçte Bir Cam Panel) */}
      <div
        style={{
          position: 'absolute',
          left: 60,
          right: 60,
          bottom: 230,
          textAlign: 'center',
          fontFamily: SERIF,
          pointerEvents: 'none',
          zIndex: 20,
        }}
      >
        {lines.map((line, idx) => {
          const nextStart = idx + 1 < lines.length ? lines[idx + 1].start : line.end + 2.0;
          const isVisible = t >= line.start - 0.35 && t < nextStart;
          if (!isVisible) return null;

          const fadeIn = interpolate(t, [line.start - 0.35, line.start + 0.15], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const fadeOut = interpolate(t, [nextStart - 0.35, nextStart], [1, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const lineOpacity = fadeIn * fadeOut;

          return (
            <div
              key={line.idx}
              style={{
                display: 'inline-block',
                background: 'rgba(6, 10, 20, 0.88)',
                border: '1px solid rgba(212, 175, 55, 0.35)',
                padding: '20px 38px',
                borderRadius: 28,
                boxShadow:
                  '0 16px 48px rgba(0,0,0,0.85), inset 0 0 24px rgba(212,175,55,0.12)',
                backdropFilter: 'blur(16px)',
                opacity: lineOpacity,
                maxWidth: 960,
              }}
            >
              {line.words.map((w, wIdx) => {
                const active = t >= w.s - 0.04 && t <= w.e + 0.18;
                const past = t > w.e + 0.18;
                const scale = active ? 1.08 : 1.0;

                return (
                  <span
                    key={wIdx}
                    style={{
                      display: 'inline-block',
                      margin: '6px 12px',
                      fontSize: 44,
                      fontWeight: active ? 800 : 500,
                      transform: `scale(${scale})`,
                      color: active
                        ? '#FFDF73'
                        : past
                        ? 'rgba(255,255,255,0.92)'
                        : 'rgba(255,255,255,0.42)',
                      textShadow: active
                        ? '0 0 24px rgba(255,223,115,0.95), 0 0 48px rgba(212,175,55,0.5)'
                        : '0 2px 8px rgba(0,0,0,0.6)',
                      transition: 'transform 0.08s ease',
                    }}
                  >
                    {w.w}
                  </span>
                );
              })}
            </div>
          );
        })}
      </div>

      {/* 5. Katman: Sahne Noktaları (Scene Dots) */}
      <div
        style={{
          position: 'absolute',
          bottom: 145,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
          gap: 12,
          zIndex: 15,
        }}
      >
        {lines.map((l, i) => (
          <div
            key={l.idx}
            style={{
              width: i === currentScene ? 36 : 12,
              height: 12,
              borderRadius: 6,
              background: i <= currentScene ? GOLD : 'rgba(255,255,255,0.22)',
              boxShadow: i === currentScene ? '0 0 14px #FFDF73' : 'none',
              transition: 'width 0.25s ease',
            }}
          />
        ))}
      </div>

      {/* 6. Katman: İlerleme Çubuğu (Progress Bar) */}
      <div
        style={{
          position: 'absolute',
          left: 120,
          right: 120,
          bottom: 96,
          height: 5,
          background: 'rgba(255,255,255,0.12)',
          borderRadius: 3,
          overflow: 'hidden',
          zIndex: 15,
        }}
      >
        <div
          style={{
            width: `${progress * 100}%`,
            height: '100%',
            background: 'linear-gradient(to right, #D4AF37, #FFDF73)',
            boxShadow: '0 0 12px #FFDF73',
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
