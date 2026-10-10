"""Synthesized sound effects (numpy only, 44.1 kHz mono float32)."""
import numpy as np

SR = 44100
_rng = np.random.default_rng(7)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a=0.005, r=0.2, shape=2.0):
    """Attack/decay envelope over n samples."""
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(t - a, 0) / max(r, 1e-4)) ** (1 / shape)
    return e.astype(np.float32)


def _lowpass(x, cutoff):
    """One-pole lowpass; cutoff may be an array (time-varying)."""
    if np.ndim(cutoff) == 0:
        from scipy.signal import lfilter
        a = np.exp(-2 * np.pi * float(cutoff) / SR)
        return lfilter([1 - a], [1, -a], x)
    cutoff = np.broadcast_to(np.asarray(cutoff, dtype=np.float64), x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def _bandish(x, lo, hi):
    return _lowpass(x, hi) - _lowpass(x, lo)


def _norm(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-9
    return (x / m * peak).astype(np.float32)


def noise(n):
    return _rng.standard_normal(n).astype(np.float64)


def whoosh(d=0.7, rise=True):
    n = int(d * SR)
    t = np.linspace(0, 1, n)
    bell = np.sin(np.pi * t) ** 2
    cut = 300 + 5000 * (t if rise else 1 - t) ** 1.5 + 2500 * bell
    x = _bandish(noise(n), 120, cut) * bell
    return _norm(x, .8)


def swish(d=0.35):
    return whoosh(d)


def pop(f0=900, f1=260, d=0.12):
    t = _t(d)
    f = f0 * (f1 / f0) ** (t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t / 0.045)
    x[:60] += noise(60) * np.linspace(1, 0, 60) * .5
    return _norm(x, .7)


def boom(d=1.8):
    t = _t(d)
    f = 70 * (38 / 70) ** (t / d)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.55)
    hit = _lowpass(noise(len(t)), 900) * np.exp(-t / 0.08) * 2.5
    tail = _lowpass(noise(len(t)), 200) * np.exp(-t / 0.7) * 1.2
    return _norm(body + hit + tail, .95)


def tick(d=0.05):
    t = _t(d)
    x = (np.sin(2 * np.pi * 3200 * t) + .6 * np.sin(2 * np.pi * 5100 * t)) * np.exp(-t / 0.006)
    return _norm(x, .5)


def stamp():
    t = _t(.5)
    thud = np.sin(2 * np.pi * 95 * t) * np.exp(-t / 0.07)
    slap = _bandish(noise(len(t)), 300, 4000) * np.exp(-t / 0.03)
    return _norm(thud * 1.4 + slap, .9)


def shutter():
    out = np.zeros(int(.25 * SR))
    for start in (0.0, 0.07):
        n = int(.04 * SR)
        s = int(start * SR)
        out[s:s + n] += _bandish(noise(n), 1500, 9000) * np.exp(-np.arange(n) / SR / 0.008)
    return _norm(out, .6)


def ding(f=1318.5, d=1.6):
    t = _t(d)
    x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / (0.6 / m ** .5)) for m, a in ((1, 1), (2.76, .5), (5.4, .25), (8.9, .12)))
    return _norm(x, .55)


def register():
    a = ding(1568, 1.4)
    b = np.zeros(int(.12 * SR) + len(a))
    b[:len(a)] += a
    c = ding(2093, 1.2)
    b[int(.12 * SR):int(.12 * SR) + len(c)] += c
    return _norm(b, .55)


def thump_loop(d, rate=9.0, cutoff=350, depth=.9):
    t = _t(d)
    mod = (0.5 + 0.5 * np.sin(2 * np.pi * rate * t)) ** 6
    x = _lowpass(noise(len(t)), cutoff) * (1 - depth + depth * mod)
    fade = np.minimum(1, np.minimum(t / .6, (d - t) / .6))
    return _norm(x * fade, .7)


def jet(d):
    t = _t(d)
    x = _lowpass(noise(len(t)), 500 + 300 * np.sin(np.pi * t / d)) + .3 * _bandish(noise(len(t)), 1500, 4000)
    fade = np.sin(np.pi * np.clip(t / d, 0, 1)) ** .7
    return _norm(x * fade, .6)


def cheer(d=3.0, claps=60):
    t = _t(d)
    crowd = _bandish(noise(len(t)), 400, 2600)
    crowd *= 0.6 + 0.4 * _lowpass(np.abs(noise(len(t))), 3)
    out = crowd * .5
    for _ in range(claps):
        s = int(_rng.uniform(0, d - .05) * SR)
        n = int(.02 * SR)
        out[s:s + n] += _bandish(noise(n), 800, 7000) * np.exp(-np.arange(n) / SR / .004) * _rng.uniform(.4, 1)
    fade = np.minimum(1, np.minimum(t / .3, (d - t) / .8))
    return _norm(out * fade, .55)


def paper(d=0.6):
    t = _t(d)
    grains = (_rng.random(len(t)) < 0.004).astype(float) * _rng.uniform(.3, 1, len(t))
    x = _bandish(noise(len(t)), 1500, 8000) * (_lowpass(grains, 60) * 40 + .05)
    fade = np.minimum(1, np.minimum(t / .05, (d - t) / .2))
    return _norm(x * fade, .45)


def scribble(d=1.8):
    t = _t(d)
    am = 0.5 + 0.5 * np.sin(2 * np.pi * 7 * t + 2 * np.sin(2 * np.pi * 1.3 * t))
    x = _bandish(noise(len(t)), 1800, 6000) * am
    fade = np.minimum(1, np.minimum(t / .05, (d - t) / .1))
    return _norm(x * fade, .35)


def phone_ring(d=2.0):
    t = _t(d)
    tone = np.sin(2 * np.pi * 440 * t) + np.sin(2 * np.pi * 480 * t)
    trill = (np.sin(2 * np.pi * 20 * t) > 0).astype(float)
    gate = ((t % 2.0) < 1.2).astype(float)
    return _norm(tone * trill * gate * np.minimum(1, (d - t) / .05), .4)


def gavel():
    out = np.zeros(int(.6 * SR))
    for s in (0.0, 0.22):
        t = _t(.25)
        knock = (np.sin(2 * np.pi * 820 * t) + .6 * np.sin(2 * np.pi * 1290 * t)) * np.exp(-t / 0.025)
        knock += _bandish(noise(len(t)), 500, 3000) * np.exp(-t / 0.01)
        i = int(s * SR)
        out[i:i + len(t)] += knock
    return _norm(out, .8)


def sparkle(d=1.0):
    t = _t(d)
    out = np.zeros(len(t))
    for k, f in enumerate((2637, 3136, 3951, 4699, 5274)):
        s = int(k * .08 * SR)
        tt = t[:len(t) - s]
        out[s:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.15)
    return _norm(out, .3)


def riser(d=1.2):
    t = _t(d)
    f = 200 * (1200 / 200) ** (t / d)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * .3 + _bandish(noise(len(t)), 300, 600 + 6000 * (t / d) ** 2) * .7
    return _norm(x * (t / d) ** 2, .6)


def car_pass(d=2.0):
    t = _t(d)
    x = _lowpass(noise(len(t)), 250 + 600 * np.exp(-((t - d / 2) / .4) ** 2))
    return _norm(x * np.exp(-((t - d / 2) / (d / 3)) ** 2), .6)


def siren_chirp(d=0.8):
    t = _t(d)
    f = 700 + 500 * np.abs(np.sin(2 * np.pi * 1.25 * t))
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .3
    return _norm(_lowpass(x, 3000) * np.minimum(1, (d - t) / .1), .25)


def gobble():
    t = _t(.6)
    f = 380 + 120 * np.sin(2 * np.pi * 28 * t)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * t))
    return _norm(_lowpass(x, 1800) * np.exp(-t / .25), .4)


def bat_crack():
    t = _t(.3)
    x = _bandish(noise(len(t)), 800, 6000) * np.exp(-t / 0.01) + np.sin(2 * np.pi * 1700 * t) * np.exp(-t / 0.02)
    return _norm(x, .7)


def heartbeat(d=1.6):
    out = np.zeros(int(d * SR))
    for s in (0.0, 0.25):
        t = _t(.2)
        beat = np.sin(2 * np.pi * 55 * t) * np.exp(-t / .05)
        i = int(s * SR)
        out[i:i + len(t)] += beat
    return _norm(out, .8)


LIB = {
    "whoosh": lambda: whoosh(.7), "swish": lambda: swish(.35), "pop": pop, "boom": boom, "tick": tick,
    "stamp": stamp, "shutter": shutter, "ding": ding, "register": register, "cheer": cheer,
    "paper": paper, "scribble": scribble, "phone": phone_ring, "gavel": gavel, "sparkle": sparkle,
    "riser": riser, "car": car_pass, "siren": siren_chirp, "gobble": gobble, "crack": bat_crack,
    "heartbeat": heartbeat, "pophi": lambda: pop(1400, 600, .09), "poplo": lambda: pop(600, 180, .14),
}
LOOPS = {"helicopter": lambda d: thump_loop(d, 9.5, 300), "jet": jet,
         "rumble": lambda d: thump_loop(d, 0.6, 140, .3), "crowd": lambda d: cheer(d, int(d * 15))}
