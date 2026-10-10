"""Generative orchestral underscore rendered with a General MIDI SoundFont.

Each chapter gets a mood (key, chord progression, instrumentation). Notes are
generated per bar, rendered with tinysoundfont, and chapters are crossfaded.
"""
import random

import numpy as np

SR = 44100

# General MIDI presets (0-based).
PIANO, CELESTA, GLOCK, MARIMBA = 0, 8, 9, 12
CONTRABASS, TREMOLO, PIZZ, HARP, TIMPANI = 43, 44, 45, 46, 47
STRINGS, SLOW_STRINGS, HORN, BRASS, BASSOON, FLUTE = 48, 49, 60, 61, 70, 73

MAJ, MIN = (0, 4, 7), (0, 3, 7)
PROG = {
    "major": [(0, MAJ), (7, MAJ), (9, MIN), (5, MAJ)],
    "minor": [(0, MIN), (8, MAJ), (3, MAJ), (10, MAJ)],
    "suspense": [(0, MIN), (0, MIN), (8, MAJ), (7, MAJ)],
    "emotional": [(0, MAJ), (7, MAJ), (9, MIN), (5, MAJ)],
}
MOODS = {
    #           tonic, progression, bpm, layers
    "epic":      (62, "minor", 84, ["pad", "ostinato", "timpani", "horn"]),
    "light":     (60, "major", 100, ["pizz", "softpad", "bass"]),
    "grand":     (65, "major", 92, ["pad", "arp", "horn", "timpani", "bass"]),
    "busy":      (67, "major", 108, ["marimba", "pizz", "softpad", "bass"]),
    "suspense":  (64, "suspense", 80, ["tremolo", "pulse", "highpiano"]),
    "tension":   (60, "suspense", 76, ["tremolo", "pulse", "timpani", "highpiano"]),
    "whimsical": (70, "major", 104, ["celesta", "pizz", "bass"]),
    "road":      (62, "major", 112, ["pad", "arp", "horn", "bass", "ostinato"]),
    "reflective": (69, "minor", 76, ["arp", "softpad"]),
    "emotional": (65, "emotional", 80, ["arp", "pad", "horn", "bass"]),
    "finale":    (60, "emotional", 76, ["arp", "pad", "horn", "bass", "timpani"]),
}
CHAPTER_MOODS = ["epic", "light", "grand", "busy", "suspense", "tension", "whimsical",
                 "road", "reflective", "emotional", "finale"]
CHANNELS = {"pad": (0, STRINGS), "softpad": (1, SLOW_STRINGS), "ostinato": (2, STRINGS), "timpani": (3, TIMPANI),
            "horn": (4, HORN), "pizz": (5, PIZZ), "bass": (6, CONTRABASS), "arp": (7, PIANO),
            "marimba": (8, MARIMBA), "tremolo": (10, TREMOLO), "pulse": (11, PIZZ), "highpiano": (12, PIANO),
            "celesta": (13, CELESTA)}


def chord_notes(tonic, root_off, quality, octave_shift=0):
    root = tonic + root_off + 12 * octave_shift
    return [root + q for q in quality]


def compose(mood, duration, seed):
    """Return note events (start, dur, chan, key, vel) for one chapter."""
    tonic, prog_name, bpm, layers = MOODS[mood]
    prog = PROG[prog_name]
    rnd = random.Random(seed)
    beat = 60 / bpm
    bar = beat * 4
    ev = []
    nbars = int(duration / bar) + 2
    melody_prev = tonic + 12
    for b in range(nbars):
        t0 = b * bar
        root_off, q = prog[b % len(prog)]
        tri = chord_notes(tonic, root_off, q)
        ch = lambda name: CHANNELS[name][0]
        if "pad" in layers:
            for k in chord_notes(tonic, root_off, q, -1) + [tri[0]]:
                ev.append((t0, bar * 1.02, ch("pad"), k, 58))
        if "softpad" in layers:
            for k in chord_notes(tonic, root_off, q, -1):
                ev.append((t0, bar * 1.02, ch("softpad"), k, 48))
        if "tremolo" in layers:
            for k in chord_notes(tonic, root_off, q, -1):
                ev.append((t0, bar * 1.02, ch("tremolo"), k, 50))
        if "bass" in layers:
            r = tonic + root_off - 24
            ev.append((t0, beat * 1.9, ch("bass"), r, 70))
            ev.append((t0 + 2 * beat, beat * 1.9, ch("bass"), r + 7 if rnd.random() < .5 else r, 62))
        if "ostinato" in layers:
            r = tonic + root_off - 12
            for i in range(8):
                ev.append((t0 + i * beat / 2, beat / 2 * .8, ch("ostinato"), r if i % 2 == 0 else r + 12, 62 if i % 4 == 0 else 50))
        if "pulse" in layers:
            r = tonic + root_off - 24
            for i in range(8):
                ev.append((t0 + i * beat / 2, beat / 3, ch("pulse"), r, 62 if i % 2 == 0 else 44))
        if "pizz" in layers:
            pattern = [tri[0] - 12, tri[1], tri[2], tri[1]]
            for i, k in enumerate(pattern):
                ev.append((t0 + i * beat, beat * .5, ch("pizz"), k, 66 if i == 0 else 54))
        if "marimba" in layers:
            for i in range(8):
                k = rnd.choice(tri) + 12 * rnd.choice([0, 1])
                if rnd.random() < .8:
                    ev.append((t0 + i * beat / 2, beat / 2, ch("marimba"), k, rnd.randint(48, 66)))
        if "arp" in layers:
            seq = chord_notes(tonic, root_off, q, -1) + tri + [tri[0] + 12]
            for i in range(8):
                k = seq[(i if (b // 2) % 2 == 0 else 7 - i) % len(seq)]
                ev.append((t0 + i * beat / 2, beat * 1.2, ch("arp"), k, 52 if i % 2 else 60))
        if "highpiano" in layers and b % 2 == 0:
            for i in (0, 3):
                ev.append((t0 + i * beat, beat * 2, ch("highpiano"), rnd.choice(tri) + 24, 42))
        if "celesta" in layers:
            scale = [0, 2, 4, 5, 7, 9, 11, 12]
            for i in range(8):
                if rnd.random() < .65:
                    k = tonic + 12 + rnd.choice(scale) + root_off * 0
                    ev.append((t0 + i * beat / 2, beat / 2, ch("celesta"), k, rnd.randint(50, 70)))
        if "horn" in layers and b % 2 == 1:
            cands = [n + 12 for n in tri] + tri
            k = min(cands, key=lambda n: abs(n - melody_prev) + rnd.random() * 4)
            melody_prev = k
            ev.append((t0, bar * 1.9, ch("horn"), k - 12, 54))
        if "timpani" in layers and b % 4 == 0:
            r = tonic + root_off - 24
            ev.append((t0, beat * 2, ch("timpani"), r, 92))
            if mood in ("tension", "epic"):
                ev.append((t0 + 2.5 * beat, beat, ch("timpani"), r, 64))
                ev.append((t0 + 3 * beat, beat, ch("timpani"), r, 72))
    return ev, bar


def render_events(events, duration, sf2, gain=0.0):
    import tinysoundfont
    synth = tinysoundfont.Synth(samplerate=SR, gain=gain)
    sfid = synth.sfload(sf2)
    used = {}
    for name, (chan, preset) in CHANNELS.items():
        used.setdefault(chan, preset)
    for chan, preset in used.items():
        synth.program_select(chan, sfid, 0, preset)
    timeline = []
    for start, dur, chan, key, vel in events:
        if start >= duration:
            continue
        timeline.append((start, 1, chan, key, vel))
        timeline.append((min(start + dur, duration + 3), 0, chan, key, 0))
    timeline.sort(key=lambda e: (e[0], e[1]))
    total = int((duration + 4) * SR)
    out = np.zeros((total, 2), dtype=np.float32)
    pos = 0
    for t, on, chan, key, vel in timeline:
        target = min(int(t * SR), total)
        if target > pos:
            buf = np.frombuffer(synth.generate(target - pos), dtype=np.float32).reshape(-1, 2)
            out[pos:target] = buf
            pos = target
        if on:
            synth.noteon(chan, key, vel)
        else:
            synth.noteoff(chan, key)
    if pos < total:
        out[pos:] = np.frombuffer(synth.generate(total - pos), dtype=np.float32).reshape(-1, 2)
    return out


def score(spans, sf2, seed=11):
    """spans: list of (start_sec, end_sec) per chapter. Returns stereo music."""
    total = spans[-1][1]
    mix = np.zeros((int((total + 6) * SR), 2), dtype=np.float32)
    for i, (a, b) in enumerate(spans):
        mood = CHAPTER_MOODS[min(i, len(CHAPTER_MOODS) - 1)]
        dur = b - a + 1.5
        ev, _ = compose(mood, dur, seed + i)
        audio = render_events(ev, dur, sf2)
        n = len(audio)
        env = np.ones(n, dtype=np.float32)
        fi = int(0.4 * SR)
        env[:fi] = np.linspace(0, 1, fi)
        last = i == len(spans) - 1
        fo_start = int((dur - (0.1 if not last else 0)) * SR) if not last else int((b - a - 3.5) * SR)
        fo_len = int((1.6 if not last else 6.0) * SR)
        if fo_start < n:
            seg = min(fo_len, n - fo_start)
            env[fo_start:fo_start + seg] *= np.linspace(1, 0, seg)
            env[fo_start + seg:] = 0
        s = int(max(a - 0.3, 0) * SR)
        e = min(s + n, len(mix))
        mix[s:e] += audio[:e - s] * env[:e - s, None]
    peak = np.max(np.abs(mix)) + 1e-9
    return mix[:int(total * SR)] / peak
