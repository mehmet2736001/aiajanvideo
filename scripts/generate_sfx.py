import os
import math
import random
import wave
import struct

SFX_DIR = os.path.join(os.path.dirname(__file__), "..", "public", "sfx")
os.makedirs(SFX_DIR, exist_ok=True)

SAMPLE_RATE = 44100

def write_wav(filename: str, samples: list):
    filepath = os.path.join(SFX_DIR, filename)
    with wave.open(filepath, "w") as wav_file:
        wav_file.setnchannels(1) # mono
        wav_file.setsampwidth(2) # 16-bit
        wav_file.setframerate(SAMPLE_RATE)
        # Convert float (-1.0 to 1.0) to 16-bit int
        packed = bytearray()
        for s in samples:
            val = max(-1.0, min(1.0, s))
            int_val = int(val * 32767.0)
            packed.extend(struct.pack("<h", int_val))
        wav_file.writeframes(packed)
    print(f"Generated SFX: {filename} ({len(samples)/SAMPLE_RATE:.2f}s)")

# 1. Pen Draw / Scratch (ASMR paper friction)
def make_pen_draw():
    duration = 0.8
    total_samples = int(duration * SAMPLE_RATE)
    samples = []
    prev = 0.0
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Envelope: attack, sustain, decay
        env = math.sin(math.pi * (t / duration)) ** 0.5
        # Noise with frequency variation
        noise = (random.random() * 2.0 - 1.0)
        # Lowpass filter
        filtered = 0.25 * noise + 0.75 * prev
        prev = filtered
        # Micro scratches
        scratch = math.sin(2.0 * math.pi * 1200 * t + filtered * 2.0) * 0.15
        samples.append((filtered * 0.5 + scratch) * env * 0.4)
    write_wav("pen_draw.wav", samples)

# 2. Marker Sweep (Squeaky highlighter glide)
def make_marker_sweep():
    duration = 0.7
    total_samples = int(duration * SAMPLE_RATE)
    samples = []
    prev = 0.0
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / duration))
        noise = (random.random() * 2.0 - 1.0)
        filtered = 0.4 * noise + 0.6 * prev
        prev = filtered
        squeak = math.sin(2.0 * math.pi * (800 + 400 * math.sin(30 * t)) * t) * 0.2
        samples.append((filtered * 0.4 + squeak) * env * 0.45)
    write_wav("marker_sweep.wav", samples)

# 3. Page Turn (Paper flip / rustle)
def make_page_turn():
    duration = 0.6
    total_samples = int(duration * SAMPLE_RATE)
    samples = []
    prev = 0.0
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Envelope: fast rise, swoosh, decay
        env = (t / 0.15) * math.exp(-t / 0.18) * 2.5
        noise = (random.random() * 2.0 - 1.0)
        filtered = 0.15 * noise + 0.85 * prev
        prev = filtered
        whoosh = math.sin(2.0 * math.pi * (180 + 120 * (1 - t / duration)) * t) * 0.3
        samples.append((filtered * 0.6 + whoosh) * env * 0.5)
    write_wav("page_turn.wav", samples)

# 4. Pop (Bouncy UI pop for cards)
def make_pop():
    duration = 0.15
    total_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-35.0 * t)
        freq = 480.0 * math.exp(-25.0 * t) + 120.0
        wave_val = math.sin(2.0 * math.pi * freq * t)
        samples.append(wave_val * env * 0.6)
    write_wav("pop.wav", samples)

# 5. Ambient Meditative Drone / Music Bed (15 seconds loop)
def make_ambient_music():
    duration = 15.0
    total_samples = int(duration * SAMPLE_RATE)
    samples = []
    # Warm chords: D3 (146.83 Hz), A3 (220 Hz), D4 (293.66 Hz), F#4 (369.99 Hz)
    freqs = [146.83, 220.0, 293.66, 369.99, 440.0]
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Long gentle fade in and out for seamless looping
        env = math.sin(math.pi * (t / duration)) ** 0.5
        val = 0.0
        for idx, f in enumerate(freqs):
            # Slow LFO detune for natural warmth
            lfo = 1.0 + 0.003 * math.sin(0.4 * t + idx)
            amp = 0.18 / (idx + 1)
            val += math.sin(2.0 * math.pi * (f * lfo) * t) * amp
        # Add subtle shimmer
        shimmer = math.sin(2.0 * math.pi * 880 * t) * 0.015 * math.sin(1.5 * t)
        samples.append((val + shimmer) * env * 0.45)
    write_wav("ambient_music.wav", samples)

# 6. Ambient Documentary / Science Pulse (15 seconds loop)
def make_ambient_documentary():
    duration = 15.0
    total_samples = int(duration * SAMPLE_RATE)
    samples = []
    # Minor 7th chord: C3 (130.81), G3 (196.0), Bb3 (233.08), D4 (293.66)
    freqs = [130.81, 196.0, 233.08, 293.66]
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / duration)) ** 0.5
        val = 0.0
        # Warm pad chords
        for idx, f in enumerate(freqs):
            lfo = 1.0 + 0.002 * math.sin(0.3 * t + idx * 1.5)
            val += math.sin(2.0 * math.pi * (f * lfo) * t) * (0.16 / (idx + 1))
        # Deep rhythmic pulse at 1.0 Hz (60 BPM)
        pulse = (math.sin(2.0 * math.pi * 1.0 * t) ** 4) * 0.12 * math.sin(2.0 * math.pi * 65.4 * t)
        # Clock tick on each second
        phase = t % 1.0
        tick = math.exp(-60.0 * phase) * math.sin(2.0 * math.pi * 2400.0 * phase) * 0.035 if phase < 0.08 else 0.0
        samples.append((val + pulse + tick) * env * 0.5)
    write_wav("ambient_documentary.wav", samples)

# 7. Ambient Epic Cinematic Swell (15 seconds loop)
def make_ambient_epic_cinematic():
    duration = 15.0
    total_samples = int(duration * SAMPLE_RATE)
    samples = []
    # Epic minor progression: A2 (110.0), E3 (164.81), C4 (261.63), E4 (329.63), B4 (493.88)
    freqs = [110.0, 164.81, 261.63, 329.63, 493.88]
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / duration)) ** 0.5
        val = 0.0
        # Swell dynamic
        swell = 0.7 + 0.3 * math.sin(2.0 * math.pi * (t / 7.5))
        for idx, f in enumerate(freqs):
            detune = 1.0 + 0.004 * math.sin(0.25 * t + idx)
            val += math.sin(2.0 * math.pi * (f * detune) * t) * (0.2 / (idx + 1)) * swell
        # Sub-bass warmth
        sub = math.sin(2.0 * math.pi * 55.0 * t) * 0.15 * swell
        samples.append((val + sub) * env * 0.48)
    write_wav("ambient_epic_cinematic.wav", samples)

# 8. Ambient Mystic / Sufi Contemplation Drone (15 seconds loop)
def make_ambient_mystic():
    duration = 15.0
    total_samples = int(duration * SAMPLE_RATE)
    samples = []
    # Warm mystic drone: D2 (73.42), A2 (110.0), D3 (146.83), F#3 (185.0), A3 (220.0)
    freqs = [73.42, 110.0, 146.83, 185.0, 220.0]
    prev_noise = 0.0
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * (t / duration)) ** 0.5
        val = 0.0
        for idx, f in enumerate(freqs):
            drift = 1.0 + 0.0035 * math.sin(0.18 * t + idx * 0.8)
            val += math.sin(2.0 * math.pi * (f * drift) * t) * (0.18 / (idx + 1))
        # Ney breath whisper (soft filtered noise fluttering at 580 Hz)
        raw_noise = (random.random() * 2.0 - 1.0)
        filtered_noise = 0.15 * raw_noise + 0.85 * prev_noise
        prev_noise = filtered_noise
        breath = filtered_noise * math.sin(2.0 * math.pi * 587.33 * t) * (0.04 + 0.02 * math.sin(1.2 * t))
        samples.append((val + breath) * env * 0.5)
    write_wav("ambient_mystic.wav", samples)

if __name__ == "__main__":
    make_pen_draw()
    make_marker_sweep()
    make_page_turn()
    make_pop()
    make_ambient_music()
    make_ambient_documentary()
    make_ambient_epic_cinematic()
    make_ambient_mystic()
    print("All SFX and Ambient Music Tracks generated successfully!")
