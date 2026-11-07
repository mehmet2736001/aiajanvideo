import React from 'react';
import { Composition } from 'remotion';
import { NotebookVideo } from './NotebookVideo';
import { IslamicMotionVideo } from './IslamicMotionVideo';
import { OlumSonMuVideo, sure as OLUM_FRAMES } from './olum-son-mu/Video';
import { Hud112Video, sureKare as HUD112_FRAMES } from './hud-112/Video';
import { TefekkurVideo, TefekkurProps, computeDurationFrames } from './templates/TefekkurVideo';
import generatedJson from './generatedData.json';
import olumWords from '../public/olum-son-mu/kelimeler.json';
import type { VideoData } from './types';

const FPS = 30;
const activeProps = generatedJson as unknown as VideoData;

/** NotebookVideo'daki tüm izleri (sahne, alıntı videoları, PIP, altyazı, ses) tarayıp süreyi saniye olarak verir. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const notebookSeconds = (p: any): number => {
  let max = 5.0;
  for (const s of p?.scenes ?? []) if (typeof s.endTime === 'number') max = Math.max(max, s.endTime);
  for (const q of p?.quoteVideos ?? []) {
    const start = q.timelineStart || 0;
    max = Math.max(max, start + (q.duration || Math.max(1, (q.trimEnd || 6) - (q.trimStart || 0))));
  }
  for (const v of p?.pipVideos ?? []) {
    const start = v.timelineStart || 0;
    max = Math.max(max, start + (v.duration || Math.max(1, (v.trimEnd || 5) - (v.trimStart || 0))));
  }
  for (const sub of p?.subtitles ?? []) if (typeof sub.end === 'number') max = Math.max(max, sub.end);
  if (typeof p?.totalDuration === 'number') max = Math.max(max, p.totalDuration);
  return max;
};

const notebookFrames = (p: unknown): number => Math.max(150, Math.ceil((notebookSeconds(p) + 0.5) * FPS));

const notebookMeta = ({ props }: { props: VideoData }) => ({ durationInFrames: notebookFrames(props) });

const tefekkurDefaults: TefekkurProps = {
  slug: 'olum-son-mu',
  title: 'Ölüm Gerçekten Son Mu?',
  words: olumWords as TefekkurProps['words'],
  audioDurationSec: 44.11,
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 0. Veri güdümlü genel şablon: orkestratör yeni senaryoları bununla render eder */}
      <Composition
        id="TefekkurVideo"
        component={TefekkurVideo}
        durationInFrames={computeDurationFrames(tefekkurDefaults, FPS)}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={tefekkurDefaults}
        calculateMetadata={({ props }) => ({ durationInFrames: computeDurationFrames(props, FPS) })}
      />

      {/* 1. 9:16 Dikey (TikTok, Reels, Shorts) */}
      <Composition
        id="NotebookVideo"
        component={NotebookVideo}
        durationInFrames={notebookFrames(activeProps)}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={activeProps}
        calculateMetadata={notebookMeta}
      />

      {/* 2. 16:9 Yatay */}
      <Composition
        id="NotebookVideo-Horizontal"
        component={NotebookVideo}
        durationInFrames={notebookFrames(activeProps)}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={activeProps}
        calculateMetadata={notebookMeta}
      />

      {/* 3. 1:1 Kare */}
      <Composition
        id="NotebookVideo-Square"
        component={NotebookVideo}
        durationInFrames={notebookFrames(activeProps)}
        fps={FPS}
        width={1080}
        height={1080}
        defaultProps={activeProps}
        calculateMetadata={notebookMeta}
      />

      {/* 4. İslami hareket tasarımı */}
      <Composition
        id="IslamicMotionVideo"
        component={IslamicMotionVideo}
        durationInFrames={2078}
        fps={FPS}
        width={1080}
        height={1920}
        calculateMetadata={() => {
          let frames = 2078;
          try {
            // eslint-disable-next-line @typescript-eslint/no-var-requires
            const c = require('./activeConcept.json');
            if (c?.totalFrames) frames = c.totalFrames;
          } catch (e) {
            // varsayılan süre
          }
          return { durationInFrames: frames };
        }}
      />

      {/* 5. Elle hazırlanmış özel videolar (kendi index.ts dosyalarıyla da render edilebilir) */}
      <Composition id="OlumSonMu" component={OlumSonMuVideo} durationInFrames={OLUM_FRAMES} fps={FPS} width={1080} height={1920} />
      <Composition id="Hud112" component={Hud112Video} durationInFrames={HUD112_FRAMES} fps={FPS} width={1080} height={1920} />
    </>
  );
};
