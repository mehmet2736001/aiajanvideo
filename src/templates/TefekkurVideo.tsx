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
  slug: string;
  title: string;
  words: Kelime[];
  audioDurationSec?: number;
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

const GOLD = '#D4AF37';
const GOLD_BRIGHT = '#FFDF73';
const GOLD_SOFT = '#F5D061';
const EMERALD = '#10B981';
const CYAN = '#38BDF8';
const PURPLE = '#A855F7';

// 8 veya N köşeli yıldız çokgeni koordinatları
const starPoints = (cx: number, cy: number, r: number, rot: number, points: number = 8) => {
  const total = points * 2;
  const pts: string[] = [];
  for (let i = 0; i < total; i++) {
    const radius = i % 2 === 0 ? r : r * 0.48;
    const a = (i * Math.PI) / points + rot;
    pts.push(`${cx + Math.cos(a) * radius},${cy + Math.sin(a) * radius}`);
  }
  return pts.join(' ');
};

// Altın oran spiral noktaları
const spiralPath = (cx: number, cy: number, maxR: number, turns: number, rot: number) => {
  const steps = 60;
  const pts: string[] = [];
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const r = t * maxR;
    const a = t * Math.PI * 2 * turns + rot;
    pts.push(`${cx + Math.cos(a) * r} ${cy + Math.sin(a) * r}`);
  }
  return 'M ' + pts.join(' L ');
};

// Deterministik parçacık havuzu (titremesiz)
const PARTICLES = Array.from({ length: 80 }, (_, i) => {
  const seed = (i * 9301 + 49297) % 233280;
  const rnd = seed / 233280.0;
  const seed2 = (seed * 9301 + 49297) % 233280;
  const rnd2 = seed2 / 233280.0;
  return {
    x: rnd * 1080,
    y: rnd2 * 1920,
    r: 1.0 + (i % 3) * 1.2,
    speed: 0.35 + (i % 4) * 0.25,
    phase: i * 0.45,
  };
});

/**
 * 15 FARKLI SAHNE DESTEKLEYEN ZENGİN 2D CANVAS GÖRSEL MOTORU
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

  // 15 modül arasında dinamik eşleme
  const m = sceneIdx % 15;

  // 0. Kozmik Kanca & Altın Şok Dalgası
  if (m === 0) {
    const shockScale = interpolate(localFrame, [0, 40], [0.3, 1.4], {
      extrapolateRight: 'clamp',
    });
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
        <svg viewBox="0 0 1080 1920" style={{ width: '100%', height: '100%', position: 'absolute' }}>
          <circle cx="540" cy="800" r={420 * pulse} fill="url(#goldAura)" opacity={0.65} />
          <g transform={`translate(540, 800) scale(${shockScale})`} fill="none" stroke={GOLD_SOFT} strokeWidth="2.5">
            <polygon points={starPoints(0, 0, 360, rot1 * 0.02)} strokeOpacity={0.8} />
            <polygon points={starPoints(0, 0, 240, rot2 * 0.02)} strokeOpacity={0.9} />
            <circle cx="0" cy="0" r="180" stroke="#FFF" strokeWidth="1.5" strokeOpacity={0.7} />
            <circle cx="0" cy="0" r="380" stroke={GOLD} strokeDasharray="8 12" strokeWidth="2" />
          </g>
        </svg>
      </AbsoluteFill>
    );
  }

  // 1. Büyük Kozmik Usturlap Mandalas
  if (m === 1) {
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -140 }}>
        <AstrolabeGoldenMandala size={740} opacity={0.85} />
      </AbsoluteFill>
    );
  }

  // 2. Atom Fe-26 Holo Model (Demir & Kuantum Yörüngeleri)
  if (m === 2) {
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -130 }}>
        <AtomFe26HoloModel scaleMultiplier={1.2} />
      </AbsoluteFill>
    );
  }

  // 3. Hakikat ve Mizan Terazisi
  if (m === 3) {
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -110 }}>
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
          leftLabel="HAK"
          rightLabel="ADALET"
          leftCount={114}
          rightCount={114}
          themeColor="#f59e0b"
          isBalanced={true}
        />
      </AbsoluteFill>
    );
  }

  // 4. Doppler Genişleyen Evren Spektrumu
  if (m === 4) {
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -140 }}>
        <DopplerExpansionHUD scaleMultiplier={1.15} mode="spectrum" />
      </AbsoluteFill>
    );
  }

  // 5. Zaman Kum Saati ve Altın Toz Şelalesi
  if (m === 5) {
    const hgPulse = 1 + Math.sin(t * 2) * 0.02;
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -120 }}>
        <svg viewBox="0 0 1080 1920" style={{ width: '100%', height: '100%', position: 'absolute' }}>
          <circle cx="540" cy="780" r={400 * pulse} fill="url(#deepGoldAura)" opacity={0.6} />
          {/* Kum Saati Telkafes */}
          <g transform={`translate(540, 780) scale(${hgPulse})`} fill="none" stroke={GOLD} strokeWidth="3">
            {/* Üst ve Alt Barlar */}
            <line x1="-160" y1="-260" x2="160" y2="-260" strokeWidth="6" stroke="#FFF" strokeOpacity={0.8} />
            <line x1="-160" y1="260" x2="160" y2="260" strokeWidth="6" stroke="#FFF" strokeOpacity={0.8} />
            {/* Cam Gövde */}
            <path d="M -150 -250 Q -80 -120 0 0 Q 80 -120 150 -250 Z" stroke={GOLD_BRIGHT} strokeWidth="2.5" />
            <path d="M -150 250 Q -80 120 0 0 Q 80 120 150 250 Z" stroke={GOLD_BRIGHT} strokeWidth="2.5" />
            {/* Merkezden Dökülen Altın Kum İpliği */}
            <line x1="0" y1="0" x2="0" y2="220" stroke="#FFF" strokeWidth="3" strokeDasharray="6 4" />
            {/* Alt Haznede Biriken Nur Kumları */}
            <path d="M -100 240 Q 0 180 100 240 Z" fill={GOLD_BRIGHT} opacity={0.4} />
          </g>
        </svg>
      </AbsoluteFill>
    );
  }

  // 6. Kâinatın Aynası & Manevi Kalp (Lotus Rosette)
  if (m === 6) {
    const heartBeat = 1 + Math.pow(Math.sin(t * Math.PI * 2), 6) * 0.15;
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -120 }}>
        <svg viewBox="0 0 1080 1920" style={{ width: '100%', height: '100%', position: 'absolute' }}>
          <circle cx="540" cy="780" r={450 * heartBeat} fill="url(#goldAura)" opacity={0.7} />
          <g transform={`translate(540, 780) scale(${heartBeat})`} fill="none" stroke={EMERALD} strokeWidth="2.5">
            {/* 8 Yapraklı Manevi Kalp Gülü */}
            {Array.from({ length: 8 }).map((_, idx) => {
              const a = (idx * Math.PI) / 4 + (frame * 0.01);
              const px = Math.cos(a) * 160;
              const py = Math.sin(a) * 160;
              return (
                <ellipse
                  key={idx}
                  cx={px}
                  cy={py}
                  rx="120"
                  ry="60"
                  transform={`rotate(${(idx * 45) + (frame * 0.5)}, ${px}, ${py})`}
                  stroke={idx % 2 === 0 ? GOLD_BRIGHT : EMERALD}
                  strokeWidth="2"
                  opacity={0.8}
                />
              );
            })}
            <circle cx="0" cy="0" r="50" fill={GOLD_BRIGHT} opacity={0.3} />
            <circle cx="0" cy="0" r="25" fill="#FFF" />
          </g>
        </svg>
      </AbsoluteFill>
    );
  }

  // 7. 432 Hz Ses ve Rezonans Dalgaları
  if (m === 7) {
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -120 }}>
        <svg viewBox="0 0 1080 1920" style={{ width: '100%', height: '100%', position: 'absolute' }}>
          <g transform="translate(540, 780)" fill="none" strokeWidth="2">
            {[100, 180, 260, 340, 420].map((radius, idx) => {
              const waveAmp = Math.sin(t * 4 + idx) * 18;
              const currentR = radius + waveAmp;
              return (
                <circle
                  key={idx}
                  cx="0"
                  cy="0"
                  r={currentR}
                  stroke={idx % 2 === 0 ? GOLD_BRIGHT : CYAN}
                  strokeDasharray={`${idx * 4 + 8} 6`}
                  opacity={0.85 - idx * 0.12}
                />
              );
            })}
            <circle cx="0" cy="0" r="40" fill={CYAN} opacity={0.4} />
          </g>
        </svg>
      </AbsoluteFill>
    );
  }

  // 8. Kozmik Pusula & Kıble İstikameti
  if (m === 8) {
    const compassRot = Math.sin(t * 0.8) * 15;
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -120 }}>
        <svg viewBox="0 0 1080 1920" style={{ width: '100%', height: '100%', position: 'absolute' }}>
          <circle cx="540" cy="780" r={380} stroke={GOLD} strokeWidth="3" fill="none" strokeDasharray="4 8" />
          <circle cx="540" cy="780" r={320} stroke={GOLD_SOFT} strokeWidth="1.5" fill="none" />
          {/* 16 Köşeli Pusula Yıldızı */}
          <polygon
            points={starPoints(540, 780, 300, 0, 16)}
            fill="none"
            stroke={GOLD_BRIGHT}
            strokeWidth="2"
            opacity={0.7}
          />
          {/* Dönen Altın İstikamet İğnesi */}
          <g transform={`translate(540, 780) rotate(${compassRot})`}>
            <polygon points="0,-240 24,0 -24,0" fill="#EF4444" opacity={0.9} />
            <polygon points="0,240 24,0 -24,0" fill={GOLD_SOFT} opacity={0.8} />
            <circle cx="0" cy="0" r="18" fill="#FFF" />
          </g>
        </svg>
      </AbsoluteFill>
    );
  }

  // 9. Warp Yıldız Seyahati Tüneli
  if (m === 9) {
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -140 }}>
        <StardustConstellation
          primaryText="KOZMİK ŞAHİTLİK"
          secondaryText="YILDIZLARIN MEVKİLERİ"
          accentColor="#FFDF73"
          glowColor="rgba(245, 158, 11, 0.75)"
          symbol="✦"
        />
      </AbsoluteFill>
    );
  }

  // 10. Kozmik Ağ & Galaktik Nöronlar
  if (m === 10) {
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -120 }}>
        <svg viewBox="0 0 1080 1920" style={{ width: '100%', height: '100%', position: 'absolute' }}>
          <g transform="translate(540, 780)">
            {Array.from({ length: 12 }).map((_, i) => {
              const a = (i * Math.PI * 2) / 12 + t * 0.1;
              const r = 240 + Math.sin(t * 3 + i) * 60;
              const nx = Math.cos(a) * r;
              const ny = Math.sin(a) * r;
              return (
                <g key={i}>
                  <line x1="0" y1="0" x2={nx} y2={ny} stroke={GOLD_SOFT} strokeWidth="1.5" opacity={0.5} />
                  <circle cx={nx} cy={ny} r="8" fill={CYAN} />
                  <circle cx={nx} cy={ny} r="18" stroke={CYAN} strokeWidth="1" opacity={0.4} />
                </g>
              );
            })}
            <circle cx="0" cy="0" r="30" fill={GOLD_BRIGHT} opacity={0.8} />
          </g>
        </svg>
      </AbsoluteFill>
    );
  }

  // 11. Kevser ve Hayat Çeşmesi
  if (m === 11) {
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -120 }}>
        <svg viewBox="0 0 1080 1920" style={{ width: '100%', height: '100%', position: 'absolute' }}>
          <g transform="translate(540, 780)" fill="none" strokeWidth="2.5">
            {[-180, -120, -60, 0, 60, 120, 180].map((offset, i) => {
              const arcH = 260 - Math.abs(offset) * 0.6;
              return (
                <path
                  key={i}
                  d={`M ${offset * 0.2} 200 Q ${offset * 1.5} ${-arcH} ${offset * 2} 220`}
                  stroke={CYAN}
                  opacity={0.7}
                />
              );
            })}
            <ellipse cx="0" cy="220" rx="360" ry="80" stroke={GOLD} strokeWidth="2" opacity={0.6} />
            <circle cx="0" cy="-60" r="40" fill={GOLD_BRIGHT} opacity={0.5} />
          </g>
        </svg>
      </AbsoluteFill>
    );
  }

  // 12. Ebediyet Sarmalı & Altın Oran Fraktalı
  if (m === 12) {
    const spiralD = spiralPath(0, 0, 380, 3.5, rot1 * 0.03);
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -120 }}>
        <svg viewBox="0 0 1080 1920" style={{ width: '100%', height: '100%', position: 'absolute' }}>
          <g transform="translate(540, 780)" fill="none">
            <path d={spiralD} stroke={GOLD_BRIGHT} strokeWidth="3" opacity={0.85} />
            <polygon points={starPoints(0, 0, 320, rot2 * 0.02)} stroke={GOLD} strokeWidth="1.5" opacity={0.4} />
            <circle cx="0" cy="0" r="25" fill="#FFF" />
          </g>
        </svg>
      </AbsoluteFill>
    );
  }

  // 13. Göksel Kubbe & Mukarnas Halesi
  if (m === 13) {
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -120 }}>
        <svg viewBox="0 0 1080 1920" style={{ width: '100%', height: '100%', position: 'absolute' }}>
          <g transform="translate(540, 780)" fill="none" stroke={GOLD} strokeWidth="2">
            {Array.from({ length: 16 }).map((_, i) => {
              const a = (i * Math.PI) / 8;
              return (
                <line
                  key={i}
                  x1={Math.cos(a) * 80}
                  y1={Math.sin(a) * 80}
                  x2={Math.cos(a) * 360}
                  y2={Math.sin(a) * 360}
                  opacity={0.6}
                />
              );
            })}
            <circle cx="0" cy="0" r="360" strokeWidth="3" />
            <circle cx="0" cy="0" r="240" strokeDasharray="6 6" />
            <circle cx="0" cy="0" r="120" strokeWidth="2" stroke={GOLD_BRIGHT} />
            <circle cx="0" cy="0" r="40" fill={GOLD_BRIGHT} opacity={0.3} />
          </g>
        </svg>
      </AbsoluteFill>
    );
  }

  // 14. Hakkın Mührü & Selam Kapanışı
  const sealScale = 1 + Math.sin(frame * 0.05) * 0.03;
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -120 }}>
      <svg viewBox="0 0 1080 1920" style={{ width: '100%', height: '100%', position: 'absolute' }}>
        <circle cx="540" cy="780" r={460 * pulse} fill="url(#deepGoldAura)" opacity={0.7} />
        <g transform={`translate(540, 780) scale(${sealScale})`} fill="none" stroke={GOLD} strokeWidth="3">
          <polygon points={starPoints(0, 0, 340, rot1 * 0.015, 12)} strokeWidth="2.5" />
          <polygon points={starPoints(0, 0, 240, rot2 * 0.02, 12)} strokeWidth="2" strokeDasharray="6 6" />
          <circle cx="0" cy="0" r="280" stroke="#FFF" strokeWidth="1.5" strokeOpacity={0.6} />
          <circle cx="0" cy="0" r="160" fill="url(#goldGrad)" opacity={0.2} />
        </g>
        <text
          x="540"
          y="795"
          textAnchor="middle"
          fill={GOLD}
          fontFamily={SERIF}
          fontSize="76"
          fontWeight="bold"
          letterSpacing="6"
          opacity="0.9"
        >
          ۞
        </text>
      </svg>
    </AbsoluteFill>
  );
};

/**
 * 15 FARKLI SAHNE DESTEKLEYEN ZENGİN 3D STORIES GÖRSEL MOTORU
 */
const SceneVisual3D: React.FC<{
  sceneIdx: number;
  localFrame: number;
  sceneDurationFrames: number;
  frame: number;
  fps: number;
}> = ({ sceneIdx, localFrame, sceneDurationFrames, frame, fps }) => {
  const m = sceneIdx % 15;

  if (m === 0) {
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

  if (m === 1) {
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -130 }}>
        <AtomFe26HoloModel scaleMultiplier={1.25} />
      </AbsoluteFill>
    );
  }

  if (m === 2) {
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -140 }}>
        <DopplerExpansionHUD scaleMultiplier={1.15} mode="spectrum" />
      </AbsoluteFill>
    );
  }

  if (m === 3) {
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -110 }}>
        <IslamicBalanceScale
          title="✦ 3D MİZAN TERAZİSİ ✦"
          leftLabel="HAK"
          rightLabel="ADALET"
          leftCount={114}
          rightCount={114}
          themeColor="#f59e0b"
          isBalanced={true}
        />
      </AbsoluteFill>
    );
  }

  if (m === 4) {
    // 3D Jiroskop Mizan Modeli (3-axis rotating gimbal rings)
    const rotX = (frame * 0.4) % 360;
    const rotY = (frame * 0.6) % 360;
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -120 }}>
        <svg viewBox="0 0 1080 1920" style={{ width: '100%', height: '100%', position: 'absolute' }}>
          <g transform="translate(540, 780)" fill="none" strokeWidth="3">
            {/* Dış Halka */}
            <ellipse rx="340" ry="340" stroke={GOLD} opacity={0.7} transform={`rotate(${rotX})`} />
            {/* Orta Eğimli Halka */}
            <ellipse rx="280" ry="140" stroke={GOLD_BRIGHT} opacity={0.8} transform={`rotate(${rotY})`} />
            {/* İç Kuantum Küresi */}
            <circle cx="0" cy="0" r="70" fill="url(#goldGrad)" opacity={0.5} />
            <circle cx="0" cy="0" r="30" fill="#FFF" />
          </g>
        </svg>
      </AbsoluteFill>
    );
  }

  if (m === 5) {
    // 3D Altın Kum Girdabı (Hourglass Vortex)
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -130 }}>
        <DopplerExpansionHUD scaleMultiplier={1.1} mode="etymology" />
      </AbsoluteFill>
    );
  }

  if (m === 6) {
    // 3D Perspektif Usturlap
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -140 }}>
        <AstrolabeGoldenMandala size={760} opacity={0.9} />
      </AbsoluteFill>
    );
  }

  if (m === 7) {
    // 3D Kuantum Çekirdek
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -130 }}>
        <AtomFe26HoloModel scaleMultiplier={1.1} />
      </AbsoluteFill>
    );
  }

  if (m === 8) {
    // 3D Spektrum Genişleme
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -140 }}>
        <DopplerExpansionHUD scaleMultiplier={1.2} mode="spectrum" />
      </AbsoluteFill>
    );
  }

  if (m === 9) {
    // 3D Derin Uzay Seyahati
    return (
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -140 }}>
        <StardustConstellation
          primaryText="EBEDİYET YOLCULUĞU"
          secondaryText="ZERREDEN KÜREYE İNTİZAM"
          accentColor="#38BDF8"
          glowColor="rgba(56, 189, 248, 0.75)"
          symbol="✦"
        />
      </AbsoluteFill>
    );
  }

  // 10-14: İleri Düzey 3D Modeller
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', top: -140 }}>
      <DopplerExpansionHUD scaleMultiplier={1.1} mode="etymology" />
    </AbsoluteFill>
  );
};

export const TefekkurVideo: React.FC<TefekkurProps> = ({
  slug,
  title,
  words,
  animationStyle = '2d_canvas',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const groupLines = (wList: Kelime[]) => {
    if (!wList || !wList.length) return [];
    const map = new Map<number, Kelime[]>();
    wList.forEach((w) => {
      const arr = map.get(w.c) || [];
      arr.push(w);
      map.set(w.c, arr);
    });
    return Array.from(map.entries())
      .sort((a, b) => a[0] - b[0])
      .map(([c, kList]) => ({
        c,
        words: kList,
        start: kList[0].s,
        end: kList[kList.length - 1].e,
        text: kList.map((k) => k.w).join(' '),
      }));
  };

  const lines = React.useMemo(() => groupLines(words), [words]);

  // Kamera Dinamiği (Hafif sinematik nefes)
  const cameraScale = 1 + Math.sin(t * 0.12) * 0.02;
  const ease = Easing.bezier(0.25, 0.1, 0.25, 1);

  return (
    <AbsoluteFill style={{ backgroundColor: '#03060E', overflow: 'hidden' }}>
      <Audio src={staticFile(`${slug}/ses.mp3`)} />

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

      {/* 2. Katman: 15 Farklı Sahne Destekli Görsel Animasyon Katmanı */}
      <AbsoluteFill style={{ transform: `scale(${cameraScale})` }}>
        {lines.map((line, idx) => {
          const nextStart = idx + 1 < lines.length ? lines[idx + 1].start : line.end + 2.0;
          const isVisible = t >= line.start - 0.45 && t < nextStart;
          if (!isVisible) return null;

          const sceneDurationFrames = Math.max(15, Math.ceil((nextStart - line.start) * fps));
          const localFrame = Math.max(0, Math.ceil((t - line.start) * fps));

          const fadeIn = interpolate(t, [line.start - 0.45, line.start + 0.25], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
            easing: ease,
          });
          const fadeOut = interpolate(t, [nextStart - 0.3, nextStart], [1, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
            easing: ease,
          });
          const sceneOpacity = Math.min(fadeIn, fadeOut);

          return (
            <AbsoluteFill key={idx} style={{ opacity: sceneOpacity }}>
              {animationStyle === '3d_motion' ? (
                <SceneVisual3D
                  sceneIdx={idx}
                  localFrame={localFrame}
                  sceneDurationFrames={sceneDurationFrames}
                  frame={frame}
                  fps={fps}
                />
              ) : (
                <SceneVisual2D
                  sceneIdx={idx}
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

      {/* 3. Katman: Alt Üçte Birlik Altyazı Kapsülü */}
      <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 110 }}>
        <div
          style={{
            width: 960,
            padding: '28px 36px',
            borderRadius: 24,
            background: 'rgba(8, 14, 26, 0.82)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(212, 175, 55, 0.28)',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.85), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 16,
          }}
        >
          {/* Sahne İlerleme Göstergesi Noktaları */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            {lines.map((l, i) => {
              const isPast = t >= l.end;
              const isCurrent = t >= l.start && t < l.end;
              return (
                <div
                  key={i}
                  style={{
                    width: isCurrent ? 24 : 8,
                    height: 5,
                    borderRadius: 3,
                    background: isCurrent ? GOLD_BRIGHT : isPast ? GOLD : 'rgba(255,255,255,0.15)',
                    boxShadow: isCurrent ? '0 0 12px #FFDF73' : 'none',
                    transition: 'all 0.2s ease',
                  }}
                />
              );
            })}
          </div>

          {/* Kinetik Canlı Kelime Vurgusu */}
          <div
            style={{
              fontFamily: "'Plus Jakarta Sans', sans-serif",
              fontSize: 32,
              lineHeight: 1.45,
              fontWeight: 600,
              color: '#CBD5E1',
              textAlign: 'center',
              letterSpacing: '-0.01em',
            }}
          >
            {(() => {
              const curLine = lines.find((l) => t >= l.start - 0.2 && t <= l.end + 0.45);
              if (!curLine) return null;
              return curLine.words.map((kw, idx) => {
                const isActive = t >= kw.s && t <= kw.e;
                const isSpoken = t > kw.e;
                return (
                  <span
                    key={idx}
                    style={{
                      display: 'inline-block',
                      marginRight: 8,
                      color: isActive ? GOLD_BRIGHT : isSpoken ? '#FFFFFF' : '#94A3B8',
                      fontWeight: isActive ? 800 : 600,
                      textShadow: isActive
                        ? '0 0 20px rgba(255, 223, 115, 0.9), 0 0 40px rgba(212, 175, 55, 0.5)'
                        : 'none',
                      transform: isActive ? 'scale(1.08)' : 'scale(1)',
                      transition: 'all 0.08s ease',
                    }}
                  >
                    {kw.w}
                  </span>
                );
              });
            })()}
          </div>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              fontSize: 12,
              fontWeight: 700,
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: EMERALD,
            }}
          >
            <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: EMERALD }} />
            <span>TURSO VOICE #0001 (DERVİŞ 114 HZ) · ÇOK SAHNELİ ANİMASYON</span>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
