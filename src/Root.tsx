import React from 'react';
import { Composition } from 'remotion';
import { NotebookVideo } from './NotebookVideo';
import { defaultVideoData } from './sampleData';

let activeProps = defaultVideoData;
try {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const generated = require('./generatedData.json');
  if (generated && (generated.headerLine1 || generated.headerMain || generated.headerSubtitle)) {
    activeProps = generated;
  }
} catch (e) {
  // fallback to defaultVideoData
}

export const RemotionRoot: React.FC = () => {
  // Dynamically calculate duration from audio/subtitles with 1.5s outro breathing room
  let dynamicDuration = 360;
  if (activeProps && activeProps.subtitles && activeProps.subtitles.length > 0) {
    const lastEnd = activeProps.subtitles[activeProps.subtitles.length - 1].end;
    const effectiveSec = Math.max(lastEnd, (activeProps as any).totalDuration || 0);
    dynamicDuration = Math.max(240, Math.ceil((effectiveSec + 1.5) * 30));
  } else if ((activeProps as any)?.totalDuration) {
    dynamicDuration = Math.max(240, Math.ceil(((activeProps as any).totalDuration + 1.5) * 30));
  } else if (activeProps && (activeProps as any).durationInFrames) {
    dynamicDuration = (activeProps as any).durationInFrames;
  }

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
