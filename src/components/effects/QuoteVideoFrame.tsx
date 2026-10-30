import React from 'react';
import { interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Video } from 'remotion';
import { QuoteVideoItem } from '../../types';

export interface QuoteVideoFrameProps {
  quoteVideos?: QuoteVideoItem[];
}

export const QuoteVideoFrame: React.FC<QuoteVideoFrameProps> = ({ quoteVideos = [] }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const currentTimeSec = frame / fps;

  if (!quoteVideos || quoteVideos.length === 0) return null;

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 48,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {quoteVideos.map((qv) => {
        const startSec = qv.timelineStart ?? 0;
        const dur = qv.duration || Math.max(1, (qv.trimEnd || 6) - (qv.trimStart || 0));
        const endSec = startSec + dur;

        if (currentTimeSec < startSec || currentTimeSec > endSec) {
          return null;
        }

        const startFrame = Math.round(startSec * fps);
        const endFrame = Math.round(endSec * fps);
        const localFrame = frame - startFrame;
        const totalFrames = endFrame - startFrame;

        // Entrance & Exit Transitions (Smooth Spring scale + fade)
        const enterSpring = spring({
          frame: localFrame,
          fps,
          config: { damping: 14, stiffness: 90 },
        });

        const exitFade = interpolate(
          localFrame,
          [Math.max(0, totalFrames - 12), totalFrames],
          [1, 0],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
        );

        const currentOpacity = enterSpring * exitFade;
        const currentScale = interpolate(enterSpring, [0, 1], [0.88, 1]);

        // Video playback trimmed range
        const trimStartSec = qv.trimStart || 0;
        const trimEndSec = qv.trimEnd || (trimStartSec + dur);
        const trimStartFrame = Math.round(trimStartSec * fps);
        const trimEndFrame = Math.round(trimEndSec * fps);

        // Resolve video source URL
        let resolvedSrc = qv.videoUrl;
        if (
          !resolvedSrc.startsWith('http://') &&
          !resolvedSrc.startsWith('https://') &&
          !resolvedSrc.startsWith('blob:') &&
          !resolvedSrc.startsWith('data:')
        ) {
          const cleanPath = resolvedSrc.replace(/^\/?(public\/)?/, '');
          resolvedSrc = staticFile(cleanPath);
        }

        // Animated Stamp calculation (appears during last 1.8 seconds)
        const stampStartFrame = Math.max(10, totalFrames - Math.round(1.8 * fps));
        const stampLocalFrame = localFrame - stampStartFrame;
        const showStamp = qv.stamp && qv.stamp !== 'none' && stampLocalFrame >= 0;

        const stampSpring = showStamp
          ? spring({
              frame: stampLocalFrame,
              fps,
              config: { damping: 10, stiffness: 180 },
            })
          : 0;

        const stampScale = interpolate(stampSpring, [0, 1], [2.4, 1]);
        const stampOpacity = interpolate(stampSpring, [0, 0.4, 1], [0, 0.8, 1]);

        // Frame dimensions (Default ~78% width for maximum punch & readability)
        const containerWidth = qv.width || Math.min(width * 0.82, 880);
        const isVerticalAspect = width < height;

        return (
          <div
            key={qv.id || `quote_${startSec}`}
            style={{
              position: 'absolute',
              width: containerWidth,
              maxWidth: '92%',
              opacity: currentOpacity,
              transform: `scale(${currentScale})`,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              filter: 'drop-shadow(0 25px 50px rgba(0, 0, 0, 0.85))',
            }}
          >
            {/* 1. TOP CALLOUT BANNER ("Arkadaşlar bu videoyu iyi izleyin...") */}
            <div
              style={{
                width: '100%',
                marginBottom: 14,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
              }}
            >
              {/* Badge Tag */}
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '6px 16px',
                  borderRadius: 9999,
                  background:
                    qv.theme === 'red_alert'
                      ? 'linear-gradient(90deg, rgba(239, 68, 68, 0.95), rgba(185, 28, 28, 0.95))'
                      : qv.theme === 'court_evidence'
                      ? 'linear-gradient(90deg, rgba(217, 119, 6, 0.95), rgba(180, 83, 9, 0.95))'
                      : qv.theme === 'news_broadcast'
                      ? 'linear-gradient(90deg, rgba(225, 29, 72, 0.95), rgba(159, 18, 57, 0.95))'
                      : 'linear-gradient(90deg, rgba(99, 102, 241, 0.95), rgba(79, 70, 229, 0.95))',
                  color: '#ffffff',
                  fontSize: 14,
                  fontWeight: 900,
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  boxShadow: '0 4px 15px rgba(0,0,0,0.5)',
                  marginBottom: 8,
                }}
              >
                <span>
                  {qv.theme === 'red_alert'
                    ? '🚨 DİKKAT: YANILTICI İÇERİK'
                    : qv.theme === 'court_evidence'
                    ? '⚖️ DELİL DOSYASI & İNCELEME'
                    : qv.theme === 'news_broadcast'
                    ? '🔴 SON DAKİKA / İDDİA'
                    : qv.theme === 'social_phone'
                    ? '📱 SOSYAL MEDYA İDDİASI'
                    : '💬 ALINTI KESİT'}
                </span>
              </div>

              {/* Main Header Text */}
              <div
                style={{
                  fontFamily: 'system-ui, -apple-system, sans-serif',
                  fontSize: isVerticalAspect ? 24 : 28,
                  fontWeight: 900,
                  color: '#ffffff',
                  lineHeight: 1.25,
                  textShadow: '0 3px 12px rgba(0, 0, 0, 0.9), 0 0 25px rgba(239, 68, 68, 0.4)',
                  padding: '0 12px',
                }}
              >
                {qv.headerText || 'Arkadaşlar bu videoyu iyi izleyin...'}
              </div>

              {/* Subheader & Author Handle */}
              {(qv.subHeaderText || qv.authorTag) && (
                <div
                  style={{
                    fontSize: 13,
                    fontWeight: 700,
                    color: '#cbd5e1',
                    marginTop: 4,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    fontFamily: 'monospace',
                  }}
                >
                  {qv.subHeaderText && <span>{qv.subHeaderText}</span>}
                  {qv.authorTag && (
                    <span style={{ color: '#38bdf8', background: 'rgba(56, 189, 248, 0.15)', padding: '2px 8px', borderRadius: 6 }}>
                      {qv.authorTag}
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* 2. THEMATIC FRAME CONTAINER */}
            <div
              style={{
                width: '100%',
                position: 'relative',
                borderRadius: qv.theme === 'social_phone' ? 44 : qv.theme === 'minimal_card' ? 24 : 20,
                overflow: 'hidden',
                background: '#000000',
                border:
                  qv.theme === 'red_alert'
                    ? '4px solid #ef4444'
                    : qv.theme === 'court_evidence'
                    ? '4px solid #f59e0b'
                    : qv.theme === 'news_broadcast'
                    ? '4px solid #f43f5e'
                    : qv.theme === 'social_phone'
                    ? '8px solid #1e293b'
                    : '3px solid rgba(255, 255, 255, 0.2)',
                boxShadow:
                  qv.theme === 'red_alert'
                    ? '0 0 40px rgba(239, 68, 68, 0.65), inset 0 0 20px rgba(239, 68, 68, 0.25)'
                    : qv.theme === 'court_evidence'
                    ? '0 0 35px rgba(245, 158, 11, 0.5), inset 0 0 15px rgba(245, 158, 11, 0.2)'
                    : '0 20px 40px rgba(0, 0, 0, 0.7)',
              }}
            >
              {/* Phone Mockup Top Speaker & Camera Notch */}
              {qv.theme === 'social_phone' && (
                <div
                  style={{
                    position: 'absolute',
                    top: 10,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    width: 100,
                    height: 18,
                    background: '#090d16',
                    borderRadius: 12,
                    zIndex: 20,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: 8,
                  }}
                >
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#1e293b' }} />
                  <div style={{ width: 36, height: 4, borderRadius: 2, background: '#1e293b' }} />
                </div>
              )}

              {/* Video Element (Trimmed from start to end) */}
              <div
                style={{
                  width: '100%',
                  aspectRatio: qv.theme === 'social_phone' ? '9/16' : '16/9',
                  maxHeight: isVerticalAspect ? '52vh' : '62vh',
                  background: '#05070e',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                <Video
                  src={resolvedSrc}
                  startFrom={trimStartFrame}
                  endAt={trimEndFrame}
                  volume={qv.volume ?? 1.0}
                  muted={qv.muted ?? false}
                  onError={(err) => {
                    console.warn('Quote video playback warning:', err);
                  }}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                  }}
                />

                {/* News Broadcast Bottom Banner */}
                {qv.theme === 'news_broadcast' && (
                  <div
                    style={{
                      position: 'absolute',
                      bottom: 0,
                      left: 0,
                      right: 0,
                      background: 'linear-gradient(90deg, #991b1b, #ef4444)',
                      padding: '8px 16px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      color: '#ffffff',
                      fontWeight: 800,
                      fontSize: 13,
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      borderTop: '2px solid #ffffff',
                    }}
                  >
                    <span>🔴 CANLI YAYIN / İDDİA KAYDI</span>
                    <span style={{ fontFamily: 'monospace', fontSize: 11 }}>ARŞİV BELGESİ</span>
                  </div>
                )}

                {/* ANIMATED DEBUNK STAMP (SLAMS DOWN IN LAST SECONDS) */}
                {showStamp && (
                  <div
                    style={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: `translate(-50%, -50%) scale(${stampScale}) rotate(-12deg)`,
                      opacity: stampOpacity,
                      zIndex: 30,
                      pointerEvents: 'none',
                    }}
                  >
                    <div
                      style={{
                        padding: '12px 24px',
                        border: '6px solid',
                        borderColor:
                          qv.stamp === 'yalan'
                            ? '#ef4444'
                            : qv.stamp === 'iddia'
                            ? '#f59e0b'
                            : qv.stamp === 'carpitma'
                            ? '#a855f7'
                            : '#ef4444',
                        background: 'rgba(0, 0, 0, 0.85)',
                        color:
                          qv.stamp === 'yalan'
                            ? '#ef4444'
                            : qv.stamp === 'iddia'
                            ? '#f59e0b'
                            : qv.stamp === 'carpitma'
                            ? '#a855f7'
                            : '#ef4444',
                        borderRadius: 14,
                        fontSize: isVerticalAspect ? 24 : 32,
                        fontWeight: 900,
                        textTransform: 'uppercase',
                        letterSpacing: '0.12em',
                        boxShadow: '0 0 40px rgba(0,0,0,0.9), inset 0 0 15px rgba(239, 68, 68, 0.4)',
                        textAlign: 'center',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {qv.stamp === 'yalan'
                        ? '❌ YALAN / ÇÜRÜTÜLDÜ'
                        : qv.stamp === 'iddia'
                        ? '⚠️ KANITSIZ İDDİA'
                        : qv.stamp === 'carpitma'
                        ? '🔴 ÇARPITILMIŞ İÇERİK'
                        : '🚨 YANILTICI BİLGİ'}
                    </div>
                  </div>
                )}
              </div>

              {/* Phone Mockup Bottom Home Bar */}
              {qv.theme === 'social_phone' && (
                <div
                  style={{
                    position: 'absolute',
                    bottom: 8,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    width: 110,
                    height: 4,
                    background: '#ffffff',
                    borderRadius: 2,
                    opacity: 0.7,
                    zIndex: 20,
                  }}
                />
              )}
            </div>

            {/* Bottom Trim Time Indicator Pill */}
            <div
              style={{
                marginTop: 10,
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                background: 'rgba(15, 23, 42, 0.85)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                padding: '4px 14px',
                borderRadius: 9999,
                fontSize: 11,
                fontFamily: 'monospace',
                color: '#94a3b8',
              }}
            >
              <span style={{ color: '#38bdf8', display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#38bdf8' }} />
                Orijinal Kesit: {trimStartSec.toFixed(1)}s - {trimEndSec.toFixed(1)}s
              </span>
              <span>·</span>
              <span>Süre: {dur.toFixed(1)}s</span>
              <span>·</span>
              <span>🔊 {qv.muted ? 'Sessiz' : 'Orijinal Ses'}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
