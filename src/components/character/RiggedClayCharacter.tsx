import React from 'react';
import { Img, staticFile } from 'remotion';

export type RigAction =
  | 'walk'             // Dinamik adım atarak yürüme (bacaklar ileri-geri sallanır, dizler bükülür, kollar zıt salınır)
  | 'wave'             // Sağ kol yukarı kalkar, el sallama hareketi yapar
  | 'reach'            // Kol ileriye doğru uzanır (perdeye/nesneye uzanma)
  | 'look_up'          // Baş yukarı kalkar, kollar semaya açılır
  | 'panic'            // İki kol başa gider, vücut ve kollar titrer
  | 'kneel'            // Diz çökmüş duruş, gövde ve baş huşu içinde
  | 'secde'            // Huşu dolu secde
  | 'idle_stand';      // Ayakta canlı nefes alma ve hafif kol salınımı

interface RiggedClayCharacterProps {
  action: RigAction;
  x?: number;
  y?: number;
  scale?: number;
  time?: number;
  walkProgress?: number; // 0..1 arası yürüyüş ilerlemesi (ekranda ilerleme)
  walkSpeed?: number;
  mirror?: boolean;      // Sağa veya sola bakış
  glowColor?: string;
}

export const RiggedClayCharacter: React.FC<RiggedClayCharacterProps> = ({
  action,
  x = 540,
  y = 1200,
  scale = 1.0,
  time = 0,
  walkProgress = 0,
  walkSpeed = 7.0,
  mirror = false,
  glowColor,
}) => {
  // Yürüme döngüsü matematiksel açıları (Walk Cycle)
  const walkPhase = time * walkSpeed;
  const walkBounce = Math.abs(Math.sin(walkPhase)) * 9; // Adım atarken vücudun yukarı-aşağı yaylanması

  // Bacak ve Kol Açıları
  let leftHip = 0;
  let leftKnee = 0;
  let rightHip = 0;
  let rightKnee = 0;
  let leftArm = 0;
  let rightArm = 0;
  let headTilt = 0;
  let torsoLean = 0;

  // Ekranda yatay yer değiştirme (Walk action ise soldan sağa yürür)
  let posX = x;
  if (action === 'walk') {
    // 1080px genişliğinde yürüyüş yolu
    const walkDistance = 240;
    posX = x - 120 + walkProgress * walkDistance;

    // Yürüyüş kinematiği: bacaklar zıt fazda sallanır
    leftHip = Math.sin(walkPhase) * 34; // -34° .. +34°
    leftKnee = Math.max(0, Math.cos(walkPhase)) * 42; // İleri adım atarken diz bükülür (0° .. 42°)

    rightHip = -Math.sin(walkPhase) * 34;
    rightKnee = Math.max(0, -Math.cos(walkPhase)) * 42;

    // Kollar bacaklara ZIT salınır (Doğal insan yürüyüşü)
    leftArm = -Math.sin(walkPhase) * 30;
    rightArm = Math.sin(walkPhase) * 30;

    headTilt = Math.sin(walkPhase * 0.5) * 4;
    torsoLean = 4; // Yürürken hafif öne eğilme
  } else if (action === 'wave') {
    // El sallama: sol kol aşağıda hafif nefes, sağ kol havada sallanır
    leftArm = Math.sin(time * 2) * 6;
    rightArm = -75 + Math.sin(time * 9) * 22; // Hızlı el sallama
    headTilt = Math.sin(time * 2) * 5;
  } else if (action === 'reach') {
    // Perdeye uzanma
    rightArm = -60 + Math.sin(time * 1.5) * 8;
    leftArm = Math.sin(time * 2) * 5;
    torsoLean = 6;
  } else if (action === 'look_up') {
    // Göğe bakış
    headTilt = -24; // Baş yukarı kalkık
    leftArm = -35 + Math.sin(time * 2.5) * 8;
    rightArm = 35 - Math.sin(time * 2.5) * 8;
  } else if (action === 'panic') {
    // Panik: kollar başta titrer
    const jitter = Math.sin(time * 25) * 6;
    leftArm = -110 + jitter;
    rightArm = -110 - jitter;
    headTilt = jitter * 0.5;
  } else if (action === 'idle_stand') {
    leftArm = Math.sin(time * 2) * 5;
    rightArm = -Math.sin(time * 2) * 5;
    headTilt = Math.sin(time * 1.5) * 3;
  }

  // Poz bazlı özel durumlar: SECDE ve KNEEL için tam 3D asset kullanımı
  if (action === 'secde') {
    return (
      <div
        style={{
          position: 'absolute',
          left: x - 240,
          top: y - 130 + Math.sin(time * 2) * 2,
          width: 480,
          height: 310,
          transform: `scale(${scale}) ${mirror ? 'scaleX(-1)' : ''}`,
          filter: glowColor ? `drop-shadow(0 0 35px ${glowColor})` : 'drop-shadow(0 15px 30px rgba(0,0,0,0.65))',
          pointerEvents: 'none',
        }}
      >
        <Img
          src={staticFile('character/char_secde.png')}
          style={{ width: '100%', height: '100%', objectFit: 'contain' }}
        />
      </div>
    );
  }

  if (action === 'kneel') {
    return (
      <div
        style={{
          position: 'absolute',
          left: x - 170,
          top: y - 200 + Math.sin(time * 2.5) * 3,
          width: 340,
          height: 480,
          transform: `scale(${scale}) ${mirror ? 'scaleX(-1)' : ''}`,
          filter: glowColor ? `drop-shadow(0 0 25px ${glowColor})` : 'drop-shadow(0 15px 30px rgba(0,0,0,0.65))',
          pointerEvents: 'none',
        }}
      >
        <Img
          src={staticFile('character/char_kneeling.png')}
          style={{ width: '100%', height: '100%', objectFit: 'contain' }}
        />
      </div>
    );
  }

  // YÜRÜYEN / HAREKET EDEN PROFİL İSKELET SİSTEMİ (Side Walk Cycle Rig)
  return (
    <div
      style={{
        position: 'absolute',
        left: posX - 120,
        top: y - 360 - walkBounce,
        width: 240,
        height: 520,
        transform: `scale(${scale}) ${mirror ? 'scaleX(-1)' : ''}`,
        transformOrigin: 'bottom center',
        pointerEvents: 'none',
        filter: glowColor ? `drop-shadow(0 0 25px ${glowColor})` : 'drop-shadow(0 15px 25px rgba(0,0,0,0.55))',
      }}
    >
      {/* 1. ZEMİN TEMAS GÖLGESİ */}
      <div
        style={{
          position: 'absolute',
          left: 40,
          top: 480 + walkBounce * 0.8,
          width: 160,
          height: 24,
          borderRadius: '50%',
          background: 'rgba(0, 0, 0, 0.65)',
          filter: 'blur(6px)',
          transform: `scale(${1.0 - (walkBounce / 25)})`,
        }}
      />

      {/* 2. ARKA BACAK (Sağ Bacak: Kalça -> Diz -> Ayak) */}
      <div
        style={{
          position: 'absolute',
          left: 88,
          top: 310,
          width: 72,
          height: 80,
          transformOrigin: 'top center',
          transform: `rotate(${rightHip}deg)`,
        }}
      >
        <Img
          src={staticFile('character/rig/side_leg_upper.png')}
          style={{ width: '100%', height: '100%', objectFit: 'contain', filter: 'brightness(0.88)' }}
        />
        {/* Alt Bacak ve Ayak */}
        <div
          style={{
            position: 'absolute',
            left: -5,
            top: 65,
            width: 82,
            height: 95,
            transformOrigin: 'top center',
            transform: `rotate(${rightKnee}deg)`,
          }}
        >
          <Img
            src={staticFile('character/rig/side_leg_lower.png')}
            style={{ width: '100%', height: '100%', objectFit: 'contain', filter: 'brightness(0.88)' }}
          />
        </div>
      </div>

      {/* 3. ARKA KOL (Sağ Kol) */}
      <div
        style={{
          position: 'absolute',
          left: 95,
          top: 180,
          width: 50,
          height: 85,
          transformOrigin: 'top center',
          transform: `rotate(${rightArm}deg)`,
        }}
      >
        <Img
          src={staticFile('character/rig/side_arm_upper.png')}
          style={{ width: '100%', height: '100%', objectFit: 'contain', filter: 'brightness(0.85)' }}
        />
        <div
          style={{
            position: 'absolute',
            left: -4,
            top: 70,
            width: 58,
            height: 95,
            transformOrigin: 'top center',
          }}
        >
          <Img
            src={staticFile('character/rig/side_arm_lower.png')}
            style={{ width: '100%', height: '100%', objectFit: 'contain', filter: 'brightness(0.85)' }}
          />
        </div>
      </div>

      {/* 4. GÖVDE (Torso & Pelvis) */}
      <div
        style={{
          position: 'absolute',
          left: 65,
          top: 170,
          width: 110,
          height: 155,
          transformOrigin: 'bottom center',
          transform: `rotate(${torsoLean}deg)`,
        }}
      >
        <Img
          src={staticFile('character/rig/side_torso.png')}
          style={{ width: '100%', height: '100%', objectFit: 'contain' }}
        />
      </div>

      {/* 5. ÖN BACAK (Sol Bacak: Kalça -> Diz -> Ayak) */}
      <div
        style={{
          position: 'absolute',
          left: 82,
          top: 310,
          width: 72,
          height: 80,
          transformOrigin: 'top center',
          transform: `rotate(${leftHip}deg)`,
        }}
      >
        <Img
          src={staticFile('character/rig/side_leg_upper.png')}
          style={{ width: '100%', height: '100%', objectFit: 'contain' }}
        />
        {/* Alt Bacak ve Ayak */}
        <div
          style={{
            position: 'absolute',
            left: -5,
            top: 65,
            width: 82,
            height: 95,
            transformOrigin: 'top center',
            transform: `rotate(${leftKnee}deg)`,
          }}
        >
          <Img
            src={staticFile('character/rig/side_leg_lower.png')}
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
          />
        </div>
      </div>

      {/* 6. BAŞ (Head & Neck - Boyundan döner) */}
      <div
        style={{
          position: 'absolute',
          left: 35,
          top: 15,
          width: 170,
          height: 175,
          transformOrigin: 'bottom center',
          transform: `rotate(${headTilt}deg)`,
        }}
      >
        <Img
          src={staticFile('character/rig/side_head.png')}
          style={{ width: '100%', height: '100%', objectFit: 'contain' }}
        />
      </div>

      {/* 7. ÖN KOL (Sol Kol: Omuz -> Dirsek -> El) */}
      <div
        style={{
          position: 'absolute',
          left: 80,
          top: 185,
          width: 50,
          height: 85,
          transformOrigin: 'top center',
          transform: `rotate(${leftArm}deg)`,
        }}
      >
        <Img
          src={staticFile('character/rig/side_arm_upper.png')}
          style={{ width: '100%', height: '100%', objectFit: 'contain' }}
        />
        {/* Alt Kol ve 5 Parmaklı El */}
        <div
          style={{
            position: 'absolute',
            left: -4,
            top: 70,
            width: 58,
            height: 95,
            transformOrigin: 'top center',
          }}
        >
          <Img
            src={staticFile('character/rig/side_arm_lower.png')}
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
          />
        </div>
      </div>
    </div>
  );
};
