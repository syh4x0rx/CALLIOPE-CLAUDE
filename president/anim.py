"""HTML pages for each video segment: animated art + kinetic text.

capture.mjs loads a page, pauses every animation and seeks it frame by frame.
Animations inside #art follow the "art clock" (continuous across consecutive
scenes that share an illustration); everything else follows the scene clock.
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

FILL_BOX = """
.drift,.fall,.steam,.tw,.ripple,.flagwave,.wavearm,.blink,.headtilt,.bob,.jump,.march,.lookaround,.pitch,
.spin,.breathe,.punch,.minutestrike,.secondhand,.popc,.nudge,.rise,.sweep,.glint,.float,.dust,.grow-y,.coinflip,
.grow-x,.quill,.searchlight,.bounce,.ballot,.pulse,.fountain,.sway,.birds,.drivein,.dropin,.hurry,.sparkle,
.pinscatter,.roll,.slidein-b,.printout,.slidein-l,.slidein-r,.stadium,.stamp,.scan,.radar,.walk,.ship,.nowline,
.ring,.gavel,.wheelspin,.parallax,.roadlines,.cruise,.shake,.slam,.swing,.follow,.signswing,.tumble,.signing,
.radarsweep,.peck,.fan,.pitchball,.wobble,.hop,.flyby,.hover,.windowcloud,.turbulence,.rotor,.tailrotor,
.liftoff,.treesway,.debris,.sandtop,.sandbot,.dooropen,.walkaway
{transform-box:fill-box;transform-origin:50% 50%}
"""

KEYFRAMES = """
.drift{animation:drift 24s ease-in-out infinite alternate}
@keyframes drift{from{transform:translateX(-160px)}to{transform:translateX(160px)}}
.fall{animation:fall 4s linear infinite}
@keyframes fall{from{transform:translate(0,-120px) rotate(0)}to{transform:translate(90px,1240px) rotate(720deg)}}
.slowfall{animation-name:slowfall}
@keyframes slowfall{from{transform:translate(0,-40px)}to{transform:translate(70px,1140px)}}
.steam{animation:steam 2.4s ease-out infinite;opacity:0}
@keyframes steam{0%{transform:translateY(0);opacity:0}30%{opacity:.7}100%{transform:translateY(-100px);opacity:0}}
.bigsteam{animation-name:bigsteam;animation-duration:3.2s}
@keyframes bigsteam{0%{transform:translate(0,0) scale(.6);opacity:0}25%{opacity:.6}100%{transform:translate(40px,-260px) scale(2.4);opacity:0}}
.tw{animation:tw 2s ease-in-out infinite alternate}
@keyframes tw{from{opacity:.15}to{opacity:1}}
.ripple{animation:ripple 1.5s linear infinite}
@keyframes ripple{from{transform:translateX(-100%)}to{transform:translateX(400%)}}
.flagwave{transform-origin:0% 50%;animation:flagwave 1.5s ease-in-out infinite alternate}
@keyframes flagwave{from{transform:skewY(-3deg) scaleX(.95)}to{transform:skewY(3deg) scaleX(1)}}
.wavearm{transform-origin:0% 100%;animation:wavearm .5s ease-in-out infinite alternate}
@keyframes wavearm{from{transform:rotate(-16deg)}to{transform:rotate(14deg)}}
.blink{animation:blink 4.5s linear infinite}
@keyframes blink{0%,93%,100%{transform:scaleY(1)}96%{transform:scaleY(.1)}}
.headtilt{transform-origin:50% 100%;animation:headtilt 3s ease-in-out infinite alternate}
@keyframes headtilt{from{transform:rotate(-3deg)}to{transform:rotate(3deg)}}
.bob{animation:bob 2.2s ease-in-out infinite alternate}
@keyframes bob{from{transform:translateY(0)}to{transform:translateY(-9px)}}
.jump{animation:jump .6s ease-out infinite alternate}
@keyframes jump{from{transform:translateY(0)}to{transform:translateY(-26px)}}
.march{animation:march .42s ease-in-out infinite alternate}
@keyframes march{from{transform:translateY(0) rotate(-1.5deg)}to{transform:translateY(-12px) rotate(1.5deg)}}
.lookaround{animation:lookaround 3.4s ease-in-out infinite alternate}
@keyframes lookaround{from{transform:translateX(-10px)}to{transform:translateX(10px)}}
.pitch{transform-origin:50% 100%;animation:pitch 1.2s ease-in-out infinite alternate}
@keyframes pitch{from{transform:rotate(2deg)}to{transform:rotate(-7deg)}}
.winflicker{animation:winflicker 5s linear infinite}
@keyframes winflicker{0%,40%{opacity:1}44%{opacity:.35}52%{opacity:1}78%{opacity:.7}100%{opacity:1}}
.spin{animation:spin 14s linear infinite}
.slowspin{animation-duration:70s}.wheel{animation-duration:22s}
@keyframes spin{to{transform:rotate(360deg)}}
.breathe{animation:breathe 2.2s ease-in-out infinite alternate}
@keyframes breathe{from{transform:scale(1)}to{transform:scale(1.025)}}
.punch{animation:punch .7s cubic-bezier(.2,.8,.3,1.3) both;animation-delay:.25s}
@keyframes punch{from{transform:scale(1.25)}to{transform:scale(1)}}
.minutestrike{animation:minutestrike 1.3s ease-out both}
@keyframes minutestrike{0%,30%{transform:rotate(-6deg)}45%{transform:rotate(3deg)}60%{transform:rotate(-1deg)}75%,100%{transform:rotate(0)}}
.secondhand{animation:secondhand 60s steps(60) infinite}
@keyframes secondhand{to{transform:rotate(360deg)}}
.popc{animation:popc .6s cubic-bezier(.34,1.56,.64,1) both}
@keyframes popc{from{transform:scale(0)}to{transform:scale(1)}}
.nudge{animation:nudge .7s ease-in-out infinite alternate}
@keyframes nudge{from{transform:translateX(-10px)}to{transform:translateX(14px)}}
.camflash{animation:camflash 2.4s linear infinite;opacity:0}
@keyframes camflash{0%{opacity:0}2%{opacity:.45}7%{opacity:0}100%{opacity:0}}
.rise{animation:rise .8s cubic-bezier(.2,.9,.3,1.1) both}
@keyframes rise{from{transform:translateY(560px)}to{transform:translateY(0)}}
.sweep{animation:sweep 5s linear infinite}
@keyframes sweep{from{transform:translateX(-700px)}to{transform:translateX(2700px)}}
.glint{animation:glint 3.2s ease-in-out infinite}
@keyframes glint{0%{transform:translateX(-300px)}60%,100%{transform:translateX(1500px)}}
.float{animation:float 2.6s ease-in-out infinite alternate}
@keyframes float{from{transform:translateY(0)}to{transform:translateY(-18px)}}
.dust{animation:dust 6s ease-in-out infinite alternate}
@keyframes dust{from{transform:translateY(0);opacity:.5}to{transform:translateY(-40px);opacity:1}}
.grow-y{transform-origin:50% 100%;animation:growy .6s cubic-bezier(.34,1.4,.64,1) both}
@keyframes growy{from{transform:scaleY(0)}to{transform:scaleY(1)}}
.coinflip{animation:coinflip 1.3s ease-in-out infinite alternate}
@keyframes coinflip{from{transform:scaleX(1)}to{transform:scaleX(.08)}}
.grow-x{transform-origin:0% 50%;animation:growx .5s ease-out both}
@keyframes growx{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.loopgrow{animation:growx 1.4s ease-in-out infinite alternate}
.candle{animation:candle .9s ease-in-out infinite alternate}
@keyframes candle{0%{opacity:1}35%{opacity:.8}60%{opacity:.95}100%{opacity:.75}}
.quill{animation:quill 1.1s linear infinite}
@keyframes quill{0%{transform:translate(0,0)}25%{transform:translate(-24px,8px)}50%{transform:translate(-44px,0)}75%{transform:translate(-24px,-8px)}100%{transform:translate(0,0)}}
.searchlight{transform-origin:50% 100%;animation:searchlight 4s ease-in-out infinite alternate}
@keyframes searchlight{from{transform:rotate(-14deg)}to{transform:rotate(14deg)}}
.bounce{animation:bounce .7s ease-in-out infinite alternate}
@keyframes bounce{from{transform:translateY(0) rotate(0)}to{transform:translateY(-22px) rotate(-2deg)}}
.ghost{animation:ghost 1.6s ease-in-out infinite alternate}
@keyframes ghost{from{opacity:.25}to{opacity:1}}
.ballot{animation:ballot 4.5s cubic-bezier(.5,0,.8,.6) infinite}
@keyframes ballot{0%{transform:translateY(-260px);opacity:0}10%{opacity:1}70%{transform:translateY(560px);opacity:1}78%,100%{transform:translateY(620px);opacity:0}}
.pulse{animation:pulse 1.4s ease-in-out infinite alternate}
@keyframes pulse{from{transform:scale(1);opacity:.85}to{transform:scale(1.07);opacity:1}}
.fountain{transform-origin:50% 100%;animation:fountain .5s ease-in-out infinite alternate}
@keyframes fountain{from{transform:scaleY(.8)}to{transform:scaleY(1.2)}}
.sway{transform-origin:50% 100%;animation:sway 3.2s ease-in-out infinite alternate}
@keyframes sway{from{transform:rotate(-2deg)}to{transform:rotate(2deg)}}
.birds{animation:birds 22s linear infinite}
@keyframes birds{from{transform:translate(-300px,40px)}to{transform:translate(2100px,-120px)}}
.drivein{animation:drivein 1.6s cubic-bezier(.2,.8,.3,1) both}
@keyframes drivein{from{transform:translateX(-1400px)}to{transform:translateX(0)}}
.dropin{animation:dropin .8s cubic-bezier(.3,0,.6,1) both}
@keyframes dropin{0%{transform:translateY(-1000px)}70%{transform:translateY(16px)}85%{transform:translateY(-8px)}100%{transform:translateY(0)}}
.hurry{animation:hurry 2.6s ease-in-out infinite alternate}
@keyframes hurry{from{transform:translateX(0)}to{transform:translateX(var(--dx))}}
.sparkle{animation:sparkle .9s ease-in-out infinite alternate}
@keyframes sparkle{from{transform:scale(.3) rotate(0);opacity:.3}to{transform:scale(1.15) rotate(36deg);opacity:1}}
.pinscatter{animation:pinscatter 2.5s linear infinite}
@keyframes pinscatter{0%,76%{transform:translateY(0) rotate(0)}80%{transform:translateY(-14px) rotate(5deg)}88%{transform:translateY(0) rotate(-3deg)}100%{transform:translateY(0) rotate(0)}}
.roll{animation:roll 2.5s cubic-bezier(.4,0,1,1) infinite}
@keyframes roll{0%{transform:translate(0,0) scale(1);opacity:1}78%{transform:translate(0,-480px) scale(.24);opacity:1}80%,100%{transform:translate(0,-480px) scale(.24);opacity:0}}
.slidein-b{animation:slideinb .8s cubic-bezier(.2,.9,.3,1.05) both}
@keyframes slideinb{from{transform:translateY(520px)}to{transform:translateY(0)}}
.fadein{animation:fadein .6s ease-out both}
@keyframes fadein{from{opacity:0}to{opacity:1}}
.blinktext{animation:blinktext 1.4s linear both}
@keyframes blinktext{0%{opacity:0}10%{opacity:1}22%{opacity:0}34%{opacity:1}46%{opacity:0}58%,100%{opacity:1}}
.printout{transform-origin:50% 0%;animation:printout 2.2s linear both}
@keyframes printout{from{transform:translateY(-900px)}to{transform:translateY(0)}}
.slidein-l{animation:slideinl .8s cubic-bezier(.2,.9,.3,1.05) both}
@keyframes slideinl{from{transform:translateX(-1500px)}to{transform:translateX(0)}}
.slidein-r{animation:slideinr .8s cubic-bezier(.2,.9,.3,1.05) both}
@keyframes slideinr{from{transform:translateX(1500px)}to{transform:translateX(0)}}
.draw{stroke-dasharray:3000;animation:draw 2.5s ease-out both}
@keyframes draw{from{stroke-dashoffset:3000}to{stroke-dashoffset:0}}
.loopdraw{animation:draw 3s ease-in-out infinite}
.stadium{animation:stadium 3.2s ease-in-out infinite}
@keyframes stadium{0%,30%,100%{transform:translateY(0)}15%{transform:translateY(-42px)}}
.stamp{animation:stamp .28s cubic-bezier(.5,0,1,1) both}
@keyframes stamp{from{transform:scale(3);opacity:0}to{transform:scale(1);opacity:1}}
.scan{animation:scan 4s linear infinite}
@keyframes scan{from{transform:translateY(-60px)}to{transform:translateY(1100px)}}
.radar{animation:radar 2s ease-out infinite}
@keyframes radar{from{transform:scale(.3);opacity:1}to{transform:scale(2.6);opacity:0}}
.walk{animation:walk 9s linear both}
@keyframes walk{from{transform:translateX(0)}to{transform:translateX(var(--dx))}}
.sunbeam{animation:sunbeam 4s ease-in-out infinite alternate}
@keyframes sunbeam{from{opacity:.5}to{opacity:1}}
.ship{animation:ship 5s ease-in-out infinite alternate}
@keyframes ship{from{transform:translateX(-24px)}to{transform:translateX(24px)}}
.nowline{animation:nowline 20s linear both}
@keyframes nowline{from{transform:translateY(0)}to{transform:translateY(760px)}}
.ring{animation:ring 1.6s linear infinite}
@keyframes ring{0%,25%{transform:rotate(0)}3%,9%,15%,21%{transform:rotate(-7deg)}6%,12%,18%,24%{transform:rotate(7deg)}26%,100%{transform:rotate(0)}}
.ringwaves{animation:ringwaves 1.6s linear infinite}
@keyframes ringwaves{0%,25%{opacity:1}30%,100%{opacity:0}}
.gavel{transform-origin:50% 100%;animation:gavel 1.6s ease-in infinite}
@keyframes gavel{0%,40%{transform:rotate(-28deg)}50%{transform:rotate(8deg)}58%{transform:rotate(0)}100%{transform:rotate(-28deg)}}
.wheelspin{animation:spin .45s linear infinite}
.flashred{animation:flashA .5s steps(1) infinite}
.flashblue{animation:flashA .5s steps(1) infinite;animation-delay:-.25s}
@keyframes flashA{0%{opacity:1}50%{opacity:.1}}
.parallax{animation:parallax 18s linear infinite}
@keyframes parallax{from{transform:translateX(0)}to{transform:translateX(-1800px)}}
.roadlines{animation:roadlines 2.4s linear infinite}
@keyframes roadlines{from{transform:translateX(0)}to{transform:translateX(-960px)}}
.cruise{animation:cruise 3s ease-in-out infinite alternate}
@keyframes cruise{from{transform:translateX(-50px)}to{transform:translateX(50px)}}
.shake{animation:shake .22s linear infinite}
@keyframes shake{0%{transform:translate(0,0)}25%{transform:translate(5px,-2px)}50%{transform:translate(-4px,2px)}75%{transform:translate(2px,3px)}100%{transform:translate(0,0)}}
.slam{animation:slam .32s cubic-bezier(.5,0,1,1) both}
@keyframes slam{from{transform:scale(2.6);opacity:0}to{transform:scale(1);opacity:1}}
.swing{transform-origin:50% 0%;animation:swing .9s ease-in-out infinite alternate}
@keyframes swing{from{transform:rotate(-7deg)}to{transform:rotate(7deg)}}
.follow{animation:follow 2s ease-in-out infinite alternate}
@keyframes follow{from{transform:translateX(0)}to{transform:translateX(-46px)}}
.signswing{animation:signswing 1.6s ease-in-out infinite alternate}
@keyframes signswing{from{transform:rotate(-5deg)}to{transform:rotate(5deg)}}
.tumble{animation:tumble 6s linear infinite}
@keyframes tumble{from{transform:translate(0,0) rotate(0)}to{transform:translate(1800px,-40px) rotate(900deg)}}
.signing{animation:signing 2.5s ease-in-out both}
@keyframes signing{0%{transform:translate(-337px,53px)}20%{transform:translate(-260px,20px)}40%{transform:translate(-180px,60px)}60%{transform:translate(-90px,30px)}80%{transform:translate(-20px,10px)}100%{transform:translate(23px,43px)}}
.screenflicker{animation:winflicker 3s linear infinite}
.radarsweep{animation:spin 2.4s linear infinite}
.blip{animation:flashA .6s steps(1) infinite}
.peck{transform-origin:50% 100%;animation:peck 1.3s ease-in-out infinite}
@keyframes peck{0%,60%,100%{transform:rotate(0)}70%{transform:rotate(14deg)}80%{transform:rotate(-4deg)}}
.fan{transform-origin:50% 100%;animation:fan 1.1s ease-in-out infinite alternate}
@keyframes fan{from{transform:scale(.93)}to{transform:scale(1.06)}}
.pitchball{animation:pitchball 2.4s ease-in infinite}
@keyframes pitchball{0%,45%{transform:translate(0,0) scale(1);opacity:1}90%{transform:translate(420px,180px) scale(.35);opacity:1}91%,100%{opacity:0}}
.wobble{transform-origin:50% 100%;animation:wobble 1.2s ease-in-out infinite alternate}
@keyframes wobble{from{transform:rotate(-9deg)}to{transform:rotate(9deg)}}
.hop{animation:hop .7s ease-out infinite alternate}
@keyframes hop{from{transform:translateY(0)}to{transform:translateY(-46px)}}
.flyby{animation:flyby 16s linear both}
@keyframes flyby{from{transform:translate(-320px,60px)}to{transform:translate(320px,-60px)}}
.hover{animation:hover 2s ease-in-out infinite alternate}
@keyframes hover{from{transform:translateY(0)}to{transform:translateY(-16px)}}
.contrail{animation:ghost .35s ease-in-out infinite alternate}
.windowcloud{animation:windowcloud 1.4s linear infinite}
@keyframes windowcloud{from{transform:translateX(140px)}to{transform:translateX(-140px)}}
.turbulence{animation:turbulence .35s ease-in-out infinite alternate}
@keyframes turbulence{from{transform:translateY(0)}to{transform:translateY(-4px)}}
.rotor{animation:rotor .16s linear infinite}
@keyframes rotor{0%,100%{transform:scaleX(1)}50%{transform:scaleX(.15)}}
.tailrotor{animation:tailrotor .1s linear infinite}
@keyframes tailrotor{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.15)}}
.liftoff{animation:liftoff 5s ease-in-out infinite alternate}
@keyframes liftoff{from{transform:translateY(70px)}to{transform:translateY(-70px)}}
.treesway{transform-origin:50% 100%;animation:sway 4s ease-in-out infinite alternate}
.flash{animation:camflash 2s linear infinite;opacity:0}
.debris{animation:debris 4s linear infinite}
@keyframes debris{from{transform:translate(0,0) rotate(0)}to{transform:translate(1500px,-320px) rotate(900deg)}}
.sandtop{transform-origin:50% 100%;animation:sandtop 14s linear both}
@keyframes sandtop{from{transform:scaleY(1)}to{transform:scaleY(.12)}}
.sandbot{transform-origin:50% 100%;animation:sandbot 14s linear both}
@keyframes sandbot{from{transform:scaleY(.3)}to{transform:scaleY(1)}}
.stream{animation:stream .4s linear infinite}
@keyframes stream{from{stroke-dashoffset:0}to{stroke-dashoffset:-48}}
.dooropen{transform-origin:100% 50%;animation:dooropen 1.6s ease-out both}
@keyframes dooropen{from{transform:scaleX(1)}to{transform:scaleX(.45)}}
.walkaway{transform-origin:50% 100%;animation:walkaway 9s linear both}
@keyframes walkaway{from{transform:translateY(0) scale(1)}to{transform:translateY(-170px) scale(.55)}}
"""

PAGE_CSS = """
@font-face{font-family:Anton;src:url('file://{FONTS}/Anton-Regular.ttf')}
@font-face{font-family:Montserrat;src:url('file://{FONTS}/Montserrat[wght].ttf');font-weight:100 900}
html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#000}
#stage{position:absolute;inset:0;overflow:hidden}
#punch,#cam{position:absolute;inset:0;transform-origin:50% 50%}
#art svg{display:block}
.card #art{filter:blur(9px) brightness(.42)}
#shade{position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(to bottom,rgba(4,8,18,.55) 0,rgba(4,8,18,0) 220px,rgba(4,8,18,0) 760px,rgba(4,8,18,.82) 1080px)}
#label{position:absolute;left:84px;top:54px;font:800 26px Montserrat;letter-spacing:4px;color:#e0b95e;text-transform:uppercase;
  text-shadow:0 2px 6px rgba(0,0,0,.6);animation:fadein .5s both}
#head{position:absolute;left:78px;top:96px;transform-origin:0% 50%;animation:headpop .55s cubic-bezier(.34,1.56,.64,1) both;animation-delay:.08s}
#head span{display:inline-block;font:400 78px/1.02 Anton;letter-spacing:1px;text-transform:uppercase;color:#fff;
  background:rgba(8,14,30,.86);padding:12px 26px 14px;border-left:10px solid #e0b95e;white-space:pre;
  box-shadow:0 10px 30px rgba(0,0,0,.35)}
#head span.gold{color:#ffd45a}
@keyframes headpop{from{transform:scale(.6) translateX(-60px);opacity:0}to{transform:scale(1) translateX(0);opacity:1}}
#cap{position:absolute;left:160px;right:160px;bottom:62px;text-align:center;font:800 46px/1.28 Montserrat;color:#fff;
  -webkit-text-stroke:2px rgba(0,0,0,.55);paint-order:stroke fill;text-shadow:0 4px 14px rgba(0,0,0,.75)}
#cap .w{display:inline-block;opacity:.35;transform:translateY(6px);animation:wordon .18s ease-out both}
#cap .w.key{color:#ffd45a}
@keyframes wordon{to{opacity:1;transform:translateY(0)}}
#bar{position:absolute;left:0;bottom:0;height:8px;background:#e0b95e}
#cardtitle{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
#cardtitle .small{font:800 40px Montserrat;letter-spacing:10px;color:#e0b95e;animation:fadein .5s both;animation-delay:.2s}
#cardtitle .big{font:400 150px/1.05 Anton;text-transform:uppercase;color:#fff;margin-top:14px;
  text-shadow:0 8px 30px rgba(0,0,0,.6);animation:slamt .5s cubic-bezier(.2,.9,.3,1.2) both;animation-delay:.35s}
#cardtitle .rule{width:260px;height:8px;background:#e0b95e;margin-top:26px;transform-origin:50% 50%;animation:growx2 .6s ease-out both;animation-delay:.6s}
@keyframes slamt{from{transform:scale(1.8);opacity:0;letter-spacing:30px}to{transform:scale(1);opacity:1;letter-spacing:2px}}
@keyframes growx2{from{transform:scaleX(0)}to{transform:scaleX(1)}}
#fade{position:absolute;inset:0;background:#000;opacity:0}
"""

KEYWORDS = {"never", "free", "noon", "president", "nuclear", "top-secret", "secret", "trillion", "billions",
            "thirty-five", "fourteen", "ten", "two-thirds", "half", "life", "football", "veto", "worse", "bad",
            "regret", "easy", "trade", "turkey", "air", "force", "one", "camp", "david", "400,000", "five",
            "hundred", "thirty-two", "situation", "room", "eight", "four", "twenty-second"}


def caption_html(text, voice_at, dur):
    words = text.split()
    total = sum(len(w) + 1 for w in words)
    acc, spans = 0, []
    for w in words:
        t = voice_at + dur * acc / total
        acc += len(w) + 1
        bare = w.strip(".,:;!?\"'").lower()
        cls = "w key" if bare in KEYWORDS or any(ch.isdigit() for ch in bare) else "w"
        spans.append(f'<span class="{cls}" style="animation-delay:{t:.2f}s">{html.escape(w)}</span>')
    return " ".join(spans)


def page(seg, art_svg, total, cam):
    """cam: dict with run_dur, zoom_in (bool), pan (+1/-1), first (bool)."""
    css = PAGE_CSS.replace("{FONTS}", FONTS)
    d = cam["run_dur"]
    z0, z1 = (1.0, 1.1) if cam["zoom_in"] else (1.1, 1.0)
    px = 34 * cam["pan"]
    cam_kf = (f"@keyframes cam{{from{{transform:scale({z0}) translateX({-px}px)}}"
              f"to{{transform:scale({z1}) translateX({px}px)}}}}"
              f"#cam{{animation:cam {d:.2f}s linear both}}")
    punch = ("#punch{animation:punchin .45s cubic-bezier(.2,.8,.3,1) both}"
             "@keyframes punchin{from{transform:scale(1.07)}to{transform:scale(1)}}") if cam["first"] else ""
    seg_dur = seg["end"] - seg["start"]
    p0, p1 = seg["start"] / total * 100, seg["end"] / total * 100
    bar = (f"#bar{{animation:barw {seg_dur:.2f}s linear both}}"
           f"@keyframes barw{{from{{width:{p0:.3f}%}}to{{width:{p1:.3f}%}}}}")
    fades = ""
    if seg["kind"] == "outro":
        fades = f"#fade{{animation:fadeout 2s linear both;animation-delay:{seg_dur - 2.2:.2f}s}}@keyframes fadeout{{to{{opacity:1}}}}"
    elif seg["start"] < 0.01:
        fades = "#fade{opacity:1;animation:fadeinb .8s linear both}@keyframes fadeinb{to{opacity:0}}"

    body = [f'<div id="stage" class="{seg["kind"]}"><div id="punch"><div id="cam"><div id="art">{art_svg}</div></div></div>']
    if seg["kind"] == "scene":
        head = seg["head"].upper()
        gold = "gold" if any(c.isdigit() for c in head) or "$" in head else ""
        voice_local = seg["voice_at"] - seg["start"]
        body.append('<div id="shade"></div>')
        body.append(f'<div id="label">{html.escape(seg["chapter"])}</div>')
        body.append(f'<div id="head"><span class="{gold}">{html.escape(head)}</span></div>')
        body.append(f'<div id="cap">{caption_html(seg["vo"], voice_local, seg["vo_dur"])}</div>')
    elif seg["kind"] == "card":
        title = seg["title"]
        small, big = ([s.strip() for s in title.split(":", 1)] if ":" in title else ("", title))
        body.append(f'<div id="cardtitle"><div class="small">{html.escape(small.upper())}</div>'
                    f'<div class="big">{html.escape(big)}</div><div class="rule"></div></div>')
    else:
        body.append('<div id="cardtitle"><div class="small">WHAT IT\'S LIKE TO BE PRESIDENT</div>'
                    '<div class="big">Would you<br>take the job?</div><div class="rule"></div></div>')
    body.append('<div id="bar"></div><div id="fade"></div></div>')
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{css}{FILL_BOX}{KEYFRAMES}{cam_kf}{punch}{bar}{fades}"
            f"</style></head><body>{''.join(body)}</body></html>")
