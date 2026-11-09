---
name: canvas-story-animation
description: Build dependency-free, cinematic, timeline-driven Canvas 2D animations and visual narratives in a single self-contained HTML file. Use when the user asks for a 2D canvas animation, animated video, visual story, beat sheet scene sequence, 16:9 or 9:16 vertical video in HTML/Canvas, or philosophical and narrative animations with scrubbing controls.
---

# Canvas Story Animation

Build self-contained, dependency-free, interactive 2D Canvas animations and visual storyboards running in a single HTML file.

## Summary

This skill guides the construction of cinematic 2D Canvas animations that tell a coherent story across fixed-duration timelines (e.g. 10s, 12s, 60s) in either 16:9 horizontal or 9:16 vertical mobile video ratios. All scenes, physics, lighting, and camera pans are driven strictly by a single time variable `t`, making the animation fully scrubbable, deterministic, and free of external libraries.

## When to Use

- When the user asks for a 2D Canvas animation or video in a single HTML file
- When building timeline-driven narrative visual experiences (stories, parables, contemplation pieces)
- When animating 16:9 widescreen or 9:16 vertical reels with beat sheets and multi-scene sequences
- When requiring full scrubbability, deterministic rendering, and keyboard/UI playback controls

## Core Architecture and Principles

### 1. Single Time Variable as Single Source of Truth

Never use independent timers, setTimeout, or CSS animations for scene elements. All visuals and text styles must be pure mathematical functions of a single time variable `t` (0 to `DUR`).

- Scrubbing to any time `t` must instantly render the exact state of that moment without needing past frames.
- Frame loop computes delta time capped at `0.05s`: `dt = Math.min(0.05, (now - lastTime) / 1000)`. Capping prevents teleporting when browser tabs lose focus.
- When `t >= DUR`, clamp `t = DUR` and set `playing = false`.

### 2. Resolution Independence and Metric System

Never use hardcoded pixel sizes for drawing coordinates or stroke widths. Derive all measurements from stage height:

- `U = H / 100;` (1% of canvas height)
- Coordinates: `cx = W * 0.5; cy = H * 0.52;`
- Strokes and radii: `lineWidth = Math.max(0.6, U * 0.15);`
- DPR capping: `dpr = Math.min(window.devicePixelRatio || 1, 2);`
- Set `canvas.width = Math.round(W * dpr)` and `canvas.height = Math.round(H * dpr)`.
- Inside `render(t)`, call `ctx.scale(dpr, dpr)` so all math remains in CSS logical units.

### 3. Smooth Transitions and Easing

Never use linear interpolation for visual transitions or fades. Use Hermite smoothstep:

```javascript
const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
function smoothstep(a, b, x) {
  const t = clamp((x - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
}
```

Every entrance, exit, scale change, and opacity blend must use smoothstep for zero-velocity start and end.

### 4. Deterministic Randomness (PRNG)

Never call `Math.random()` inside the frame loop. Calling it every frame causes severe visual jitter.

- Generate all particle parameters (angle, phase, speed, sway, birth time) once at startup using a seeded Linear Congruential Generator (LCG):

```javascript
function prng(seed) {
  return () => {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    return seed / 4294967296;
  };
}
const R = prng(0x4a92c1);
```

- In `render(t)`, compute position algebraically using `t`, `birth`, and `phase`.

### 5. Multi-Layer Canvas Stacking

The `.stage` container contains five stacked layers matching the exact bounding box:

1. `<canvas>`: all rendering, procedural shapes, god rays, and lighting.
2. `.veil`: radial vignette gradient darkening edges (`pointer-events: none`).
3. `.scrim`: linear dark gradient driven dynamically by JS opacity to ensure text readability against bright scenes.
4. `.layer` / `.caption-overlay`: HTML text elements driven by JS (`opacity`, `transform: translateY`, `filter: blur`).
5. `.controls`: playback UI placed strictly OUTSIDE the `.stage` box.

### 6. Beat Sheet Sequence Workflow

Divide the total duration (`DUR`) into discrete, numbered scenes with clear timing windows:

- For short pieces (10-12s): 3-4 progressive emotional beats.
- For 60s vertical videos: 10-15 distinct scenes (each 4-6s).
- Stagger entrance and exit times so visual elements overlap smoothly rather than cutting abruptly.
- Synchronize text blur and vertical lift: as opacity increases from 0 to 1, blur decreases to 0px and translateY decreases to 0px.

### 7. Controls and Accessibility

Provide complete interactive controls:

- Play/pause/replay button switching SVG icons dynamically.
- Range slider timeline (`input[type="range"]`) with CSS gradient progress track (`--p: %`).
- Time counter readout (`t.toFixed(1) + "s / " + DUR.toFixed(1) + "s"`).
- Keyboard shortcuts: `Space` for play/pause, `ArrowLeft` and `ArrowRight` for seeking, calling `e.preventDefault()`.
- Respect `prefers-reduced-motion`: if set, initialize at `t = DUR` with `playing = false` so users see the completed artistic composition rather than an empty frame.

## Gotchas and Checklist

- Never use CSS keyframe animations for narrative text; always drive styles from JS using `t` so scrubbing stays in sync.
- Always reset `ctx.globalCompositeOperation = 'source-over'` and `ctx.globalAlpha = 1.0` after using `'lighter'` blend modes.
- Set `pointer-events: none` on all overlays above the canvas so scrubbing and clicks are never intercepted.
- Ensure 320px mobile viewport has zero horizontal scroll.
