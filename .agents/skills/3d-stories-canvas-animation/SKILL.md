---
name: 3d-stories-canvas-animation
description: Build dependency-free, cinematic, timeline-driven 3D Canvas and perspective-projected visual narratives in a single self-contained HTML/Canvas file or Remotion composition. Use when the user asks for 3D canvas animation, 3D stories, 3D animated video, 3D holographic models (atom Fe-26, celestial astrolabes, gyroscopes), depth-sorted wireframes, camera dolly/yaw/pitch motions, or 9:16 vertical 3D contemplative videos driven strictly by time t.
---

# 3D Stories Canvas Animation

Build self-contained, dependency-free, interactive 3D Canvas animations, spatial visual narratives, and perspective-projected storyboards running in a single HTML file or Remotion composition.

## Summary

This skill guides the construction of cinematic 3D Canvas visual narratives that tell a coherent story across fixed-duration timelines (e.g. 15s, 30s, 60s) in 9:16 vertical or 16:9 widescreen formats. All 3D rotations, perspective matrix projections, particle depth fields, camera dollies, and lighting are driven strictly by a single time variable `t = frame / FPS`, making the animation fully scrubbable, deterministic, and free of heavyweight 3D library dependencies.

## When to Use

- When the user asks for a 3D Canvas animation, 3D story, or 3D animated video.
- When projecting 3D procedural wireframes (3D Holo Atom Fe-26, Gyroscope Mizan, Seljuk 3D stellations, rotating hypercubes/polyhedra) onto a 2D Canvas context.
- When creating deep space warp tunnels, 3D stardust constellation fields, or Doppler redshift expansions.
- When requiring full scrubbability, deterministic rendering, and 3D camera transitions without Three.js or WebGL bloat.

## Core Architecture and Principles

### 1. Single Time Variable as Single Source of Truth
Never use independent timers or requestAnimationFrame state mutations. All 3D camera transforms, angles, and geometry vertices must be pure mathematical functions of a single time variable `t` (0 to `DUR`).
Scrubbing to any time `t` instantly computes the exact 3D coordinates and projection.

### 2. Resolution Independence & Metric Scale
Derive all 3D camera coordinates and projection scales from stage height:
- `U = H / 100;` (1% of canvas height, e.g. 19.2px for 1080x1920)
- Focal length: `focal = 35 * U;`
- Vanishing point: `cx = W * 0.5; cy = H * 0.46;`

### 3. Pure 3D Perspective Projection Engine (No Three.js needed)
Every 3D point `P(x, y, z)` is projected onto 2D canvas coordinates using 3D rotation matrices and perspective divide:

```javascript
function project3D(x, y, z, yaw, pitch, roll, camZ, cx, cy, focal, U) {
  // 1. Yaw rotation (Y axis)
  const cosY = Math.cos(yaw), sinY = Math.sin(yaw);
  const x1 = x * cosY - z * sinY;
  const z1 = z * cosY + x * sinY;

  // 2. Pitch rotation (X axis)
  const cosP = Math.cos(pitch), sinP = Math.sin(pitch);
  const y2 = y * cosP - z1 * sinP;
  const z2 = z1 * cosP + y * sinP;

  // 3. Camera distance & Perspective Divide
  const zTotal = z2 + camZ;
  if (zTotal <= 1) return null; // Behind camera clipping

  const scale = focal / zTotal;
  return {
    px: cx + x1 * scale * U,
    py: cy + y2 * scale * U,
    scale: scale,
    depth: zTotal,
    alpha: Math.min(1, Math.max(0, 1 - (zTotal - 20) / 60)) // Depth fog
  };
}
```

### 4. Depth Sorting (Painter's Algorithm)
To prevent depth fighting when drawing multiple 3D elements, sort all 3D render objects (particles, rings, faces) by depth descending (`b.depth - a.depth`) before executing `ctx.stroke()` or `ctx.fill()`.

### 5. Signature 3D Procedural Story Assets
1. **Warp 3D Stardust Vortex**: 300 particles moving toward camera along Z axis:
   `z = ((p.initialZ - t * p.speed) % maxZ);`
2. **3D Holo-Atom Fe-26 (Hadid 25)**: 3 concentric orbital rings tilted at angles $(0^\circ, 60^\circ, 120^\circ)$, rotating with traveling electron beads and glowing proton nucleus.
3. **3D Gyroscope Mizan**: Gimbal-mounted rotating brass rings enclosing a levitating celestial sphere, representing cosmic equilibrium.
4. **Doppler Redshift HUD**: 3D wireframe sphere grid expanding radially with color shift from blue (`#38BDF8`) to deep red (`#EF4444`).

### 6. Hermite Smoothstep Camera Easing
All camera transitions (dolly-in, orbiting yaw, tilt changes) must use Hermite smoothstep for zero-velocity acceleration and deceleration:
```javascript
const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
function smoothstep(a, b, x) {
  const t = clamp((x - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
}
```

### 7. Multi-Layer Stacking
1. `<canvas>`: 3D perspective projection, procedural geometry, depth fog, dynamic lighting.
2. `.vignette`: Deep radial vignette darkening corners.
3. `.subtitles`: Lower-third frosted glass capsule with word-level Whisper highlighting.
4. `.hud`: Top diagnostic tracking (Scene index, time code, FOV, 3D camera coordinates).
