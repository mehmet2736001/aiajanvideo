import React from 'react';
import { Composition } from 'remotion';
import { NotebookVideo } from './NotebookVideo';
import { defaultVideoData } from './sampleData';

let activeProps = {
  is_empty: true,
  scenes: [],
  subtitles: [],
  words: [],
  totalDuration: 0.0,
  theme: 'dark_minimalist'
};
try {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const generated = require('./generatedData.json');
  if (generated) {
    activeProps = generated;
  }
} catch (e) {
  // fallback
}

export const RemotionRoot: React.FC = () => {
  // Dynamically calculate duration considering ALL tracks: Scenes, Quote Videos, PIPs, Subtitles, Audio
  let maxTrackSec = 5.0;
  if (activeProps) {
    if (activeProps.scenes) {
      for (const s of activeProps.scenes) {
        if (typeof s.endTime === 'number') maxTrackSec = Math.max(maxTrackSec, s.endTime);
      }
    }
    if (activeProps.quoteVideos) {
      for (const q of activeProps.quoteVideos) {
        const start = q.timelineStart || 0;
        const dur = q.duration || Math.max(1, (q.trimEnd || 6) - (q.trimStart || 0));
        maxTrackSec = Math.max(maxTrackSec, start + dur);
      }
    }
    if (activeProps.pipVideos) {
      for (const p of activeProps.pipVideos) {
        const start = p.timelineStart || 0;
        const dur = p.duration || Math.max(1, (p.trimEnd || 5) - (p.trimStart || 0));
        maxTrackSec = Math.max(maxTrackSec, start + dur);
      }
    }
    if (activeProps.subtitles) {
      for (const sub of activeProps.subtitles) {
        if (typeof sub.end === 'number') maxTrackSec = Math.max(maxTrackSec, sub.end);
      }
    }
    if (typeof (activeProps as any).totalDuration === 'number') {
      maxTrackSec = Math.max(maxTrackSec, (activeProps as any).totalDuration);
    }
  }
  const dynamicDuration = Math.max(150, Math.ceil((maxTrackSec + 0.5) * 30));

  return (
    <>
      {/* 1. 9:16 Vertical (TikTok, Instagram Reels, YouTube Shorts) */}
      <Composition
        id="NotebookVideo"
        component={NotebookVideo}
        durationInFrames={dynamicDuration}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={activeProps}
        calculateMetadata={({ props }) => {
          let maxTrackSec = 5.0;
          const p = props || activeProps;
          if (p.scenes) {
            for (const s of p.scenes) {
              if (typeof s.endTime === 'number') maxTrackSec = Math.max(maxTrackSec, s.endTime);
            }
          }
          if (p.quoteVideos) {
            for (const q of p.quoteVideos) {
              const start = q.timelineStart || 0;
              const dur = q.duration || Math.max(1, (q.trimEnd || 6) - (q.trimStart || 0));
              maxTrackSec = Math.max(maxTrackSec, start + dur);
            }
          }
          if (typeof p.totalDuration === 'number') {
            maxTrackSec = Math.max(maxTrackSec, p.totalDuration);
          }
          const durFrames = Math.max(150, Math.ceil((maxTrackSec + 0.5) * 30));
          return { durationInFrames: durFrames };
        }}
      />

      {/* 2. 16:9 Landscape (YouTube Long-form, Desktop, TV) */}
      <Composition
        id="NotebookVideo-Horizontal"
        component={NotebookVideo}
        durationInFrames={dynamicDuration}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={activeProps}
      />

      {/* 3. 1:1 Square (Instagram Feed, LinkedIn, Twitter/X) */}
      <Composition
        id="NotebookVideo-Square"
        component={NotebookVideo}
        durationInFrames={dynamicDuration}
        fps={30}
        width={1080}
        height={1080}
        defaultProps={activeProps}
      />
    </>
  );
};
