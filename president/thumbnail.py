#!/usr/bin/env python3
"""YouTube thumbnail (1280x720 PNG) built from the video's illustrations.

Usage: python3 thumbnail.py OUT.png
"""
import os
import subprocess
import sys

import art

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")


def build_html():
    bg = art.a_white_house_night()
    # Big waving president and the nuclear briefcase, drawn in the art style.
    pres = art.person(0, 0, 1.0, skin=art.SKIN[0], arm_up=True, wave_arm=False, motion="")
    case = ('<g transform="translate(-152,-178) scale(.55)">'
            '<rect x="0" y="40" width="300" height="190" rx="22" fill="#151515"/>'
            '<rect x="0" y="40" width="300" height="40" rx="22" fill="#242424"/>'
            '<path d="M100,40 L100,0 L200,0 L200,40" stroke="#2c2c2c" stroke-width="22" fill="none"/>'
            f'<rect x="125" y="70" width="50" height="22" rx="5" fill="{art.GOLD}"/></g>')
    figure = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-260 -520 520 560" width="620" height="668">'
              f'<g>{pres}</g>'
              f'{case}</svg>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Anton;src:url('file://{FONTS}/Anton-Regular.ttf')}}
@font-face{{font-family:Montserrat;src:url('file://{FONTS}/Montserrat[wght].ttf');font-weight:100 900}}
*{{animation:none!important}}
html,body{{margin:0;width:1280px;height:720px;overflow:hidden;background:#0b1a33}}
#bg{{position:absolute;inset:0;transform:scale(1.15);transform-origin:70% 60%}}
#bg svg{{width:1280px;height:720px;filter:saturate(1.25) brightness(.8)}}
#glow{{position:absolute;right:-80px;top:40px;width:760px;height:760px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,214,110,.55),rgba(255,214,110,0) 65%)}}
#fig{{position:absolute;right:20px;bottom:-34px}}
#fig svg{{filter:drop-shadow(0 18px 30px rgba(0,0,0,.6))}}
#txt{{position:absolute;left:46px;top:58px;width:720px}}
.l1{{font:400 92px/0.95 Anton;color:#fff;text-transform:uppercase;letter-spacing:1px;
  -webkit-text-stroke:5px #000;paint-order:stroke fill;text-shadow:0 8px 0 rgba(0,0,0,.45)}}
.l2{{font:400 178px/0.92 Anton;color:#ffd23f;text-transform:uppercase;-webkit-text-stroke:7px #000;paint-order:stroke fill;
  text-shadow:0 10px 0 rgba(0,0,0,.45)}}
.tag{{display:inline-block;margin-top:18px;background:#d7263d;color:#fff;font:900 46px Montserrat;padding:8px 22px 10px;white-space:nowrap;
  transform:rotate(-3deg);box-shadow:0 8px 0 rgba(0,0,0,.4);border:4px solid #000}}
#arrow{{position:absolute;left:640px;top:420px}}
#clock{{position:absolute;left:46px;bottom:34px;font:800 34px Montserrat;color:#fff;background:rgba(0,0,0,.6);
  padding:8px 18px;border-radius:10px;border:3px solid #ffd23f}}
</style></head><body>
<div id="bg">{bg}</div><div id="glow"></div><div id="fig">{figure}</div>
<div id="txt"><div class="l1">Your first day as</div><div class="l2">President</div><div class="tag">NOBODY TELLS YOU THIS</div></div>
<svg id="arrow" width="220" height="140" viewBox="0 0 220 140"><path d="M10,30 Q120,10 170,90" stroke="#000" stroke-width="30" fill="none" stroke-linecap="round"/>
<path d="M10,30 Q120,10 170,90" stroke="#ffd23f" stroke-width="18" fill="none" stroke-linecap="round"/>
<path d="M130,95 L205,125 L190,45Z" fill="#ffd23f" stroke="#000" stroke-width="6" stroke-linejoin="round"/></svg>
<div id="clock">11:59 → 12:00</div>
</body></html>"""


def main():
    out = os.path.abspath(sys.argv[1])
    html_path = os.path.splitext(out)[0] + ".html"
    with open(html_path, "w") as f:
        f.write(build_html())
    subprocess.run(["/opt/pw-browsers/chromium", "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--window-size=1280,720", "--virtual-time-budget=4000", f"--screenshot={out}", f"file://{html_path}"],
                   check=True, capture_output=True, timeout=120)
    os.remove(html_path)
    print("wrote", out)


if __name__ == "__main__":
    main()
