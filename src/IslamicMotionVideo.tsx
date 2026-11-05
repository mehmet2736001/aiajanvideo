import React from 'react';
import { useCurrentFrame, interpolate, Easing, Img, staticFile, AbsoluteFill } from 'remotion';
import { AtomFe26HoloModel } from './components/effects/AtomFe26HoloModel';
import { EbcedFlyingCards } from './components/effects/EbcedFlyingCards';
import { IslamicBalanceScale } from './components/effects/IslamicBalanceScale';
import { AstrolabeGoldenMandala } from './components/effects/AstrolabeGoldenMandala';
import { EarthShieldTelemetryHUD } from './components/effects/EarthShieldTelemetryHUD';
import { DopplerExpansionHUD } from './components/effects/DopplerExpansionHUD';

let conceptData: any = null;
try {
  conceptData = require('./activeConcept.json');
} catch (e) {
  conceptData = null;
}

export const IslamicMotionVideo: React.FC = () => {
  const frame = useCurrentFrame();

  const totalFrames = conceptData?.totalFrames || 2078;
  const scenes = conceptData?.scenes || [];

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#03050a',
        fontFamily: "'Cinzel', serif",
        overflow: 'hidden',
        width: 1080,
        height: 1920,
      }}
    >
      {scenes.map((sc: any, idx: number) => {
        const isVisible = frame >= sc.startFrame && frame < sc.endFrame;
        if (!isVisible) return null;

        const sceneDuration = sc.endFrame - sc.startFrame;
        const localFrame = frame - sc.startFrame;

        // Snappy, cinematic 12-frame (0.4s) cross dissolve
        const sceneOpacity = interpolate(
          localFrame,
          [0, 12, sceneDuration - 12, sceneDuration],
          [0, 1, 1, 0],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
        );

        // Dynamic 3D Camera Move (Ken Burns with slight 3D rotation)
        let scale = 1.0;
        let transX = 0;
        let transY = 0;
        let rotZ = 0;

        if (sc.motion === 'zoom-in') {
          scale = interpolate(localFrame, [0, sceneDuration], [1.0, 1.18], {
            easing: Easing.bezier(0.2, 0.1, 0.3, 1),
            extrapolateRight: 'clamp',
          });
          rotZ = interpolate(localFrame, [0, sceneDuration], [-0.5, 0.5]);
        } else if (sc.motion === 'zoom-out') {
          scale = interpolate(localFrame, [0, sceneDuration], [1.18, 1.02], {
            easing: Easing.bezier(0.2, 0.1, 0.3, 1),
            extrapolateRight: 'clamp',
          });
          rotZ = interpolate(localFrame, [0, sceneDuration], [0.5, -0.5]);
        } else if (sc.motion === 'pan-right') {
          scale = 1.1;
          transX = interpolate(localFrame, [0, sceneDuration], [-40, 40], {
            easing: Easing.linear,
          });
        } else if (sc.motion === 'tilt-up') {
          scale = 1.1;
          transY = interpolate(localFrame, [0, sceneDuration], [45, -45], {
            easing: Easing.linear,
          });
        } else {
          scale = interpolate(localFrame, [0, sceneDuration], [1.02, 1.15]);
        }

        // Dynamic Sweeping Volumetric Light Beam (Animates across the screen)
        const lightSweepX = interpolate(localFrame, [0, sceneDuration], [-300, 1380], {
          easing: Easing.linear,
        });

        // Staggered text entrance
        const headlineScale = interpolate(localFrame, [0, 16], [0.9, 1.0], {
          easing: Easing.out(Easing.cubic),
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        const textY = interpolate(localFrame, [0, 18], [30, 0], {
          easing: Easing.out(Easing.cubic),
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });

        // Determine which flying infographic widget to render dynamically from scene schema:
        const showDopplerSpectrum = sc.infographic === 'doppler_spectrum';
        const showArabicEtymology = sc.infographic === 'arabic_etymology';
        const showAtomHolo = sc.infographic === 'atom_holo';
        const showEbcedCards = sc.infographic === 'ebced_cards';
        const showBalanceScale = sc.infographic === 'balance_scale';
        const showEarthShield = sc.infographic === 'earth_shield';
        const showMandala = sc.infographic === 'astrolabe_mandala';

        return (
          <div
            key={idx}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: 1080,
              height: 1920,
              opacity: sceneOpacity,
              overflow: 'hidden',
            }}
          >
            {/* LAYER 1: Visual Asset with Dynamic Camera Motion & Organic Color Grade */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: 1080,
                height: 1920,
                transform: `scale(${scale}) translate(${transX}px, ${transY}px) rotate(${rotZ}deg)`,
                transformOrigin: 'center center',
              }}
            >
              <Img
                src={staticFile(sc.image)}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  filter: 'contrast(1.12) brightness(0.88)',
                }}
              />
            </div>

            {/* LAYER 2: Dynamic Sweeping Volumetric Light Beam */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: lightSweepX,
                width: 450,
                height: 1920,
                background:
                  'linear-gradient(90deg, transparent 0%, rgba(212, 175, 55, 0.12) 50%, transparent 100%)',
                transform: 'skewX(-25deg)',
                pointerEvents: 'none',
              }}
            />

            {/* LAYER 3: Cinematic Vignette & Deep Contrast Gradients */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: 1080,
                height: 1920,
                background:
                  'radial-gradient(circle at 50% 45%, rgba(0,0,0,0) 25%, rgba(3,5,12,0.78) 100%)',
                pointerEvents: 'none',
              }}
            />
            <div
              style={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                width: 1080,
                height: 920,
                background:
                  'linear-gradient(to top, rgba(3,5,10,0.98) 0%, rgba(3,5,10,0.88) 40%, rgba(3,5,10,0.2) 75%, transparent 100%)',
                pointerEvents: 'none',
              }}
            />
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: 1080,
                height: 400,
                background:
                  'linear-gradient(to bottom, rgba(3,5,10,0.9) 0%, rgba(3,5,10,0.35) 65%, transparent 100%)',
                pointerEvents: 'none',
              }}
            />

            {/* LAYER 4: Rotating Astrolabe Sacred Geometry Mandala (Ambient HUD) */}
            {showMandala && (
              <div
                style={{
                  position: 'absolute',
                  top: '420px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  zIndex: 2,
                }}
              >
                <AstrolabeGoldenMandala size={640} opacity={0.38} />
              </div>
            )}

            {/* LAYER 5: FLYING INFOGRAPHICS & HOLOGRAPHIC MODELS IN MID-AIR */}
            {showDopplerSpectrum && (
              <div
                style={{
                  position: 'absolute',
                  top: '380px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  zIndex: 5,
                }}
              >
                <DopplerExpansionHUD scaleMultiplier={0.95} mode="spectrum" />
              </div>
            )}

            {showArabicEtymology && (
              <div
                style={{
                  position: 'absolute',
                  top: '360px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  zIndex: 5,
                }}
              >
                <DopplerExpansionHUD scaleMultiplier={0.95} mode="etymology" />
              </div>
            )}

            {showAtomHolo && (
              <div
                style={{
                  position: 'absolute',
                  top: '400px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  zIndex: 5,
                }}
              >
                <AtomFe26HoloModel scaleMultiplier={0.95} />
              </div>
            )}

            {showEbcedCards && (
              <div
                style={{
                  position: 'absolute',
                  top: '380px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  zIndex: 5,
                }}
              >
                <EbcedFlyingCards scaleMultiplier={0.95} />
              </div>
            )}

            {showBalanceScale && (
              <div
                style={{
                  position: 'absolute',
                  top: '360px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  zIndex: 5,
                }}
              >
                <IslamicBalanceScale
                  leftLabel="EBCED (HADÎD)"
                  rightLabel="ATOM NUMARASI"
                  leftCount={26}
                  rightCount={26}
                  leftSubtext="SÛRE NO: 57"
                  rightSubtext="Fe-57 İZOTOPU"
                  title="26 VE 57'NİN KUSURSUZ MİZANI"
                  themeColor="#d4af37"
                />
              </div>
            )}

            {showEarthShield && (
              <div
                style={{
                  position: 'absolute',
                  top: '420px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  zIndex: 5,
                }}
              >
                <EarthShieldTelemetryHUD scaleMultiplier={0.95} />
              </div>
            )}

            {/* LAYER 6: Floating 24K Gold Particles Overlay */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: 1080,
                height: 1920,
                pointerEvents: 'none',
                zIndex: 6,
              }}
            >
              {[...Array(20)].map((_, pi) => {
                const seedX = ((pi * 67) % 980) + 50;
                const seedSpeed = 0.9 + (pi % 5) * 0.45;
                const particleY = 1920 - ((localFrame * seedSpeed * 4.0 + pi * 105) % 2100);
                const particleSize = 3 + (pi % 4) * 2.5;
                const pAlpha = 0.35 + ((pi * 19) % 55) / 100;

                return (
                  <div
                    key={pi}
                    style={{
                      position: 'absolute',
                      left: seedX,
                      top: particleY,
                      width: particleSize,
                      height: particleSize,
                      borderRadius: '50%',
                      backgroundColor: '#fef08a',
                      boxShadow: '0 0 10px #d4af37, 0 0 22px #f59e0b',
                      opacity: pAlpha,
                    }}
                  />
                );
              })}
            </div>

            {/* LAYER 7: Top Ornate Pill Tag */}
            <div
              style={{
                position: 'absolute',
                top: '110px',
                left: 0,
                width: '1080px',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                zIndex: 10,
              }}
            >
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  padding: '8px 24px',
                  backgroundColor: 'rgba(8, 12, 24, 0.85)',
                  border: '1.5px solid rgba(212, 175, 55, 0.75)',
                  borderRadius: '30px',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.8), inset 0 0 12px rgba(212, 175, 55, 0.3)',
                  backdropFilter: 'blur(10px)',
                }}
              >
                <span style={{ color: '#d4af37', fontSize: '18px', marginRight: '10px' }}>✦</span>
                <span
                  style={{
                    color: '#f8fafc',
                    fontFamily: "'Cinzel', serif",
                    fontSize: '20px',
                    fontWeight: 800,
                    letterSpacing: '4px',
                    textTransform: 'uppercase',
                  }}
                >
                  {sc.tag}
                </span>
                <span style={{ color: '#d4af37', fontSize: '18px', marginLeft: '10px' }}>✦</span>
              </div>
            </div>

            {/* LAYER 8: Arabic Scripture Calligraphy (Amiri Font with 3-Tier Gold Glow) */}
            {sc.arabic && (
              <div
                style={{
                  position: 'absolute',
                  top: '230px',
                  left: 0,
                  width: '1080px',
                  padding: '0 50px',
                  textAlign: 'center',
                  zIndex: 10,
                }}
              >
                <div
                  style={{
                    fontFamily: "'Amiri', 'Traditional Arabic', serif",
                    fontSize: '48px',
                    lineHeight: '1.6',
                    color: '#ffffff',
                    textShadow:
                      '0 0 16px rgba(212, 175, 55, 0.9), 0 0 35px rgba(212, 175, 55, 0.5), 0 4px 12px rgba(0,0,0,0.95)',
                    direction: 'rtl',
                  }}
                >
                  {sc.arabic}
                </div>
              </div>
            )}

            {/* LAYER 9: Bottom Content Area (Elevated +90px for Mobile Safe Zone & Contrast Backdrop) */}
            <div
              style={{
                position: 'absolute',
                bottom: '240px',
                left: '50%',
                transform: `translateX(-50%) scale(${headlineScale}) translateY(${textY}px)`,
                width: '980px',
                padding: '26px 44px',
                textAlign: 'center',
                zIndex: 10,
                background:
                  'linear-gradient(180deg, rgba(5, 8, 18, 0.72) 0%, rgba(3, 5, 12, 0.88) 100%)',
                backdropFilter: 'blur(14px)',
                borderRadius: '28px',
                border: '1px solid rgba(212, 175, 55, 0.35)',
                boxShadow:
                  '0 16px 45px rgba(0,0,0,0.9), 0 0 25px rgba(212, 175, 55, 0.15)',
              }}
            >
              {/* Gold Shimmer Headline */}
              <div
                style={{
                  fontSize: '44px',
                  fontWeight: 900,
                  letterSpacing: '3px',
                  marginBottom: '14px',
                  textTransform: 'uppercase',
                  background: 'linear-gradient(180deg, #FFFFFF 15%, #F7E2A4 60%, #D4AF37 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  filter: 'drop-shadow(0 4px 16px rgba(0,0,0,0.95))',
                }}
              >
                {sc.headline}
              </div>

              {/* Subtext */}
              <div
                style={{
                  fontSize: '28px',
                  fontWeight: 600,
                  lineHeight: '1.45',
                  color: '#f1f5f9',
                  textShadow:
                    '0 3px 12px rgba(0,0,0,0.98), 0 1px 4px rgba(0,0,0,0.95)',
                  maxWidth: '900px',
                  margin: '0 auto',
                }}
              >
                {sc.subtext}
              </div>
            </div>

            {/* LAYER 10: Outer Subtle Sacred Border Frame with Ornate Corners */}
            <div
              style={{
                position: 'absolute',
                top: 25,
                left: 25,
                right: 25,
                bottom: 25,
                border: '1px solid rgba(212, 175, 55, 0.28)',
                pointerEvents: 'none',
                zIndex: 10,
              }}
            >
              <div
                style={{
                  position: 'absolute',
                  top: -1,
                  left: -1,
                  width: 24,
                  height: 24,
                  borderTop: '3px solid #d4af37',
                  borderLeft: '3px solid #d4af37',
                }}
              />
              <div
                style={{
                  position: 'absolute',
                  top: -1,
                  right: -1,
                  width: 24,
                  height: 24,
                  borderTop: '3px solid #d4af37',
                  borderRight: '3px solid #d4af37',
                }}
              />
              <div
                style={{
                  position: 'absolute',
                  bottom: -1,
                  left: -1,
                  width: 24,
                  height: 24,
                  borderBottom: '3px solid #d4af37',
                  borderLeft: '3px solid #d4af37',
                }}
              />
              <div
                style={{
                  position: 'absolute',
                  bottom: -1,
                  right: -1,
                  width: 24,
                  height: 24,
                  borderBottom: '3px solid #d4af37',
                  borderRight: '3px solid #d4af37',
                }}
              />
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
