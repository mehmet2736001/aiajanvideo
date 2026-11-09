import React, { useLayoutEffect, useRef } from 'react';
import { AbsoluteFill, Audio, Composition, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import rawWords from '../../public/canvas-story-demo/kelimeler.json';

export const FPS = 30;
export const TOTAL_DURATION_SEC = 37.0;
export const TOTAL_FRAMES = Math.round(TOTAL_DURATION_SEC * FPS);

interface WordItem {
  w: string;
  s: number;
  e: number;
  c: number;
}

const words: WordItem[] = rawWords as WordItem[];

// ============================================================================
// CANVAS STORY ANIMATION ENGINE (SKILL-COMPLIANT ARCHITECTURE)
// ============================================================================

// 1. Math Utilities & Hermite Smoothstep Easing
function clamp(v: number, min: number, max: number): number {
  return v < min ? min : v > max ? max : v;
}

function smoothstep(a: number, b: number, x: number): number {
  const p = clamp((x - a) / (b - a), 0, 1);
  return p * p * (3 - 2 * p);
}

// 2. Deterministic PRNG (Linear Congruential Generator - No Math.random in loop)
function createPrng(seed: number) {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

const R = createPrng(0x7f4a9b21);

// Pre-generated deterministic cosmic particles
const PARTICLE_COUNT = 140;
interface Particle {
  x: number;
  y: number;
  radius: number;
  speed: number;
  orbitRadius: number;
  angleOffset: number;
  phase: number;
  colorType: 'gold' | 'cyan' | 'emerald' | 'amber';
}

const PARTICLES: Particle[] = Array.from({ length: PARTICLE_COUNT }, () => {
  const angle = R() * Math.PI * 2;
  const dist = 50 + R() * 500;
  return {
    x: Math.cos(angle) * dist,
    y: Math.sin(angle) * dist,
    radius: 0.8 + R() * 2.2,
    speed: 0.2 + R() * 0.8,
    orbitRadius: dist,
    angleOffset: angle,
    phase: R() * Math.PI * 2,
    colorType: R() > 0.4 ? 'gold' : R() > 0.2 ? 'cyan' : 'emerald',
  };
});

// Scene Time Windows
const SCENES = [
  { id: 0, start: 0.0, end: 3.8, title: 'Kanca: Hakikat ve Nizam' },
  { id: 1, start: 3.8, end: 9.8, title: 'Kozmik Usturlap Mandalas' },
  { id: 2, start: 9.8, end: 16.0, title: 'Kuantum Mizan & Holo Atom' },
  { id: 3, start: 16.0, end: 23.0, title: 'İstikamet & İlahi Terazi' },
  { id: 4, start: 23.0, end: 30.0, title: 'Kâinatın Aynası & Kalp' },
  { id: 5, start: 30.0, end: 37.0, title: 'Ömür Sermayesi & Ebediyet' },
];

// ============================================================================
// MAIN CANVAS DRAW FUNCTION (Rendered deterministically strictly from `t`)
// ============================================================================
function renderCanvasStory(ctx: CanvasRenderingContext2D, t: number, W: number, H: number) {
  // Metric unit: U = 1% of stage height (SKILL Principle 2)
  const U = H / 100; // 19.2px
  const cx = W * 0.5;
  const cy = H * 0.44;

  ctx.save();
  ctx.clearRect(0, 0, W, H);

  // Layer 1: Deep Cosmic Space Background
  const bgGrad = ctx.createRadialGradient(cx, cy, 2 * U, cx, cy, 60 * U);
  bgGrad.addColorStop(0, '#0a1020');
  bgGrad.addColorStop(0.5, '#050810');
  bgGrad.addColorStop(1, '#020306');
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, W, H);

  // Layer 2: Procedural God Rays (Radial Light Streaks)
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  const rayCount = 16;
  const rayRot = t * 0.08;
  for (let i = 0; i < rayCount; i++) {
    const angle = rayRot + (i * Math.PI * 2) / rayCount;
    const pulse = 0.5 + 0.5 * Math.sin(t * 1.5 + i);
    const rayLength = (25 + 10 * pulse) * U;
    const grad = ctx.createLinearGradient(
      cx,
      cy,
      cx + Math.cos(angle) * rayLength,
      cy + Math.sin(angle) * rayLength
    );
    grad.addColorStop(0, 'rgba(212, 175, 55, 0.12)');
    grad.addColorStop(0.4, 'rgba(99, 102, 241, 0.04)');
    grad.addColorStop(1, 'transparent');

    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, rayLength, angle - 0.06, angle + 0.06);
    ctx.closePath();
    ctx.fill();
  }
  ctx.restore();

  // Layer 3: Deterministic Stardust Particles
  ctx.save();
  for (let i = 0; i < PARTICLES.length; i++) {
    const p = PARTICLES[i];
    const currentAngle = p.angleOffset + t * 0.12 * p.speed;
    const breathe = 1 + 0.08 * Math.sin(t * 2 + p.phase);
    const dist = p.orbitRadius * breathe;
    const px = cx + Math.cos(currentAngle) * dist;
    const py = cy + Math.sin(currentAngle) * dist * 0.85;

    if (px < 0 || px > W || py < 0 || py > H) continue;

    const alpha = 0.35 + 0.5 * Math.sin(t * 3 + p.phase);
    ctx.fillStyle =
      p.colorType === 'gold'
        ? `rgba(255, 223, 115, ${alpha})`
        : p.colorType === 'cyan'
        ? `rgba(56, 189, 248, ${alpha * 0.8})`
        : `rgba(52, 211, 153, ${alpha * 0.8})`;

    ctx.beginPath();
    ctx.arc(px, py, p.radius * (U * 0.08), 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();

  // Layer 4: Multi-Scene Narrative Visuals
  // --------------------------------------------------------------------------
  // SCENE 0: Primordial Portal & Divine Shockwave (0.0s - 3.8s)
  // --------------------------------------------------------------------------
  const s0Blend = smoothstep(0.0, 0.8, t) * (1 - smoothstep(3.2, 3.8, t));
  if (s0Blend > 0.001) {
    ctx.save();
    ctx.globalAlpha = s0Blend;

    // Expanding shockwave rings
    const shockR = ((t * 8) % 35) * U;
    ctx.strokeStyle = 'rgba(212, 175, 55, 0.4)';
    ctx.lineWidth = Math.max(1, U * 0.12);
    ctx.beginPath();
    ctx.arc(cx, cy, shockR, 0, Math.PI * 2);
    ctx.stroke();

    // Central pulsing star
    const starR = (4 + Math.sin(t * 6) * 1) * U;
    const starGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, starR);
    starGrad.addColorStop(0, '#FFFFFF');
    starGrad.addColorStop(0.3, '#F5D061');
    starGrad.addColorStop(0.7, '#D4AF37');
    starGrad.addColorStop(1, 'transparent');
    ctx.fillStyle = starGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, starR, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  // --------------------------------------------------------------------------
  // SCENE 1: Astrolabe Mandala (Usturlap) (3.8s - 9.8s)
  // --------------------------------------------------------------------------
  const s1Blend = smoothstep(3.5, 4.2, t) * (1 - smoothstep(9.2, 9.8, t));
  if (s1Blend > 0.001) {
    ctx.save();
    ctx.globalAlpha = s1Blend;

    const rot1 = (t - 3.8) * 0.25;
    const rot2 = -(t - 3.8) * 0.18;
    const rBase = 18 * U;

    // Outer Geared Ring
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(rot1);
    ctx.strokeStyle = 'rgba(212, 175, 55, 0.6)';
    ctx.lineWidth = Math.max(1, U * 0.14);
    ctx.beginPath();
    ctx.arc(0, 0, rBase, 0, Math.PI * 2);
    ctx.stroke();

    // 12 Astrological / Wisdom Nodes
    for (let i = 0; i < 12; i++) {
      const a = (i * Math.PI * 2) / 12;
      ctx.fillStyle = '#FFDF73';
      ctx.beginPath();
      ctx.arc(Math.cos(a) * rBase, Math.sin(a) * rBase, U * 0.25, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();

    // Inner Counter-Rotating Seljuk Geometric Star
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(rot2);
    ctx.strokeStyle = 'rgba(245, 208, 97, 0.7)';
    ctx.lineWidth = Math.max(0.8, U * 0.1);
    const starRadius = rBase * 0.65;
    ctx.beginPath();
    for (let i = 0; i < 8; i++) {
      const a1 = (i * Math.PI * 2) / 8;
      const a2 = ((i + 3) * Math.PI * 2) / 8;
      ctx.moveTo(Math.cos(a1) * starRadius, Math.sin(a1) * starRadius);
      ctx.lineTo(Math.cos(a2) * starRadius, Math.sin(a2) * starRadius);
    }
    ctx.stroke();
    ctx.restore();

    // Central Sun Seal
    const centerGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, 4 * U);
    centerGrad.addColorStop(0, '#FFFFFF');
    centerGrad.addColorStop(0.4, '#F5D061');
    centerGrad.addColorStop(1, 'transparent');
    ctx.fillStyle = centerGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, 4 * U, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  // --------------------------------------------------------------------------
  // SCENE 2: 3D Holographic Atom Model (9.8s - 16.0s)
  // --------------------------------------------------------------------------
  const s2Blend = smoothstep(9.5, 10.2, t) * (1 - smoothstep(15.4, 16.0, t));
  if (s2Blend > 0.001) {
    ctx.save();
    ctx.globalAlpha = s2Blend;

    const atomR = 16 * U;
    const ringCount = 3;

    // 3 Inclined Quantum Ellipses
    for (let r = 0; r < ringCount; r++) {
      const ringAngle = (r * Math.PI) / ringCount;
      const ringRot = (t - 9.8) * 0.6 + r * 1.2;

      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(ringAngle);
      ctx.scale(1, 0.45); // isometric 3D tilt

      ctx.strokeStyle = r === 0 ? 'rgba(56, 189, 248, 0.65)' : r === 1 ? 'rgba(212, 175, 55, 0.7)' : 'rgba(168, 85, 247, 0.65)';
      ctx.lineWidth = Math.max(1, U * 0.12);
      ctx.beginPath();
      ctx.arc(0, 0, atomR, 0, Math.PI * 2);
      ctx.stroke();

      // Traveling Quantum Electron
      const electronAngle = ringRot;
      const ex = Math.cos(electronAngle) * atomR;
      const ey = Math.sin(electronAngle) * atomR;
      ctx.fillStyle = '#FFFFFF';
      ctx.shadowColor = '#38BDF8';
      ctx.shadowBlur = 15;
      ctx.beginPath();
      ctx.arc(ex, ey, U * 0.35, 0, Math.PI * 2);
      ctx.fill();

      ctx.restore();
    }

    // Glowing Atomic Nucleus
    const nucleusR = (2.5 + 0.4 * Math.sin(t * 5)) * U;
    const nGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, nucleusR * 2);
    nGrad.addColorStop(0, '#FFFFFF');
    nGrad.addColorStop(0.3, '#38BDF8');
    nGrad.addColorStop(0.7, '#6366F1');
    nGrad.addColorStop(1, 'transparent');
    ctx.fillStyle = nGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, nucleusR * 2, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  // --------------------------------------------------------------------------
  // SCENE 3: Divine Mizan (Cosmic Balance Scales) (16.0s - 23.0s)
  // --------------------------------------------------------------------------
  const s3Blend = smoothstep(15.7, 16.5, t) * (1 - smoothstep(22.3, 23.0, t));
  if (s3Blend > 0.001) {
    ctx.save();
    ctx.globalAlpha = s3Blend;

    // Laser Plumb Line of Absolute Straightness (İstikamet)
    ctx.save();
    ctx.strokeStyle = 'rgba(255, 223, 115, 0.55)';
    ctx.lineWidth = Math.max(1, U * 0.08);
    ctx.setLineDash([8, 8]);
    ctx.beginPath();
    ctx.moveTo(cx, cy - 22 * U);
    ctx.lineTo(cx, cy + 22 * U);
    ctx.stroke();
    ctx.restore();

    // Central Vertical Pivot Pillar
    ctx.strokeStyle = '#D4AF37';
    ctx.lineWidth = Math.max(2, U * 0.22);
    ctx.beginPath();
    ctx.moveTo(cx, cy - 12 * U);
    ctx.lineTo(cx, cy + 14 * U);
    ctx.stroke();

    // Tilting Balance Beam: Damps gently to zero equilibrium
    const dampTime = t - 16.0;
    const tiltAngle = Math.sin(dampTime * 1.8) * Math.exp(-dampTime * 0.25) * 0.12;
    const beamLength = 16 * U;

    ctx.save();
    ctx.translate(cx, cy - 6 * U);
    ctx.rotate(tiltAngle);

    ctx.strokeStyle = '#F5D061';
    ctx.lineWidth = Math.max(2, U * 0.18);
    ctx.beginPath();
    ctx.moveTo(-beamLength, 0);
    ctx.lineTo(beamLength, 0);
    ctx.stroke();

    // Fulcrum Jewel
    ctx.fillStyle = '#34D399';
    ctx.beginPath();
    ctx.arc(0, 0, U * 0.5, 0, Math.PI * 2);
    ctx.fill();

    // Left Scale Pan
    ctx.strokeStyle = 'rgba(212, 175, 55, 0.7)';
    ctx.lineWidth = Math.max(1, U * 0.08);
    ctx.beginPath();
    ctx.moveTo(-beamLength, 0);
    ctx.lineTo(-beamLength - 3 * U, 7 * U);
    ctx.moveTo(-beamLength, 0);
    ctx.lineTo(-beamLength + 3 * U, 7 * U);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(-beamLength, 7 * U, 3.2 * U, 0, Math.PI);
    ctx.stroke();

    // Right Scale Pan
    ctx.beginPath();
    ctx.moveTo(beamLength, 0);
    ctx.lineTo(beamLength - 3 * U, 7 * U);
    ctx.moveTo(beamLength, 0);
    ctx.lineTo(beamLength + 3 * U, 7 * U);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(beamLength, 7 * U, 3.2 * U, 0, Math.PI);
    ctx.stroke();

    ctx.restore();
    ctx.restore();
  }

  // --------------------------------------------------------------------------
  // SCENE 4: The Heart (Kalp & Basiret Mandala) (23.0s - 30.0s)
  // --------------------------------------------------------------------------
  const s4Blend = smoothstep(22.7, 23.5, t) * (1 - smoothstep(29.3, 30.0, t));
  if (s4Blend > 0.001) {
    ctx.save();
    ctx.globalAlpha = s4Blend;

    // Heartbeat Pulse (1 Hz = 60 BPM)
    const hb = Math.pow(Math.sin((t - 23.0) * Math.PI * 2), 6);
    const pulseScale = 1 + hb * 0.18;
    const heartR = 15 * U * pulseScale;

    // Expanding Warm Emerald-Gold Halo
    const haloGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, heartR * 1.5);
    haloGrad.addColorStop(0, 'rgba(52, 211, 153, 0.35)');
    haloGrad.addColorStop(0.4, 'rgba(212, 175, 55, 0.2)');
    haloGrad.addColorStop(1, 'transparent');
    ctx.fillStyle = haloGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, heartR * 1.5, 0, Math.PI * 2);
    ctx.fill();

    // Sacred Heart Geometry (Nested 8-pointed star rosette)
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate((t - 23.0) * 0.15);
    ctx.strokeStyle = 'rgba(52, 211, 153, 0.75)';
    ctx.lineWidth = Math.max(1, U * 0.14);

    for (let layer = 0; layer < 3; layer++) {
      const lr = heartR * (0.5 + layer * 0.25);
      ctx.beginPath();
      for (let i = 0; i < 8; i++) {
        const a = (i * Math.PI * 2) / 8;
        const x = Math.cos(a) * lr;
        const y = Math.sin(a) * lr;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.stroke();
    }
    ctx.restore();

    ctx.restore();
  }

  // --------------------------------------------------------------------------
  // SCENE 5: Golden Hourglass of Time & Eternity (30.0s - 37.0s)
  // --------------------------------------------------------------------------
  const s5Blend = smoothstep(29.7, 30.5, t);
  if (s5Blend > 0.001) {
    ctx.save();
    ctx.globalAlpha = s5Blend;

    // Hourglass Wireframe
    const hgW = 12 * U;
    const hgH = 20 * U;
    ctx.strokeStyle = 'rgba(212, 175, 55, 0.7)';
    ctx.lineWidth = Math.max(1.5, U * 0.16);

    ctx.beginPath();
    // Top bar
    ctx.moveTo(cx - hgW, cy - hgH);
    ctx.lineTo(cx + hgW, cy - hgH);
    // Upper triangle to neck
    ctx.lineTo(cx, cy);
    // Lower triangle
    ctx.lineTo(cx - hgW, cy + hgH);
    // Bottom bar
    ctx.lineTo(cx + hgW, cy + hgH);
    // Back to neck
    ctx.lineTo(cx, cy);
    // Close to top left
    ctx.lineTo(cx - hgW, cy - hgH);
    ctx.stroke();

    // Falling Golden Sand Stream
    ctx.save();
    ctx.strokeStyle = '#FFDF73';
    ctx.lineWidth = Math.max(1, U * 0.1);
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx, cy + hgH * 0.9);
    ctx.stroke();

    // Cascading sand particles in lower bulb
    for (let i = 0; i < 30; i++) {
      const sx = cx + (R() - 0.5) * 8 * U;
      const sy = cy + 2 * U + ((t * 15 + i * 2) % (hgH * 0.8));
      ctx.fillStyle = 'rgba(255, 223, 115, 0.8)';
      ctx.beginPath();
      ctx.arc(sx, sy, U * 0.12, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();

    ctx.restore();
  }

  // Layer 5: Vignette & Border Polish
  const vignette = ctx.createRadialGradient(cx, cy, 35 * U, cx, cy, 55 * U);
  vignette.addColorStop(0, 'transparent');
  vignette.addColorStop(1, 'rgba(3, 5, 8, 0.7)');
  ctx.fillStyle = vignette;
  ctx.fillRect(0, 0, W, H);

  ctx.restore();
}

// ============================================================================
// REMOTION REACT ROOT COMPONENT
// ============================================================================
export const CanvasStoryVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const t = frame / FPS;
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Synchronous paint before frame capture
  useLayoutEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    renderCanvasStory(ctx, t, width, height);
  }, [frame, t, width, height]);

  // Current Scene Index
  const currentSceneIdx = SCENES.findIndex((s) => t >= s.start && t < s.end);
  const activeScene = SCENES[currentSceneIdx >= 0 ? currentSceneIdx : SCENES.length - 1];

  // Active Line & Words
  const currentWords = words.filter((w) => w.c === activeScene.id);
  const activeWordIdx = currentWords.findIndex((w) => t >= w.s && t <= w.e);

  // Top Progress Percentage
  const progressPct = clamp((t / TOTAL_DURATION_SEC) * 100, 0, 100);

  return (
    <AbsoluteFill style={{ backgroundColor: '#070A10', overflow: 'hidden' }}>
      {/* 1. Hardware-Accelerated 2D Canvas */}
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
        }}
      />

      {/* 2. Top Header HUD Badge & Progress Track */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          padding: '48px 40px 24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          zIndex: 20,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span
              style={{
                fontSize: '12px',
                fontWeight: 700,
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: '#F5D061',
                padding: '4px 10px',
                borderRadius: '8px',
                background: 'rgba(212, 175, 55, 0.12)',
                border: '1px solid rgba(212, 175, 55, 0.3)',
              }}
            >
              CANVAS 2D SKILL // DEMO
            </span>
            <span style={{ fontSize: '13px', color: '#94A3B8', fontFamily: 'monospace' }}>
              SAHNE {activeScene.id + 1}/6
            </span>
          </div>

          <div style={{ fontSize: '12px', color: '#64748B', fontFamily: 'monospace' }}>
            {t.toFixed(1)}s / {TOTAL_DURATION_SEC.toFixed(1)}s
          </div>
        </div>

        {/* Scene Progress Bar */}
        <div
          style={{
            width: '100%',
            height: '4px',
            backgroundColor: 'rgba(255, 255, 255, 0.08)',
            borderRadius: '2px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${progressPct}%`,
              height: '100%',
              background: 'linear-gradient(90deg, #6366F1, #D4AF37, #F5D061)',
            }}
          />
        </div>
      </div>

      {/* 3. Lower-Third Frosted Glass Subtitles Capsule */}
      <div
        style={{
          position: 'absolute',
          bottom: '80px',
          left: '48px',
          right: '48px',
          padding: '24px 32px',
          borderRadius: '24px',
          background: 'rgba(11, 17, 26, 0.82)',
          backdropFilter: 'blur(24px)',
          border: '1px solid rgba(212, 175, 55, 0.28)',
          boxShadow: '0 20px 50px rgba(0, 0, 0, 0.65)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 30,
        }}
      >
        <p
          style={{
            margin: 0,
            fontSize: '28px',
            lineHeight: 1.45,
            fontWeight: 600,
            textAlign: 'center',
            color: '#CBD5E1',
            fontFamily: "'Plus Jakarta Sans', sans-serif",
            letterSpacing: '-0.01em',
          }}
        >
          {currentWords.map((item, idx) => {
            const isHighlighted = idx === activeWordIdx;
            const isPast = t > item.e;
            return (
              <span
                key={idx}
                style={{
                  color: isHighlighted ? '#FFDF73' : isPast ? '#FFFFFF' : '#94A3B8',
                  textShadow: isHighlighted ? '0 0 16px rgba(255, 223, 115, 0.85)' : 'none',
                  fontWeight: isHighlighted ? 800 : 600,
                  transition: 'all 0.1s ease',
                  marginRight: '6px',
                  display: 'inline-block',
                }}
              >
                {item.w}
              </span>
            );
          })}
        </p>

        {/* Voiceover Seal Badge */}
        <div
          style={{
            marginTop: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '11px',
            color: '#10B981',
            fontWeight: 700,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
          }}
        >
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#10B981' }} />
          <span>Turso Voice #0001 (Derviş 114 Hz) · Studio Mastering</span>
        </div>
      </div>

      {/* 4. Audio Voiceover Track */}
      <Audio src={staticFile('canvas-story-demo/ses.mp3')} />
    </AbsoluteFill>
  );
};

export const Root: React.FC = () => (
  <Composition
    id="CanvasStoryDemo"
    component={CanvasStoryVideo}
    durationInFrames={TOTAL_FRAMES}
    fps={FPS}
    width={1080}
    height={1920}
  />
);
