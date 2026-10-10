#!/usr/bin/env python3
"""Animated flat vector illustrations for the president video.

Each a_<name>() returns an SVG (1920x1080) whose parts carry CSS animation
classes (defined in anim.py: bob, flagwave, rotor, pop, fall, ...). anim.py
puts the SVG in an HTML page and Chromium captures it frame by frame.

Rule for animated groups: a class that animates `transform` never goes on an
element that also has a transform attribute (CSS would replace it), so motion
lives on wrapper <g> elements.
"""
import math
import random

W, H = 1920, 1080
NAVY, DEEP, MID = "#0b1a33", "#14284d", "#1f3d6e"
RED, CREAM, GOLD, WHITE = "#b5283b", "#f1e6cf", "#e0b95e", "#f7f4ec"
SKIN = ["#f0c9a4", "#c98e63", "#8d5a3b", "#e2b48c"]
SUIT = "#151b27"
_rng = random.Random(1234)


def svg(body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}"><defs>{defs}</defs>{body}</svg>')


def g(cls, body, style=""):
    st = f' style="{style}"' if style else ""
    return f'<g class="{cls}"{st}>{body}</g>'


def delay(sec):
    return f"animation-delay:{sec:.2f}s"


def desync(dur_lo=1.8, dur_hi=3.0):
    return f"animation-delay:-{_rng.uniform(0, 4):.2f}s;animation-duration:{_rng.uniform(dur_lo, dur_hi):.2f}s"


def grad(id_, top, bot, x2=0, y2=1):
    return (f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/>'
            f'</linearGradient>')


def radial(id_, inner, outer, cx=0.5, cy=0.5, r=0.6):
    return (f'<radialGradient id="{id_}" cx="{cx}" cy="{cy}" r="{r}">'
            f'<stop offset="0" stop-color="{inner}"/><stop offset="1" stop-color="{outer}"/>'
            f'</radialGradient>')


def sky(top, bot, id_="sky"):
    return grad(id_, top, bot), f'<rect width="{W}" height="{H}" fill="url(#{id_})"/>'


def stars(n=120, seed=1, ymax=600, opacity=0.8):
    r = random.Random(seed)
    return "".join(
        f'<circle class="tw" style="{desync(1.2, 3.5)}" cx="{r.uniform(0, W):.0f}" cy="{r.uniform(0, ymax):.0f}" '
        f'r="{r.choice([1, 1.4, 2, 2.6])}" fill="#fff" opacity="{r.uniform(.3, opacity):.2f}"/>'
        for _ in range(n))


def clouds(n=6, seed=40, y0=80, y1=420, op=0.85, speed=1.0):
    r = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = r.uniform(-200, W), r.uniform(y0, y1)
        rx = r.uniform(140, 300)
        body = (f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rx:.0f}" ry="{rx * .28:.0f}" fill="#fff" opacity="{op}"/>'
                f'<ellipse cx="{x - rx * .3:.0f}" cy="{y - rx * .15:.0f}" rx="{rx * .4:.0f}" ry="{rx * .25:.0f}" fill="#fff" opacity="{op}"/>'
                f'<ellipse cx="{x + rx * .2:.0f}" cy="{y - rx * .2:.0f}" rx="{rx * .45:.0f}" ry="{rx * .3:.0f}" fill="#fff" opacity="{op}"/>')
        out.append(g("drift", body, f"animation-duration:{r.uniform(18, 30) / speed:.1f}s;animation-delay:-{r.uniform(0, 20):.1f}s"))
    return "".join(out)


def confetti(n=120, seed=7, colors=(RED, WHITE, GOLD, "#3f6fd8")):
    r = random.Random(seed)
    out = []
    for _ in range(n):
        x = r.uniform(0, W)
        c = r.choice(colors)
        out.append(g("fall", f'<rect x="{x:.0f}" y="-40" width="14" height="24" fill="{c}"/>',
                     f"animation-duration:{r.uniform(3, 6):.1f}s;animation-delay:-{r.uniform(0, 6):.1f}s"))
    return "".join(out)


def snow(n=140, seed=8):
    r = random.Random(seed)
    return "".join(g("fall slowfall", f'<circle cx="{r.uniform(0, W):.0f}" cy="-20" r="{r.uniform(2, 6):.1f}" fill="#fff" opacity=".85"/>',
                     f"animation-duration:{r.uniform(7, 12):.1f}s;animation-delay:-{r.uniform(0, 12):.1f}s")
                   for _ in range(n))


def steam(x, y, n=3, scale=1.0):
    out = []
    for i in range(n):
        out.append(g("steam", f'<path d="M{x + i * 22 * scale},{y} q-14,-30 0,-60 q14,-30 0,-60" stroke="#fff" '
                              f'stroke-width="{7 * scale}" fill="none" stroke-linecap="round"/>',
                     f"animation-delay:-{i * .8:.1f}s"))
    return "".join(out)


def star_shape(cx, cy, R, fill, opacity=1.0):
    pts = []
    for p in range(10):
        a = -math.pi / 2 + p * math.pi / 5
        rr = R if p % 2 == 0 else R * 0.42
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" opacity="{opacity}"/>'


def flag(x, y, w, h, wave=0.0, pole=True):
    """US-style flag (13 stripes, star canton) that waves; the pole stays still."""
    out = []
    if pole:
        out.append(f'<rect x="{x - 8}" y="{y - 20}" width="8" height="{h * 3.2}" fill="#c9c2b0"/>'
                   f'<circle cx="{x - 4}" cy="{y - 24}" r="9" fill="{GOLD}"/>')
    cloth = []
    sh = h / 13
    for i in range(13):
        col = RED if i % 2 == 0 else WHITE
        yy = y + i * sh
        if wave:
            d = (f"M{x},{yy} C{x + w * .33},{yy - wave} {x + w * .66},{yy + wave} {x + w},{yy} "
                 f"L{x + w},{yy + sh + .5} C{x + w * .66},{yy + sh + wave} {x + w * .33},{yy + sh - wave} {x},{yy + sh + .5}Z")
            cloth.append(f'<path d="{d}" fill="{col}"/>')
        else:
            cloth.append(f'<rect x="{x}" y="{yy}" width="{w}" height="{sh + .5}" fill="{col}"/>')
    cloth.append(f'<rect x="{x}" y="{y}" width="{w * .4}" height="{sh * 7}" fill="#22356b"/>')
    for r_ in range(4):
        for c in range(5):
            cloth.append(star_shape(x + w * .4 * (c + .5) / 5, y + sh * 7 * (r_ + .5) / 4, sh * .45, WHITE))
    out.append(g("flagwave", "".join(cloth), desync(1.2, 1.8)))
    return "".join(out)


def _shade(hex_color, f):
    """Darken (f<1) or lighten (f>1) a #rrggbb colour."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return hex_color
    c = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    c = [max(0, min(255, int(v * f if f < 1 else v + (255 - v) * (f - 1)))) for v in c]
    return "#%02x%02x%02x" % tuple(c)


HAIR_STYLES = {
    "side": '<path d="M-48,-408 Q-52,-468 -4,-466 Q44,-470 50,-412 Q46,-440 18,-446 Q-10,-436 -30,-446 Q-44,-432 -48,-408Z" fill="{h}"/>'
            '<path d="M-30,-446 Q-6,-458 24,-450" stroke="{hl}" stroke-width="5" fill="none" opacity=".5"/>',
    "short": '<path d="M-48,-404 Q-50,-470 0,-468 Q50,-470 48,-404 Q40,-440 0,-444 Q-40,-440 -48,-404Z" fill="{h}"/>',
    "bald": '<path d="M-48,-392 Q-50,-420 -40,-430 L-38,-396Z M48,-392 Q50,-420 40,-430 L38,-396Z" fill="{h}"/>',
    "long": '<path d="M-54,-300 Q-64,-470 0,-470 Q64,-470 54,-300 L34,-300 Q40,-400 30,-430 Q0,-410 -30,-430 Q-40,-400 -34,-300Z" fill="{h}"/>',
    "bun": '<circle cx="0" cy="-470" r="22" fill="{h}"/><path d="M-48,-404 Q-50,-468 0,-466 Q50,-468 48,-404 Q40,-436 0,-440 Q-40,-436 -48,-404Z" fill="{h}"/>',
    "cap": '<path d="M-50,-412 Q-50,-470 0,-470 Q50,-470 50,-412Z" fill="{h}"/><path d="M-50,-414 L-74,-406 L50,-414Z" fill="{hl}"/>',
}


def person(x, y, s=1.0, suit=SUIT, skin=SKIN[0], tie=RED, shades=False, earpiece=False,
           hair="#2a1d14", arm_up=False, wave_arm=True, motion="bob", who=None, hair_style="side",
           shirt=WHITE, hat=None, gesture=False, pants=None):
    """Standing cartoon figure, feet at (x, y), ~480*s tall.

    Idle motion, breathing, blinks and head tilt are always on. `who` names the
    figure so a talking animation can target its mouth (.mouthopen) and arm.
    """
    pants = pants or _shade(suit, .85)
    dark, light = _shade(suit, .72), _shade(suit, 1.18)
    skin_d = _shade(skin, .84)
    p = [f'<g transform="translate({x},{y}) scale({s})">',
         '<ellipse cx="0" cy="2" rx="86" ry="15" fill="#000" opacity=".22"/>']
    # Legs and shoes.
    p.append(f'<path d="M-40,-200 L-38,-22 Q-38,-12 -26,-12 L-10,-12 Q-4,-12 -4,-22 L-2,-200Z" fill="{pants}"/>'
             f'<path d="M2,-200 L4,-22 Q4,-12 12,-12 L26,-12 Q38,-12 38,-22 L40,-200Z" fill="{_shade(pants, .85)}"/>'
             '<path d="M-44,-4 Q-46,-26 -22,-26 L-4,-26 Q2,-26 2,-14 L2,-4Z" fill="#14161b"/>'
             '<path d="M-2,-4 L-2,-14 Q-2,-26 6,-26 L24,-26 Q48,-26 46,-4Z" fill="#14161b"/>')
    upper = []
    # Back arm (left) behind the torso.
    upper.append(f'<path d="M-60,-326 Q-82,-268 -76,-206" stroke="{dark}" stroke-width="30" fill="none" stroke-linecap="round"/>'
                 f'<circle cx="-76" cy="-194" r="16" fill="{skin_d}"/>')
    # Torso: jacket with shading, shirt, lapels, tie, buttons.
    upper.append(f'<path d="M-70,-330 Q-76,-250 -62,-172 L62,-172 Q76,-250 70,-330 Q36,-352 0,-352 Q-36,-352 -70,-330Z" fill="{suit}"/>'
                 f'<path d="M14,-350 Q40,-348 70,-330 Q76,-250 62,-172 L14,-172Z" fill="{dark}" opacity=".55"/>'
                 f'<path d="M-20,-350 L0,-292 L20,-350Z" fill="{shirt}"/>'
                 f'<path d="M-24,-350 L-4,-286 L-16,-250 L-34,-338Z" fill="{light}" opacity=".6"/>'
                 f'<path d="M24,-350 L4,-286 L16,-250 L34,-338Z" fill="{dark}" opacity=".6"/>')
    if tie:
        upper.append(f'<path d="M-7,-336 L7,-336 L10,-322 L0,-316 L-10,-322Z" fill="{_shade(tie, .8)}"/>'
                     f'<path d="M-6,-318 L6,-318 L12,-246 L0,-232 L-12,-246Z" fill="{tie}"/>')
    upper.append(f'<circle cx="0" cy="-214" r="4" fill="{dark}"/><circle cx="0" cy="-194" r="4" fill="{dark}"/>')
    # Front arm (right): waving, gesturing or relaxed.
    if arm_up:
        arm = (f'<path d="M58,-324 Q100,-380 114,-452" stroke="{suit}" stroke-width="30" fill="none" stroke-linecap="round"/>'
               f'<rect x="102" y="-462" width="26" height="10" rx="4" fill="{shirt}" transform="rotate(-20 115 -457)"/>'
               f'<ellipse cx="118" cy="-474" rx="16" ry="19" fill="{skin}"/>')
        upper.append(g("wavearm", arm, desync(.45, .6)) if wave_arm else arm)
    else:
        arm = (f'<path d="M62,-326 Q84,-266 78,-206" stroke="{suit}" stroke-width="30" fill="none" stroke-linecap="round"/>'
               f'<circle cx="78" cy="-194" r="16" fill="{skin}"/>')
        cls = "gesture" if gesture else "armidle"
        upper.append(g(cls, arm, desync(2.5, 3.5)))
    # Head.
    head = [f'<path d="M-14,-366 L-14,-344 Q0,-336 14,-344 L14,-366Z" fill="{skin_d}"/>']
    if hair_style == "long":
        head.append(HAIR_STYLES["long"].format(h=hair, hl=_shade(hair, 1.4)))
    head.append(f'<circle cx="-47" cy="-402" r="11" fill="{skin_d}"/><circle cx="47" cy="-402" r="11" fill="{skin_d}"/>'
                f'<ellipse cx="0" cy="-405" rx="47" ry="53" fill="{skin}"/>'
                f'<path d="M20,-452 Q47,-430 46,-400 Q44,-372 22,-356 Q40,-390 20,-452Z" fill="{skin_d}" opacity=".45"/>')
    if hair_style != "long":
        head.append(HAIR_STYLES.get(hair_style, HAIR_STYLES["side"]).format(h=hair, hl=_shade(hair, 1.4)))
    else:
        head.append(f'<path d="M-46,-410 Q-40,-466 0,-462 Q40,-466 46,-410 Q30,-438 0,-440 Q-30,-438 -46,-410Z" fill="{hair}"/>')
    head.append(f'<path d="M-28,-428 Q-18,-434 -8,-428" stroke="{_shade(hair, .8)}" stroke-width="5" fill="none" stroke-linecap="round"/>'
                f'<path d="M8,-428 Q18,-434 28,-428" stroke="{_shade(hair, .8)}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    if shades:
        head.append('<path d="M-36,-414 L-4,-414 L-6,-396 Q-20,-390 -34,-398Z M4,-414 L36,-414 L34,-398 Q20,-390 6,-396Z" fill="#0a0a0a"/>'
                    '<rect x="-6" y="-412" width="12" height="4" fill="#0a0a0a"/>'
                    '<path d="M-30,-410 L-22,-410" stroke="#fff" stroke-width="3" opacity=".5"/>')
    else:
        eyes = ('<ellipse cx="-18" cy="-406" rx="6" ry="7.5" fill="#1d1d24"/><ellipse cx="18" cy="-406" rx="6" ry="7.5" fill="#1d1d24"/>'
                '<circle cx="-16" cy="-409" r="2.2" fill="#fff"/><circle cx="20" cy="-409" r="2.2" fill="#fff"/>')
        head.append(g("blink", eyes, f"animation-delay:-{_rng.uniform(0, 4):.1f}s;animation-duration:{_rng.uniform(3.5, 5.5):.1f}s"))
    head.append(f'<path d="M-3,-398 Q4,-386 -4,-382" stroke="{skin_d}" stroke-width="4" fill="none" stroke-linecap="round"/>'
                '<circle cx="-30" cy="-384" r="9" fill="#e86a6a" opacity=".18"/><circle cx="30" cy="-384" r="9" fill="#e86a6a" opacity=".18"/>')
    head.append('<path d="M-13,-372 Q0,-362 13,-372" stroke="#7a3b2e" stroke-width="4" fill="none" stroke-linecap="round" class="mouthclosed"/>'
                '<g class="mouthopen" style="opacity:0"><ellipse cx="0" cy="-369" rx="12" ry="9" fill="#5a1f1f"/>'
                '<ellipse cx="0" cy="-364" rx="7" ry="4" fill="#d9666b"/><rect x="-8" y="-377" width="16" height="4" rx="2" fill="#fff"/></g>')
    if earpiece:
        head.append('<path d="M46,-398 Q60,-372 46,-344 L36,-306" stroke="#e8e8e8" stroke-width="3" fill="none"/>')
    if hat == "chef":
        head.append('<rect x="-40" y="-478" width="80" height="34" fill="#fff"/><ellipse cx="0" cy="-500" rx="56" ry="40" fill="#fff"/>'
                    '<ellipse cx="-34" cy="-488" rx="30" ry="26" fill="#fff"/><ellipse cx="34" cy="-488" rx="30" ry="26" fill="#fff"/>'
                    '<rect x="-40" y="-452" width="80" height="8" fill="#e8e2d6"/>')
    upper.append(g("headtilt", "".join(head), desync(2.5, 4)))
    p.append(g("breathe2", "".join(upper), desync(2.6, 3.6)))
    p.append('</g>')
    body = "".join(p)
    if who:
        body = f'<g data-who="{who}">{body}</g>'
    return g(motion, body, desync(1.6, 2.6)) if motion else body


def crowd(y, n=40, seed=3, color="#0a1222", scale=1.0, cheer=False):
    r = random.Random(seed)
    out = []
    for i in range(n):
        x = i * W / n + r.uniform(-15, 15)
        s = scale * r.uniform(.8, 1.15)
        body = (f'<circle cx="{x:.0f}" cy="{y - 95 * s:.0f}" r="{24 * s:.0f}" fill="{color}"/>'
                f'<path d="M{x - 45 * s:.0f},{y + 20} Q{x - 45 * s:.0f},{y - 65 * s:.0f} {x:.0f},{y - 68 * s:.0f} '
                f'Q{x + 45 * s:.0f},{y - 65 * s:.0f} {x + 45 * s:.0f},{y + 20}Z" fill="{color}"/>')
        if cheer and r.random() < .5:
            body += (f'<path d="M{x + 20 * s:.0f},{y - 50 * s:.0f} L{x + 50 * s:.0f},{y - 150 * s:.0f}" stroke="{color}" '
                     f'stroke-width="{16 * s:.0f}" stroke-linecap="round"/>')
        out.append(g("jump" if cheer else "bob", body, desync(.45, .8) if cheer else desync(1.5, 3)))
    return "".join(out)


def white_house(cx, base, s=1.0, lit=True, fill=CREAM):
    """Front of the White House: portico with columns, two wings, windows."""
    out = [f'<g transform="translate({cx},{base}) scale({s})">']
    win = "#ffd98a" if lit else "#3b4c6b"
    out.append(f'<rect x="-560" y="-300" width="1120" height="300" fill="{fill}"/>')
    out.append('<rect x="-580" y="-318" width="1160" height="22" fill="#e4d7bb"/>')
    for i in range(-560, 561, 28):
        out.append(f'<rect x="{i}" y="-334" width="16" height="18" fill="#e4d7bb"/>')
    r = random.Random(int(cx))
    for yy in (-250, -130):
        for x in list(range(-520, -170, 88)) + list(range(200, 540, 88)):
            w_ = f'<rect x="{x}" y="{yy}" width="44" height="72" fill="{win}"/>'
            if lit and r.random() < .35:
                w_ = g("winflicker", w_, desync(3, 7))
            out.append(w_ + f'<path d="M{x - 6},{yy - 4} L{x + 22},{yy - 22} L{x + 50},{yy - 4}Z" fill="#ddd0b3"/>')
    out.append('<path d="M-230,-380 L0,-470 L230,-380Z" fill="#efe4cb"/>')
    out.append('<path d="M-200,-388 L0,-450 L200,-388Z" fill="#e2d4b5"/>')
    out.append('<rect x="-240" y="-382" width="480" height="30" fill="#e8dcc2"/>')
    for x in range(-210, 211, 70):
        out.append(f'<rect x="{x - 14}" y="-352" width="28" height="352" fill="#fbf6ea"/>'
                   f'<rect x="{x - 18}" y="-356" width="36" height="10" fill="#e4d7bb"/>')
    out.append(f'<rect x="-36" y="-150" width="72" height="150" fill="#8a6a3d"/>'
               f'<rect x="-30" y="-144" width="60" height="140" fill="{win}" opacity=".85"/>')
    out.append('<rect x="-600" y="0" width="1200" height="20" fill="#d9ccb0"/>')
    out.append(flag(-6, -560, 120, 70, wave=6))
    out.append('</g>')
    return "".join(out)


def lawn(y, top="#2f6b3a", bot="#173d22"):
    return (grad("lawn", top, bot),
            f'<rect x="0" y="{y}" width="{W}" height="{H - y}" fill="url(#lawn)"/>')


def rays(cx, cy, n=14, color="#fff", op=.06, length=1600):
    parts = []
    for i in range(n):
        a = i * 2 * math.pi / n
        a2 = a + math.pi / n * .6
        parts.append(f'<path d="M{cx},{cy} L{cx + length * math.cos(a):.0f},{cy + length * math.sin(a):.0f} '
                     f'L{cx + length * math.cos(a2):.0f},{cy + length * math.sin(a2):.0f}Z" fill="{color}" opacity="{op}"/>')
    return g("spin slowspin", "".join(parts))


# ---------------------------------------------------------------- clocks

def clock(cx, cy, r, h, m, face=CREAM, mode="tick"):
    """mode: 'tick' = second hand ticking; 'strike' = minute hand snaps to 12."""
    out = [f'<circle cx="{cx}" cy="{cy + 14}" r="{r + 30}" fill="#000" opacity=".25"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{r + 30}" fill="{GOLD}"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{face}"/>']
    for i in range(60):
        a = i * math.pi / 30
        l = 40 if i % 5 == 0 else 16
        w = 10 if i % 5 == 0 else 4
        out.append(f'<line x1="{cx + (r - 20) * math.sin(a):.1f}" y1="{cy - (r - 20) * math.cos(a):.1f}" '
                   f'x2="{cx + (r - 20 - l) * math.sin(a):.1f}" y2="{cy - (r - 20 - l) * math.cos(a):.1f}" '
                   f'stroke="{NAVY}" stroke-width="{w}"/>')
    ha = (h % 12 + m / 60) * math.pi / 6
    out.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + r * .5 * math.sin(ha):.1f}" y2="{cy - r * .5 * math.cos(ha):.1f}" stroke="{NAVY}" stroke-width="22" stroke-linecap="round"/>')
    minute = f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - r * .8:.1f}" stroke="{NAVY}" stroke-width="12" stroke-linecap="round"/>'
    # Rotate around the clock centre: a square box centred on it makes fill-box centre = clock centre.
    box = f'<rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" fill="none"/>'
    if mode == "strike":
        out.append(g("minutestrike", box + minute))
    else:
        out.append(g("", box + minute, "") .replace('<g class=""', f'<g transform="rotate({m * 6} {cx} {cy})"'))
    sec = f'<line x1="{cx}" y1="{cy + 30}" x2="{cx}" y2="{cy - r * .88:.1f}" stroke="{RED}" stroke-width="5"/>'
    out.append(g("secondhand", box + sec))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="20" fill="{RED}"/>')
    return "".join(out)


def a_clock_1159():
    d, s = sky("#0f2347", "#3b2a4d")
    return svg(s + stars(60, 9, 400) + g("breathe", clock(959, 500, 330, 11, 59)), d)


def a_clock_noon():
    d, s = sky("#3f6fb0", "#f2c879")
    sun = g("pulse", '<circle cx="1500" cy="220" r="120" fill="#ffe6a3" opacity=".7"/>')
    return svg(s + rays(959, 500, 18, "#fff", .08) + sun + g("punch", clock(959, 500, 330, 12, 0, face=WHITE, mode="strike")), d)


def a_choice():
    d = grad("ch", "#0b1a33", "#e0b95e", 1, 0)
    b = [f'<rect width="{W}" height="{H}" fill="url(#ch)"/>', stars(90, 91, 1080, .6)]
    b.append(g("popc", clock(500, 540, 220, 11, 59), delay(.1)))
    b.append(g("popc", clock(1420, 540, 220, 12, 0, face=WHITE), delay(.5)))
    b.append(g("nudge", '<path d="M840,520 L1040,520 L1040,470 L1120,540 L1040,610 L1040,560 L840,560Z" fill="#fff" opacity=".85"/>'))
    return svg("".join(b), d)


# ---------------------------------------------------------------- scenes

def a_capitol():
    d, s = sky("#9cc3e6", "#f4e3c3")
    d2, l = lawn(880, "#5c8a4c", "#2c4f2c")
    b = [s, clouds(5, 41, 60, 300)]
    b.append(f'<rect x="360" y="620" width="1200" height="260" fill="{CREAM}"/>')
    b.append('<rect x="340" y="600" width="1240" height="26" fill="#e5d8bc"/>')
    for x in range(380, 1550, 46):
        b.append(f'<rect x="{x}" y="640" width="18" height="230" fill="#fbf6ea"/>')
    b.append('<path d="M760,600 L960,520 L1160,600Z" fill="#efe4cb"/>')
    b.append(f'<rect x="780" y="380" width="360" height="150" fill="{CREAM}"/>')
    for x in range(795, 1130, 30):
        b.append(f'<rect x="{x}" y="395" width="12" height="125" fill="#fbf6ea"/>')
    b.append(f'<path d="M800,380 Q800,190 960,170 Q1120,190 1120,380Z" fill="{WHITE}"/>')
    for x in range(830, 1100, 45):
        b.append(f'<path d="M{x},378 Q{x + 5},260 960,180" stroke="#e1d6bf" stroke-width="4" fill="none"/>')
    b.append(f'<rect x="935" y="120" width="50" height="55" fill="{WHITE}"/>'
             f'<path d="M930,122 Q960,80 990,122Z" fill="{WHITE}"/><rect x="954" y="62" width="12" height="40" fill="#cfc6b2"/>')
    b.append(f'<rect x="700" y="780" width="520" height="100" fill="{NAVY}"/>')
    for i in range(6):
        x = 700 + i * 87
        b.append(f'<path d="M{x},780 Q{x + 43},830 {x + 87},780Z" fill="{RED}"/>'
                 f'<path d="M{x + 10},780 Q{x + 43},815 {x + 77},780Z" fill="{WHITE}"/>')
    b.append(flag(420, 470, 150, 90, wave=6) + flag(1420, 470, 150, 90, wave=6))
    b.append(g("camflash", '<rect width="1920" height="1080" fill="#fff"/>'))
    b.append(l + crowd(1080, 34, 5, "#14223b", 1.3, cheer=True))
    return svg("".join(b), d + d2)


def a_oath():
    d, s = sky("#1b335f", "#0b1a33")
    b = [s, '<rect x="0" y="0" width="1920" height="1080" fill="url(#spot)"/>', rays(960, 300, 16, "#fff3d0", .05)]
    defs = d + radial("spot", "#f6deb0", "#0b1a33", .5, .3, .7)
    b.append(flag(140, 120, 360, 220, wave=10) + flag(1420, 120, 360, 220, wave=10))
    hand = (f'<path d="M560,1080 Q600,760 760,560 L840,600 Q720,800 720,1080Z" fill="{SUIT}"/>'
            f'<path d="M745,560 Q735,420 770,330 Q790,300 812,320 L812,250 Q830,232 846,252 L848,236 Q868,220 880,244 '
            f'L884,262 Q904,252 912,276 L900,420 Q880,520 840,600Z" fill="{SKIN[1]}"/>')
    b.append(g("rise", hand, delay(.1)))
    book = (f'<path d="M1060,1080 Q1100,900 1200,860 L1400,870 Q1340,980 1360,1080Z" fill="{SUIT}"/>'
            f'<rect x="1080" y="820" width="420" height="80" rx="10" fill="#4a1f1f"/>'
            f'<rect x="1090" y="805" width="400" height="20" fill="{CREAM}"/>'
            f'<rect x="1080" y="790" width="420" height="22" rx="8" fill="#5a2626"/>'
            f'<path d="M1180,812 Q1290,760 1400,800 L1400,830 Q1290,800 1180,840Z" fill="{SKIN[1]}"/>')
    b.append(g("rise", book, delay(.35)))
    return svg("".join(b), defs)


def a_briefcase():
    d, s = sky("#141c2c", "#05080f")
    b = [s, g("sweep", '<path d="M-400,0 L200,0 L800,1080 L400,1080Z" fill="#fff" opacity=".06"/>')]
    case = ['<ellipse cx="960" cy="900" rx="560" ry="60" fill="#000" opacity=".5"/>',
            '<rect x="560" y="430" width="800" height="470" rx="40" fill="#1a1a1a"/>',
            '<rect x="560" y="430" width="800" height="90" rx="40" fill="#242424"/>',
            '<path d="M840,430 L840,350 Q840,320 870,320 L1050,320 Q1080,320 1080,350 L1080,430" stroke="#2c2c2c" stroke-width="34" fill="none"/>',
            f'<rect x="900" y="500" width="120" height="50" rx="8" fill="{GOLD}"/>',
            f'<rect x="640" y="480" width="70" height="40" rx="6" fill="{GOLD}"/><rect x="1210" y="480" width="70" height="40" rx="6" fill="{GOLD}"/>']
    for x in range(600, 1330, 60):
        case.append(f'<line x1="{x}" y1="560" x2="{x + 20}" y2="880" stroke="#222" stroke-width="2"/>')
    case.append(g("glint", '<rect x="560" y="420" width="60" height="500" fill="#fff" opacity=".12" transform="skewX(-20)"/>'))
    b.append(g("float", "".join(case)))
    b.append(g("dust", "".join(f'<circle cx="{_rng.uniform(300, 1600):.0f}" cy="{_rng.uniform(100, 1000):.0f}" r="2" fill="#fff" opacity=".4"/>' for _ in range(40))))
    return svg("".join(b), d)


def a_money():
    d, s = sky("#173d2b", "#06140d")
    b = [s, rays(1650, 330, 12, "#e0b95e", .05)]
    r = random.Random(4)
    for stack in range(9):
        x = 260 + stack * 160 + r.uniform(-20, 20)
        hgt = r.randint(6, 18)
        st = []
        for i in range(hgt):
            y = 900 - i * 34
            st.append(f'<rect x="{x}" y="{y}" width="220" height="30" rx="4" fill="#8fbf8a" stroke="#2e5a33" stroke-width="3"/>'
                      f'<rect x="{x + 95}" y="{y}" width="30" height="30" fill="#e6d9a8"/>')
        b.append(g("grow-y", "".join(st), delay(.1 + stack * .12)))
    b.append(g("coinflip", f'<circle cx="1650" cy="330" r="130" fill="{GOLD}" opacity=".95"/>'
             f'<text x="1650" y="388" text-anchor="middle" font-family="serif" font-size="180" font-weight="bold" fill="#5b4310">$</text>'))
    return svg("".join(b), d)


def a_constitution():
    d, s = sky("#3a2a1a", "#120b05")
    b = [s, '<rect x="0" y="760" width="1920" height="320" fill="#5a3b22"/>',
         g("candle", '<ellipse cx="1650" cy="420" rx="420" ry="360" fill="#ffb84a" opacity=".12"/>')]
    paper = ['<path d="M480,180 L1420,160 L1460,900 L460,930Z" fill="#e9d7ab"/>',
             '<path d="M480,180 L1420,160 L1460,900 L460,930Z" fill="url(#age)" opacity=".5"/>',
             '<text x="960" y="300" text-anchor="middle" font-family="serif" font-style="italic" font-size="110" fill="#3a2a16">We the People</text>']
    r = random.Random(2)
    for row in range(14):
        y = 380 + row * 34
        x = 560
        line = []
        while x < 1340:
            w = r.randint(30, 110)
            line.append(f'<rect x="{x}" y="{y}" width="{w}" height="8" rx="4" fill="#6b5634" opacity=".55"/>')
            x += w + 18
        paper.append(g("grow-x", "".join(line), delay(.2 + row * .18)))
    b.append("".join(paper))
    b.append(g("quill", '<path d="M1500,980 L1250,520 Q1240,470 1290,490 L1530,960Z" fill="#f7f2e6"/>'
               '<path d="M1255,525 L1245,505 L1265,512Z" fill="#222"/>'))
    return svg("".join(b), d + radial("age", "#fff7e0", "#a8854e", .5, .5, .8))


def a_campaign():
    d, s = sky("#22163f", "#0b1a33")
    defs = d + radial("beam", "#7a5fbf", "#0b1a33", .5, .2, .6)
    b = [s, '<rect width="1920" height="1080" fill="url(#beam)"/>']
    for i, x in enumerate((300, 960, 1620)):
        b.append(g("searchlight", f'<path d="M{x},1080 L{x - 120},0 L{x + 120},0Z" fill="#fff" opacity=".05"/>', desync(3, 5)))
    b.append(confetti(160, 7))
    b.append(flag(260, 200, 300, 180, wave=8) + flag(1380, 200, 300, 180, wave=8))
    b.append(person(960, 780, 1.15, arm_up=True, skin=SKIN[3], who="pres"))
    b.append(f'<path d="M820,640 L1100,640 L1060,880 L860,880Z" fill="{NAVY}"/>'
             f'{star_shape(960, 740, 60, GOLD)}<rect x="900" y="610" width="120" height="30" fill="#2a2a2a"/>')
    b.append(crowd(1080, 30, 11, "#060b16", 1.6, cheer=True))
    for i in range(8):
        x = 140 + i * 230
        sign = (f'<rect x="{x}" y="820" width="150" height="80" fill="{[RED, WHITE, "#2d58b8"][i % 3]}" transform="rotate({(-1) ** i * 6} {x} 820)"/>'
                f'<rect x="{x + 70}" y="900" width="10" height="120" fill="#888"/>')
        b.append(g("jump", sign, desync(.5, .8)))
    return svg("".join(b), defs)


def a_statefair():
    d, s = sky("#7ec4f0", "#ffe9b8")
    b = [s, clouds(4, 12, 40, 250), '<rect x="0" y="820" width="1920" height="260" fill="#9ccf6a"/>']
    cx, cy, R = 1420, 460, 320
    b.append(f'<path d="M{cx},{cy} L{cx - 160},{820} M{cx},{cy} L{cx + 160},{820}" stroke="#ddd" stroke-width="16"/>')
    wheel = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{RED}" stroke-width="14"/>']
    for i in range(12):
        a = i * math.pi / 6
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        wheel.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" stroke="#fff" stroke-width="6"/>'
                     f'<circle cx="{x:.0f}" cy="{y:.0f}" r="22" fill="{[GOLD, "#3f6fd8", RED][i % 3]}"/>')
    b.append(g("spin wheel", "".join(wheel)))
    for x in (80, 520):
        tent = [f'<path d="M{x},820 L{x},620 L{x + 180},500 L{x + 360},620 L{x + 360},820Z" fill="{WHITE}"/>']
        for k in range(0, 360, 72):
            tent.append(f'<path d="M{x + k},620 L{x + 180},500 L{x + k + 36},620Z" fill="{RED}"/>')
        b.append("".join(tent))
    r = random.Random(77)
    for i in range(9):
        x, y = r.uniform(120, 1000), r.uniform(320, 640)
        col = r.choice([RED, GOLD, "#3f6fd8", "#e75a7c", WHITE])
        b.append(g("float", f'<path d="M{x:.0f},{y + 60:.0f} q-12,60 6,130" stroke="#ddd" stroke-width="3" fill="none"/>'
                            f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="46" ry="58" fill="{col}"/>'
                            f'<ellipse cx="{x - 14:.0f}" cy="{y - 20:.0f}" rx="10" ry="16" fill="#fff" opacity=".45"/>', desync(2, 3.5)))
    return svg("".join(b), d)


def a_speech():
    d, s = sky("#101a30", "#05080f")
    b = [s]
    for i in range(5):
        x = 260 + i * 350
        b.append(g("searchlight", f'<path d="M{x},0 L{x + 140},0 L{x + 260},1080 L{x - 120},1080Z" fill="#fff" opacity=".05"/>', desync(3, 5)))
    b.append(crowd(1080, 26, 23, "#05080f", 1.5, cheer=True))
    b.append(person(960, 900, 1.4, skin=SKIN[2], who="pres", gesture=True))
    b.append(f'<path d="M790,700 L1130,700 L1090,1000 L830,1000Z" fill="#3a2516"/>'
             f'<circle cx="960" cy="820" r="70" fill="{GOLD}" opacity=".8"/>{star_shape(960, 820, 48, NAVY)}')
    for i in range(3):
        b.append(f'<rect x="{900 + i * 40}" y="640" width="14" height="70" fill="#333"/><circle cx="{907 + i * 40}" cy="636" r="16" fill="#222"/>')
    return svg("".join(b), d)


def a_election():
    d, s = sky("#0b1a33", "#21305a")
    b = [s, stars(80, 4, 400)]
    r = random.Random(5)
    for i in range(10):
        x = 860 + r.uniform(-60, 120)
        bal = (f'<g transform="rotate({r.uniform(-25, 25):.0f} {x:.0f} 0)"><rect x="{x - 60:.0f}" y="-80" width="120" height="160" fill="{CREAM}"/>'
               f'<rect x="{x - 40:.0f}" y="-50" width="16" height="16" fill="none" stroke="#333" stroke-width="3"/>'
               f'<path d="M{x - 38:.0f},-42 l6,8 l12,-16" stroke="{RED}" stroke-width="4" fill="none"/></g>')
        b.append(g("ballot", bal, f"animation-delay:-{i * .45:.2f}s"))
    b.append(f'<path d="M640,520 L1280,520 L1240,960 L680,960Z" fill="{WHITE}"/>'
             f'<rect x="620" y="480" width="680" height="60" rx="10" fill="#dcd5c4"/>'
             f'<rect x="840" y="496" width="240" height="20" rx="8" fill="#333"/>')
    b.append(g("pulse", star_shape(960, 730, 110, "#2d58b8")))
    return svg("".join(b), d)


def a_white_house_day():
    d, s = sky("#7fb1e3", "#e7f0f7")
    d2, l = lawn(860)
    b = [s, g("pulse", '<circle cx="1600" cy="200" r="90" fill="#fff6d0"/>'), clouds(5, 21, 40, 300),
         white_house(960, 860, 1.25, lit=False), l]
    b.append('<ellipse cx="960" cy="1000" rx="260" ry="50" fill="#5c9c5a"/><ellipse cx="960" cy="990" rx="70" ry="20" fill="#9fd3f0"/>')
    b.append(g("fountain", '<path d="M960,990 Q940,900 960,880 Q980,900 960,990" fill="#cfeaff" opacity=".8"/>'))
    for x in (150, 1770):
        b.append(g("sway", f'<circle cx="{x}" cy="700" r="170" fill="#2d5e32"/>', desync(3, 4)) +
                 f'<rect x="{x - 15}" y="780" width="30" height="100" fill="#4a3320"/>')
    b.append(g("birds", "".join(f'<path d="M{x},{y} q15,-14 30,0 q15,-14 30,0" stroke="#223" stroke-width="5" fill="none"/>'
                                for x, y in ((200, 200), (280, 240), (340, 190)))))
    return svg("".join(b), d + d2)


def a_white_house_night():
    d, s = sky("#0b1a33", "#304a7a")
    d2, l = lawn(860, "#1d3b2a", "#0b1a12")
    b = [s, stars(150, 6, 500), g("pulse", '<circle cx="1620" cy="190" r="70" fill="#f4efd6"/>'),
         '<ellipse cx="960" cy="560" rx="700" ry="320" fill="#ffe2a0" opacity=".08"/>',
         white_house(960, 860, 1.25, lit=True, fill="#e7dcc4"), l]
    for x in (300, 1620):
        b.append(g("searchlight", f'<path d="M{x},860 L{x - 90},0 L{x + 90},0Z" fill="#fff" opacity=".05"/>', desync(4, 6)))
    return svg("".join(b), d + d2)


def a_movers():
    d, s = sky("#9cc8ec", "#eef4f7")
    d2, l = lawn(820)
    b = [s, clouds(4, 31, 40, 260), white_house(1300, 820, .9, lit=False), l]
    truck = (f'<rect x="120" y="560" width="620" height="320" rx="16" fill="{WHITE}"/>'
             f'<path d="M740,640 L900,640 L960,740 L960,880 L740,880Z" fill="{RED}"/>'
             '<path d="M770,660 L880,660 L920,740 L770,740Z" fill="#a9d3f0"/>'
             '<circle cx="260" cy="890" r="56" fill="#222"/><circle cx="820" cy="890" r="56" fill="#222"/>'
             '<circle cx="260" cy="890" r="22" fill="#999"/><circle cx="820" cy="890" r="22" fill="#999"/>')
    b.append(g("drivein", truck))
    for i, (x, y) in enumerate(((1000, 880), (1080, 880), (1040, 800), (1180, 880))):
        b.append(g("dropin", f'<rect x="{x}" y="{y - 80}" width="76" height="80" fill="#c99b5f" stroke="#8a6232" stroke-width="3"/>'
                             f'<rect x="{x + 28}" y="{y - 80}" width="20" height="80" fill="#e1c07f"/>', delay(.8 + i * .25)))
    b.append(person(560, 990, .55, suit="#30507a", skin=SKIN[1], motion="march", who="mover", hair_style="cap", hair="#c0392b", tie=None, gesture=True))
    b.append(g("hurry", person(1400, 1000, .55, suit="#30507a", skin=SKIN[2], motion="march")
               + '<rect x="1340" y="640" width="120" height="100" fill="#c99b5f" stroke="#8a6232" stroke-width="3"/>', "--dx:-200px"))
    return svg("".join(b), d + d2)


def a_toothbrush():
    d, s = sky("#e8eef3", "#c4d2dc")
    b = [s, '<rect x="0" y="700" width="1920" height="380" fill="#f6f2ea"/>',
         '<rect x="0" y="690" width="1920" height="20" fill="#d9d2c4"/>']
    for x in range(0, 1920, 120):
        b.append(f'<line x1="{x}" y1="0" x2="{x}" y2="690" stroke="#d3dde4" stroke-width="3"/>')
    b.append('<rect x="560" y="160" width="800" height="420" rx="30" fill="#dfe9ef" stroke="#c9b27a" stroke-width="18"/>')
    b.append(g("glint", '<rect x="560" y="160" width="80" height="420" fill="#fff" opacity=".4" transform="skewX(-20)"/>'))
    b.append('<path d="M820,700 L800,440 L960,440 L940,700Z" fill="#9fc6dd" opacity=".9"/>')
    b.append(g("dropin", f'<rect x="900" y="300" width="22" height="260" rx="10" fill="{RED}" transform="rotate(-12 911 430)"/>'
                         f'<rect x="860" y="260" width="30" height="70" rx="6" fill="{WHITE}" transform="rotate(-12 911 430)"/>', delay(.2)))
    b.append(g("dropin", '<rect x="960" y="320" width="22" height="240" rx="10" fill="#2d58b8" transform="rotate(10 971 440)"/>', delay(.45)))
    for i, (x, y, r_) in enumerate(((1500, 300, 50), (1380, 220, 26), (600, 260, 30))):
        b.append(g("sparkle", star_shape(x, y, r_, GOLD, .8), f"animation-delay:-{i * .5:.1f}s"))
    return svg("".join(b), d)


def a_bowling():
    d, s = sky("#2b1838", "#0f0a16")
    b = [s, '<path d="M760,1080 L900,380 L1020,380 L1160,1080Z" fill="#d7a76a"/>']
    for k in range(-3, 4):
        b.append(f'<line x1="{960 + k * 28}" y1="380" x2="{960 + k * 60}" y2="1080" stroke="#b9884f" stroke-width="3"/>')
    b.append('<path d="M640,1080 L880,380 L900,380 L760,1080Z" fill="#222"/><path d="M1280,1080 L1040,380 L1020,380 L1160,1080Z" fill="#222"/>')
    pins = []
    for row, n in enumerate((4, 3, 2, 1)):
        for i in range(n):
            x = 960 + (i - (n - 1) / 2) * 34
            y = 380 + row * 22
            pins.append(f'<ellipse cx="{x}" cy="{y}" rx="12" ry="34" fill="{WHITE}"/><rect x="{x - 10}" y="{y - 20}" width="20" height="5" fill="{RED}"/>')
    b.append(g("pinscatter", "".join(pins)))
    b.append(g("roll", f'<circle cx="960" cy="900" r="110" fill="{NAVY}"/><circle cx="930" cy="860" r="12" fill="#000"/>'
             f'<circle cx="970" cy="845" r="12" fill="#000"/><circle cx="975" cy="885" r="12" fill="#000"/>'))
    b.append('<rect x="0" y="0" width="1920" height="120" fill="#120b1a"/>')
    for x in range(100, 1900, 300):
        b.append(g("tw", f'<circle cx="{x}" cy="120" r="30" fill="#ffd98a" opacity=".6"/>', desync(1, 2)))
    return svg("".join(b), d)


def a_chef():
    d, s = sky("#f4ece0", "#d8cbb6")
    b = [s, '<rect x="0" y="720" width="1920" height="360" fill="#7a5233"/>',
         '<rect x="0" y="700" width="1920" height="30" fill="#5e3e26"/>']
    b.append(g("slidein-b", '<ellipse cx="960" cy="760" rx="380" ry="80" fill="#fff"/><ellipse cx="960" cy="755" rx="300" ry="58" fill="#f2eee7"/>'
             '<ellipse cx="960" cy="740" rx="160" ry="40" fill="#8a4a2a"/><ellipse cx="900" cy="735" rx="60" ry="22" fill="#5d9c4a"/>'))
    b.append(steam(920, 690, 3, 1.2))
    b.append('<path d="M1360,720 L1360,560 M1400,720 L1400,560" stroke="#bbb" stroke-width="10"/>'
             '<path d="M520,720 L520,540 Q560,560 540,640 L540,720" fill="#ccc"/>')
    b.insert(1, person(1380, 980, 1.05, suit="#f4f1ea", skin=SKIN[2], tie=None, hair="#1a1a1a", hair_style="short",
                       hat="chef", who="chef", gesture=True, pants="#2b2b33", shirt="#e8e2d6"))
    return svg("".join(b), d)


def a_receipt():
    d, s = sky("#273a5c", "#0e1830")
    b = [s, '<rect x="0" y="800" width="1920" height="280" fill="#6b4529"/>']
    r = ['<path d="M700,100 L1220,100 L1220,960 L1194,940 L1168,960 L1142,940 L1116,960 L1090,940 L1064,960 L1038,940 '
         'L1012,960 L986,940 L960,960 L934,940 L908,960 L882,940 L856,960 L830,940 L804,960 L778,940 L752,960 L726,940 L700,960Z" fill="#fbf8f0"/>',
         '<text x="960" y="200" text-anchor="middle" font-family="monospace" font-size="54" font-weight="bold" fill="#222">THE WHITE HOUSE</text>',
         '<line x1="740" y1="240" x2="1180" y2="240" stroke="#999" stroke-dasharray="10 8" stroke-width="3"/>']
    items = [("GROCERIES", "$$$"), ("SNACKS", "$$"), ("TOOTHPASTE", "$"), ("DRY CLEANING", "$$"), ("COFFEE", "$")]
    for i, (a, c) in enumerate(items):
        y = 320 + i * 90
        r.append(g("fadein", f'<text x="750" y="{y}" font-family="monospace" font-size="42" fill="#333">{a}</text>'
                             f'<text x="1170" y="{y}" text-anchor="end" font-family="monospace" font-size="42" fill="#333">{c}</text>', delay(.7 + i * .3)))
    r.append('<line x1="740" y1="780" x2="1180" y2="780" stroke="#999" stroke-dasharray="10 8" stroke-width="3"/>')
    r.append(g("blinktext", f'<text x="750" y="860" font-family="monospace" font-size="50" font-weight="bold" fill="{RED}">TOTAL DUE</text>', delay(2.3)))
    b.append(g("printout", "".join(r)))
    return svg("".join(b), d)


def a_paycheck():
    d, s = sky("#173d2b", "#0a1a12")
    b = [s, rays(960, 540, 16, "#e0b95e", .05)]
    chk = ['<g transform="rotate(-6 960 540)">',
           '<rect x="360" y="300" width="1200" height="520" rx="20" fill="#e8f0dc" stroke="#7aa37a" stroke-width="8"/>',
           '<text x="420" y="390" font-family="serif" font-size="44" fill="#2e5a33">UNITED STATES TREASURY</text>',
           '<text x="420" y="520" font-family="serif" font-size="40" fill="#333">PAY TO THE ORDER OF</text>',
           '<line x1="420" y1="600" x2="1160" y2="600" stroke="#333" stroke-width="3"/>',
           '<text x="430" y="585" font-family="serif" font-style="italic" font-size="56" fill="#22356b">The President</text>',
           '<rect x="1200" y="470" width="300" height="90" fill="#fff" stroke="#333" stroke-width="3"/>',
           '<text x="1350" y="535" text-anchor="middle" font-family="monospace" font-size="48" font-weight="bold" fill="#111">$400,000</text>',
           '<line x1="1100" y1="740" x2="1500" y2="740" stroke="#333" stroke-width="3"/>',
           '<path class="draw" d="M1120,730 q40,-50 70,-10 t60,-5 t70,-20 t80,10" stroke="#22356b" stroke-width="5" fill="none"/>',
           f'{star_shape(1450, 370, 40, GOLD)}</g>']
    b.append(g("slidein-l", "".join(chk)))
    return svg("".join(b), d)


def a_population():
    d, s = sky("#1f3d6e", "#0b1a33")
    b = [s]
    r = random.Random(8)
    for row in range(9):
        y = 260 + row * 95
        s_ = .35 + row * .06
        for i in range(30):
            x = (i + .5 * (row % 2)) * 68 + r.uniform(-8, 8)
            col = r.choice(["#e8d6b5", "#c98e63", "#8d5a3b", "#f0c9a4", "#6f4630"])
            shirt = r.choice([RED, WHITE, "#3f6fd8", GOLD, "#5b8a5a", "#7a5fbf"])
            body = (f'<circle cx="{x:.0f}" cy="{y - 60 * s_:.0f}" r="{22 * s_:.1f}" fill="{col}"/>'
                    f'<path d="M{x - 34 * s_:.0f},{y + 40 * s_:.0f} Q{x - 34 * s_:.0f},{y - 30 * s_:.0f} {x:.0f},{y - 32 * s_:.0f} Q{x + 34 * s_:.0f},{y - 30 * s_:.0f} {x + 34 * s_:.0f},{y + 40 * s_:.0f}Z" fill="{shirt}"/>')
            # Stadium wave: delay follows x.
            b.append(g("stadium", body, f"animation-delay:{x / W * 1.6 - 3:.2f}s"))
    return svg("".join(b), d)


def a_pdb():
    d, s = sky("#f2b26b", "#3d2a4d")
    b = [s, g("pulse", '<rect x="200" y="80" width="700" height="560" fill="#ffd9a0" opacity=".25"/>'),
         '<line x1="550" y1="80" x2="550" y2="640" stroke="#3d2a4d" stroke-width="16"/>',
         '<line x1="200" y1="360" x2="900" y2="360" stroke="#3d2a4d" stroke-width="16"/>',
         '<rect x="0" y="640" width="1920" height="440" fill="#5a3a24"/>']
    b.append(g("slidein-b", '<g transform="rotate(-4 1000 820)"><rect x="620" y="620" width="760" height="380" rx="14" fill="#1d2f55"/>'
             '<rect x="640" y="640" width="720" height="340" rx="10" fill="#22386a"/>'
             f'<circle cx="1000" cy="770" r="80" fill="none" stroke="{GOLD}" stroke-width="8"/>{star_shape(1000, 770, 50, GOLD)}</g>'))
    b.append(g("stamp", f'<g transform="rotate(-4 1000 820)"><rect x="800" y="880" width="400" height="56" fill="{RED}"/>'
                        '<text x="1000" y="924" text-anchor="middle" font-family="sans-serif" font-weight="bold" font-size="40" fill="#fff">TOP SECRET</text></g>', delay(.9)))
    b.append('<ellipse cx="1560" cy="900" rx="110" ry="30" fill="#ece5d6"/><rect x="1490" y="780" width="140" height="120" rx="14" fill="#f7f2e6"/>'
             '<ellipse cx="1560" cy="785" rx="70" ry="16" fill="#3a2414"/><path d="M1630,800 Q1690,820 1630,870" stroke="#f7f2e6" stroke-width="16" fill="none"/>')
    b.append(steam(1530, 760, 3, 1.0))
    return svg("".join(b), d)


def a_world_map():
    d, s = sky("#0a1c30", "#020810")
    b = [s]
    for x in range(0, W, 80):
        b.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#1d4060" stroke-width="2"/>')
    for y in range(0, H, 80):
        b.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#1d4060" stroke-width="2"/>')
    b.append(g("scan", '<rect x="0" y="0" width="1920" height="60" fill="#4ab0d8" opacity=".12"/>'))
    blobs = ["M260,260 Q420,180 560,260 Q620,400 520,470 Q450,560 470,640 Q380,600 330,470 Q220,380 260,260Z",
             "M520,640 Q600,620 640,720 Q620,880 560,960 Q500,860 500,740Z",
             "M860,240 Q980,200 1060,250 Q1040,330 960,340 Q880,320 860,240Z",
             "M900,380 Q1040,360 1080,460 Q1060,640 980,720 Q900,620 880,480Z",
             "M1080,220 Q1380,160 1600,260 Q1640,380 1500,420 Q1380,480 1240,440 Q1120,380 1080,220Z",
             "M1480,640 Q1600,620 1640,700 Q1580,760 1500,740Z"]
    for p in blobs:
        b.append(f'<path d="{p}" fill="#1f5e7a" stroke="#4ab0d8" stroke-width="3"/>')
    for i, (x, y) in enumerate(((1400, 330), (1000, 520), (380, 360))):
        b.append(g("radar", f'<circle cx="{x}" cy="{y}" r="60" fill="none" stroke="{RED}" stroke-width="6"/>', f"animation-delay:-{i * .6:.1f}s"))
        b.append(g("popc", f'<circle cx="{x}" cy="{y}" r="16" fill="#ff6b6b"/>', delay(.3 + i * .5)))
    b.append('<path class="draw" d="M1400,330 Q1200,120 1000,520" stroke="#ffcf5a" stroke-width="5" fill="none" stroke-dasharray="16 12"/>')
    return svg("".join(b), d)


def a_colonnade():
    d, s = sky("#9ccbf0", "#f5f0e2")
    b = [s, clouds(3, 51, 30, 140), '<rect x="0" y="760" width="1920" height="320" fill="#c9bfa8"/>']
    for i in range(9):
        x = 120 + i * 210
        h = 520 + i * 10
        b.append(f'<rect x="{x}" y="{760 - h}" width="60" height="{h}" fill="{WHITE}"/>'
                 f'<rect x="{x - 12}" y="{760 - h - 20}" width="84" height="22" fill="#e6dcc4"/>')
    b.append(f'<rect x="0" y="160" width="1920" height="70" fill="{CREAM}"/>')
    b.append(g("walk", person(500, 900, .7, skin=SKIN[0], motion="march"), "--dx:900px;animation-duration:9s"))
    r = random.Random(3)
    for i in range(40):
        x = r.uniform(0, W)
        b.append(g("sway", f'<circle cx="{x:.0f}" cy="{r.uniform(800, 1060):.0f}" r="{r.uniform(18, 34):.0f}" fill="{r.choice([RED, "#e75a7c", "#f39ab0"])}"/>', desync(2, 3)))
    for i in range(30):
        b.append(f'<circle cx="{r.uniform(0, W):.0f}" cy="{r.uniform(830, 1080):.0f}" r="{r.uniform(26, 50):.0f}" fill="#3d7a3d" opacity=".8"/>')
    return svg("".join(b), d)


def oval_office(desk=True, extra="", behind=""):
    d = grad("wall", "#efe4c6", "#d9c9a2") + radial("rug", "#2e4f8a", "#1a2f57", .5, .5, .6)
    b = [f'<rect width="{W}" height="{H}" fill="url(#wall)"/>']
    for x in (300, 1500):
        b.append(f'<rect x="{x}" y="120" width="140" height="440" fill="#bcd8ef"/>'
                 + g("sway", f'<rect x="{x - 40}" y="100" width="60" height="520" fill="#a5323f"/>', desync(3, 4))
                 + g("sway", f'<rect x="{x + 120}" y="100" width="60" height="520" fill="#a5323f"/>', desync(3, 4))
                 + f'<line x1="{x + 70}" y1="120" x2="{x + 70}" y2="560" stroke="#fff" stroke-width="8"/>')
    b.append('<rect x="760" y="80" width="400" height="460" fill="#cfe3f3"/>'
             + g("sunbeam", '<path d="M760,80 L1160,80 L1500,1080 L500,1080Z" fill="#fff6d8" opacity=".12"/>')
             + '<rect x="740" y="60" width="440" height="30" fill="#a5323f"/>'
             '<line x1="893" y1="80" x2="893" y2="540" stroke="#fff" stroke-width="8"/><line x1="1026" y1="80" x2="1026" y2="540" stroke="#fff" stroke-width="8"/>')
    b.append(flag(600, 220, 120, 260, wave=4) + flag(1240, 220, 120, 260, wave=4))
    b.append('<ellipse cx="960" cy="980" rx="1100" ry="260" fill="url(#rug)"/>'
             f'<ellipse cx="960" cy="980" rx="320" ry="90" fill="none" stroke="{GOLD}" stroke-width="6"/>')
    b.append(behind)
    if desk:
        b.append('<rect x="560" y="600" width="800" height="330" fill="#5a3418"/>'
                 '<rect x="540" y="580" width="840" height="40" fill="#6d4020"/>'
                 '<rect x="860" y="660" width="200" height="270" fill="#4a2a12"/>'
                 f'<circle cx="960" cy="780" r="60" fill="none" stroke="{GOLD}" stroke-width="6"/>'
                 '<rect x="600" y="650" width="220" height="250" fill="#4e2e14"/><rect x="1100" y="650" width="220" height="250" fill="#4e2e14"/>'
                 '<rect x="1180" y="540" width="60" height="44" fill="#222"/><rect x="700" y="555" width="120" height="30" fill="#f6f0e2"/>')
    b.append(extra)
    return svg("".join(b), d)


def a_oval_office():
    return oval_office()


def a_resolute_desk():
    d, s = sky("#2c1a0e", "#120a05")
    b = [s, '<rect x="160" y="320" width="1600" height="680" rx="20" fill="#6b3c1a"/>',
         '<rect x="120" y="280" width="1680" height="70" rx="16" fill="#7d4a22"/>']
    b.append(g("ship", '<path d="M500,240 L1420,240 L1340,180 L580,180Z" fill="#fff" opacity=".07"/>'
             '<path d="M760,180 L760,40 M960,180 L960,20 M1160,180 L1160,50" stroke="#fff" stroke-width="8" opacity=".07"/>'))
    for x in (220, 1220):
        b.append(f'<rect x="{x}" y="400" width="480" height="560" rx="10" fill="#5a3014"/>'
                 f'<rect x="{x + 30}" y="430" width="420" height="500" rx="10" fill="none" stroke="#8a5a2e" stroke-width="10"/>')
    b.append('<rect x="740" y="400" width="440" height="560" fill="#4a2810"/>')
    seal = [f'<circle cx="960" cy="640" r="150" fill="none" stroke="{GOLD}" stroke-width="12"/>']
    for k in range(13):
        a = k * 2 * math.pi / 13
        seal.append(f'<circle cx="{960 + 120 * math.cos(a):.0f}" cy="{640 + 120 * math.sin(a):.0f}" r="7" fill="{GOLD}"/>')
    b.append(g("spin slowspin", "".join(seal)))
    b.append(g("pulse", star_shape(960, 640, 70, GOLD)))
    b.append(g("glint", '<rect x="160" y="320" width="120" height="700" fill="#fff" opacity=".07" transform="skewX(-20)"/>'))
    return svg("".join(b), d)


def a_schedule():
    d, s = sky("#e9eef5", "#c9d4e2")
    b = [s, '<rect x="300" y="80" width="1320" height="920" rx="24" fill="#fff"/>',
         f'<rect x="300" y="80" width="1320" height="110" rx="24" fill="{NAVY}"/>',
         '<text x="360" y="155" font-family="sans-serif" font-weight="bold" font-size="54" fill="#fff">TODAY</text>']
    r = random.Random(12)
    cols = [RED, "#3f6fd8", GOLD, "#5b8a5a", "#7a5fbf"]
    for i in range(16):
        y = 220 + i * 48
        b.append(f'<text x="330" y="{y + 32}" font-family="monospace" font-size="24" fill="#888">{8 + i // 4}:{(i % 4) * 15:02d}</text>'
                 f'<line x1="440" y1="{y}" x2="1580" y2="{y}" stroke="#e3e3e3" stroke-width="2"/>')
        b.append(g("grow-x", f'<rect x="460" y="{y + 6}" width="{r.randint(500, 1080)}" height="36" rx="8" fill="{cols[i % 5]}" opacity=".85"/>', delay(.1 + i * .09)))
    b.append(g("nowline", '<rect x="440" y="215" width="1150" height="4" fill="#e33"/>'))
    return svg("".join(b), d)


def a_phone_call():
    extra = (g("ring", f'<path d="M1240,520 Q1260,470 1300,470 L1380,470 Q1420,470 1430,520 L1400,540 L1270,540Z" fill="{NAVY}"/>'
                       f'<rect x="1270" y="530" width="140" height="50" rx="10" fill="{NAVY}"/>')
             + g("ringwaves", '<path d="M1450,470 q30,30 0,60 M1480,450 q45,50 0,100" stroke="#e33" stroke-width="6" fill="none"/>')
)
    return oval_office(extra=extra, behind=person(960, 760, .75, skin=SKIN[3], who="pres", gesture=True))


def a_little_league():
    d, s = sky("#86c3f0", "#eaf5fb")
    d2, l = lawn(700, "#6aa84f", "#3d7a33")
    b = [s, clouds(4, 61, 40, 200), l, white_house(960, 700, .6, lit=False)]
    for i in range(9):
        x = 360 + i * 150
        b.append(person(x, 1020, .55, suit=["#c0392b", "#2d58b8"][i % 2], skin=SKIN[i % 4], tie="#fff", hair="#3a2a1a",
                        arm_up=i % 3 == 0, motion="jump"))
    b.append(person(1080, 1040, .7, skin=SKIN[0]))
    b.append(g("camflash", '<rect width="1920" height="1080" fill="#fff"/>', "animation-duration:3s"))
    return svg("".join(b), d + d2)


def a_congress():
    d, s = sky("#2a1820", "#0f0a12")
    b = [s]
    r = random.Random(2)
    for row in range(6):
        r_ = 300 + row * 110
        for i in range(18):
            a = math.pi + (i + .5) * math.pi / 18
            x, y = 960 + r_ * math.cos(a), 1050 + r_ * .55 * math.sin(a)
            col = RED if (i + row) % 2 else "#3f6fd8"
            b.append(g("jump" if r.random() < .3 else "bob", f'<circle cx="{x:.0f}" cy="{y:.0f}" r="22" fill="{col}"/>', desync(.5, 1.2)))
    b.append('<rect x="760" y="820" width="400" height="200" fill="#5a3418"/>')
    b.append(g("gavel", '<rect x="900" y="740" width="200" height="40" rx="12" fill="#6d4020"/><rect x="990" y="760" width="20" height="120" fill="#6d4020"/>'))
    return svg("".join(b), d)


def a_secret_service():
    d, s = sky("#3a4a62", "#141b26")
    b = [s, '<rect x="0" y="880" width="1920" height="200" fill="#1b222e"/>']
    for i, x in enumerate((420, 960, 1500)):
        p = person(x, 1000 if i != 1 else 1040, 1.25 if i == 1 else 1.05, shades=True, earpiece=True, skin=SKIN[i], tie="#111", who="agent" if i == 1 else None, hair_style=["short", "bald", "short"][i], hair="#1a1a1a")
        b.append(g("slidein-l" if i == 0 else ("rise" if i == 1 else "slidein-r"), p, delay(i * .2)))
    b.append(g("sweep", '<path d="M-400,0 L200,0 L800,1080 L400,1080Z" fill="#fff" opacity=".05"/>'))
    return svg("".join(b), d)


def a_hallway_door():
    d = grad("hall", "#1d2433", "#0a0d14")
    b = [f'<rect width="{W}" height="{H}" fill="url(#hall)"/>',
         '<path d="M0,0 L760,320 L760,800 L0,1080Z" fill="#232c3d"/><path d="M1920,0 L1160,320 L1160,800 L1920,1080Z" fill="#232c3d"/>',
         '<path d="M760,800 L1160,800 L1920,1080 L0,1080Z" fill="#7a2230"/>',
         '<rect x="860" y="420" width="200" height="380" fill="#4a2e18"/>',
         g("winflicker", '<rect x="870" y="430" width="180" height="370" fill="#ffd98a" opacity=".5"/>', "animation-duration:5s")]
    b.append(person(560, 1020, 1.0, shades=True, earpiece=True, skin=SKIN[2], tie="#111", motion="lookaround", who="agent", hair_style="short", hair="#111"))
    b.append(person(1360, 1020, 1.0, shades=True, earpiece=True, skin=SKIN[0], tie="#111", motion="lookaround"))
    return svg("".join(b), d)


def car(x, y, flagged=False, flash=False):
    c = (f'<g transform="translate({x},{y})"><rect x="0" y="0" width="460" height="120" rx="30" fill="#0d0d0f"/>'
         '<path d="M60,0 L120,-80 L340,-80 L400,0Z" fill="#141418"/>'
         '<path d="M130,-8 L160,-64 L310,-64 L340,-8Z" fill="#33445a"/>'
         + g("wheelspin", '<circle cx="100" cy="120" r="44" fill="#000"/><circle cx="100" cy="120" r="18" fill="#777"/><rect x="96" y="80" width="8" height="80" fill="#333"/>')
         + g("wheelspin", '<circle cx="360" cy="120" r="44" fill="#000"/><circle cx="360" cy="120" r="18" fill="#777"/><rect x="356" y="80" width="8" height="80" fill="#333"/>')
         + '<rect x="440" y="20" width="22" height="16" fill="#fff6c8"/>')
    if flagged:
        c += f'<rect x="380" y="-110" width="6" height="40" fill="#bbb"/>{flag(386, -110, 46, 28, pole=False)}'
    if flash:
        c += (g("flashred", '<circle cx="200" cy="-90" r="14" fill="#ff3030"/>') +
              g("flashblue", '<circle cx="260" cy="-90" r="14" fill="#3070ff"/>'))
    return c + '</g>'


def a_motorcade():
    d, s = sky("#2b3a55", "#9aa7bc")
    b = [s, '<rect x="0" y="700" width="1920" height="380" fill="#2c2c30"/>']
    city = "".join(f'<rect x="{x}" y="{420 + (x * 7) % 90}" width="140" height="{280 - (x * 7) % 90}" fill="#3a465c"/>' for x in range(0, 3840, 180))
    b.append(g("parallax", city))
    b.append(g("roadlines", "".join(f'<rect x="{x}" y="880" width="120" height="12" fill="#e9e3d0" opacity=".6"/>' for x in range(0, 3840, 240))))
    cars = "".join(car(x, 720, flagged=(i == 2), flash=(i in (0, 3))) for i, x in enumerate((-80, 520, 1120, 1720)))
    b.append(g("cruise", cars))
    return svg("".join(b), d)


def a_no_driving():
    d, s = sky("#88b8e0", "#e8f0f6")
    b = [s, clouds(4, 71, 30, 260), '<rect x="0" y="720" width="1920" height="360" fill="#3a3a40"/>',
         '<rect x="0" y="880" width="1920" height="14" fill="#f1d36a"/>']
    b.append(g("shake", '<rect x="560" y="560" width="800" height="200" rx="60" fill="#c0392b"/>'
             '<path d="M700,560 L800,420 L1120,420 L1220,560Z" fill="#a32e22"/>'
             '<path d="M760,550 L830,440 L1090,440 L1160,550Z" fill="#9fc6e0"/>'
             '<circle cx="740" cy="770" r="70" fill="#111"/><circle cx="1180" cy="770" r="70" fill="#111"/>'))
    b.append(g("slam", f'<circle cx="960" cy="540" r="380" fill="none" stroke="{RED}" stroke-width="50" opacity=".9"/>'
             f'<line x1="690" y1="270" x2="1230" y2="810" stroke="{RED}" stroke-width="50" opacity=".9"/>', delay(.6)))
    return svg("".join(b), d)


def a_aide():
    d, s = sky("#5a6a84", "#1b2230")
    b = [s, '<rect x="0" y="860" width="1920" height="220" fill="#2a3242"/>']
    aide = (person(700, 980, 1.25, suit="#1b2b4a", skin=SKIN[1], tie="#1b2b4a", hair="#111", motion="", who="aide", hair_style="short", gesture=True)
            + g("swing", '<rect x="760" y="760" width="220" height="160" rx="16" fill="#111"/><path d="M820,760 Q870,720 920,760" stroke="#111" stroke-width="16" fill="none"/>')
            + f'<rect x="590" y="660" width="220" height="16" fill="{GOLD}"/>')
    b.append(g("follow", aide))
    b.append(g("follow", person(1300, 980, 1.25, skin=SKIN[0], motion=""), "animation-delay:-.3s"))
    return svg("".join(b), d)


def a_crossroads():
    d, s = sky("#3c2a52", "#e8925a")
    b = [s, g("pulse", '<circle cx="960" cy="700" r="200" fill="#ffd38a" opacity=".5"/>'), '<rect x="0" y="700" width="1920" height="380" fill="#3a2a2a"/>',
         '<path d="M860,1080 L940,700 L980,700 L1060,1080Z" fill="#5e4a42"/>',
         '<path d="M940,700 L300,1080 L560,1080 L960,700Z" fill="#5e4a42"/><path d="M980,700 L1620,1080 L1360,1080 L960,700Z" fill="#5e4a42"/>',
         '<rect x="946" y="300" width="28" height="560" fill="#6b4a2a"/>']
    b.append(g("signswing", f'<path d="M700,340 L940,340 L940,420 L700,420 L650,380Z" fill="{CREAM}"/>'
             '<text x="810" y="398" text-anchor="middle" font-family="sans-serif" font-weight="bold" font-size="50" fill="#333">BAD</text>', "transform-origin:100% 50%"))
    b.append(g("signswing", f'<path d="M980,460 L1220,460 L1270,500 L1220,540 L980,540Z" fill="{CREAM}"/>'
             '<text x="1110" y="518" text-anchor="middle" font-family="sans-serif" font-weight="bold" font-size="50" fill="#333">WORSE</text>', "transform-origin:0% 50%;animation-delay:-1s"))
    b.append(g("tumble", '<path d="M300,1000 q20,-30 40,0 q20,-30 40,0" stroke="#7a5a3a" stroke-width="10" fill="none"/>'))
    return svg("".join(b), d)


def a_troops():
    d, s = sky("#c9a46a", "#6a5032")
    b = [s, '<rect x="0" y="760" width="1920" height="320" fill="#8a6a42"/>', flag(1500, 260, 260, 160, wave=8)]
    for i in range(10):
        x = 120 + i * 180
        b.append(f'<g opacity="{.5 + .05 * i}">{person(x, 980 - (i % 2) * 20, .8, suit="#4e5a34", skin=SKIN[i % 4], tie="#4e5a34", hair="#4e5a34", motion="march")}</g>')
    b.append(g("dust", "".join(f'<circle cx="{_rng.uniform(0, W):.0f}" cy="{_rng.uniform(900, 1060):.0f}" r="{_rng.uniform(8, 20):.0f}" fill="#c9a46a" opacity=".35"/>' for _ in range(30))))
    return svg("".join(b), d)


def a_bill_signing(pen_only=False):
    d, s = sky("#3b2414", "#1a0f08")
    b = [s, '<rect x="0" y="560" width="1920" height="520" fill="#6d4020"/>']
    b.append('<path d="M600,520 L1320,520 L1360,1000 L560,1000Z" fill="#f6f0e2"/>')
    b.append('<text x="960" y="620" text-anchor="middle" font-family="serif" font-weight="bold" font-size="56" fill="#333">AN ACT</text>')
    r = random.Random(6)
    for row in range(8):
        y = 670 + row * 34
        b.append(f'<rect x="650" y="{y}" width="{r.randint(400, 620)}" height="10" rx="5" fill="#9a8e78"/>')
    b.append('<path class="draw" d="M760,960 Q820,920 880,950 Q940,980 1000,930 Q1050,900 1120,950" stroke="#22356b" stroke-width="6" fill="none"/>')
    pen = (f'<g transform="rotate(35 1200 760)"><rect x="1180" y="560" width="40" height="320" rx="16" fill="{NAVY}"/>'
           f'<path d="M1180,880 L1220,880 L1200,940Z" fill="{GOLD}"/><rect x="1180" y="600" width="40" height="14" fill="{GOLD}"/></g>')
    arm = f'<path d="M1500,1080 Q1480,820 1300,760 L1260,800 Q1380,880 1360,1080Z" fill="{SUIT}"/>' if not pen_only else ""
    b.append(g("signing", pen + arm))
    return svg("".join(b), d)


def a_veto():
    d, s = sky("#4a1a1a", "#120606")
    b = [s, '<rect x="0" y="560" width="1920" height="520" fill="#4a2a14"/>',
         '<path d="M600,180 L1320,180 L1360,900 L560,900Z" fill="#f6f0e2" transform="rotate(-4 960 540)"/>']
    b.append(g("stamp", f'<g transform="rotate(-14 960 520)"><rect x="620" y="420" width="680" height="200" rx="16" fill="none" stroke="{RED}" stroke-width="20"/>'
             f'<text x="960" y="575" text-anchor="middle" font-family="sans-serif" font-weight="bold" font-size="150" fill="{RED}">VETOED</text></g>', delay(.35)))
    return svg("".join(b), d)


def a_situation_room():
    d = grad("sr", "#0e1420", "#05070b")
    b = [f'<rect width="{W}" height="{H}" fill="url(#sr)"/>']
    for i, x in enumerate((180, 760, 1340)):
        b.append(g("screenflicker", f'<rect x="{x}" y="90" width="420" height="250" rx="8" fill="#0b2a44" stroke="#2a5a80" stroke-width="6"/>', desync(2, 4)))
    b.append('<path class="draw loopdraw" d="M240,300 Q320,180 420,260 Q500,320 560,200" stroke="#4ab0d8" stroke-width="6" fill="none"/>'
             '<circle cx="970" cy="215" r="80" fill="none" stroke="#4ab0d8" stroke-width="4"/>')
    b.append(g("radarsweep", '<rect x="890" y="135" width="160" height="160" fill="none"/><path d="M970,215 L970,135" stroke="#4ab0d8" stroke-width="4"/>'))
    b.append(g("blip", f'<circle cx="1010" cy="190" r="10" fill="{RED}"/>'))
    for k, w in enumerate((320, 240, 280)):
        b.append(g("grow-x loopgrow", f'<rect x="1390" y="{140 + k * 50}" width="{w}" height="20" fill="#4ab0d8"/>', f"animation-delay:-{k * .7:.1f}s"))
    b.append('<ellipse cx="960" cy="800" rx="760" ry="170" fill="#3a2414"/><ellipse cx="960" cy="790" rx="740" ry="160" fill="#4a2e1a"/>')
    r = random.Random(14)
    for i in range(10):
        a = math.pi * (i + .5) / 10
        x, y = 960 - 800 * math.cos(a), 760 - 190 * math.sin(a) + 40
        b.append(g("bob", f'<circle cx="{x:.0f}" cy="{y - 110:.0f}" r="34" fill="{r.choice(SKIN)}"/>'
                          f'<path d="M{x - 60:.0f},{y + 10:.0f} Q{x - 60:.0f},{y - 70:.0f} {x:.0f},{y - 72:.0f} Q{x + 60:.0f},{y - 70:.0f} {x + 60:.0f},{y + 10:.0f}Z" fill="{SUIT}"/>', desync(2, 3.5)))
    for i in range(6):
        b.append(f'<rect x="{560 + i * 140}" y="760" width="70" height="48" rx="4" fill="#f6f0e2"/><ellipse cx="{620 + i * 140}" cy="800" rx="18" ry="8" fill="#ddd"/>')
    b.append(steam(600, 790, 2, .6) + steam(1160, 790, 2, .6))
    return svg("".join(b), d)


def a_divided():
    d = grad("div", RED, "#2d58b8", 1, 0)
    b = [f'<rect width="{W}" height="{H}" fill="url(#div)"/>']
    r = random.Random(21)
    for side, col in ((0, "#6b1420"), (1, "#14306b")):
        for i in range(60):
            x = r.uniform(80 + side * 1000, 840 + side * 1000)
            y = r.uniform(300, 1000)
            s_ = r.uniform(.6, 1.0)
            b.append(g("jump", f'<circle cx="{x:.0f}" cy="{y - 60 * s_:.0f}" r="{22 * s_:.0f}" fill="{col}"/>'
                               f'<path d="M{x - 34 * s_:.0f},{y + 30 * s_:.0f} Q{x - 34 * s_:.0f},{y - 30 * s_:.0f} {x:.0f},{y - 32 * s_:.0f} Q{x + 34 * s_:.0f},{y - 30 * s_:.0f} {x + 34 * s_:.0f},{y + 30 * s_:.0f}Z" fill="{col}"/>', desync(.5, 1)))
    b.append(g("pulse", '<rect x="950" y="0" width="20" height="1080" fill="#fff" opacity=".7"/>'))
    return svg("".join(b), d)


def a_letters():
    d, s = sky("#1a1410", "#0a0705")
    b = [s, g("candle", '<ellipse cx="960" cy="420" rx="700" ry="420" fill="#ffd98a" opacity=".18"/>'),
         '<rect x="0" y="620" width="1920" height="460" fill="#5a3418"/>',
         '<path d="M1500,620 L1440,300 L1700,300 L1640,620Z" fill="#2d5e32"/><rect x="1555" y="300" width="30" height="40" fill="#c9a14a"/>']
    r = random.Random(9)
    for i in range(16):
        x, y = r.uniform(440, 1340), r.uniform(560, 900)
        rot = r.uniform(-25, 25)
        env = (f'<g transform="rotate({rot:.0f} {x:.0f} {y:.0f})"><rect x="{x - 130:.0f}" y="{y - 80:.0f}" width="260" height="160" fill="{r.choice([CREAM, WHITE, "#e8f0f7"])}" stroke="#b9ad92" stroke-width="2"/>'
               f'<path d="M{x - 130:.0f},{y - 80:.0f} L{x:.0f},{y + 10:.0f} L{x + 130:.0f},{y - 80:.0f}" stroke="#b9ad92" stroke-width="3" fill="none"/>'
               f'<rect x="{x + 70:.0f}" y="{y - 66:.0f}" width="44" height="52" fill="{r.choice([RED, "#3f6fd8"])}"/></g>')
        b.append(g("dropin", env, delay(.05 + i * .12)))
    return svg("".join(b), d)


def a_letter_open():
    d, s = sky("#2a1d14", "#0f0a06")
    b = [s, g("candle", '<rect x="0" y="0" width="1920" height="1080" fill="url(#lamp)"/>')]
    paper = ['<rect x="560" y="80" width="800" height="940" fill="#fbf7ec"/>',
             '<text x="660" y="230" font-family="serif" font-style="italic" font-size="64" fill="#2a2a5a">Dear President,</text>']
    r = random.Random(17)
    for row in range(14):
        y = 320 + row * 52
        paper.append(f'<path class="draw" style="animation-delay:{.3 + row * .35:.2f}s" d="M660,{y} q{r.randint(80, 120)},-14 {r.randint(160, 240)},0 t{r.randint(160, 260)},0 t{r.randint(100, 200)},0" '
                     f'stroke="#2a2a5a" stroke-width="5" fill="none" opacity=".75"/>')
    b.append(f'<g transform="rotate(-3 960 540)">{"".join(paper)}</g>')
    return svg("".join(b), d + radial("lamp", "#7a5a32", "#0f0a06", .5, .3, .8))


def a_turkey():
    d, s = sky("#9cc8ec", "#f3e3c3")
    d2, l = lawn(760)
    b = [s, clouds(4, 81, 30, 260), l, flag(240, 300, 200, 120, wave=6)]
    tail = []
    for i in range(9):
        a = math.pi + (i + .5) * math.pi / 9
        cx, cy = 960 + 230 * math.cos(a), 620 + 230 * math.sin(a)
        tail.append(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="70" ry="170" '
                    f'fill="{["#8a4a22", "#c27a2c", "#5a2e14"][i % 3]}" transform="rotate({math.degrees(a) + 90:.0f} {cx:.0f} {cy:.0f})"/>')
    b.append(g("fan", "".join(tail)))
    b.append('<ellipse cx="960" cy="700" rx="170" ry="150" fill="#5a3418"/>'
             '<path d="M900,840 L900,920 M1020,840 L1020,920" stroke="#e8b830" stroke-width="12"/>')
    b.append(g("peck", '<ellipse cx="960" cy="520" rx="60" ry="80" fill="#6b3c1a"/><circle cx="960" cy="440" r="50" fill="#7d4a22"/>'
             f'<path d="M960,470 Q930,520 950,560" stroke="{RED}" stroke-width="22" fill="none"/>'
             '<path d="M1000,440 L1050,450 L1000,460Z" fill="#e8b830"/><circle cx="980" cy="430" r="8" fill="#111"/>'))
    b.append(person(1480, 980, 1.0, skin=SKIN[0], arm_up=True, who="pres"))
    return svg("".join(b), d + d2)


def a_baseball():
    d, s = sky("#1d3b6e", "#4f7fc0")
    b = [s, '<rect x="0" y="380" width="1920" height="700" fill="#3d8a3d"/>',
         '<path d="M960,520 L1440,860 L960,1200 L480,860Z" fill="#c98e5a"/>',
         '<path d="M960,600 L1320,860 L960,1120 L600,860Z" fill="#3d8a3d"/>',
         '<ellipse cx="960" cy="860" rx="90" ry="40" fill="#c98e5a"/>']
    for x in range(0, 1920, 64):
        b.append(g("jump", f'<rect x="{x}" y="200" width="40" height="180" fill="{["#222", "#2a2a2a"][x // 64 % 2]}"/>', desync(.5, .9)))
    for x in (200, 1720):
        b.append(f'<rect x="{x - 10}" y="40" width="20" height="340" fill="#888"/>' + g("tw", f'<rect x="{x - 90}" y="20" width="180" height="80" fill="#eee"/>', desync(.8, 1.4)))
    b.append(person(960, 880, .9, skin=SKIN[1], arm_up=True, wave_arm=False, motion="pitch", who="pres"))
    b.append(g("pitchball", '<circle cx="1062" cy="470" r="26" fill="#fff"/><path d="M1047,455 Q1062,470 1047,485 M1077,455 Q1062,470 1077,485" stroke="red" stroke-width="3" fill="none"/>'))
    return svg("".join(b), d)


def a_easter():
    d, s = sky("#a8d8f0", "#f5f0d8")
    d2, l = lawn(700, "#7cc06a", "#4a8a3a")
    b = [s, clouds(4, 91, 30, 200), white_house(960, 700, .55, lit=False), l]
    r = random.Random(30)
    for i in range(40):
        x, y = r.uniform(60, 1860), r.uniform(760, 1060)
        b.append(g("wobble", f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="22" ry="30" fill="{r.choice(["#f39ab0", "#9ad0f3", "#f3e19a", "#b39af3", "#9af3b8"])}"/>', desync(.8, 1.6)))
    for i in range(6):
        x = 240 + i * 290
        kid = (f'<g transform="translate({x},1000) scale(.45)"><circle cx="0" cy="-200" r="50" fill="{SKIN[i % 4]}"/>'
               f'<path d="M-60,0 Q-60,-150 0,-150 Q60,-150 60,0Z" fill="{["#f39ab0", "#9ad0f3", "#f3e19a"][i % 3]}"/>'
               '<path d="M60,-90 L140,-60" stroke="#8a6232" stroke-width="10"/><ellipse cx="150" cy="-50" rx="40" ry="18" fill="#c9a14a"/></g>')
        b.append(g("hop", kid, desync(.5, .8)))
    return svg("".join(b), d + d2)


def a_christmas_tree():
    d, s = sky("#0b1a33", "#1f3d6e")
    b = [s, stars(120, 31, 700), '<rect x="0" y="880" width="1920" height="200" fill="#e8eef5"/>',
         white_house(1500, 880, .45, lit=True, fill="#d8dfe8")]
    for w, y in ((520, 880), (440, 720), (360, 570), (260, 430)):
        b.append(f'<path d="M{760 - w / 2 + 100},{y} L{860},{y - 260} L{960 + w / 2 - 100},{y}Z" fill="#1f6b3a"/>')
    r = random.Random(32)
    for i in range(70):
        y = r.uniform(240, 860)
        half = (y - 170) * .42
        x = 860 + r.uniform(-half, half)
        b.append(g("tw", f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="{r.choice(["#ffd98a", RED, "#9ad0f3", "#fff"])}"/>', desync(.6, 1.5)))
    b.append(g("pulse", star_shape(860, 170, 60, GOLD)) + '<rect x="830" y="880" width="60" height="80" fill="#5a3418"/>')
    b.append(snow())
    return svg("".join(b), d)


def a_air_force_one():
    d, s = sky("#5f9fe0", "#dfeefa")
    b = [s, clouds(5, 101, 80, 500, .7, speed=2.5)]
    plane = ['<g transform="rotate(-8 960 480)">',
             '<path d="M300,470 Q300,420 380,410 L1500,410 Q1640,420 1680,470 Q1640,520 1500,530 L380,530 Q300,520 300,470Z" fill="#f6f6f2"/>',
             '<path d="M1500,410 Q1600,415 1650,450 L1480,450 Z" fill="#cfe0ef"/>',
             '<path d="M380,410 Q500,360 680,360 L760,410Z" fill="#f6f6f2"/>',
             '<path d="M300,470 L1680,470 Q1660,500 1600,510 L380,510 Q320,505 300,470Z" fill="#7fb4de"/>',
             '<rect x="380" y="470" width="1220" height="10" fill="#1f3d6e"/>',
             '<path d="M820,500 L1140,500 L980,820 L860,820Z" fill="#dcdcd6"/><path d="M820,420 L1060,420 L960,180 L880,180Z" fill="#e6e6e0"/>',
             '<path d="M340,440 L280,250 L360,250 L460,420Z" fill="#7fb4de"/>',
             flag(300, 290, 70, 42, pole=False)]
    for x in range(480, 1500, 44):
        plane.append(f'<rect x="{x}" y="438" width="20" height="16" rx="5" fill="#1f3d6e"/>')
    plane.append('<rect x="880" y="640" width="90" height="40" rx="18" fill="#bbb"/><rect x="940" y="740" width="90" height="40" rx="18" fill="#bbb"/>')
    plane.append(g("contrail", '<rect x="40" y="652" width="840" height="10" rx="5" fill="#fff" opacity=".7"/><rect x="100" y="752" width="840" height="10" rx="5" fill="#fff" opacity=".7"/>'))
    plane.append('</g>')
    b.append(g("flyby", g("hover", "".join(plane))))
    b.append(clouds(3, 103, 700, 1000, .9, speed=4))
    return svg("".join(b), d)


def a_plane_interior():
    d = grad("cab", "#e9e2d2", "#b9ae96")
    b = [f'<rect width="{W}" height="{H}" fill="url(#cab)"/>',
         '<path d="M0,0 L1920,0 L1920,140 Q960,240 0,140Z" fill="#f6f2ea"/>',
         '<rect x="0" y="760" width="1920" height="320" fill="#1f3d6e"/>']
    for i, x in enumerate((160, 480, 1360, 1680)):
        b.append(f'<clipPath id="win{i}"><rect x="{x}" y="260" width="120" height="170" rx="56"/></clipPath>'
                 f'<rect x="{x}" y="260" width="120" height="170" rx="56" fill="#9fc6e0"/>'
                 f'<g clip-path="url(#win{i})">{g("windowcloud", f"<ellipse cx=\"{x + 60}\" cy=\"350\" rx=\"70\" ry=\"24\" fill=\"#fff\"/>", f"animation-delay:-{i * .7:.1f}s")}</g>'
                 f'<rect x="{x}" y="260" width="120" height="170" rx="56" fill="none" stroke="#ddd" stroke-width="10"/>')
    b.append(g("turbulence", '<rect x="660" y="520" width="600" height="60" fill="#6b3c1a"/><rect x="700" y="580" width="40" height="200" fill="#5a3014"/><rect x="1180" y="580" width="40" height="200" fill="#5a3014"/>'
             '<rect x="560" y="440" width="120" height="340" rx="20" fill="#c9b27a"/><rect x="1240" y="440" width="120" height="340" rx="20" fill="#c9b27a"/>'
             + steam(900, 500, 2, .6) + '<rect x="880" y="490" width="50" height="40" rx="6" fill="#fff"/>'))
    b.append(g("pulse", f'<circle cx="960" cy="400" r="70" fill="none" stroke="{GOLD}" stroke-width="8"/>{star_shape(960, 400, 40, GOLD)}'))
    return svg("".join(b), d)


def heli(x, y, sc, op):
    body = ('<ellipse cx="0" cy="0" rx="300" ry="110" fill="#1d3a27"/><rect x="-300" y="0" width="600" height="80" fill="#f2f0ea"/>'
            '<ellipse cx="0" cy="40" rx="300" ry="70" fill="#f2f0ea"/><path d="M250,-20 L620,-40 L640,10 L260,40Z" fill="#1d3a27"/>'
            '<path d="M600,-90 L660,-90 L650,40 L610,40Z" fill="#1d3a27"/>'
            '<rect x="-160" y="-40" width="80" height="50" rx="10" fill="#9fc6e0"/><rect x="-60" y="-40" width="80" height="50" rx="10" fill="#9fc6e0"/>'
            '<rect x="-12" y="-160" width="24" height="60" fill="#333"/>'
            + g("rotor", '<rect x="-520" y="-175" width="1040" height="16" rx="8" fill="#333" opacity=".8"/>')
            + g("tailrotor", '<rect x="620" y="-110" width="16" height="90" rx="8" fill="#333"/>')
            + '<path d="M-200,110 L-200,150 M200,110 L200,150 M-260,150 L260,150" stroke="#333" stroke-width="10"/>')
    return g("hover", f'<g transform="translate({x},{y}) scale({sc})" opacity="{op}">{body}</g>', desync(1.4, 2.2))


def a_helicopter():
    d, s = sky("#86b8e6", "#f0e7d2")
    d2, l = lawn(820)
    b = [s, clouds(4, 111, 40, 300), white_house(1350, 820, .55, lit=False), l]
    b.append(g("sway", '<rect x="0" y="820" width="1920" height="60" fill="#3a7a3a" opacity=".5"/>', "animation-duration:.6s"))
    b.append(heli(300, 260, .5, .8) + heli(1500, 220, .45, .8))
    b.append(g("liftoff", heli(760, 420, 1.0, 1)))
    return svg("".join(b), d + d2)


def a_camp_david():
    d, s = sky("#e89a5a", "#5a3a5e")
    b = [s, g("pulse", '<circle cx="1400" cy="520" r="120" fill="#ffd38a" opacity=".85"/>'), clouds(3, 121, 60, 300, .35)]
    r = random.Random(50)
    for col, base in (("#3b2f4a", 640), ("#24352a", 760), ("#182419", 900)):
        trees = []
        for i in range(30):
            x = i * 70 + r.uniform(-20, 20)
            h = r.uniform(140, 300)
            trees.append(g("treesway", f'<path d="M{x - 60:.0f},{base} L{x:.0f},{base - h:.0f} L{x + 60:.0f},{base}Z" fill="{col}"/>', desync(3, 5)))
        b.append("".join(trees))
    b.append('<rect x="0" y="900" width="1920" height="180" fill="#121a12"/>')
    b.append('<rect x="720" y="760" width="420" height="180" fill="#6b4a2a"/><path d="M690,770 L930,640 L1170,770Z" fill="#3a2414"/>'
             '<rect x="1040" y="660" width="40" height="70" fill="#4a3020"/>'
             + g("winflicker", '<rect x="780" y="810" width="70" height="60" fill="#ffd98a"/>', desync(2, 4))
             + g("winflicker", '<rect x="1010" y="810" width="70" height="60" fill="#ffd98a"/>', desync(2, 4))
             + '<rect x="900" y="830" width="60" height="110" fill="#3a2414"/>')
    b.append(g("smoke", "".join(g("steam bigsteam", f'<circle cx="1060" cy="650" r="{14 + i * 4}" fill="#ccc" opacity=".5"/>', f"animation-delay:-{i * .7:.1f}s") for i in range(4))))
    return svg("".join(b), d)


def a_portrait_aging():
    d = grad("pa", "#e8dfcc", "#cbbd9d")
    b = [f'<rect width="{W}" height="{H}" fill="url(#pa)"/>']
    for k, (x, hair) in enumerate(((560, "#2a1d14"), (1360, "#c9c9c9"))):
        frame = (f'<rect x="{x - 300}" y="120" width="600" height="760" fill="{GOLD}"/><rect x="{x - 270}" y="150" width="540" height="700" fill="#1f3d6e"/>'
                 f'<g transform="translate(0,-30)">{person(x, 1210, 1.6, skin=SKIN[0], hair=hair, motion="")}</g>')
        if k == 1:
            frame += f'<path d="M{x - 40},560 q15,6 30,0 M{x + 10},560 q15,6 30,0 M{x - 30},612 q30,10 60,0" stroke="#9a7a5a" stroke-width="4" fill="none"/>'
        frame += f'<rect x="{x - 300}" y="850" width="600" height="230" fill="url(#pa)"/>'
        b.append(g("popc", frame, delay(.1 + k * .9)))
    b.append(g("nudge", '<path d="M900,500 L1020,500 L1020,460 L1090,530 L1020,600 L1020,560 L900,560Z" fill="#7a5a32"/>'))
    return svg("".join(b), d)


def a_press():
    d = grad("pr", "#1c2a4a", "#0a1020")
    b = [f'<rect width="{W}" height="{H}" fill="url(#pr)"/>',
         '<rect x="0" y="0" width="1920" height="620" fill="#22355e"/>',
         '<rect x="560" y="120" width="800" height="380" rx="12" fill="#2c4476"/>',
         f'<circle cx="960" cy="300" r="130" fill="none" stroke="{GOLD}" stroke-width="10"/>',
         star_shape(960, 300, 70, GOLD),
         '<rect x="0" y="600" width="1920" height="40" fill="#162441"/>']
    b.append(flag(300, 180, 160, 300, wave=5) + flag(1500, 180, 160, 300, wave=5))
    b.append(person(960, 900, 1.05, skin=SKIN[1]))
    b.append(f'<path d="M800,640 L1120,640 L1090,980 L830,980Z" fill="#3a2516"/><rect x="790" y="625" width="340" height="24" rx="6" fill="#4a3020"/>')
    b.append(f'<circle cx="960" cy="790" r="64" fill="{GOLD}" opacity=".9"/>{star_shape(960, 790, 42, NAVY)}')
    for i in range(3):
        b.append(f'<rect x="{935 + i * 22}" y="575" width="8" height="55" fill="#222"/><ellipse cx="{939 + i * 22}" cy="570" rx="10" ry="14" fill="#111"/>')
    r = random.Random(60)
    reporters = []
    for i in range(14):
        x = 70 + i * 135 + r.uniform(-15, 15)
        body = (f'<circle cx="{x:.0f}" cy="985" r="40" fill="#0b111d"/>'
                f'<path d="M{x - 70:.0f},1090 Q{x - 70:.0f},1020 {x:.0f},1018 Q{x + 70:.0f},1020 {x + 70:.0f},1090Z" fill="#0b111d"/>')
        if i % 3 == 1:
            body += (f'<rect x="{x + 20:.0f}" y="930" width="70" height="46" rx="8" fill="#151515"/>'
                     f'<circle cx="{x + 55:.0f}" cy="953" r="15" fill="#333"/>'
                     + g("flash", f'<circle cx="{x + 30:.0f}" cy="938" r="60" fill="#fff"/>',
                         f"animation-delay:-{r.uniform(0, 3):.2f}s;animation-duration:{r.uniform(1.6, 3):.2f}s"))
        reporters.append(g("bob", body, desync(1.5, 2.5)))
    b.append("".join(reporters))
    return svg("".join(b), d)


def a_homecoming():
    d, s = sky("#9ccbf0", "#f7e8c8")
    b = [s, confetti(80, 17), '<rect x="0" y="780" width="1920" height="300" fill="#b9b2a4"/>']
    b.append(flag(140, 120, 600, 360, wave=16, pole=False) + flag(1180, 120, 600, 360, wave=16, pole=False))
    for i in range(7):
        x = 200 + i * 250
        b.append(person(x, 1000, .85, suit="#5a6a3a", tie="#5a6a3a", skin=SKIN[i % 4], hair="#4e5a34", motion="march",
                        hair_style="cap", who="soldier" if i == 2 else None, shirt="#6b7b4a"))
    b.append(person(960, 1060, 1.0, skin=SKIN[3], arm_up=True))
    return svg("".join(b), d)


def a_tornado_town():
    d, s = sky("#4a5568", "#a0aec0")
    b = [s, clouds(5, 131, 40, 320, .3, speed=3), '<rect x="0" y="780" width="1920" height="300" fill="#6b5a44"/>']
    for x, h in ((100, 220), (420, 160), (1240, 240), (1560, 180)):
        b.append(f'<rect x="{x}" y="{780 - h}" width="260" height="{h}" fill="#8a7a62"/>'
                 f'<path d="M{x - 20},{780 - h} L{x + 130},{780 - h - 110} L{x + 280},{780 - h}Z" fill="#5a3a2a"/>')
    b.append('<path d="M760,780 L820,640 L900,700 L960,600 L1040,690 L1100,780Z" fill="#7a6a52"/>')
    r = random.Random(70)
    for i in range(30):
        x, y = r.uniform(700, 1150), r.uniform(720, 800)
        b.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{r.uniform(40, 120):.0f}" height="12" fill="#5a4a32" transform="rotate({r.uniform(-40, 40):.0f} {x:.0f} {y:.0f})"/>')
    for i in range(10):
        b.append(g("debris", f'<rect x="{r.uniform(0, 600):.0f}" y="{r.uniform(200, 600):.0f}" width="20" height="8" fill="#5a4a32"/>', f"animation-delay:-{r.uniform(0, 4):.1f}s"))
    for i in range(6):
        b.append(person(560 + i * 170, 1020, .7, suit=["#30507a", "#7a3030", "#3a6a3a"][i % 3], skin=SKIN[i % 4], tie="#fff", arm_up=(i == 2)))
    return svg("".join(b), d)


def a_amendment():
    d, s = sky("#2a1d14", "#120c08")
    b = [s, g("candle", '<ellipse cx="960" cy="540" rx="800" ry="500" fill="#ffd98a" opacity=".08"/>'),
         '<rect x="440" y="140" width="1040" height="800" fill="#ead9b0"/>',
         g("fadein", '<text x="960" y="300" text-anchor="middle" font-family="serif" font-weight="bold" font-size="90" fill="#3a2a16">AMENDMENT XXII</text>', delay(.1)),
         g("fadein", '<text x="960" y="400" text-anchor="middle" font-family="serif" font-style="italic" font-size="48" fill="#5a4426">No person shall be elected</text>', delay(.6)),
         g("fadein", '<text x="960" y="470" text-anchor="middle" font-family="serif" font-style="italic" font-size="48" fill="#5a4426">to the office of the President</text>', delay(1.0)),
         g("fadein", '<text x="960" y="540" text-anchor="middle" font-family="serif" font-style="italic" font-size="48" fill="#5a4426">more than twice...</text>', delay(1.4))]
    for k, x in enumerate((780, 1140)):
        b.append(g("popc", f'<rect x="{x - 90}" y="640" width="180" height="200" rx="12" fill="#1f3d6e"/>{star_shape(x, 740, 60, GOLD)}', delay(1.9 + k * .4)))
    return svg("".join(b), d)


def a_hourglass():
    d, s = sky("#1f3d6e", "#0b1a33")
    b = [s, stars(80, 81, 1080, .5),
         f'<rect x="700" y="120" width="520" height="40" rx="12" fill="{GOLD}"/><rect x="700" y="920" width="520" height="40" rx="12" fill="{GOLD}"/>',
         '<path d="M740,160 L1180,160 Q1180,420 980,540 Q1180,660 1180,920 L740,920 Q740,660 940,540 Q740,420 740,160Z" fill="#cfe3f3" opacity=".35"/>',
         g("sandtop", '<path d="M840,300 L1080,300 Q1040,440 960,520 Q880,440 840,300Z" fill="#e0b95e"/>'),
         g("sandbot", '<path d="M780,920 Q960,700 1140,920Z" fill="#e0b95e"/>'),
         g("stream", '<line x1="960" y1="540" x2="960" y2="900" stroke="#e0b95e" stroke-width="6" stroke-dasharray="10 14"/>')]
    return svg("".join(b), d)


def a_desk_letter():
    extra = g("dropin", '<g transform="rotate(-8 960 600)"><rect x="840" y="540" width="240" height="150" fill="#fbf7ec" stroke="#b9ad92" stroke-width="3"/>'
              '<path d="M840,540 L960,620 L1080,540" stroke="#b9ad92" stroke-width="3" fill="none"/>'
              f'<circle cx="960" cy="620" r="18" fill="{RED}"/></g>', delay(.3))
    return oval_office(desk=True, extra=extra)


def a_exit_door():
    d = grad("ex", "#f5ead0", "#d8c49a")
    b = [f'<rect width="{W}" height="{H}" fill="#1a140e"/>',
         '<rect x="660" y="120" width="600" height="900" fill="url(#ex)"/>',
         '<rect x="640" y="100" width="640" height="30" fill="#e6dcc4"/><rect x="620" y="100" width="40" height="920" fill="#e6dcc4"/><rect x="1260" y="100" width="40" height="920" fill="#e6dcc4"/>',
         g("dooropen", '<path d="M660,120 L460,60 L460,1080 L660,1020Z" fill="#5a3418"/>'),
         g("pulse", '<path d="M660,1020 L1260,1020 L1800,1080 L120,1080Z" fill="#ffe8b0" opacity=".25"/>')]
    walker = person(960, 1020, .9, suit="#0e0e12", skin="#0e0e12", hair="#0e0e12", tie="#0e0e12", motion="march", shirt="#0e0e12")
    b.append(g("walkaway", f'<g transform="translate(960,1020) scale(1.3)"><g transform="translate(-960,-1020)">{walker}</g></g>'))
    return svg("".join(b), d)


def a_library():
    d, s = sky("#8fc0ea", "#f2e7cf")
    b = [s, clouds(4, 141, 30, 250), '<rect x="0" y="820" width="1920" height="260" fill="#6aa84f"/>',
         f'<rect x="420" y="420" width="1080" height="400" fill="{CREAM}"/><rect x="400" y="400" width="1120" height="30" fill="#e2d4b5"/>',
         '<rect x="420" y="430" width="1080" height="80" fill="#b9d7ee" opacity=".7"/>']
    for x in range(470, 1460, 100):
        b.append(f'<rect x="{x}" y="520" width="40" height="300" fill="#fbf6ea"/>')
    b.append(flag(1560, 300, 160, 100, wave=6))
    return svg("".join(b), d)


def a_final():
    d, s = sky("#0b1a33", "#3a2a4d")
    d2, l = lawn(860, "#1d3b2a", "#0b1a12")
    b = [s, stars(200, 99, 600), white_house(960, 860, 1.25, lit=True, fill="#e7dcc4"), l,
         g("walkaway", person(960, 1060, .55, skin="#0e0e12", suit="#0e0e12", hair="#0e0e12", tie="#0e0e12", motion="march"))]
    return svg("".join(b), d + d2)


ART = {name[2:]: fn for name, fn in list(globals().items()) if name.startswith("a_") and callable(fn)}
