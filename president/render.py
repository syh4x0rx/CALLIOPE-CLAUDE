#!/usr/bin/env python3
"""Render "What It's Like to Be President" from scenes.txt.

Pipeline: parse scenes -> synthesize narration per scene (Kokoro, offline)
-> draw the illustrations (art.py) -> lay out a timeline -> animate frames with
Pillow over the illustrations -> encode with ffmpeg.

Usage:
  python3 render.py --models DIR --work DIR --out president.mp4 [--speed 1.0]
DIR for --models must hold kokoro-v1.0.int8.onnx and voices-v1.0.bin
(https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0).
"""
import argparse
import json
import math
import os
import re
import subprocess
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 25
SR = 24000
HERE = os.path.dirname(os.path.abspath(__file__))
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

GOLD = (222, 184, 98)
WHITE = (245, 242, 235)
SCENE_GAP = 0.55        # silence after each scene
PARAGRAPH_GAP = 0.90    # extra silence at a paragraph break
CHAPTER_CARD = 3.2      # seconds a chapter title card holds
INTRO_PAD = 0.6
OUTRO = 4.0

# How the narrator should pronounce things the caption shows as digits.
SAY = [
    ("11:59", "eleven fifty-nine"),
    ("January 20th", "January twentieth"),
    ("1951", "nineteen fifty-one"),
    ("Mr.", "Mister"),
]


def parse_scenes(path):
    chapters, para = [], 0
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if line.startswith("# ") or line == "#":
            continue
        if line.startswith("## "):
            chapters.append({"title": line[3:].strip(), "scenes": []})
            para += 1
            continue
        if not line.strip():
            para += 1
            continue
        head, vo = [s.strip() for s in line.split("|", 1)]
        chapters[-1]["scenes"].append(
            {"head": head.replace("\\n", "\n"), "vo": vo, "para": para})
    return chapters


def spoken(text):
    for a, b in SAY:
        text = text.replace(a, b)
    return text


def synth(chapters, models, work, speed, voice):
    from kokoro_onnx import Kokoro
    import soundfile as sf
    k = Kokoro(os.path.join(models, "kokoro-v1.0.int8.onnx"),
               os.path.join(models, "voices-v1.0.bin"))
    os.makedirs(os.path.join(work, "vo"), exist_ok=True)
    i = 0
    for ch in chapters:
        for sc in ch["scenes"]:
            path = os.path.join(work, "vo", f"{i:03d}.wav")
            key = f"{voice}|{speed}|{spoken(sc['vo'])}"
            meta = path + ".key"
            if not (os.path.exists(path) and os.path.exists(meta)
                    and open(meta).read() == key):
                samples, sr = k.create(spoken(sc["vo"]), voice=voice,
                                       speed=speed, lang="en-us")
                assert sr == SR
                sf.write(path, samples, sr)
                open(meta, "w").write(key)
            sc["wav"] = path
            sc["dur"] = sf.info(path).duration
            i += 1


def build_timeline(chapters):
    """Return a flat list of segments with absolute start/end seconds."""
    from art_map import ART_FOR, REPEAT
    seen = set()
    for ch in chapters:
        for sc in ch["scenes"]:
            h = sc["head"]
            sc["art"] = REPEAT[h] if h in seen and h in REPEAT else ART_FOR[h]
            seen.add(h)
    t, segs, prev_para = INTRO_PAD, [], None
    for ci, ch in enumerate(chapters):
        if ci > 0:  # the cold open starts straight on the hook
            segs.append({"kind": "card", "ci": ci, "start": t,
                         "end": t + CHAPTER_CARD, "title": ch["title"],
                         "art": ch["scenes"][0]["art"]})
            t += CHAPTER_CARD
        for sc in ch["scenes"]:
            if prev_para is not None and sc["para"] != prev_para:
                t += PARAGRAPH_GAP
            prev_para = sc["para"]
            segs.append({"kind": "scene", "ci": ci, "start": t,
                         "voice_at": t + 0.15, "end": t + 0.15 + sc["dur"] + SCENE_GAP,
                         "head": sc["head"], "vo": sc["vo"], "wav": sc["wav"], "art": sc["art"],
                         "chapter": ch["title"]})
            t = segs[-1]["end"]
        prev_para = None
    # Stretch each segment to cover any pause before the next one.
    for a, b in zip(segs, segs[1:]):
        a["end"] = b["start"]
    segs.append({"kind": "outro", "ci": len(chapters) - 1, "start": segs[-1]["end"],
                 "end": segs[-1]["end"] + OUTRO, "art": "final"})
    return segs


# ---------------------------------------------------------------- audio

def pad_music(total, chapters_starts):
    """Quiet synthesized string-like pad that shifts chord every chapter."""
    n = int(total * SR)
    t = np.arange(n) / SR
    chords = [
        [110.0, 164.81, 220.0, 261.63],   # A minor
        [98.0, 146.83, 196.0, 246.94],    # G
        [87.31, 130.81, 174.61, 220.0],   # F
        [130.81, 196.0, 261.63, 329.63],  # C
    ]
    out = np.zeros(n, dtype=np.float32)
    bounds = list(chapters_starts) + [total]
    for i in range(len(bounds) - 1):
        a, b = int(bounds[i] * SR), int(bounds[i + 1] * SR)
        a0, b1 = max(0, a - SR), min(n, b + SR)  # 1 s overlap crossfade
        seg_t = t[a0:b1]
        env = np.ones(b1 - a0, dtype=np.float32)
        ramp = min(SR, (b1 - a0) // 2)
        env[:ramp] = np.linspace(0, 1, ramp)
        env[-ramp:] = np.linspace(1, 0, ramp)
        wave = np.zeros(b1 - a0, dtype=np.float32)
        for j, f in enumerate(chords[i % len(chords)]):
            lfo = 0.6 + 0.4 * np.sin(2 * math.pi * (0.05 + 0.02 * j) * seg_t + j)
            for h, amp in ((1, 1.0), (2, 0.35), (3, 0.15)):
                wave += amp * lfo * np.sin(2 * math.pi * f * h * seg_t + j * h)
        out[a0:b1] += wave * env
    out /= np.max(np.abs(out)) + 1e-9
    fade = np.ones(n, dtype=np.float32)
    fade[:3 * SR] = np.linspace(0, 1, 3 * SR)
    fade[-4 * SR:] = np.linspace(1, 0, 4 * SR)
    return out * fade * 10 ** (-27 / 20)


def build_audio(segs, work):
    import soundfile as sf
    total = segs[-1]["end"]
    mix = np.zeros(int(total * SR) + SR, dtype=np.float32)
    for s in segs:
        if s["kind"] != "scene":
            continue
        data, _ = sf.read(s["wav"], dtype="float32")
        a = int(s["voice_at"] * SR)
        mix[a:a + len(data)] += data * 0.95
    starts = [0.0] + [s["start"] for s in segs if s["kind"] == "card"]
    mix[:int(total * SR)] += pad_music(total, starts)
    mix = np.clip(mix, -1, 1)
    path = os.path.join(work, "mix.wav")
    sf.write(path, mix, SR)
    return path


# ---------------------------------------------------------------- visuals

def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            trial = (cur + " " + word).strip()
            if draw.textlength(trial, font=fnt) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def fit_headline(draw, text):
    for size in (118, 106, 96, 86, 76, 68):
        f = font(SERIF_BOLD, size)
        lines = wrap(draw, text, f, W - 400)
        if len(lines) <= 2 and all(draw.textlength(l, font=f) <= W - 400 for l in lines):
            return f, lines
    return f, lines


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def text_layer_scene(seg):
    """Lower-third text pieces rendered once per scene; animated by offsets/alpha."""
    scratch = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    cap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(cap)
    cf = font(SANS, 38)
    clines = wrap(d, seg["vo"], cf, W - 300)
    cap_top = H - 70 - 52 * len(clines)
    for i, line in enumerate(clines):
        x, y = 150, cap_top + i * 52
        d.text((x + 2, y + 2), line, font=cf, fill=(0, 0, 0, 200))
        d.text((x, y), line, font=cf, fill=WHITE)

    hf, hlines = fit_headline(scratch, seg["head"])
    head = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(head)
    lh = int(hf.size * 1.05)
    block_h = lh * len(hlines)
    y0 = cap_top - 34 - block_h
    for i, line in enumerate(hlines):
        x, y = 146, y0 + i * lh
        for ox, oy in ((4, 5), (2, 3), (-2, 3)):
            d.text((x + ox, y + oy), line, font=hf, fill=(0, 0, 0, 170))
        d.text((x, y), line, font=hf, fill=WHITE)
    rule_y = y0 - 18

    label = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(label)
    lf = font(SANS_BOLD, 26)
    d.text((92, 62), seg["chapter"].upper(), font=lf, fill=GOLD + (230,))
    return head, rule_y, cap, label


def render_segment(args):
    seg, idx, work, total = args
    out = os.path.join(work, "frames", f"{idx:03d}.mp4")
    meta = out + ".json"
    sig = json.dumps({k: seg.get(k) for k in ("kind", "head", "vo", "title", "start", "end", "ci", "art")})
    if os.path.exists(out) and os.path.exists(meta) and open(meta).read() == sig:
        return out
    art_img = Image.open(os.path.join(work, "art", seg["art"] + ".png")).convert("RGB")
    art_img = art_img.resize((int(W * 1.12), int(H * 1.12)), Image.LANCZOS)
    if seg["kind"] != "scene":
        art_img = art_img.filter(ImageFilter.GaussianBlur(10))
        art_img = Image.eval(art_img, lambda v: int(v * 0.45))
    aw, ah = art_img.size
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if seg["kind"] == "scene":
        col = np.zeros((H, 1), dtype=np.float32)
        yy = np.arange(H, dtype=np.float32)
        col[:, 0] = np.maximum(np.clip(1 - yy / 200, 0, 1) * 150,
                               np.clip((yy - (H - 470)) / 380, 0, 1) ** 0.8 * 225)
        alpha = Image.fromarray(np.repeat(col, W, axis=1).astype(np.uint8), "L")
        shade = Image.new("RGBA", (W, H), (5, 8, 16, 255))
        shade.putalpha(alpha)
    zoom_in = idx % 2 == 0
    pan = (-1) ** (idx // 2)
    f0 = round(seg["start"] * FPS)
    f1 = round(seg["end"] * FPS)
    n = f1 - f0
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
         "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", out],
        stdin=subprocess.PIPE)

    if seg["kind"] == "scene":
        head, rule_y, cap, label = text_layer_scene(seg)
    else:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        if seg["kind"] == "card":
            title = seg["title"]
            if ":" in title:
                small, big = [s.strip() for s in title.split(":", 1)]
            else:
                small, big = "", title
            sf_ = font(SANS_BOLD, 40)
            bf = font(SERIF_BOLD, 130)
            lines = wrap(d, big, bf, W - 300)
            y = H / 2 - (len(lines) * 145) / 2 + 20
            if small:
                tw = d.textlength(small.upper(), font=sf_)
                d.text(((W - tw) / 2, y - 90), small.upper(), font=sf_, fill=GOLD)
            for i, line in enumerate(lines):
                tw = d.textlength(line, font=bf)
                d.text(((W - tw) / 2 + 5, y + i * 145 + 6), line, font=bf, fill=(0, 0, 0, 150))
                d.text(((W - tw) / 2, y + i * 145), line, font=bf, fill=WHITE)
            d.rectangle([W / 2 - 120, y + len(lines) * 145 + 30,
                         W / 2 + 120, y + len(lines) * 145 + 36], fill=GOLD)
        else:  # outro
            bf = font(SERIF_BOLD, 120)
            itf = font(SERIF_ITALIC, 52)
            for text, f_, y, col in (("Would you take the job?", bf, H / 2 - 110, WHITE),
                                     ("What it's like to be President", itf, H / 2 + 60, GOLD)):
                tw = d.textlength(text, font=f_)
                d.text(((W - tw) / 2, y), text, font=f_, fill=col)

    for i in range(n):
        lt = i / FPS                      # local time
        gt = seg["start"] + lt            # global time
        # Ken Burns: slow zoom plus a gentle pan across the illustration.
        p = i / max(n - 1, 1)
        z = 1.0 + 0.10 * (p if zoom_in else 1 - p)
        cw, chh = aw / 1.12 / z, ah / 1.12 / z
        cx = aw / 2 + pan * (p - 0.5) * (aw - cw) * 0.8
        cy = ah / 2
        box = (cx - cw / 2, cy - chh / 2, cx + cw / 2, cy + chh / 2)
        frame = art_img.resize((W, H), Image.BILINEAR, box=box).convert("RGBA")
        frame.alpha_composite(shade)
        if seg["kind"] == "scene":
            a = ease(lt / 0.45)
            dy = int((1 - a) * 40)
            h = head.copy()
            if a < 1:
                h.putalpha(h.getchannel("A").point(lambda v, a=a: int(v * a)))
            frame.alpha_composite(h, (0, dy))
            # Gold rule above the headline grows in from the left.
            g = ease((lt - 0.2) / 0.6)
            if g > 0:
                ImageDraw.Draw(frame).rectangle(
                    [150, rule_y + dy, 150 + 200 * g, rule_y + 6 + dy], fill=GOLD)
            c = ease((lt - 0.1) / 0.3)
            if c < 1:
                cc = cap.copy()
                cc.putalpha(cc.getchannel("A").point(lambda v, c=c: int(v * c)))
                frame.alpha_composite(cc)
            else:
                frame.alpha_composite(cap)
            frame.alpha_composite(label)
        else:
            a = ease(lt / 0.8)
            l2 = layer.copy()
            l2.putalpha(l2.getchannel("A").point(lambda v, a=a: int(v * a)))
            frame.alpha_composite(l2)
        # Progress bar.
        ImageDraw.Draw(frame).rectangle([0, H - 8, int(W * gt / total), H], fill=GOLD + (200,))
        rgb = frame.convert("RGB")
        # Fades: in/out around chapter cards, and at the very start and end.
        fade = 1.0
        if seg["kind"] in ("card", "outro"):
            fade = min(fade, ease(lt / 0.5))
        if seg["kind"] == "outro":
            fade = min(fade, (seg["end"] - gt) / 2.0)
        if gt < 0.8:
            fade = min(fade, gt / 0.8)
        if fade < 1:
            rgb = Image.eval(rgb, lambda v, f=max(fade, 0): int(v * f))
        proc.stdin.write(rgb.tobytes())
    proc.stdin.close()
    proc.wait()
    open(meta, "w").write(sig)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", default="president.mp4")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--voice", default="am_michael")
    ap.add_argument("--audio-only", action="store_true")
    ap.add_argument("--jobs", type=int, default=os.cpu_count())
    args = ap.parse_args()

    chapters = parse_scenes(os.path.join(HERE, "scenes.txt"))
    synth(chapters, args.models, args.work, args.speed, args.voice)
    segs = build_timeline(chapters)
    total = segs[-1]["end"]
    nscenes = sum(s["kind"] == "scene" for s in segs)
    print(f"{nscenes} scenes, {len(chapters)} chapters, total {total:.1f}s ({total / 60:.2f} min)")
    with open(os.path.join(args.work, "timeline.json"), "w") as f:
        json.dump(segs, f, indent=1)
    if args.audio_only:
        return
    import art
    art.render_all(os.path.join(args.work, "art"))
    audio = build_audio(segs, args.work)
    os.makedirs(os.path.join(args.work, "frames"), exist_ok=True)
    with Pool(args.jobs) as pool:
        parts = pool.map(render_segment, [(s, i, args.work, total) for i, s in enumerate(segs)],
                         chunksize=1)
    lst = os.path.join(args.work, "parts.txt")
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-i", audio, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", args.out], check=True)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
