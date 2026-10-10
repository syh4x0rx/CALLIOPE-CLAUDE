#!/usr/bin/env python3
"""Render "What It's Like to Be President" from scenes.txt.

Pipeline:
  1. parse scenes.txt and synthesize narration per scene (Kokoro, offline)
  2. lay out a timeline (chapter cards, scenes, pauses, outro)
  3. audio: narration + generative orchestral score (music.py, ducked under
     the voice) + synthesized sound effects cued to the animation (sfx.py)
  4. video: one animated HTML page per segment (anim.py + art.py), captured
     frame by frame with headless Chromium (capture.mjs)
  5. concat + mux + loudness-normalize with ffmpeg; thumbnail (thumbnail.py)

Usage:
  python3 render.py --models DIR --sf2 FILE --work DIR --out president.mp4
--models holds kokoro-v1.0.onnx and voices-v1.0.bin
(https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0);
--sf2 is a General MIDI SoundFont (GeneralUser GS:
https://github.com/mrbumpy409/GeneralUser-GS).
"""
import argparse
import json
import os
import subprocess

import numpy as np

FPS = 25
VOICE_SR = 24000
SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))

SCENE_GAP = 0.80        # silence after each scene
PARAGRAPH_GAP = 1.20    # extra silence at a paragraph break
CHAPTER_CARD = 4.0      # seconds a chapter title card holds
INTRO_PAD = 0.8
OUTRO = 8.0

# How the narrator should pronounce things the caption shows as digits.
SAY = [
    ("11:59", "eleven fifty-nine"),
    ("January 20th", "January twentieth"),
    ("1951", "nineteen fifty-one"),
    ("Mr.", "Mister"),
]

# Sound effects cued at the start of a run of scenes sharing an illustration:
# (effect, seconds after the run starts, gain). "@" entries fill the whole run.
ART_SFX = {
    "clock_1159": [("@ticks", 0, .5)],
    "clock_noon": [("boom", .32, 1.0), ("whoosh", 0, .5)],
    "choice": [("pop", .1, .6), ("pop", .5, .6), ("@ticks", 0, .3)],
    "capitol": [("@crowd", 0, .25), ("@shutters", 0, .3)],
    "oath": [("whoosh", .05, .5), ("swish", .35, .4)],
    "briefcase": [("heartbeat", .2, .7), ("heartbeat", 1.8, .6)],
    "money": [("pophi", .1 + i * .12, .35) for i in range(9)] + [("register", 1.3, .6)],
    "constitution": [("scribble", .3, .5), ("paper", .1, .5)],
    "campaign": [("@crowd", 0, .45)],
    "statefair": [("pop", .2, .4), ("@crowd", 0, .15)],
    "speech": [("whoosh", 0, .4), ("@crowd", 0, .12)],
    "election": [("paper", .5, .5), ("paper", 2.0, .4), ("paper", 3.5, .4)],
    "movers": [("car", 0, .7)] + [("poplo", .8 + i * .25, .5) for i in range(4)],
    "toothbrush": [("sparkle", .3, .6), ("pop", .25, .4), ("pop", .5, .4)],
    "bowling": [("@bowling", 0, .7)],
    "chef": [("ding", .2, .5)],
    "receipt": [("scribble", 0, .4), ("register", 2.3, .6)],
    "paycheck": [("whoosh", 0, .5), ("scribble", .3, .4), ("register", 1.2, .6)],
    "population": [("@crowd", 0, .3)],
    "pdb": [("paper", .1, .6), ("stamp", .95, .9)],
    "world_map": [("pophi", .3, .5), ("pophi", .8, .5), ("pophi", 1.3, .5), ("riser", 0, .25)],
    "resolute_desk": [("sparkle", .4, .4)],
    "schedule": [("pophi", .1 + i * .18, .25) for i in range(8)],
    "phone_call": [("@phone", 0, .35)],
    "little_league": [("@shutters", 0, .5), ("@crowd", 0, .15)],
    "congress": [("@gavel", 0, .6), ("@crowd", 0, .12)],
    "secret_service": [("swish", 0, .5), ("swish", .2, .5), ("swish", .4, .5)],
    "hallway_door": [("heartbeat", .3, .4)],
    "motorcade": [("@rumble", 0, .5), ("siren", .2, .4)],
    "no_driving": [("car", 0, .6), ("stamp", .62, .9)],
    "aide": [("heartbeat", .2, .5)],
    "crossroads": [("whoosh", 0, .4)],
    "troops": [("@rumble", 0, .4)],
    "bill_signing": [("scribble", 0, .6)],
    "veto": [("stamp", .37, 1.0)],
    "situation_room": [("@rumble", 0, .3), ("heartbeat", .5, .35)],
    "divided": [("@crowd", 0, .3)],
    "letters": [("paper", .05 + i * .36, .4) for i in range(5)],
    "letter_open": [("scribble", .3, .4), ("paper", 0, .4)],
    "turkey": [("gobble", .6, .7), ("gobble", 3.2, .6), ("@crowd", 0, .12)],
    "baseball": [("@crowd", 0, .3), ("crack", 2.2, .5)],
    "easter": [("sparkle", .2, .4), ("@crowd", 0, .12)],
    "christmas_tree": [("sparkle", 0, .5), ("ding", 1.0, .35)],
    "air_force_one": [("@jet", 0, .55)],
    "plane_interior": [("@rumble", 0, .4)],
    "helicopter": [("@helicopter", 0, .6)],
    "portrait_aging": [("pop", .1, .5), ("pop", 1.0, .5)],
    "press": [("@shutters", 0, .7)],
    "homecoming": [("@crowd", 0, .45)],
    "tornado_town": [("@rumble", 0, .4), ("whoosh", 0, .3)],
    "amendment": [("paper", .1, .4), ("pop", 1.9, .5), ("pop", 2.3, .5)],
    "hourglass": [("@ticks", 0, .25)],
    "desk_letter": [("paper", .3, .5)],
    "exit_door": [("whoosh", 0, .3)],
    "library": [("poplo", .2, .5), ("poplo", .5, .5), ("poplo", .8, .5)],
}


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


def synth(chapters, models, work, speed, voice, model_file="kokoro-v1.0.onnx"):
    import soundfile as sf
    k = None
    os.makedirs(os.path.join(work, "vo"), exist_ok=True)
    i = 0
    for ch in chapters:
        for sc in ch["scenes"]:
            path = os.path.join(work, "vo", f"{i:03d}.wav")
            key = f"{voice}|{speed}|{spoken(sc['vo'])}"
            meta = path + ".key"
            if not (os.path.exists(path) and os.path.exists(meta)
                    and open(meta).read() == key):
                if k is None:
                    from kokoro_onnx import Kokoro
                    k = Kokoro(os.path.join(models, model_file), os.path.join(models, "voices-v1.0.bin"))
                samples, sr = k.create(spoken(sc["vo"]), voice=voice, speed=speed, lang="en-us")
                assert sr == VOICE_SR
                sf.write(path, samples, sr)
                open(meta, "w").write(key)
            sc["wav"] = path
            sc["dur"] = sf.info(path).duration
            i += 1


def build_timeline(chapters):
    """Flat list of segments with absolute start/end seconds and camera runs."""
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
            segs.append({"kind": "card", "ci": ci, "start": t, "end": t + CHAPTER_CARD,
                         "title": ch["title"], "art": ch["scenes"][0]["art"]})
            t += CHAPTER_CARD
        for sc in ch["scenes"]:
            if prev_para is not None and sc["para"] != prev_para:
                t += PARAGRAPH_GAP
            prev_para = sc["para"]
            segs.append({"kind": "scene", "ci": ci, "start": t, "voice_at": t + 0.25,
                         "end": t + 0.25 + sc["dur"] + SCENE_GAP, "vo_dur": sc["dur"],
                         "head": sc["head"], "vo": sc["vo"], "wav": sc["wav"], "art": sc["art"],
                         "chapter": ch["title"]})
            t = segs[-1]["end"]
        prev_para = None
    segs[0]["start"] = 0.0
    for a, b in zip(segs, segs[1:]):
        a["end"] = b["start"]
    segs.append({"kind": "outro", "ci": len(chapters) - 1, "start": segs[-1]["end"],
                 "end": segs[-1]["end"] + OUTRO, "art": "final"})
    # Runs: consecutive scenes that share an illustration keep one camera move
    # and one animation clock.
    run_i, i = 0, 0
    while i < len(segs):
        j = i
        while (j + 1 < len(segs) and segs[j + 1]["art"] == segs[i]["art"]
               and segs[j + 1]["kind"] == "scene" and segs[i]["kind"] == "scene"):
            j += 1
        for k in range(i, j + 1):
            segs[k]["run"] = {"index": run_i, "start": segs[i]["start"], "end": segs[j]["end"],
                              "offset": segs[k]["start"] - segs[i]["start"], "first": k == i}
        run_i += 1
        i = j + 1
    return segs


# ---------------------------------------------------------------- audio

def _resample(x, sr_in, sr_out):
    from math import gcd
    from scipy.signal import resample_poly
    g_ = gcd(sr_in, sr_out)
    return resample_poly(x, sr_out // g_, sr_in // g_).astype(np.float32)


def _smooth(x, sec):
    from scipy.signal import lfilter
    a = np.exp(-1 / (sec * SR))
    return lfilter([1 - a], [1, -a], x)


def build_audio(segs, work, sf2):
    import soundfile as sf
    import music
    import sfx

    total = segs[-1]["end"]
    n = int(total * SR) + SR
    voice = np.zeros(n, dtype=np.float32)
    for s in segs:
        if s["kind"] != "scene":
            continue
        data, sr = sf.read(s["wav"], dtype="float32")
        data = _resample(data, sr, SR)
        a = int(s["voice_at"] * SR)
        voice[a:a + len(data)] += data
    voice *= 0.9 / (np.max(np.abs(voice)) + 1e-9)

    # Music: one span per chapter (from its card to the next card), ducked
    # under the narration.
    starts = [0.0] + [s["start"] for s in segs if s["kind"] == "card"]
    spans = list(zip(starts, starts[1:] + [total]))
    score = music.score(spans, sf2)
    mus = np.zeros((n, 2), dtype=np.float32)
    mus[:min(n, len(score))] = score[:n]
    act = (_smooth(np.abs(voice), 0.05) > 0.01).astype(np.float64)
    duck = _smooth(_smooth(act, 0.25)[::-1], 0.08)[::-1]
    gain = 0.30 - 0.19 * np.clip(duck, 0, 1)
    mus *= gain[:, None].astype(np.float32)

    # Sound effects.
    fx = np.zeros(n, dtype=np.float32)
    cache = {}

    def add(x, t, g_):
        a = int(max(t, 0) * SR)
        if a >= n:
            return
        b = min(n, a + len(x))
        fx[a:b] += x[:b - a] * g_

    def place(name, t, g_):
        if name not in cache:
            cache[name] = sfx.LIB[name]()
        add(cache[name], t, g_)

    for s in segs:
        if s["kind"] == "card":
            place("whoosh", s["start"] - 0.15, .6)
            place("boom", s["start"] + .38, .55)
        elif s["kind"] == "outro":
            place("boom", s["start"] + .38, .6)
        elif s["kind"] == "scene":
            place("swish", s["start"] + .05, .18)
        if not s["run"]["first"]:
            continue
        r0, r1 = s["run"]["start"], s["run"]["end"]
        dur = r1 - r0
        for name, off, g_ in ART_SFX.get(s["art"], []):
            if not name.startswith("@"):
                place(name, r0 + off, g_)
                continue
            loop = name[1:]
            if loop == "ticks":
                for k in range(int(dur)):
                    place("tick", r0 + k + .02, g_)
            elif loop == "shutters":
                rng = np.random.default_rng(int(r0 * 10))
                for tt in np.sort(rng.uniform(0, dur, int(dur * 1.2))):
                    place("shutter", r0 + tt, g_ * rng.uniform(.5, 1))
            elif loop == "bowling":
                for k in range(int(dur / 2.5) + 1):
                    place("crack", r0 + 1.95 + k * 2.5, g_ * .7)
            elif loop == "gavel":
                for k in range(int(dur / 1.6) + 1):
                    place("gavel", r0 + .8 + k * 1.6, g_)
            elif loop == "phone":
                add(sfx.phone_ring(min(dur, 6)), r0, g_)
            else:
                add(sfx.LOOPS[loop](dur), r0, g_)
    fx *= 0.5

    mix = mus + (voice + fx)[:, None]
    mix = np.clip(mix, -1, 1)[:int(total * SR)]
    path = os.path.join(work, "mix.wav")
    sf.write(path, mix, SR)
    return path


# ---------------------------------------------------------------- video

def build_pages(segs, work):
    import anim
    import art
    total = segs[-1]["end"]
    os.makedirs(os.path.join(work, "pages"), exist_ok=True)
    os.makedirs(os.path.join(work, "clips"), exist_ok=True)
    art_cache, jobs = {}, []
    for i, s in enumerate(segs):
        if s["art"] not in art_cache:
            art_cache[s["art"]] = art.ART[s["art"]]()
        run = s["run"]
        cam = {"run_dur": run["end"] - run["start"], "zoom_in": run["index"] % 2 == 0,
               "pan": 1 if (run["index"] // 2) % 2 == 0 else -1, "first": run["first"]}
        html_path = os.path.join(work, "pages", f"{i:03d}.html")
        doc = anim.page(s, art_cache[s["art"]], total, cam)
        out = os.path.join(work, "clips", f"{i:03d}.mp4")
        f0, f1 = round(s["start"] * FPS), round(s["end"] * FPS)
        job = {"html": html_path, "out": out, "frames": f1 - f0, "fps": FPS, "artOffset": run["offset"]}
        sig = json.dumps(job) + doc
        if not (os.path.exists(html_path + ".sig") and open(html_path + ".sig").read() == sig):
            with open(html_path, "w") as f:
                f.write(doc)
            with open(html_path + ".sig", "w") as f:
                f.write(sig)
            for stale in (out, out + ".ok"):
                if os.path.exists(stale):
                    os.remove(stale)
        jobs.append(job)
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True)
    ap.add_argument("--sf2", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", default="president.mp4")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only", help="comma-separated segment indexes to capture (preview)")
    ap.add_argument("--audio-only", action="store_true")
    ap.add_argument("--node-modules", default=None, help="dir containing playwright-core")
    args = ap.parse_args()

    chapters = parse_scenes(os.path.join(HERE, "scenes.txt"))
    synth(chapters, args.models, args.work, args.speed, args.voice)
    segs = build_timeline(chapters)
    total = segs[-1]["end"]
    print(f"{sum(s['kind'] == 'scene' for s in segs)} scenes, {len(chapters)} chapters, "
          f"total {total:.1f}s ({total / 60:.2f} min)", flush=True)
    with open(os.path.join(args.work, "timeline.json"), "w") as f:
        json.dump(segs, f, indent=1)
    if not args.only:
        audio = build_audio(segs, args.work, args.sf2)
        print("audio:", audio, flush=True)
    if args.audio_only:
        return
    jobs = build_pages(segs, args.work)
    run_jobs = [jobs[int(i)] for i in args.only.split(",")] if args.only else jobs
    jobs_path = os.path.join(args.work, "jobs.json")
    with open(jobs_path, "w") as f:
        json.dump(run_jobs, f)
    env = dict(os.environ)
    if args.node_modules:
        env["PLAYWRIGHT_CORE"] = os.path.join(args.node_modules, "playwright-core")
    subprocess.run(["node", os.path.join(HERE, "capture.mjs"), jobs_path, str(args.workers)], check=True, env=env)
    if args.only:
        return
    lst = os.path.join(args.work, "clips.txt")
    with open(lst, "w") as f:
        for j in jobs:
            f.write(f"file '{j['out']}'\n")
    video = os.path.join(args.work, "video.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", video], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", audio, "-c:v", "copy",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", args.out], check=True)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
