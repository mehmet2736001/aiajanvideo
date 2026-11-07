import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Composition,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import { SERIF } from '../fonts';
import veri from '../../public/olum-son-mu/kelimeler.json';

export type Kelime = { w: string; s: number; e: number; c: number };
const K = veri as Kelime[];
const FPS = 30;

// Kelimeye bağlı an fonksiyonu
const an = (satir: number, kelime = 0): number => {
  const satirdakiler = K.filter((k) => k.c === satir);
  if (!satirdakiler.length) return 0;
  const k = satirdakiler[Math.min(kelime, satirdakiler.length - 1)];
  return k ? k.s : 0;
};

// Bezier eğrisiyle yumuşak geçiş
const gir = (t: number, t0: number, sure = 0.8) =>
  interpolate(t, [t0, t0 + sure], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.45, 0, 0.55, 1),
  });

// Lineer karışım
const karis = (a: number, b: number, u: number) => a + (b - a) * u;

// Kinetik Altyazı Bileşeni
export const Altyazi: React.FC<{ t: number }> = ({ t }) => {
  const aktif = K.filter((k) => k.s - 0.05 <= t && t <= k.e + 0.35).pop();
  if (!aktif) return null;

  const satirdakiler = K.filter((k) => k.c === aktif.c);

  return (
    <div
      style={{
        position: 'absolute',
        left: 80,
        right: 80,
        bottom: 220,
        textAlign: 'center',
        fontFamily: SERIF,
        fontWeight: 600,
        fontSize: 52,
        lineHeight: 1.35,
        letterSpacing: '0.02em',
        pointerEvents: 'none',
      }}
    >
      <div
        style={{
          display: 'inline-block',
          background: 'rgba(6, 8, 16, 0.72)',
          padding: '16px 36px',
          borderRadius: 24,
          border: '1px solid rgba(212, 175, 55, 0.25)',
          boxShadow: '0 12px 40px rgba(0, 0, 0, 0.8)',
          backdropFilter: 'blur(8px)',
        }}
      >
        {satirdakiler.map((k, i) => {
          const isCurrent = k === aktif;
          const isPast = t >= k.s - 0.05;
          return (
            <span
              key={i}
              style={{
                opacity: isPast ? 1 : 0.22,
                color: isCurrent ? '#FADB7F' : '#F8FAFC',
                textShadow: isCurrent
                  ? '0 0 20px rgba(243, 208, 129, 0.8), 0 2px 8px rgba(0,0,0,0.9)'
                  : '0 2px 6px rgba(0,0,0,0.8)',
              }}
            >
              {k.w}{' '}
            </span>
          );
        })}
      </div>
    </div>
  );
};

// Altın Tozları Katmanı
const StardustLayer: React.FC<{ t: number; count?: number }> = ({ t, count = 28 }) => {
  const particles = React.useMemo(() => {
    return Array.from({ length: count }, (_, i) => ({
      x: ((i * 137.5) % 1000) + 40,
      yBase: ((i * 97.3) % 1800) + 60,
      r: (i % 3) * 1.2 + 1.2,
      speed: ((i % 5) + 3) * 12,
      phase: i * 1.7,
      glow: (i % 2) === 0,
    }));
  }, [count]);

  return (
    <g>
      {particles.map((p, i) => {
        const y = (p.yBase - t * p.speed) % 1920;
        const currentY = y < 0 ? y + 1920 : y;
        const opacity = (Math.sin(t * 1.5 + p.phase) * 0.5 + 0.5) * 0.65 + 0.15;
        return (
          <circle
            key={i}
            cx={p.x + Math.sin(t * 0.8 + p.phase) * 20}
            cy={currentY}
            r={p.r}
            fill="#F3D081"
            opacity={opacity}
            filter={p.glow ? 'url(#glow)' : undefined}
          />
        );
      })}
    </g>
  );
};

export const OlumSonMuVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;

  // Zaman Çapa Noktaları (Cümle anları)
  const tS0 = an(0, 0); // 0.00s
  const tS1 = an(1, 0); // 6.74s
  const tS2 = an(2, 0); // 11.44s
  const tS3 = an(3, 0); // 16.31s
  const tS4 = an(4, 0); // 22.41s
  const tS5 = an(5, 0); // 25.99s
  const tS6 = an(6, 0); // 32.11s
  const tS7 = an(7, 0); // 37.94s

  // Geçiş Eğrileri (0 -> 1)
  const g01 = gir(t, tS1, 1.2); // S0 -> S1
  const g12 = gir(t, tS2, 1.0); // S1 -> S2 (Çatlama başlıyor)
  const g23 = gir(t, tS3, 1.4); // S2 -> S3 (Büyük aydınlanma/doğum)
  const g34 = gir(t, tS4, 1.2); // S3 -> S4 ("İşte ölüm de böyledir")
  const g45 = gir(t, tS5, 1.2); // S4 -> S5 (Kapı açılıyor)
  const g56 = gir(t, tS6, 1.4); // S5 -> S6 (Beden toprağa, ruh göğe)
  const g67 = gir(t, tS7, 1.5); // S6 -> S7 (Ebedi şafak & vuslat)

  // Canlı mikro nefes ve nabız (duraksamayı engeller)
  const nefes = Math.sin(t * 1.6) * 6;
  const nabiz = Math.sin(t * 2.8) * 0.04;

  // Kamera Zum & Kayma
  // S0-S1 arası hafif yakınlaşma, S3'te görkemli açılma, S5'te kapıya doğru süzülme
  const camScale = karis(
    karis(1.0, 1.18, gir(t, tS0, 5.0)),
    karis(1.18, 0.88, g23),
    g23
  ) * (1 + (g45 > 0 ? karis(0, 0.25, g45) : 0));

  const camY = karis(
    karis(0, -60, g01),
    karis(-60, 140, g23),
    g23
  ) + karis(0, -220, g56);

  // Sahnelerin Görünürlük Katmanları
  const opacRahim = (1 - g23); // Rahim dünyası S3'te kaybolur
  const opacAydinlik = Math.max(0, g23 - g34); // S3 geniş aydınlık
  const opacKapi = Math.max(0, g34 - g56); // S4 ve S5 kapı menzili
  const opacYükselis = Math.max(0, g56 - g67); // S6 ruhun yükselişi
  const opacSafak = g67; // S7 ebedi şafak

  return (
    <AbsoluteFill style={{ background: '#05070E', overflow: 'hidden' }}>
      <Audio src={staticFile('olum-son-mu/ses.mp3')} />

      <svg
        width={1080}
        height={1920}
        viewBox="0 0 1080 1920"
        style={{ position: 'absolute', top: 0, left: 0 }}
      >
        <defs>
          {/* Parıltı ve Glow Filtreleri */}
          <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur1" />
            <feGaussianBlur in="SourceGraphic" stdDeviation="24" result="blur2" />
            <feMerge>
              <feMergeNode in="blur2" />
              <feMergeNode in="blur1" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Kozmik Zemin Gradyanları */}
          <radialGradient id="bgGlow" cx="50%" cy="46%" r="65%">
            <stop offset="0%" stopColor="#1B1425" stopOpacity="0.8" />
            <stop offset="60%" stopColor="#080A14" stopOpacity="0.95" />
            <stop offset="100%" stopColor="#030408" stopOpacity="1" />
          </radialGradient>

          <radialGradient id="rahimGlow" cx="50%" cy="48%" r="50%">
            <stop offset="0%" stopColor="#4A2511" stopOpacity="0.85" />
            <stop offset="50%" stopColor="#251208" stopOpacity="0.7" />
            <stop offset="90%" stopColor="#120703" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#05070E" stopOpacity="0" />
          </radialGradient>

          <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FFF2B2" />
            <stop offset="40%" stopColor="#D4AF37" />
            <stop offset="100%" stopColor="#997A15" />
          </linearGradient>

          <linearGradient id="portalGlow" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#FFF7D6" />
            <stop offset="50%" stopColor="#E5B942" />
            <stop offset="100%" stopColor="#6C480E" />
          </linearGradient>
        </defs>

        {/* 1. Arka Plan Derinliği */}
        <rect width={1080} height={1920} fill="url(#bgGlow)" />

        {/* 2. Kamera Dönüşüm Grubu */}
        <g
          transform={`translate(540, 960) scale(${camScale}) translate(-540, ${-960 + camY})`}
        >
          {/* Stardust Parçacıkları */}
          <StardustLayer t={t} count={35} />

          {/* ========================================================= */}
          {/* BÖLÜM 1: RAHİM VE BEBEK DÜNYASI (S0, S1, S2)              */}
          {/* ========================================================= */}
          {opacRahim > 0.01 && (
            <g opacity={opacRahim}>
              {/* Rahim Işıması */}
              <circle
                cx={540}
                cy={880}
                r={karis(380, 310, g01) * (1 + nabiz)}
                fill="url(#rahimGlow)"
              />

              {/* Dış Membran Halkaları */}
              <circle
                cx={540}
                cy={880}
                r={karis(360, 290, g01)}
                fill="none"
                stroke="rgba(212, 175, 55, 0.45)"
                strokeWidth={5}
                strokeDasharray="14 10"
                transform={`rotate(${t * 3}, 540, 880)`}
                filter="url(#softGlow)"
              />

              <circle
                cx={540}
                cy={880}
                r={karis(320, 260, g01)}
                fill="none"
                stroke="rgba(243, 208, 129, 0.25)"
                strokeWidth={3}
              />

              {/* Daralan Duvar Vurgusu (S1) */}
              {g01 > 0.05 && (
                <text
                  x={540}
                  y={570}
                  textAnchor="middle"
                  fill="rgba(212, 175, 55, 0.75)"
                  fontFamily={SERIF}
                  fontSize={28}
                  letterSpacing="0.2em"
                  opacity={karis(0, 0.9, g01) * (1 - g12)}
                >
                  DAR VE SINIRLI ÂLEM
                </text>
              )}

              {/* Cenin / Yüzsüz Minimalist Bebek Silüeti */}
              <g
                transform={`translate(540, ${880 + nefes}) scale(${karis(1, 0.9, g01)}) translate(-540, -880)`}
              >
                {/* Göbek Bağı / Nur Çizgisi */}
                <path
                  d={`M 540 890 C 470 940, 420 860, ${karis(360, 290, g01)} 880`}
                  fill="none"
                  stroke="rgba(212, 175, 55, 0.5)"
                  strokeWidth={4}
                  strokeLinecap="round"
                />

                {/* Baş Silüeti */}
                <ellipse
                  cx={540}
                  cy={810}
                  rx={46}
                  ry={52}
                  fill="url(#goldGradient)"
                  filter="url(#softGlow)"
                />

                {/* Bükülmüş Sırt ve Gövde Yayı */}
                <path
                  d="M 540 858 C 470 880, 460 980, 540 1000 C 580 1010, 590 950, 540 920"
                  fill="none"
                  stroke="url(#goldGradient)"
                  strokeWidth={22}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  filter="url(#softGlow)"
                />

                {/* Göğse Çekilmiş Dizler ve Ayaklar */}
                <path
                  d="M 530 990 C 560 970, 570 920, 540 900"
                  fill="none"
                  stroke="url(#goldGradient)"
                  strokeWidth={16}
                  strokeLinecap="round"
                />

                {/* Başa Yaklaşan Eller */}
                <circle cx={510} cy={860} r={10} fill="#FFF2B2" />
              </g>

              {/* S2: Çatlaklar ve Işık Sızıntıları (Doğum Anı) */}
              {g12 > 0.02 && (
                <g opacity={g12} filter="url(#glow)">
                  <path
                    d="M 540 520 L 530 650 L 555 740 L 535 830 L 560 950 L 535 1080 L 540 1240"
                    fill="none"
                    stroke="#FFFDF0"
                    strokeWidth={karis(3, 20, g12)}
                    strokeLinecap="round"
                  />
                  <path
                    d="M 530 650 L 440 690 M 555 740 L 630 760 M 535 830 L 420 860 M 560 950 L 660 970"
                    fill="none"
                    stroke="#F3D081"
                    strokeWidth={karis(2, 10, g12)}
                    strokeLinecap="round"
                  />
                  {/* Dışarıdan vuran nur huzmesi */}
                  <polygon
                    points="540,520 780,1350 300,1350"
                    fill="url(#goldGradient)"
                    opacity={karis(0, 0.45, g12)}
                  />
                </g>
              )}
            </g>
          )}

          {/* ========================================================= */}
          {/* BÖLÜM 2: DIŞ ÂLEME DOĞUŞ & GENİŞLEME (S3)                 */}
          {/* ========================================================= */}
          {opacAydinlik > 0.01 && (
            <g opacity={opacAydinlik}>
              {/* Devasa Göksel Nur Patlaması */}
              <circle
                cx={540}
                cy={880}
                r={karis(200, 750, g23)}
                fill="url(#bgGlow)"
                stroke="url(#goldGradient)"
                strokeWidth={6}
                opacity={0.8}
                filter="url(#glow)"
              />

              {/* Göğe Doğru Yükselen Nur Hüzmeleri */}
              {Array.from({ length: 12 }, (_, i) => {
                const angle = (i * 30 * Math.PI) / 180;
                const len = karis(300, 700, g23);
                return (
                  <line
                    key={i}
                    x1={540}
                    y1={880}
                    x2={540 + Math.cos(angle) * len}
                    y2={880 + Math.sin(angle) * len}
                    stroke="rgba(243, 208, 129, 0.4)"
                    strokeWidth={4}
                    strokeDasharray="16 12"
                  />
                );
              })}

              {/* Geniş Dünyada Ayakta Duran Kul Silüeti */}
              <g transform="translate(540, 980)">
                <ellipse cx={0} cy={-120} rx={22} ry={26} fill="url(#goldGradient)" />
                <path
                  d="M 0 -94 L 0 -10 M -45 -55 L 45 -55 M -20 80 L 0 -10 L 20 80"
                  fill="none"
                  stroke="url(#goldGradient)"
                  strokeWidth={14}
                  strokeLinecap="round"
                />
              </g>

              <text
                x={540}
                y={620}
                textAnchor="middle"
                fill="#FFF2B2"
                fontFamily={SERIF}
                fontSize={36}
                letterSpacing="0.25em"
                filter="url(#softGlow)"
              >
                GERÇEK HAYAT YENİ BAŞLADI
              </text>
            </g>
          )}

          {/* ========================================================= */}
          {/* BÖLÜM 3: İKİ ÂLEM VE SONSUZLUK KAPISI (S4, S5)             */}
          {/* ========================================================= */}
          {opacKapi > 0.01 && (
            <g opacity={opacKapi}>
              {/* Antik Kemerli Giriş Kapısı */}
              <g transform="translate(540, 840)">
                {/* Kapı Arkasındaki Galaksi Işığı */}
                <rect
                  x={-160}
                  y={-280}
                  width={320}
                  height={560}
                  rx={160}
                  fill="url(#portalGlow)"
                  filter="url(#glow)"
                  opacity={karis(0.3, 1, g45)}
                />

                {/* Kemer Süslemesi */}
                <path
                  d="M -180 280 L -180 -120 A 180 180 0 0 1 180 -120 L 180 280"
                  fill="none"
                  stroke="#D4AF37"
                  strokeWidth={16}
                  filter="url(#softGlow)"
                />

                {/* Açılan Sol Kanat */}
                <path
                  d={`M -180 280 L -180 -120 A 180 180 0 0 1 0 -180 L ${karis(0, -140, g45)} 280 Z`}
                  fill="#1B1425"
                  stroke="#D4AF37"
                  strokeWidth={6}
                />

                {/* Açılan Sağ Kanat */}
                <path
                  d={`M 180 280 L 180 -120 A 180 180 0 0 0 0 -180 L ${karis(0, 140, g45)} 280 Z`}
                  fill="#1B1425"
                  stroke="#D4AF37"
                  strokeWidth={6}
                />

                {/* Kapı Eşiğindeki Yolcu Silüeti */}
                <g transform={`translate(0, ${180 + nefes})`}>
                  <circle cx={0} cy={-70} r={18} fill="url(#goldGradient)" />
                  <path
                    d="M 0 -52 L 0 20 M -30 -20 L 30 -20 M -15 90 L 0 20 L 15 90"
                    fill="none"
                    stroke="url(#goldGradient)"
                    strokeWidth={10}
                    strokeLinecap="round"
                  />
                </g>
              </g>

              {/* Başlık Vurgusu */}
              <text
                x={540}
                y={460}
                textAnchor="middle"
                fill="#FFF2B2"
                fontFamily={SERIF}
                fontSize={32}
                letterSpacing="0.25em"
              >
                SON DEĞİL; SONSUZLUK KAPISI
              </text>
            </g>
          )}

          {/* ========================================================= */}
          {/* BÖLÜM 4: BEDEN TOPRAĞA, RUH ASIL VATANINA (S6)           */}
          {/* ========================================================= */}
          {opacYükselis > 0.01 && (
            <g opacity={opacYükselis}>
              {/* Alt Bölge: Toprak Rahmi */}
              <rect x={0} y={1300} width={1080} height={620} fill="#140D07" />
              <line x1={0} y1={1300} x2={1080} y2={1300} stroke="#D4AF37" strokeWidth={4} />

              {/* Toprağa Bırakılan Tohum (Beden) */}
              <g transform={`translate(540, ${karis(1250, 1550, g56)})`}>
                <ellipse cx={0} cy={0} rx={22} ry={12} fill="#A67C2E" opacity={0.8} />
                <circle cx={0} cy={0} r={8} fill="#D4AF37" filter="url(#softGlow)" />
                <text
                  x={0}
                  y={40}
                  textAnchor="middle"
                  fill="rgba(212, 175, 55, 0.7)"
                  fontFamily={SERIF}
                  fontSize={22}
                >
                  BEDEN TOPRAĞA
                </text>
              </g>

              {/* Göğe Yükselen Nurdan Ruh */}
              <g transform={`translate(540, ${karis(1100, 480, g56)})`}>
                <circle cx={0} cy={0} r={32} fill="#FFF9DF" filter="url(#glow)" />
                <circle cx={0} cy={0} r={55} fill="none" stroke="#F3D081" strokeWidth={3} strokeDasharray="8 6" />
                <path
                  d="M 0 45 L 0 160"
                  stroke="url(#portalGlow)"
                  strokeWidth={6}
                  strokeLinecap="round"
                  strokeDasharray="12 10"
                />
                <text
                  x={0}
                  y={-50}
                  textAnchor="middle"
                  fill="#FFFDF0"
                  fontFamily={SERIF}
                  fontSize={26}
                  letterSpacing="0.15em"
                >
                  RUH ASIL VATANINA UYANIR
                </text>
              </g>
            </g>
          )}

          {/* ========================================================= */}
          {/* BÖLÜM 5: EBEDİ ŞAFAK VE VUSLAT (S7 - Kapanış)              */}
          {/* ========================================================= */}
          {opacSafak > 0.01 && (
            <g opacity={opacSafak}>
              {/* Ufukta Doğan Altın Şafak Nur Hüzmesi */}
              <circle
                cx={540}
                cy={1050}
                r={360}
                fill="url(#portalGlow)"
                filter="url(#glow)"
                opacity={0.65}
              />

              {/* Hilal & Yıldız Sembolizmi */}
              <path
                d="M 540 680 A 90 90 0 1 1 540 860 A 75 75 0 1 0 540 680 Z"
                fill="url(#goldGradient)"
                filter="url(#softGlow)"
                transform="rotate(-25, 540, 770)"
              />

              {/* Kapanış Mührü */}
              <text
                x={540}
                y={1180}
                textAnchor="middle"
                fill="#FFFDF0"
                fontFamily={SERIF}
                fontWeight={700}
                fontSize={46}
                letterSpacing="0.12em"
                filter="url(#glow)"
              >
                ÖLÜM BİR SON DEĞİL;
              </text>
              <text
                x={540}
                y={1260}
                textAnchor="middle"
                fill="#F3D081"
                fontFamily={SERIF}
                fontWeight={600}
                fontSize={56}
                letterSpacing="0.18em"
                filter="url(#glow)"
              >
                VUSLATTIR
              </text>
            </g>
          )}
        </g>
      </svg>

      {/* Kinetik Altyazı */}
      <Altyazi t={t} />
    </AbsoluteFill>
  );
};

export const sure = Math.ceil((K[K.length - 1].e + 2.4) * FPS);

export const Root: React.FC = () => (
  <Composition
    id="OlumSonMu"
    component={OlumSonMuVideo}
    durationInFrames={sure}
    fps={FPS}
    width={1080}
    height={1920}
  />
);
