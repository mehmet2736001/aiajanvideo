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
import veri from '../../public/hud-112/kelimeler.json';

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
        left: 60,
        right: 60,
        bottom: 240,
        textAlign: 'center',
        fontFamily: "'Cinzel', 'Georgia', 'Playfair Display', serif",
        fontWeight: 600,
        fontSize: 48,
        lineHeight: 1.4,
        letterSpacing: '0.02em',
        pointerEvents: 'none',
      }}
    >
      <div
        style={{
          display: 'inline-block',
          background: 'rgba(6, 10, 20, 0.88)',
          border: '1px solid rgba(212, 175, 55, 0.35)',
          padding: '16px 36px',
          borderRadius: 24,
          boxShadow: '0 12px 40px rgba(0,0,0,0.85), inset 0 0 20px rgba(212,175,55,0.1)',
          backdropFilter: 'blur(12px)',
        }}
      >
        {satirdakiler.map((kel, i) => {
          const suAn = t >= kel.s && t <= kel.e + 0.25;
          const gecti = t > kel.e + 0.25;
          return (
            <span
              key={i}
              style={{
                color: suAn ? '#FFDF73' : gecti ? '#FFFFFFDD' : '#FFFFFF66',
                textShadow: suAn
                  ? '0 0 24px rgba(255, 223, 115, 0.9), 0 0 45px rgba(212, 175, 55, 0.5)'
                  : 'none',
                fontWeight: suAn ? 800 : 500,
                transform: suAn ? 'scale(1.08)' : 'scale(1)',
                display: 'inline-block',
                margin: '4px 10px',
                transition: 'all 0.12s ease',
              }}
            >
              {kel.w}
            </span>
          );
        })}
      </div>
    </div>
  );
};

export const Hud112Video: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;

  // Cümle Başlangıç Zamanları
  const t0 = an(0, 0); // 0.00s  - Saçlarına ak düşüren sır
  const t1 = an(1, 0); // ~5.6s  - Sahabe sordu
  const t2 = an(2, 0); // ~11.3s - Beni Hûd sûresi kocattı
  const t3 = an(3, 0); // ~16.8s - Dağları ezen emir
  const t4 = an(4, 0); // ~22.7s - Festekim kemâ umirt
  const t5 = an(5, 0); // ~28.9s - Gönlünce değil
  const t6 = an(6, 0); // ~34.1s - İstikamet terazisi
  const t7 = an(7, 0); // ~39.4s - Bir ömrü hizalamak
  const t8 = an(8, 0); // ~45.1s - İlahi ağırlık
  const t9 = an(9, 0); // ~50.6s - Peki senin istikametin?

  // Yumuşak Geçiş Opasiteleri
  const u0 = gir(t, t0, 0.8);
  const u1 = gir(t, t1, 0.8);
  const u2 = gir(t, t2, 0.8);
  const u3 = gir(t, t3, 0.8);
  const u4 = gir(t, t4, 0.8);
  const u5 = gir(t, t5, 0.8);
  const u6 = gir(t, t6, 0.8);
  const u7 = gir(t, t7, 0.8);
  const u8 = gir(t, t8, 0.8);
  const u9 = gir(t, t9, 0.8);

  const opacS0 = u0 * (1 - u1);
  const opacS1 = u1 * (1 - u2);
  const opacS2 = u2 * (1 - u4); // Hûd suresi & dağlar (S2 + S3)
  const opacS4 = u4 * (1 - u5); // Festekim kemâ umirt
  const opacS5 = u5 * (1 - u6); // İki yol / sapan yollar
  const opacS6 = u6 * (1 - u8); // Terazi & hizalama (S6 + S7)
  const opacS8 = u8 * (1 - u9); // İlahi ağırlık ve nur
  const opacS9 = u9;            // Kapanış mührü

  // Animasyon Değişkenleri
  const nabiz = Math.sin(frame * 0.08) * 0.06 + 1;
  const yavasDonus = frame * 0.15;
  const hizliDeprem = Math.sin(frame * 0.9) * 5;

  return (
    <AbsoluteFill style={{ backgroundColor: '#040711', overflow: 'hidden' }}>
      {/* 44.1kHz Stüdyo Master Sesi */}
      <Audio src={staticFile('hud-112/ses.mp3')} />

      <svg
        viewBox="0 0 1080 1920"
        style={{ width: '100%', height: '100%', position: 'absolute' }}
      >
        <defs>
          {/* Gradyanlar */}
          <radialGradient id="deepCosmos" cx="50%" cy="45%" r="65%">
            <stop offset="0%" stopColor="#0B1528" />
            <stop offset="60%" stopColor="#050B16" />
            <stop offset="100%" stopColor="#020408" />
          </radialGradient>

          <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FFF2B2" />
            <stop offset="35%" stopColor="#F5D061" />
            <stop offset="70%" stopColor="#D4AF37" />
            <stop offset="100%" stopColor="#8A6714" />
          </linearGradient>

          <linearGradient id="silverHairGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="50%" stopColor="#E2E8F0" />
            <stop offset="100%" stopColor="#94A3B8" />
          </linearGradient>

          <linearGradient id="straightLaser" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="rgba(255,242,178,0)" />
            <stop offset="15%" stopColor="#FFFDF0" />
            <stop offset="50%" stopColor="#FFDF73" />
            <stop offset="85%" stopColor="#D4AF37" />
            <stop offset="100%" stopColor="rgba(212,175,55,0)" />
          </linearGradient>

          <radialGradient id="auraGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(255, 223, 115, 0.45)" />
            <stop offset="50%" stopColor="rgba(212, 175, 55, 0.18)" />
            <stop offset="100%" stopColor="rgba(4, 7, 17, 0)" />
          </radialGradient>

          <linearGradient id="redDeviate" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#EF4444" />
            <stop offset="100%" stopColor="#7F1D1D" />
          </linearGradient>

          {/* Filtreler */}
          <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="10" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          <filter id="heavyGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="22" result="blur1" />
            <feGaussianBlur stdDeviation="12" result="blur2" />
            <feMerge>
              <feMergeNode in="blur1" />
              <feMergeNode in="blur2" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* 1. Sonsuz Kozmik Zemin */}
        <rect width={1080} height={1920} fill="url(#deepCosmos)" />

        {/* Yıldız Tozları */}
        {[...Array(36)].map((_, i) => {
          const px = (i * 97 + (frame * 0.4) * (i % 3 + 1)) % 1080;
          const py = (i * 137 + (frame * 0.25) * (i % 2 + 1)) % 1920;
          const pOpac = (Math.sin(frame * 0.05 + i) + 1) * 0.35 + 0.1;
          return (
            <circle
              key={i}
              cx={px}
              cy={py}
              r={(i % 3) * 0.9 + 1}
              fill="#F8FAFC"
              opacity={pOpac}
            />
          );
        })}

        {/* ========================================================= */}
        {/* SAHNE 0: SAÇLARINA AK DÜŞÜREN SIR                         */}
        {/* ========================================================= */}
        {opacS0 > 0.01 && (
          <g opacity={opacS0}>
            {/* Merkez Nur Aurası */}
            <circle cx={540} cy={760} r={340 * nabiz} fill="url(#auraGlow)" />

            {/* Dönen Geometrik Halka */}
            <g transform={`rotate(${yavasDonus}, 540, 760)`}>
              <circle
                cx={540}
                cy={760}
                r={260}
                fill="none"
                stroke="url(#goldGrad)"
                strokeWidth={1.5}
                strokeDasharray="8 14"
                opacity={0.4}
              />
              <circle
                cx={540}
                cy={760}
                r={210}
                fill="none"
                stroke="url(#goldGrad)"
                strokeWidth={1}
                strokeDasharray="2 10"
                opacity={0.3}
              />
            </g>

            {/* Ağaran Saç Teli (Gümüş & Altın Kıvrım) */}
            <path
              d={`M 540 420 C ${580 + Math.sin(frame * 0.08) * 20} 560, ${500 - Math.sin(frame * 0.08) * 25} 740, 540 920 C 560 1020, 520 1100, 540 1180`}
              fill="none"
              stroke="url(#silverHairGrad)"
              strokeWidth={4.5}
              filter="url(#heavyGlow)"
            />

            {/* İkincil Nur Hüzmesi */}
            <path
              d={`M 536 440 C ${560 - Math.sin(frame * 0.07) * 15} 580, ${520 + Math.sin(frame * 0.07) * 20} 720, 538 900`}
              fill="none"
              stroke="url(#goldGrad)"
              strokeWidth={2}
              opacity={0.7}
              filter="url(#glow)"
            />

            {/* Başlık Metni */}
            <text
              x={540}
              y={1340}
              textAnchor="middle"
              fill="#E2E8F0"
              fontFamily="'Cinzel', 'Playfair Display', serif"
              fontWeight={700}
              fontSize={42}
              letterSpacing="0.12em"
              filter="url(#glow)"
            >
              KUTLU BAŞIN SIRRI
            </text>
            <text
              x={540}
              y={1400}
              textAnchor="middle"
              fill="#D4AF37"
              fontFamily="'Cinzel', 'Playfair Display', serif"
              fontWeight={600}
              fontSize={28}
              letterSpacing="0.25em"
              opacity={0.9}
            >
              SAÇLARA AK DÜŞÜREN AĞIRLIK
            </text>
          </g>
        )}

        {/* ========================================================= */}
        {/* SAHNE 1: SAHABENİN SORUSU & MESCİD MECLİSİ                */}
        {/* ========================================================= */}
        {opacS1 > 0.01 && (
          <g opacity={opacS1}>
            {/* Medine Kemeri Silüeti */}
            <path
              d="M 280 1100 L 280 680 C 280 480, 540 380, 540 380 C 540 380, 800 480, 800 680 L 800 1100"
              fill="none"
              stroke="url(#goldGrad)"
              strokeWidth={3}
              opacity={0.5}
              filter="url(#glow)"
            />

            {/* İç Kemer */}
            <path
              d="M 340 1100 L 340 710 C 340 540, 540 450, 540 450 C 540 450, 740 540, 740 710 L 740 1100"
              fill="none"
              stroke="url(#goldGrad)"
              strokeWidth={1.5}
              strokeDasharray="6 8"
              opacity={0.35}
            />

            {/* Kemer Tepesindeki Hilal */}
            <path
              d="M 540 320 A 32 32 0 1 1 540 384 A 26 26 0 1 0 540 320 Z"
              fill="url(#goldGrad)"
              filter="url(#glow)"
              transform="rotate(-20, 540, 352)"
            />

            {/* Ashabın Sorusu Simgesi (Işıltılı Halka & Soru Noktası) */}
            <circle
              cx={540}
              cy={720}
              r={110 * nabiz}
              fill="none"
              stroke="url(#goldGrad)"
              strokeWidth={3}
              filter="url(#glow)"
            />
            <circle cx={540} cy={720} r={14} fill="#FFFDF0" filter="url(#heavyGlow)" />

            <text
              x={540}
              y={930}
              textAnchor="middle"
              fill="#FFFDF0"
              fontFamily="'Cinzel', 'Playfair Display', serif"
              fontWeight={700}
              fontSize={44}
              letterSpacing="0.08em"
              filter="url(#glow)"
            >
              "SENİ NE İHTİYARLATTI?"
            </text>
            <text
              x={540}
              y={990}
              textAnchor="middle"
              fill="#94A3B8"
              fontFamily="'Cinzel', 'Playfair Display', serif"
              fontWeight={500}
              fontSize={26}
              letterSpacing="0.18em"
            >
              ASHABIN DERİN HAYRETİ
            </text>
          </g>
        )}

        {/* ========================================================= */}
        {/* SAHNE 2 & 3: BENİ HÛD SÛRESİ KOCATTI & SARSILAN DAĞLAR    */}
        {/* ========================================================= */}
        {opacS2 > 0.01 && (
          <g opacity={opacS2}>
            {/* Sarsılan Dağ Silüetleri (Deprem Titreşimi) */}
            <g transform={`translate(${hizliDeprem}, 0)`}>
              {/* Arka Dağ Sırası */}
              <polygon
                points="0,1320 220,980 440,1180 680,920 900,1120 1080,960 1080,1400 0,1400"
                fill="#0F172A"
                opacity={0.65}
              />
              {/* Ön Dağ Sırası */}
              <polygon
                points="0,1400 280,1050 540,1260 820,1020 1080,1280 1080,1600 0,1600"
                fill="#090E1A"
              />
              {/* Dağ Üstündeki Çatlak Işıkları */}
              <path
                d="M 680 920 L 700 980 L 670 1040 L 710 1100"
                fill="none"
                stroke="url(#goldGrad)"
                strokeWidth={2}
                filter="url(#glow)"
                opacity={0.8}
              />
            </g>

            {/* Gökten İnen Mukaddes Levha */}
            <g transform="translate(160, 420)">
              {/* Levha Zemin */}
              <rect
                x={0}
                y={0}
                width={760}
                height={400}
                rx={28}
                fill="rgba(11, 21, 40, 0.94)"
                stroke="url(#goldGrad)"
                strokeWidth={3}
                filter="url(#glow)"
              />
              <rect
                x={14}
                y={14}
                width={732}
                height={372}
                rx={20}
                fill="none"
                stroke="url(#goldGrad)"
                strokeWidth={1.5}
                strokeDasharray="8 10"
                opacity={0.4}
              />

              {/* Arapça Başlık: Sûretü Hûd */}
              <text
                x={380}
                y={150}
                textAnchor="middle"
                fill="#FFFDF0"
                fontFamily="'Traditional Arabic', 'Amiri', 'Georgia', serif"
                fontWeight={700}
                fontSize={86}
                filter="url(#heavyGlow)"
              >
                سُورَةُ هُود
              </text>
              <text
                x={380}
                y={235}
                textAnchor="middle"
                fill="#FFDF73"
                fontFamily="'Cinzel', 'Playfair Display', serif"
                fontWeight={800}
                fontSize={32}
                letterSpacing="0.14em"
                filter="url(#glow)"
              >
                BENİ HÛD SÛRESİ KOCATTI
              </text>
              <text
                x={380}
                y={295}
                textAnchor="middle"
                fill="#CBD5E1"
                fontFamily="'Cinzel', 'Playfair Display', serif"
                fontWeight={600}
                fontSize={24}
                letterSpacing="0.18em"
              >
                DAĞLARI EZEN İLAHİ EMİR
              </text>
            </g>

            {/* Levhadan Dağlara Vuran Yıldırım Nur Hattı */}
            <rect
              x={538}
              y={800}
              width={4}
              height={350}
              rx={2}
              fill="url(#goldGrad)"
              filter="url(#heavyGlow)"
            />
          </g>
        )}

        {/* ========================================================= */}
        {/* SAHNE 4: FESTEKİM KEMÂ UMİRT (İLAHİ FERMAN & NUR KILICI)  */}
        {/* ========================================================= */}
        {opacS4 > 0.01 && (
          <g opacity={opacS4}>
            {/* Ortadan İnen Dümdüz Altın Lazer / Sırat-ı Müstakim */}
            <rect
              x={534}
              y={0}
              width={12}
              height={1920}
              fill="url(#straightLaser)"
              filter="url(#heavyGlow)"
            />
            <rect
              x={538}
              y={0}
              width={4}
              height={1920}
              fill="#FFFFFF"
              filter="url(#glow)"
            />

            {/* Hat Üzerinde Dönen Hizalama Çemberleri */}
            {[500, 780, 1060].map((cy, idx) => (
              <g key={idx} transform={`rotate(${frame * (idx % 2 === 0 ? 0.3 : -0.3)}, 540, ${cy})`}>
                <circle
                  cx={540}
                  cy={cy}
                  r={120 + idx * 25}
                  fill="none"
                  stroke="url(#goldGrad)"
                  strokeWidth={1.5}
                  strokeDasharray="12 16"
                  opacity={0.65}
                />
                <circle
                  cx={540 + (120 + idx * 25)}
                  cy={cy}
                  r={6}
                  fill="#FFFDF0"
                  filter="url(#glow)"
                />
              </g>
            ))}

            {/* Arapça Kaligrafi Metni: FESTEKİM KEMÂ UMİRT */}
            <g transform="translate(0, 520)">
              <text
                x={540}
                y={0}
                textAnchor="middle"
                fill="#FFFDF0"
                fontFamily="'Traditional Arabic', 'Amiri', 'Georgia', serif"
                fontWeight={700}
                fontSize={96}
                filter="url(#heavyGlow)"
              >
                فَاسْتَقِمْ كَمَا أُمِرْتَ
              </text>
              <text
                x={540}
                y={80}
                textAnchor="middle"
                fill="#FFDF73"
                fontFamily="'Cinzel', 'Playfair Display', serif"
                fontWeight={800}
                fontSize={38}
                letterSpacing="0.14em"
                filter="url(#glow)"
              >
                "EMROLUNDUĞUN GİBİ DOSDOĞRU OL!"
              </text>
              <text
                x={540}
                y={130}
                textAnchor="middle"
                fill="#CBD5E1"
                fontFamily="'Cinzel', 'Playfair Display', serif"
                fontWeight={600}
                fontSize={24}
                letterSpacing="0.25em"
              >
                [HÛD SÛRESİ, 112]
              </text>
            </g>
          </g>
        )}

        {/* ========================================================= */}
        {/* SAHNE 5: GÖNLÜNCE DEĞİL, EMROLUNDUĞUN GİBİ (ZITLIK)        */}
        {/* ========================================================= */}
        {opacS5 > 0.01 && (
          <g opacity={opacS5}>
            {/* Ortadaki Kusursuz Doğru */}
            <line
              x1={540}
              y1={250}
              x2={540}
              y2={1350}
              stroke="url(#goldGrad)"
              strokeWidth={5}
              filter="url(#heavyGlow)"
            />

            {/* Sola Sapan Eğri (Gönlünce Yaşamak / Nefis) */}
            <path
              d="M 540 650 Q 320 850, 180 1200"
              fill="none"
              stroke="url(#redDeviate)"
              strokeWidth={3}
              strokeDasharray="8 6"
              opacity={0.7}
            />
            {/* Sağa Sapan Eğri (Kolayına Geldiği Gibi / İhmal) */}
            <path
              d="M 540 650 Q 760 850, 900 1200"
              fill="none"
              stroke="url(#redDeviate)"
              strokeWidth={3}
              strokeDasharray="8 6"
              opacity={0.7}
            />

            {/* Sol Uyarı Etiketi */}
            <g transform="translate(140, 1020)">
              <text
                x={0}
                y={0}
                fill="#F87171"
                fontFamily="'Cinzel', 'Georgia', serif"
                fontWeight={600}
                fontSize={28}
                letterSpacing="0.08em"
              >
                ✕ GÖNLÜNCE DEĞİL
              </text>
            </g>

            {/* Sağ Uyarı Etiketi */}
            <g transform="translate(720, 1020)">
              <text
                x={0}
                y={0}
                fill="#F87171"
                fontFamily="'Cinzel', 'Georgia', serif"
                fontWeight={600}
                fontSize={28}
                letterSpacing="0.08em"
              >
                ✕ KOLAYINA GÖRE DEĞİL
              </text>
            </g>

            {/* Merkez Vurgusu */}
            <circle cx={540} cy={650} r={28} fill="#FFFDF0" filter="url(#heavyGlow)" />
            <text
              x={540}
              y={580}
              textAnchor="middle"
              fill="#FFDF73"
              fontFamily="'Cinzel', 'Playfair Display', serif"
              fontWeight={800}
              fontSize={40}
              letterSpacing="0.1em"
              filter="url(#glow)"
            >
              HAKK'IN EMRİNE HİZALAN
            </text>
          </g>
        )}

        {/* ========================================================= */}
        {/* SAHNE 6: İSTİKAMET VE ADALET TERAZİSİ (MİZAN)              */}
        {/* ========================================================= */}
        {opacS6 > 0.01 && (
          <g opacity={opacS6}>
            {/* Terazi Ana Gövdesi (Y=720) */}
            <g transform="translate(540, 720)">
              {/* Dikey Direk */}
              <rect
                x={-3}
                y={-180}
                width={6}
                height={500}
                rx={3}
                fill="url(#goldGrad)"
                filter="url(#glow)"
              />
              <circle cx={0} cy={-180} r={16} fill="#FFFDF0" filter="url(#glow)" />
              <circle cx={0} cy={320} r={24} fill="url(#goldGrad)" />

              {/* Yatay Denge Kolu (Kusursuz Yatay Denge 0.00 Derece) */}
              <rect
                x={-300}
                y={-103}
                width={600}
                height={6}
                rx={3}
                fill="url(#goldGrad)"
                filter="url(#glow)"
              />

              {/* Sol Kefe Zincirleri ve Kefe */}
              <line x1={-300} y1={-100} x2={-370} y2={60} stroke="#D4AF37" strokeWidth={1.5} opacity={0.7} />
              <line x1={-300} y1={-100} x2={-230} y2={60} stroke="#D4AF37" strokeWidth={1.5} opacity={0.7} />
              <path
                d="M -400 60 Q -300 120, -200 60 Z"
                fill="url(#goldGrad)"
                opacity={0.85}
                filter="url(#glow)"
              />

              {/* Sağ Kefe Zincirleri ve Kefe */}
              <line x1={300} y1={-100} x2={230} y2={60} stroke="#D4AF37" strokeWidth={1.5} opacity={0.7} />
              <line x1={300} y1={-100} x2={370} y2={60} stroke="#D4AF37" strokeWidth={1.5} opacity={0.7} />
              <path
                d="M 200 60 Q 300 120, 400 60 Z"
                fill="url(#goldGrad)"
                opacity={0.85}
                filter="url(#glow)"
              />

              {/* Merkezde 8 Köşeli Selçuklu Yıldızı */}
              <g transform={`rotate(${yavasDonus * 0.8}, 0, -100)`}>
                <rect x={-28} y={-28} width={56} height={56} fill="url(#goldGrad)" />
                <rect x={-28} y={-28} width={56} height={56} fill="url(#goldGrad)" transform="rotate(45)" />
              </g>
              <circle cx={0} cy={-100} r={12} fill="#FFFDF0" filter="url(#heavyGlow)" />
            </g>

            {/* Terazi Açıklama Metni */}
            <text
              x={540}
              y={1180}
              textAnchor="middle"
              fill="#FFFDF0"
              fontFamily="'Cinzel', 'Playfair Display', serif"
              fontWeight={700}
              fontSize={44}
              letterSpacing="0.08em"
              filter="url(#glow)"
            >
              KILDAN İNCE, KILIÇTAN KESKİN
            </text>
            <text
              x={540}
              y={1240}
              textAnchor="middle"
              fill="#D4AF37"
              fontFamily="'Cinzel', 'Playfair Display', serif"
              fontWeight={600}
              fontSize={28}
              letterSpacing="0.22em"
            >
              ZERRECE SAPMAYAN İSTİKAMET TERAZİSİ
            </text>
          </g>
        )}

        {/* ========================================================= */}
        {/* SAHNE 8: İLAHİ AĞIRLIK VE NURLU GÖKYÜZÜ                   */}
        {/* ========================================================= */}
        {opacS8 > 0.01 && (
          <g opacity={opacS8}>
            {/* Tepeden İnen Sonsuz Nur Işınları */}
            {[...Array(16)].map((_, i) => {
              const aci = (i * 22.5) * (Math.PI / 180);
              const lx = 540 + Math.cos(aci) * 700;
              const ly = 550 + Math.sin(aci) * 700;
              return (
                <line
                  key={i}
                  x1={540}
                  y1={550}
                  x2={lx}
                  y2={ly}
                  stroke="url(#goldGrad)"
                  strokeWidth={2}
                  opacity={0.35 * nabiz}
                  filter="url(#glow)"
                />
              );
            })}

            {/* Merkezdeki Büyük Nur Küresi */}
            <circle cx={540} cy={550} r={220 * nabiz} fill="url(#auraGlow)" />
            <circle cx={540} cy={550} r={130} fill="#FFFDF0" filter="url(#heavyGlow)" />

            <text
              x={540}
              y={880}
              textAnchor="middle"
              fill="#FFFDF0"
              fontFamily="'Cinzel', 'Playfair Display', serif"
              fontWeight={800}
              fontSize={52}
              letterSpacing="0.12em"
              filter="url(#heavyGlow)"
            >
              İLAHİ AĞIRLIK
            </text>
            <text
              x={540}
              y={945}
              textAnchor="middle"
              fill="#D4AF37"
              fontFamily="'Cinzel', 'Playfair Display', serif"
              fontWeight={600}
              fontSize={30}
              letterSpacing="0.25em"
            >
              BİR PEYGAMBERİN SAÇLARINI AĞARTTI
            </text>
          </g>
        )}

        {/* ========================================================= */}
        {/* SAHNE 9: KAPANIŞ MÜHRÜ VE TEFEKKÜR SORUSU                 */}
        {/* ========================================================= */}
        {opacS9 > 0.01 && (
          <g opacity={opacS9}>
            {/* Göğe Doğru Yönelen Altın Pusula / Mihrap İbresi */}
            <g transform="translate(540, 680)">
              {/* Dış Pusula Kadranı */}
              <circle
                cx={0}
                cy={0}
                r={240}
                fill="none"
                stroke="url(#goldGrad)"
                strokeWidth={2}
                filter="url(#glow)"
              />
              <circle
                cx={0}
                cy={0}
                r={210}
                fill="none"
                stroke="url(#goldGrad)"
                strokeWidth={1}
                strokeDasharray="4 8"
                opacity={0.5}
              />

              {/* Pusula İbresi (Tam 12 Yönü - Göğe Doğru Kilitli) */}
              <polygon
                points="0,-190 28,-30 0,0 -28,-30"
                fill="url(#goldGrad)"
                filter="url(#heavyGlow)"
              />
              <polygon
                points="0,150 20,20 0,0 -20,20"
                fill="#475569"
                opacity={0.6}
              />
              <circle cx={0} cy={0} r={18} fill="#FFFDF0" filter="url(#glow)" />
            </g>

            {/* Nihai Tefekkür Mührü */}
            <text
              x={540}
              y={1080}
              textAnchor="middle"
              fill="#E2E8F0"
              fontFamily="'Cinzel', 'Playfair Display', serif"
              fontWeight={700}
              fontSize={40}
              letterSpacing="0.1em"
              filter="url(#glow)"
            >
              PEKİ SENİN İSTİKAMETİN
            </text>
            <text
              x={540}
              y={1150}
              textAnchor="middle"
              fill="#FFDF73"
              fontFamily="'Cinzel', 'Playfair Display', serif"
              fontWeight={800}
              fontSize={54}
              letterSpacing="0.12em"
              filter="url(#heavyGlow)"
            >
              NEREYE BAKIYOR?
            </text>

            <line
              x1={340}
              y1={1200}
              x2={740}
              y2={1200}
              stroke="url(#goldGrad)"
              strokeWidth={2}
              opacity={0.7}
            />

            <text
              x={540}
              y={1270}
              textAnchor="middle"
              fill="#D4AF37"
              fontFamily="'Traditional Arabic', 'Amiri', serif"
              fontWeight={700}
              fontSize={46}
              filter="url(#glow)"
            >
              فَاسْتَقِمْ كَمَا أُمِرْتَ
            </text>
            <text
              x={540}
              y={1325}
              textAnchor="middle"
              fill="#94A3B8"
              fontFamily="'Cinzel', 'Playfair Display', serif"
              fontWeight={600}
              fontSize={24}
              letterSpacing="0.25em"
            >
              HÛD SÛRESİ, 112
            </text>
          </g>
        )}
      </svg>

      {/* Kinetik Canlı Altyazı */}
      <Altyazi t={t} />
    </AbsoluteFill>
  );
};

// Toplam Süre: Ses dosyasının bitişi + 2 saniye kapanış payı
const sonKelime = K[K.length - 1];
const sureKare = Math.ceil((sonKelime.e + 2.5) * FPS);

export const Root: React.FC = () => (
  <Composition
    id="Hud112"
    component={Hud112Video}
    durationInFrames={sureKare}
    fps={FPS}
    width={1080}
    height={1920}
  />
);
