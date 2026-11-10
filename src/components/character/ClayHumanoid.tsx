import React from 'react';

export type ClayPose =
  | 'waving'            // Referans görseldeki gibi: ayakta, sağ el havada el sallıyor (5 parmak açık), sol el yanda
  | 'waking_up'         // Yatakta doğrulmuş, şaşkınlıkla saate bakıyor, eller yatakta, bacaklar/ayaklar önde
  | 'reaching_curtain'  // Ayakta, sağ kol ve 5 parmaklı el perdeye uzanmış, ayaklar zemin üstünde
  | 'looking_up_street' // Ayakta, baş ve kollar göğe kalkmış, 5 parmaklı eller açık, ayaklar yerde
  | 'holding_phone'     // Ayakta, iki elinde parlayan akıllı telefon, gözler telefonda, ayaklar yerde
  | 'panic'             // Ayakta, iki el başında/şakaklarında panik içinde, ağız açık, ayaklar titriyor
  | 'macro_head'        // Yakın plan dev 3D kafa ve göz, gözbebeğinde zaman yansıması
  | 'facing_horizon'    // Arkadan/üç çeyrek ayakta, eller iki yanda açık, batıdan doğan güneşe bakıyor
  | 'shock_mouth'       // Ayakta, iki el parmaklarıyla ağzını kapatmış dehşet içinde, fal taşı gözler
  | 'kneeling'          // Diz çökmüş, dizler ve ayaklar yerde, eller dizlerde, baş öne eğik
  | 'praying_repentance'// Diz çökmüş, eller göğüste duada kenetlenmiş, yanaklardan süzülen parlayan gözyaşları
  | 'morning_relief'    // Ayakta sabah güneşinde kollar iki yana açık, yüzünde tebessüm, ayaklar yerde
  | 'secde';            // TAM HUŞU İÇİNDE SECDE: Alın seccadede, iki el seccadeye basılı (parmaklar açık), dizler ve ayaklar seccadede

interface ClayHumanoidProps {
  pose: ClayPose;
  x?: number;
  y?: number;
  scale?: number;
  time?: number;
  rimColor?: string;
  tearProgress?: number;
}

export const ClayHumanoid: React.FC<ClayHumanoidProps> = ({
  pose,
  x = 540,
  y = 1280,
  scale = 1.0,
  time = 0,
  rimColor = 'rgba(255, 255, 255, 0.45)',
  tearProgress = 0,
}) => {
  // Canlı mikro nefes ve hareket
  const breath = Math.sin(time * 2.5) * 4;
  const eyeBlink = Math.sin(time * 0.8) > 0.96 ? 0.15 : 1.0;

  return (
    <g transform={`translate(${x}, ${y}) scale(${scale})`}>
      <defs>
        {/* 3D Küre Kafa / Gövde Radial Gölgelendirme (Referans Görseldeki Mat Beyaz Vinil) */}
        <radialGradient id="clayHeadMat" cx="36%" cy="30%" r="65%">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="45%" stopColor="#F8FAFC" />
          <stop offset="78%" stopColor="#CBD5E1" />
          <stop offset="94%" stopColor="#64748B" />
          <stop offset="100%" stopColor="#334155" />
        </radialGradient>

        {/* 3D Silindirik Uzuv (Kollar, Bacaklar, Parmaklar) */}
        <linearGradient id="clayLimbMat" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#64748B" />
          <stop offset="25%" stopColor="#F8FAFC" />
          <stop offset="65%" stopColor="#E2E8F0" />
          <stop offset="100%" stopColor="#475569" />
        </linearGradient>

        {/* Bacak ve Ayak Gölgelendirmesi */}
        <linearGradient id="clayLegMat" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#475569" />
          <stop offset="30%" stopColor="#FFFFFF" />
          <stop offset="75%" stopColor="#CBD5E1" />
          <stop offset="100%" stopColor="#334155" />
        </linearGradient>

        {/* Parlak Siyah Gözler (Referans Görsel) */}
        <radialGradient id="clayEyeGloss" cx="35%" cy="30%" r="70%">
          <stop offset="0%" stopColor="#1E293B" />
          <stop offset="55%" stopColor="#0F172A" />
          <stop offset="100%" stopColor="#020617" />
        </radialGradient>

        {/* Ağız İçi ve Dil (Referans Görsel) */}
        <linearGradient id="clayMouthInterior" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0F172A" />
          <stop offset="70%" stopColor="#881337" />
          <stop offset="100%" stopColor="#FB7185" />
        </linearGradient>

        {/* Gözyaşı Parıltısı */}
        <radialGradient id="divineTear" cx="30%" cy="30%" r="70%">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="40%" stopColor="#38BDF8" />
          <stop offset="100%" stopColor="#0284C7" />
        </radialGradient>

        {/* Zemin Yumuşak Temas Gölgesi */}
        <radialGradient id="contactShadow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="rgba(0, 0, 0, 0.75)" />
          <stop offset="60%" stopColor="rgba(0, 0, 0, 0.35)" />
          <stop offset="100%" stopColor="rgba(0, 0, 0, 0)" />
        </radialGradient>

        {/* Rim Light / Işık Vurgu Filtresi */}
        <filter id="clayRim" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>

      {/* ========================================================
          POZ 12: TAM HUŞU İÇİNDE SECDE
          ======================================================== */}
      {pose === 'secde' && (
        <g>
          {/* Seccade Temas Gölgesi */}
          <ellipse cx="0" cy="10" rx="220" ry="40" fill="url(#contactShadow)" />

          {/* Ayaklar & Topuklar (Seccadede arkada bükülü) */}
          <ellipse cx="140" cy="-5" rx="32" ry="18" fill="url(#clayLegMat)" />
          <ellipse cx="160" cy="-2" rx="28" ry="16" fill="url(#clayLegMat)" />

          {/* Dizler ve Alt Bacaklar (Seccadede yere basılı) */}
          <path d="M 120 -10 Q 70 -40 20 -15" stroke="url(#clayLimbMat)" strokeWidth="48" strokeLinecap="round" fill="none" />
          <path d="M 140 -5 Q 90 -35 40 -10" stroke="url(#clayLimbMat)" strokeWidth="46" strokeLinecap="round" fill="none" />

          {/* Eğimli Gövde / Kalça */}
          <path d="M 110 -25 Q 30 -85 -70 -20" stroke="url(#clayLimbMat)" strokeWidth="66" strokeLinecap="round" fill="none" />

          {/* Kollar: Dirsekler yukarıda, eller seccadede alnın iki yanında */}
          {/* Sol Kol & 5 Parmaklı El */}
          <path d="M -30 -35 Q -80 -80 -120 -15" stroke="url(#clayLimbMat)" strokeWidth="32" strokeLinecap="round" fill="none" />
          {/* Sol El ve Parmaklar (Yere düz basılı) */}
          <g transform="translate(-125, -15)">
            <ellipse cx="0" cy="0" rx="20" ry="10" fill="url(#clayHeadMat)" />
            <line x1="-15" y1="0" x2="-30" y2="-5" stroke="url(#clayLimbMat)" strokeWidth="7" strokeLinecap="round" />
            <line x1="-15" y1="2" x2="-32" y2="2" stroke="url(#clayLimbMat)" strokeWidth="7" strokeLinecap="round" />
            <line x1="-15" y1="5" x2="-30" y2="7" stroke="url(#clayLimbMat)" strokeWidth="6.5" strokeLinecap="round" />
            <line x1="-12" y1="8" x2="-25" y2="12" stroke="url(#clayLimbMat)" strokeWidth="6" strokeLinecap="round" />
            <line x1="-5" y1="8" x2="-14" y2="15" stroke="url(#clayLimbMat)" strokeWidth="6" strokeLinecap="round" />
          </g>

          {/* Sağ Kol & 5 Parmaklı El */}
          <path d="M -20 -30 Q -65 -75 -100 -5" stroke="url(#clayLimbMat)" strokeWidth="32" strokeLinecap="round" fill="none" />
          <g transform="translate(-105, -5)">
            <ellipse cx="0" cy="0" rx="20" ry="10" fill="url(#clayHeadMat)" />
            <line x1="-15" y1="0" x2="-30" y2="-4" stroke="url(#clayLimbMat)" strokeWidth="7" strokeLinecap="round" />
            <line x1="-15" y1="2" x2="-32" y2="2" stroke="url(#clayLimbMat)" strokeWidth="7" strokeLinecap="round" />
            <line x1="-15" y1="5" x2="-30" y2="6" stroke="url(#clayLimbMat)" strokeWidth="6.5" strokeLinecap="round" />
            <line x1="-12" y1="8" x2="-25" y2="11" stroke="url(#clayLimbMat)" strokeWidth="6" strokeLinecap="round" />
            <line x1="-5" y1="8" x2="-14" y2="14" stroke="url(#clayLimbMat)" strokeWidth="6" strokeLinecap="round" />
          </g>

          {/* Seccadeye Değen Baş (Alın Yerde) */}
          <circle cx="-135" cy="-28" r="62" fill="url(#clayHeadMat)" stroke={rimColor} strokeWidth="3" filter="url(#clayRim)" />
        </g>
      )}

      {/* ========================================================
          POZ 10: DİZ ÇÖKMÜŞ TÖVBE VE GÖZYAŞI (DUA)
          ======================================================== */}
      {pose === 'praying_repentance' && (
        <g>
          {/* Zemin Temas Gölgesi */}
          <ellipse cx="0" cy="15" rx="140" ry="30" fill="url(#contactShadow)" />

          {/* Yere Basan Dizler ve Bükülü Ayaklar */}
          <ellipse cx="-45" cy="5" rx="36" ry="18" fill="url(#clayLegMat)" />
          <ellipse cx="45" cy="5" rx="36" ry="18" fill="url(#clayLegMat)" />
          {/* Ayak Parmakları / Tabanlar arkada */}
          <ellipse cx="-35" cy="12" rx="22" ry="10" fill="url(#clayLimbMat)" />
          <ellipse cx="35" cy="12" rx="22" ry="10" fill="url(#clayLimbMat)" />

          {/* Uyluk Kemikleri */}
          <path d="M -35 -50 L -45 5" stroke="url(#clayLegMat)" strokeWidth="48" strokeLinecap="round" />
          <path d="M 35 -50 L 45 5" stroke="url(#clayLegMat)" strokeWidth="48" strokeLinecap="round" />

          {/* Gövde */}
          <path d={`M 0 ${-55 + breath} Q 0 -130 0 -170`} stroke="url(#clayHeadMat)" strokeWidth="74" strokeLinecap="round" />

          {/* Kollar: Göğüste duaya kalkmış iki kol */}
          <path d="M -35 -145 Q -65 -105 -20 -85" stroke="url(#clayLimbMat)" strokeWidth="28" strokeLinecap="round" fill="none" />
          <path d="M 35 -145 Q 65 -105 20 -85" stroke="url(#clayLimbMat)" strokeWidth="28" strokeLinecap="round" fill="none" />

          {/* Duada Birleşen 5 Parmaklı Eller */}
          <g transform="translate(0, -85)">
            {/* Avuçlar */}
            <ellipse cx="-12" cy="0" rx="16" ry="12" fill="url(#clayHeadMat)" />
            <ellipse cx="12" cy="0" rx="16" ry="12" fill="url(#clayHeadMat)" />
            {/* Açık Parmaklar (Semaya doğru) */}
            <line x1="-16" y1="-5" x2="-22" y2="-22" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
            <line x1="-11" y1="-8" x2="-14" y2="-26" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
            <line x1="-5" y1="-8" x2="-6" y2="-27" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
            <line x1="0" y1="-8" x2="0" y2="-25" stroke="url(#clayLimbMat)" strokeWidth="5" strokeLinecap="round" />
            <line x1="5" y1="-8" x2="6" y2="-27" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
            <line x1="11" y1="-8" x2="14" y2="-26" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
            <line x1="16" y1="-5" x2="22" y2="-22" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
          </g>

          {/* Baş */}
          <g transform={`translate(0, ${-245 + breath * 0.5})`}>
            <circle cx="0" cy="0" r="70" fill="url(#clayHeadMat)" stroke={rimColor} strokeWidth="3" filter="url(#clayRim)" />
            {/* Kapanmış Huşu Gözleri */}
            <path d="M -30 -6 Q -20 8 -10 -6" stroke="#334155" strokeWidth="4.5" fill="none" strokeLinecap="round" />
            <path d="M 10 -6 Q 20 8 30 -6" stroke="#334155" strokeWidth="4.5" fill="none" strokeLinecap="round" />
            {/* Hüzünlü Kaşlar */}
            <path d="M -32 -22 Q -22 -14 -12 -24" stroke="#475569" strokeWidth="3.5" fill="none" strokeLinecap="round" />
            <path d="M 12 -24 Q 22 -14 32 -22" stroke="#475569" strokeWidth="3.5" fill="none" strokeLinecap="round" />
            {/* Süzülen Parlayan Gözyaşları */}
            <path d={`M -18 8 Q -20 ${24 + (tearProgress % 40)} -18 ${32 + (tearProgress % 40)}`} stroke="url(#divineTear)" strokeWidth="4" strokeLinecap="round" />
            <path d={`M 18 8 Q 20 ${24 + (tearProgress % 40)} 18 ${32 + (tearProgress % 40)}`} stroke="url(#divineTear)" strokeWidth="4" strokeLinecap="round" />
            {/* Dudaklar (Hafif aralık zikir halinde) */}
            <ellipse cx="0" cy="24" rx="10" ry="6" fill="#1E293B" />
          </g>
        </g>
      )}

      {/* ========================================================
          POZ: AYAKTA TAM BOY (WAVING / STANDING / REFERENCE POSE)
          Referans Görselin Birebir Aynısı:
          Baş, Gözler, Kaşlar, Ağız, Gövde, Kollar, 5 Parmaklı Eller, Bacaklar ve Ayaklar!
          ======================================================== */}
      {(pose === 'waving' ||
        pose === 'reaching_curtain' ||
        pose === 'looking_up_street' ||
        pose === 'holding_phone' ||
        pose === 'panic' ||
        pose === 'shock_mouth' ||
        pose === 'morning_relief' ||
        pose === 'facing_horizon') && (
        <g>
          {/* Zemin Temas Gölgesi (Ayakların Altında) */}
          <ellipse cx="0" cy="5" rx="120" ry="22" fill="url(#contactShadow)" />

          {/* 1. SAĞ VE SOL AYAKLAR (ZEMİNE OTURMUŞ, REFERANS GÖRSELDEKİ BEYAZ VİNİL AYAKLAR) */}
          {/* Sol Ayak */}
          <g transform="translate(-46, 0)">
            <ellipse cx="0" cy="-6" rx="28" ry="15" fill="url(#clayLegMat)" />
            {/* Yuvarlak Burun ve Taban */}
            <path d="M -24 -4 Q 0 8 26 -4 L 24 -14 Q 0 -18 -22 -12 Z" fill="url(#clayHeadMat)" />
          </g>
          {/* Sağ Ayak */}
          <g transform="translate(46, 0)">
            <ellipse cx="0" cy="-6" rx="28" ry="15" fill="url(#clayLegMat)" />
            <path d="M -26 -4 Q 0 8 24 -4 L 22 -14 Q 0 -18 -24 -12 Z" fill="url(#clayHeadMat)" />
          </g>

          {/* 2. BACAKLAR (BALDIRLAR VE UYLUKLAR) */}
          {/* Sol Bacak */}
          <path d="M -30 -140 Q -42 -70 -46 -6" stroke="url(#clayLegMat)" strokeWidth="42" strokeLinecap="round" />
          {/* Sağ Bacak */}
          <path d="M 30 -140 Q 42 -70 46 -6" stroke="url(#clayLegMat)" strokeWidth="42" strokeLinecap="round" />

          {/* 3. GÖVDE (REFERANS GÖRSELDEKİ PÜRÜZSÜZ VİNİL GÖVDE) */}
          <path
            d={`M 0 -140 Q 0 -210 0 ${-270 + breath}`}
            stroke="url(#clayHeadMat)"
            strokeWidth="78"
            strokeLinecap="round"
          />

          {/* 4. KOLLAR VE 5 PARMAKLIK ELLER */}

          {/* A) WAVING POZU (REFERANS GÖRSELİN BİREBİR AYNISI) */}
          {pose === 'waving' && (
            <g>
              {/* Sol Kol (Aşağıda rahat, parmaklar aşağı doğru) */}
              <path d="M -38 -240 Q -70 -170 -65 -90" stroke="url(#clayLimbMat)" strokeWidth="30" strokeLinecap="round" fill="none" />
              {/* Sol El ve Parmaklar (Aşağıda kıvrık) */}
              <g transform="translate(-65, -90)">
                <ellipse cx="0" cy="8" rx="16" ry="14" fill="url(#clayHeadMat)" />
                {/* 5 Parmak */}
                <path d="M -12 16 L -16 32" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <path d="M -6 18 L -8 36" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <path d="M 0 18 L 0 37" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <path d="M 6 18 L 7 35" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <path d="M 12 14 L 15 28" stroke="url(#clayLimbMat)" strokeWidth="5" strokeLinecap="round" />
              </g>

              {/* Sağ Kol (Havada el sallıyor - Referans Görseldeki Gibi!) */}
              <path d="M 38 -240 Q 95 -290 140 -340" stroke="url(#clayLimbMat)" strokeWidth="30" strokeLinecap="round" fill="none" />
              {/* Sağ El (5 Parmak Açık, El Sallıyor) */}
              <g transform="translate(142, -345) rotate(15)">
                <ellipse cx="0" cy="0" rx="20" ry="16" fill="url(#clayHeadMat)" />
                {/* Başparmak */}
                <path d="M -16 -4 Q -26 -16 -24 -26" stroke="url(#clayLimbMat)" strokeWidth="6.5" strokeLinecap="round" />
                {/* İşaret Parmağı */}
                <path d="M -8 -12 Q -12 -30 -10 -40" stroke="url(#clayLimbMat)" strokeWidth="6.5" strokeLinecap="round" />
                {/* Orta Parmak */}
                <path d="M 0 -14 Q 0 -34 2 -45" stroke="url(#clayLimbMat)" strokeWidth="6.5" strokeLinecap="round" />
                {/* Yüzük Parmağı */}
                <path d="M 8 -12 Q 12 -30 14 -41" stroke="url(#clayLimbMat)" strokeWidth="6" strokeLinecap="round" />
                {/* Serçe Parmak */}
                <path d="M 15 -6 Q 24 -20 26 -32" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
              </g>
            </g>
          )}

          {/* B) PERDEYE UZANMA POZU */}
          {pose === 'reaching_curtain' && (
            <g>
              <path d="M -38 -240 Q -65 -160 -60 -90" stroke="url(#clayLimbMat)" strokeWidth="30" strokeLinecap="round" fill="none" />
              {/* Sağ Kol İleri/Perdeye Uzanan */}
              <path d="M 38 -240 Q 110 -220 180 -210" stroke="url(#clayLimbMat)" strokeWidth="30" strokeLinecap="round" fill="none" />
              {/* Perdeyi Tutan 5 Parmaklı El */}
              <g transform="translate(185, -210)">
                <ellipse cx="0" cy="0" rx="18" ry="14" fill="url(#clayHeadMat)" />
                <path d="M -10 -8 L 12 -18" stroke="url(#clayLimbMat)" strokeWidth="6" strokeLinecap="round" />
                <path d="M -6 -4 L 16 -10" stroke="url(#clayLimbMat)" strokeWidth="6" strokeLinecap="round" />
                <path d="M 0 0 L 18 0" stroke="url(#clayLimbMat)" strokeWidth="6" strokeLinecap="round" />
                <path d="M 6 4 L 16 10" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <path d="M 10 8 L 14 18" stroke="url(#clayLimbMat)" strokeWidth="5" strokeLinecap="round" />
              </g>
            </g>
          )}

          {/* C) SOKAKTA GÖĞE BAKMA POZU */}
          {pose === 'looking_up_street' && (
            <g>
              {/* İki Kol Semaya Açılmış */}
              <path d="M -38 -240 Q -95 -230 -110 -160" stroke="url(#clayLimbMat)" strokeWidth="30" strokeLinecap="round" fill="none" />
              <path d="M 38 -240 Q 95 -230 110 -160" stroke="url(#clayLimbMat)" strokeWidth="30" strokeLinecap="round" fill="none" />
              {/* İki Açık El */}
              <g transform="translate(-112, -155)">
                <ellipse cx="0" cy="0" rx="18" ry="14" fill="url(#clayHeadMat)" />
                <path d="M -12 -5 L -26 -18" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <path d="M -5 -8 L -12 -25" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <path d="M 2 -8 L 2 -27" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <path d="M 9 -6 L 14 -22" stroke="url(#clayLimbMat)" strokeWidth="5" strokeLinecap="round" />
              </g>
              <g transform="translate(112, -155)">
                <ellipse cx="0" cy="0" rx="18" ry="14" fill="url(#clayHeadMat)" />
                <path d="M 12 -5 L 26 -18" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <path d="M 5 -8 L 12 -25" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <path d="M -2 -8 L -2 -27" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <path d="M -9 -6 L -14 -22" stroke="url(#clayLimbMat)" strokeWidth="5" strokeLinecap="round" />
              </g>
            </g>
          )}

          {/* D) TELEFON TUTMA POZU */}
          {pose === 'holding_phone' && (
            <g>
              <path d="M -38 -240 Q -65 -180 -25 -170" stroke="url(#clayLimbMat)" strokeWidth="28" strokeLinecap="round" fill="none" />
              <path d="M 38 -240 Q 65 -180 25 -170" stroke="url(#clayLimbMat)" strokeWidth="28" strokeLinecap="round" fill="none" />
              {/* Telefon ve İki El */}
              <g transform="translate(0, -170)">
                <rect x="-35" y="-55" width="70" height="110" rx="10" fill="#0F172A" stroke="#38BDF8" strokeWidth="2.5" />
                <rect x="-30" y="-48" width="60" height="96" rx="6" fill="#020617" />
                <text x="0" y="-15" textAnchor="middle" fill="#38BDF8" fontFamily="monospace" fontSize="16" fontWeight="bold">12:30</text>
                <text x="0" y="8" textAnchor="middle" fill="#EF4444" fontSize="8" fontWeight="bold">ŞEBEKE YOK</text>
                {/* Telefonu Tutan Sol ve Sağ Parmaklar */}
                <circle cx="-35" cy="-20" r="6" fill="url(#clayHeadMat)" />
                <circle cx="-36" cy="-5" r="6" fill="url(#clayHeadMat)" />
                <circle cx="-35" cy="10" r="6" fill="url(#clayHeadMat)" />
                <circle cx="35" cy="-20" r="6" fill="url(#clayHeadMat)" />
                <circle cx="36" cy="-5" r="6" fill="url(#clayHeadMat)" />
                <circle cx="35" cy="10" r="6" fill="url(#clayHeadMat)" />
              </g>
            </g>
          )}

          {/* E) PANİK / ELLER BAŞTA */}
          {pose === 'panic' && (
            <g>
              <path d="M -38 -240 Q -85 -280 -55 -320" stroke="url(#clayLimbMat)" strokeWidth="30" strokeLinecap="round" fill="none" />
              <path d="M 38 -240 Q 85 -280 55 -320" stroke="url(#clayLimbMat)" strokeWidth="30" strokeLinecap="round" fill="none" />
              {/* Şakaklara Yapışmış Eller */}
              <g transform="translate(-55, -320)">
                <ellipse cx="0" cy="0" rx="16" ry="12" fill="url(#clayHeadMat)" />
                <line x1="-5" y1="-8" x2="10" y2="-18" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <line x1="0" y1="-5" x2="15" y2="-12" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
              </g>
              <g transform="translate(55, -320)">
                <ellipse cx="0" cy="0" rx="16" ry="12" fill="url(#clayHeadMat)" />
                <line x1="5" y1="-8" x2="-10" y2="-18" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <line x1="0" y1="-5" x2="-15" y2="-12" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
              </g>
            </g>
          )}

          {/* F) DEHŞET / ELLER AĞIZI KAPATMIŞ */}
          {pose === 'shock_mouth' && (
            <g>
              <path d="M -38 -240 Q -55 -270 -16 -290" stroke="url(#clayLimbMat)" strokeWidth="28" strokeLinecap="round" fill="none" />
              <path d="M 38 -240 Q 55 -270 16 -290" stroke="url(#clayLimbMat)" strokeWidth="28" strokeLinecap="round" fill="none" />
              {/* Ağzı Kapatan İki El ve Titreyen Parmaklar */}
              <g transform="translate(0, -295)">
                <ellipse cx="-12" cy="0" rx="16" ry="12" fill="url(#clayHeadMat)" />
                <ellipse cx="12" cy="0" rx="16" ry="12" fill="url(#clayHeadMat)" />
                <line x1="-15" y1="-5" x2="-5" y2="-15" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <line x1="-10" y1="-3" x2="0" y2="-16" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <line x1="15" y1="-5" x2="5" y2="-15" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <line x1="10" y1="-3" x2="0" y2="-16" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
              </g>
            </g>
          )}

          {/* G) SABAH RAHMETİ / ŞÜKÜR */}
          {pose === 'morning_relief' && (
            <g>
              <path d="M -38 -240 Q -85 -220 -115 -270" stroke="url(#clayLimbMat)" strokeWidth="30" strokeLinecap="round" fill="none" />
              <path d="M 38 -240 Q 85 -220 115 -270" stroke="url(#clayLimbMat)" strokeWidth="30" strokeLinecap="round" fill="none" />
              <g transform="translate(-115, -275)">
                <ellipse cx="0" cy="0" rx="18" ry="14" fill="url(#clayHeadMat)" />
                <line x1="-5" y1="-8" x2="-15" y2="-25" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <line x1="2" y1="-8" x2="0" y2="-27" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <line x1="9" y1="-6" x2="14" y2="-24" stroke="url(#clayLimbMat)" strokeWidth="5" strokeLinecap="round" />
              </g>
              <g transform="translate(115, -275)">
                <ellipse cx="0" cy="0" rx="18" ry="14" fill="url(#clayHeadMat)" />
                <line x1="5" y1="-8" x2="15" y2="-25" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <line x1="-2" y1="-8" x2="0" y2="-27" stroke="url(#clayLimbMat)" strokeWidth="5.5" strokeLinecap="round" />
                <line x1="-9" y1="-6" x2="-14" y2="-24" stroke="url(#clayLimbMat)" strokeWidth="5" strokeLinecap="round" />
              </g>
            </g>
          )}

          {/* H) BATI UFKUNA BAKIŞ */}
          {pose === 'facing_horizon' && (
            <g>
              <path d="M -38 -240 Q -65 -160 -60 -110" stroke="url(#clayLimbMat)" strokeWidth="30" strokeLinecap="round" fill="none" />
              <path d="M 38 -240 Q 65 -160 60 -110" stroke="url(#clayLimbMat)" strokeWidth="30" strokeLinecap="round" fill="none" />
            </g>
          )}

          {/* 5. 3D KÜRE KAFA VE YÜZ (REFERANS GÖRSELİN BİREBİR AYNISI) */}
          <g transform={`translate(0, ${-345 + breath * 0.5})`}>
            {/* Analitik Küre Baş */}
            <circle cx="0" cy="0" r="72" fill="url(#clayHeadMat)" stroke={rimColor} strokeWidth="3.5" filter="url(#clayRim)" />

            {/* Arkaya bakış değilse yüz öğelerini çiz */}
            {pose !== 'facing_horizon' && (
              <g>
                {/* Sol Göz (İri Parlak Siyah + Beyaz Yansıma Noktaları) */}
                <ellipse cx="-23" cy="-4" rx="17" ry={20 * eyeBlink} fill="url(#clayEyeGloss)" />
                {eyeBlink > 0.5 && (
                  <>
                    <circle cx="-18" cy="-12" r="5.5" fill="#FFFFFF" />
                    <circle cx="-25" cy="3" r="2.2" fill="#FFFFFF" opacity={0.8} />
                  </>
                )}

                {/* Sağ Göz (İri Parlak Siyah + Beyaz Yansıma Noktaları) */}
                <ellipse cx="23" cy="-4" rx="17" ry={20 * eyeBlink} fill="url(#clayEyeGloss)" />
                {eyeBlink > 0.5 && (
                  <>
                    <circle cx="28" cy="-12" r="5.5" fill="#FFFFFF" />
                    <circle cx="21" cy="3" r="2.2" fill="#FFFFFF" opacity={0.8} />
                  </>
                )}

                {/* İnce Gri Kaşlar (Referans Görseldeki Kavis) */}
                {pose === 'panic' || pose === 'shock_mouth' ? (
                  <>
                    <path d="M -36 -28 Q -24 -38 -12 -28" stroke="#334155" strokeWidth="4" fill="none" strokeLinecap="round" />
                    <path d="M 12 -28 Q 24 -38 36 -28" stroke="#334155" strokeWidth="4" fill="none" strokeLinecap="round" />
                  </>
                ) : (
                  <>
                    <path d="M -36 -26 Q -23 -34 -12 -24" stroke="#475569" strokeWidth="3.8" fill="none" strokeLinecap="round" />
                    <path d="M 12 -24 Q 23 -34 36 -26" stroke="#475569" strokeWidth="3.8" fill="none" strokeLinecap="round" />
                  </>
                )}

                {/* Ağız (Referans Görseldeki Gülen / İfadeli Ağız + Pembe Dil) */}
                {pose === 'panic' || pose === 'shock_mouth' ? (
                  <ellipse cx="0" cy="28" rx="16" ry="18" fill="#0F172A" stroke="#334155" strokeWidth="2" />
                ) : (
                  <g transform="translate(0, 24)">
                    <path d="M -22 -2 Q 0 24 22 -2 Z" fill="url(#clayMouthInterior)" stroke="#334155" strokeWidth="1.5" />
                    {/* Açık Pembe Dil */}
                    <path d="M -12 8 Q 0 4 12 8 Q 0 18 -12 8 Z" fill="#FB7185" opacity={0.9} />
                  </g>
                )}
              </g>
            )}
          </g>
        </g>
      )}
    </g>
  );
};
