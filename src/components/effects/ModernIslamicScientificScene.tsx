import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { loadFont as loadCinzel } from '@remotion/google-fonts/Cinzel';
import { loadFont as loadCormorantGaramond } from '@remotion/google-fonts/CormorantGaramond';
import { loadFont as loadAmiri } from '@remotion/google-fonts/Amiri';
import { VideoScene } from '../../types';
import { StardustConstellation } from './StardustConstellation';
import { ScientificPieChart } from './ScientificPieChart';
import { TectonicGlobeMap } from './TectonicGlobeMap';
import { ThermalMetricGauge } from './ThermalMetricGauge';
import { HydrothermalVentWindow } from './HydrothermalVentWindow';
import { EtymologyRootCard } from './EtymologyRootCard';
import { IslamicBalanceScale } from './IslamicBalanceScale';
import { QuranMatrixTable } from './QuranMatrixTable';

interface ModernIslamicScientificSceneProps {
  scene: VideoScene;
  theme?: string;
  sceneIndex: number;
}

export const ModernIslamicScientificScene: React.FC<ModernIslamicScientificSceneProps> = ({
  scene,
  theme = 'gold_luxury',
  sceneIndex,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Load Google Fonts
  loadCinzel();
  loadCormorantGaramond();
  loadAmiri();

  // Gentle cinematic spring entrance
  const entrance = spring({
    frame,
    fps,
    config: { damping: 18, stiffness: 85, mass: 0.9 },
  });

  const fadeIn = interpolate(frame, [0, 14], [0, 1], {
    extrapolateRight: 'clamp',
  });

  const floatY = Math.sin(frame * 0.05) * 6;

  // Metadata resolution
  const arabicText = (scene as any).arabicVerse || (scene.quoteSpotlight as any)?.ayahArabic || '';
  const quoteText = scene.quoteSpotlight?.quoteText || scene.narration || '';

  // Symmetrical Quranic / Chapter Citation Header
  let citationHeader = scene.citation || scene.headerSubtitle || '';
  if (!citationHeader) {
    if (sceneIndex === 0) {
      citationHeader = '· ۞ · İSLÂM TEFEKKÜRÜ · ۞ · CAHİLİYE ÇAĞI · ۞ ·';
    } else if (sceneIndex === 1) {
      citationHeader = '· ۞ · سُورَةُ الإِسْرَاءِ · ۞ · İSRÂ · 17:81 · ۞ ·';
    } else if (sceneIndex === 2) {
      citationHeader = '· ۞ · NEFS MUHASEBESİ · ۞ · GÜNÜMÜZ DÜNYASI · ۞ ·';
    } else if (sceneIndex === 3) {
      citationHeader = '· ۞ · سُورَةُ الفُرْقَانِ · ۞ · FURKÂN · 25:43 · ۞ ·';
    } else {
      citationHeader = '· ۞ · سُورَةُ الزُّمَرِ · ۞ · ZÜMER · 39:53 · ۞ ·';
    }
  }

  // Stardust Numbers & Focal Typography determination
  let stardustPrimary = scene.stardustPrimary || '';
  let stardustSecondary = scene.stardustSecondary || '';
  let stardustSymbol = scene.stardustSymbol || '۞';

  if (!stardustPrimary) {
    if (sceneIndex === 0) {
      stardustPrimary = '360';
      stardustSecondary = 'TAŞ PUT DEVRİLDİ';
      stardustSymbol = '✦';
    } else if (sceneIndex === 1) {
      stardustPrimary = 'HAK GELDİ';
      stardustSecondary = 'BÂTIL YOK OLDU';
      stardustSymbol = '۞';
    } else if (sceneIndex === 2) {
      stardustPrimary = '24 SAAT';
      stardustSecondary = 'PARLAYAN EKRANLAR';
      stardustSymbol = '✦';
    } else if (sceneIndex === 3) {
      stardustPrimary = '1 NEFİS';
      stardustSecondary = 'HEVÂ VE HEVES';
      stardustSymbol = '۞';
    } else {
      stardustPrimary = 'TÖVBE ET';
      stardustSecondary = 'KALBİNİN KÂBESİNİ TEMİZLE';
      stardustSymbol = '✦';
    }
  }

  // Determine which scientific visual component to render
  const graphicType = scene.scientificGraphicType;

  // Function to highlight key spiritual keywords in classical serif translation
  const formatSpiritualText = (text: string) => {
    const keywords = [
      'üç yüz altmış', '360', 'taş put', 'Hak geldi', 'bâtıl yok oldu',
      'mahvoldur', 'parlayan ekranlar', 'secdeye', 'heba edilen',
      'nefsinin arzusunu', 'ilah edineni', 'Kâbe', 'kalbinin Kâbe’sindeki',
      'kalbinin Kâbe\'sindeki', 'putları', 'ne zaman kıracaksın',
      'Su ateşi söndürür', '1200', '1200°C', 'Mescûr', 'el-mescûr', 'Secr',
      'tutuşturulmuş deniz', 'fırın', 'okyanus tabanı', '%80'
    ];

    return (
      <span>
        {text.split(new RegExp(`(${keywords.join('|')})`, 'gi')).map((part, i) => {
          const isMatch = keywords.some(k => k.toLowerCase() === part.toLowerCase());
          if (isMatch) {
            return (
              <span
                key={i}
                style={{
                  color: '#f3d081',
                  fontWeight: 800,
                  textShadow: '0 0 16px rgba(243, 208, 129, 0.65)',
                }}
              >
                {part}
              </span>
            );
          }
          return <span key={i}>{part}</span>;
        })}
      </span>
    );
  };

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '0 50px',
        zIndex: 10,
        opacity: fadeIn,
      }}
    >
      {/* 1. Top Symmetrical Quranic / Chapter Citation Banner */}
      <div
        style={{
          marginTop: 110,
          transform: `scale(${entrance}) translateY(${floatY * 0.4}px)`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 14,
          padding: '10px 32px',
          borderRadius: 9999,
          backgroundColor: 'rgba(5, 8, 18, 0.78)',
          border: '1.5px solid rgba(245, 158, 11, 0.55)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.8), 0 0 25px rgba(245, 158, 11, 0.25)',
          backdropFilter: 'blur(20px)',
        }}
      >
        <span
          style={{
            fontFamily: '"Cinzel", "Amiri", serif',
            fontSize: 21,
            fontWeight: 800,
            letterSpacing: '3px',
            color: '#facc15',
            textShadow: '0 0 15px rgba(250, 204, 21, 0.6)',
            textTransform: 'uppercase',
          }}
        >
          {citationHeader}
        </span>
      </div>

      {/* 2. DYNAMIC SCIENTIFIC & VISUAL INFOGRAPHIC LAYER */}
      {graphicType === 'pie_chart' || scene.pieChart ? (
        <ScientificPieChart {...scene.pieChart} />
      ) : graphicType === 'tectonic_map' || scene.tectonicMap ? (
        <TectonicGlobeMap {...scene.tectonicMap} />
      ) : graphicType === 'thermal_gauge' || scene.thermalGauge ? (
        <ThermalMetricGauge {...scene.thermalGauge} />
      ) : graphicType === 'vent_window' || scene.ventWindow ? (
        <HydrothermalVentWindow {...scene.ventWindow} />
      ) : graphicType === 'etymology_card' || scene.etymologyCard ? (
        <EtymologyRootCard {...scene.etymologyCard} />
      ) : graphicType === 'balance_scale' || scene.balanceScale ? (
        <IslamicBalanceScale {...scene.balanceScale} />
      ) : graphicType === 'matrix_table' || scene.matrixTable ? (
        <QuranMatrixTable {...scene.matrixTable} />
      ) : (
        /* Default Stardust Constellation Centerpiece */
        <div style={{ marginTop: 24, width: '100%' }}>
          <StardustConstellation
            primaryText={stardustPrimary}
            secondaryText={stardustSecondary}
            symbol={stardustSymbol}
            glowColor={sceneIndex === 2 ? 'rgba(56, 189, 248, 0.6)' : 'rgba(245, 158, 11, 0.65)'}
          />
        </div>
      )}

      {/* 3. Authentic Celi Sülüs / Uthmani Arabic Calligraphy (If Ayet is present and not an etymology card) */}
      {arabicText && graphicType !== 'etymology_card' ? (
        <div
          style={{
            transform: `scale(${entrance})`,
            fontFamily: '"Amiri", "Scheherazade New", serif',
            fontSize: arabicText.length > 50 ? 38 : 46,
            fontWeight: 700,
            direction: 'rtl',
            color: '#fef08a',
            textAlign: 'center',
            lineHeight: 1.55,
            marginTop: 14,
            marginBottom: 16,
            padding: '16px 36px',
            borderRadius: 22,
            backgroundColor: 'rgba(4, 7, 16, 0.82)',
            border: '1.5px solid rgba(245, 158, 11, 0.65)',
            boxShadow: '0 14px 45px rgba(0, 0, 0, 0.9), 0 0 35px rgba(245, 158, 11, 0.35)',
            backdropFilter: 'blur(24px)',
            maxWidth: 960,
            textShadow: `
              0 0 25px rgba(245, 158, 11, 0.75),
              0 4px 18px rgba(0, 0, 0, 0.95)
            `,
          }}
        >
          {arabicText}
        </div>
      ) : null}

      {/* 4. Classical Serif Spiritual Contemplation Card (If quoteText is present and not covered by graphic card) */}
      {quoteText && !scene.pieChart && !scene.tectonicMap && !scene.thermalGauge && !scene.ventWindow && !scene.etymologyCard && (
        <div
          style={{
            transform: `scale(${entrance}) translateY(${floatY * 0.6}px)`,
            marginTop: arabicText ? 10 : 20,
            padding: '22px 38px',
            borderRadius: 22,
            backgroundColor: 'rgba(4, 7, 16, 0.76)',
            border: '1.5px solid rgba(255, 255, 255, 0.12)',
            boxShadow: '0 12px 36px rgba(0, 0, 0, 0.85)',
            backdropFilter: 'blur(20px)',
            maxWidth: 940,
            textAlign: 'center',
          }}
        >
          <div
            style={{
              fontFamily: '"Cormorant Garamond", "Cinzel", Georgia, serif',
              fontSize: 32,
              fontWeight: 600,
              fontStyle: 'italic',
              color: '#e2e8f0',
              lineHeight: 1.48,
              letterSpacing: '0.4px',
              textShadow: '0 2px 18px rgba(0, 0, 0, 0.95)',
            }}
          >
            “{formatSpiritualText(quoteText)}”
          </div>
        </div>
      )}
    </div>
  );
};
