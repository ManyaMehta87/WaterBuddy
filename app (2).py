"""WaterBuddy - Wick the turtle hydration companion (FA-1). All art is original inline SVG/CSS."""
import json
import random
from datetime import date, timedelta

import streamlit as st

MASCOT_NAME, BOTTLE_ML, QUICK_ML = "Wick", 2000, 250
DARK, WATER, G = "#37474F", "#4FC3F7", "#1B5E20"
AGE_GROUPS = {"Children (4–8 yrs)": 1200, "Teens (9–13 yrs)": 1700,
              "Adults (14–64 yrs)": 2400, "Seniors (65+ yrs)": 1800}
CHEERS = ["Great job today! 💧", "Nice sip! Wick is smiling! 🐢", "Your body says thank you! 💙",
          "Hydration hero in action! 🦸", "Splash! One step closer! 🎯"]
TIPS = ["Keep your water bottle on your desk so it's always in sight.",
        "Drink a glass of water first thing in the morning.",
        "Sip a little after every break.", "Add lemon or mint if plain water feels boring.",
        "Drink a glass before each meal."]
# mood: (walk step seconds, small steps?, ground scroll seconds, sky, weather emoji)
MOODS = {"gloomy": (2.4, 1, 14, "#B0BEC5,#CFD8DC", "🌧️"), "okay": (1.2, 0, 7, "#B3E5FC,#ECEFF1", "☁️"),
         "happy": (.8, 0, 4.5, "#81D4FA,#E1F5FE", "🌤️"), "excited": (.5, 0, 2.6, "#4FC3F7,#E1F5FE", "☀️"),
         "party": (.34, 0, 1.4, "#29B6F6,#FFF9C4", "🎉")}

st.set_page_config(page_title="WaterBuddy", page_icon="🐢", layout="centered")


def html(m):
    return "".join(x.strip() for x in m.splitlines())


# ---------------- state ----------------
def init_state():
    s = st.session_state
    for k, v in dict(screen="welcome", age=None, goal=2400, total=0, prev=0, log=[], fills=0,
                     just_logged=False, celebrate=False, today=date.today(), real=date.today(),
                     history={}, restored="").items():
        s.setdefault(k, v)
    if s.real != date.today():
        s.real = date.today()
        new_day()


def reset_day():
    s = st.session_state
    s.total = s.prev = 0
    s.log = []
    s.just_logged = s.celebrate = False


def new_day():
    s = st.session_state
    s.history[s.today.isoformat()] = {"ml": s.total, "goal": s.goal}
    s.today += timedelta(days=1)
    reset_day()


def add_water(ml):
    s = st.session_state
    before = s.prev = s.total
    s.total += ml
    s.log.append(ml)
    s.fills += 1
    s.just_logged = True
    hit = [m for m in (50, 75, 100) if before * 100 < s.goal * m <= s.total * 100]
    if hit:
        st.toast({50: "Halfway there! Keep sipping! 💧", 75: "You're doing great! 🌟",
                  100: "Goal achieved! Great job! 🎉"}[max(hit)], icon="🐢")
        s.celebrate = max(hit) == 100
    else:
        st.toast(random.choice(CHEERS))


def undo_last():
    s = st.session_state
    if s.log:
        s.prev = s.total
        s.total = max(0, s.total - s.log.pop())
        s.just_logged = False


def go(screen):
    st.session_state.screen = screen


def streaks():
    s = st.session_state
    met = {d for d, v in s.history.items() if v["goal"] and v["ml"] >= v["goal"]}
    if s.goal and s.total >= s.goal:
        met.add(s.today.isoformat())
    d = s.today if s.today.isoformat() in met else s.today - timedelta(days=1)
    cur = 0
    while d.isoformat() in met:
        cur, d = cur + 1, d - timedelta(days=1)
    best = run = 0
    prev = None
    for iso in sorted(met):
        dd = date.fromisoformat(iso)
        run = run + 1 if prev and (dd - prev).days == 1 else 1
        best, prev = max(best, run), dd
    return cur, best


def mood_for(p):
    return "party" if p >= 100 else "excited" if p >= 75 else "happy" if p >= 50 else "okay" if p >= 25 else "gloomy"


def message_for(p, n):
    if n == 0:
        return "I'm so dry I'm crumbling… water please? 🥺"
    return ("Goal achieved! Great job! 🎉" if p >= 100 else "You're doing great! Almost there!" if p >= 75
            else "Halfway there! Keep sipping!" if p >= 50 else "Ooh, that helps! A little more?" if p >= 25
            else "Thanks! I feel a bit better…")


# ---------------- graphics ----------------
def wick_svg(mood="happy", size=200, animate=True):
    d, small, *_ = MOODS[mood]
    sf = "s" if small else ""

    def leg(x, n, dark=False):
        a = f"animation:{n}{sf} {d}s ease-in-out infinite;" if animate else ""
        c = "#689F38" if dark else "#8BC34A"
        return (f'<g style="transform-origin:{x}px 120px;{a}"><rect x="{x-11}" y="118" width="22" height="34" rx="11" '
                f'fill="{c}" stroke="{G}" stroke-width="3"/><ellipse cx="{x+4}" cy="152" rx="14" ry="7" fill="{c}" '
                f'stroke="{G}" stroke-width="3"/></g>')

    eye = (f'<circle cx="196" cy="86" r="7" fill="#fff" stroke="{G}" stroke-width="2"/><circle cx="198" cy="87" r="3.6" fill="{DARK}"/>'
           '<circle cx="199.6" cy="85.4" r="1.4" fill="#fff"/>')
    mouth = {"gloomy": "M196 107 Q203 99 210 107", "okay": "M196 102 Q203 106 210 102", "happy": "M195 100 Q203 110 211 100"}
    face = f'<path d="{mouth.get(mood, "")}" stroke="{G}" stroke-width="3" fill="none" stroke-linecap="round"/>'
    extra = ""
    if mood == "gloomy":
        eye += (f'<path d="M188.5 86 A7.5 7.5 0 0 1 203.5 86Z" fill="#AED581" stroke="{G}" stroke-width="2"/>'
                f'<path d="M189 80 L204 73" stroke="{G}" stroke-width="3" stroke-linecap="round"/>')
        extra = '<path class="wk-sweat" d="M176 58 Q171 68 176 72 Q181 68 176 58Z" fill="#4FC3F7"/>'
    elif mood in ("excited", "party"):
        eye = (f'<path d="M188 88 Q196 77 204 88" stroke="{G}" stroke-width="3.5" fill="none" stroke-linecap="round"/>' if mood == "party"
               else eye + '<circle cx="193.5" cy="88.5" r="1.1" fill="#fff"/>')
        face = f'<path d="M194 98 Q203 119 212 98Z" fill="#4E342E" stroke="{G}" stroke-width="2"/><path d="M198 108 Q203 113 208 108Z" fill="#F48FB1"/>'
        extra = ('<text x="148" y="46" font-size="20" fill="#FFD54F">✦</text><text x="205" y="44" font-size="24" fill="#FFB74D">★</text>'
                 '<text x="120" y="30" font-size="14" fill="#F48FB1">✦</text>'
                 f'<g class="wk-line" stroke="#90A4AE" stroke-width="3" stroke-linecap="round"><path d="M4 70H30M0 90H26M6 110H30"/></g>')
    cheek = "" if mood == "gloomy" else '<ellipse cx="189" cy="100" rx="5.5" ry="3.3" fill="#F48FB1" opacity=".6"/>'
    bob = "animation:wksag 3s ease-in-out infinite;" if mood == "gloomy" else f"animation:wkstep {d/2}s ease-in-out infinite;"
    head_t = "transform:translate(2px,10px) rotate(9deg);transform-origin:165px 110px;" if mood == "gloomy" else ""
    hexes = "".join(f'<polygon points="{p}" fill="#66BB6A" opacity=".55" stroke="{G}" stroke-width="2"/>' for p in (
        "117,84 108.5,98.7 91.5,98.7 83,84 91.5,69.3 108.5,69.3", "81,102 74.5,113 61.5,113 55,102 61.5,91 74.5,91",
        "145,102 138.5,113 125.5,113 119,102 125.5,91 138.5,91"))
    filt = "filter:saturate(.5) brightness(.93);" if mood == "gloomy" else ""
    return html(f"""<svg width="{size}" height="{int(size*.78)}" viewBox="0 0 225 170" style="{filt}overflow:visible" role="img" aria-label="{MASCOT_NAME} the turtle">
    <defs><linearGradient id="wksh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#66BB6A"/><stop offset="1" stop-color="#2E7D32"/></linearGradient></defs>
    <ellipse cx="110" cy="158" rx="78" ry="7" fill="{DARK}" opacity=".15"/>
    <g style="{bob if animate else ''}">
    {leg(80, "wkB", True)}{leg(120, "wkA", True)}
    <path d="M38 124 L16 134 L40 140Z" fill="#8BC34A" stroke="{G}" stroke-width="3" stroke-linejoin="round"/>
    <g style="{head_t}"><rect x="156" y="98" width="26" height="30" rx="11" fill="#9CCC65" stroke="{G}" stroke-width="3"/>
    <ellipse cx="188" cy="90" rx="27" ry="24" fill="#AED581" stroke="{G}" stroke-width="3"/>
    {eye}{cheek}{face}<circle cx="209" cy="93" r="1.3" fill="{G}"/></g>
    <path d="M35 130 C35 70 68 38 100 38 C132 38 165 70 165 130Z" fill="url(#wksh)" stroke="{G}" stroke-width="3.5"/>
    {hexes}<ellipse cx="72" cy="62" rx="14" ry="6" fill="#fff" opacity=".28" transform="rotate(-30 72 62)"/>
    <rect x="30" y="122" width="140" height="16" rx="8" fill="#FFE082" stroke="{G}" stroke-width="3"/>
    {leg(62, "wkA")}{leg(140, "wkB")}{extra}</g></svg>""")


def scene_html(mood, msg, jump):
    d, _, gd, sky, wx = MOODS[mood]
    s1, s2 = sky.split(",")
    row = "🌳 🌷 🌿 🌼 🌲 🌷 🌿 🌳 " * 2
    return html(f"""<div class="wb-scene" style="background:linear-gradient(180deg,{s1},{s2})">
    <div class="wb-wx">{wx}</div><div class="wb-say">{msg}</div>
    <div class="wb-hill" style="left:-12%;width:60%"></div><div class="wb-hill" style="right:-15%;width:70%;height:110px;background:#81C784"></div>
    <div class="wb-trees" style="animation-duration:{gd*2}s">{row}{row}</div>
    <div class="wb-ground"><div class="wb-path" style="animation-duration:{gd/4}s"></div></div>
    <div class="wb-wick" style="{'animation:wkjump .8s ease-out;' if jump else ''}">{wick_svg(mood, 210)}</div></div>""")


def bottle_svg(total, prev, goal, fills, drip):
    def off(ml):
        f = min(ml, BOTTLE_ML) / BOTTLE_ML
        return 290 * (1 - f) + (22 if f == 0 else 0)
    a, b, nm = off(prev), off(total), f"wbfill{fills}"
    ticks = "".join(f'<line x1="120" y1="{50+290*(1-m/BOTTLE_ML)}" x2="130" y2="{50+290*(1-m/BOTTLE_ML)}" stroke="{DARK}" stroke-width="2"/>'
                    f'<text x="134" y="{54+290*(1-m/BOTTLE_ML)}" font-size="11" fill="{DARK}" font-weight="600">{m/1000:g}L</text>'
                    for m in (500, 1000, 1500, 2000))
    gy = 50 + 290 * (1 - min(goal, BOTTLE_ML) / BOTTLE_ML)
    st.markdown(f"<style>@keyframes {nm}{{from{{transform:translateY({a}px)}}to{{transform:translateY({b}px)}}}}</style>", unsafe_allow_html=True)
    return html(f"""<svg viewBox="0 -40 180 400" class="wb-bottle" role="img" aria-label="2 litre bottle, {total} ml">
    <defs><clipPath id="wbc"><rect x="20" y="50" width="100" height="290" rx="30"/></clipPath>
    <linearGradient id="wbw" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#81D4FA"/><stop offset="1" stop-color="#29B6F6"/></linearGradient></defs>
    <rect x="44" y="6" width="52" height="16" rx="5" fill="{DARK}"/><rect x="48" y="20" width="44" height="36" rx="6" fill="#fff" stroke="{DARK}" stroke-width="3"/>
    <rect x="20" y="50" width="100" height="290" rx="30" fill="#fff" opacity=".85"/>
    <g clip-path="url(#wbc)"><g style="transform:translateY({b}px);animation:{nm} 1.4s ease-out">
    <g class="wb-wave"><path d="M0 50 Q25 40 50 50 T100 50 T150 50 T200 50 T250 50 T300 50 V70H0Z" fill="url(#wbw)"/></g>
    <rect x="0" y="60" width="200" height="320" fill="url(#wbw)"/>
    <circle cx="45" cy="120" r="3" fill="#fff" opacity=".5"/><circle cx="90" cy="160" r="2" fill="#fff" opacity=".5"/><circle cx="60" cy="210" r="4" fill="#fff" opacity=".4"/></g></g>
    <line x1="20" y1="{gy}" x2="120" y2="{gy}" stroke="#2E7D32" stroke-width="2" stroke-dasharray="5 4"/><text x="26" y="{gy-4}" font-size="9" fill="#2E7D32" font-weight="700">GOAL</text>
    <text x="70" y="190" text-anchor="middle" font-size="17" font-weight="800" fill="{DARK}">{max(0, goal-total)} ml</text>
    <text x="70" y="206" text-anchor="middle" font-size="10" fill="{DARK}">remaining</text>
    <rect x="20" y="50" width="100" height="290" rx="30" fill="none" stroke="{DARK}" stroke-width="4"/>{ticks}
    {'<circle class="wb-drip" cx="70" cy="-14" r="6" fill="#4FC3F7"/>' if drip else ''}</svg>""")


CSS = """<style>
.stApp{background:linear-gradient(180deg,#E1F5FE 0%,#B3E5FC 40%,#C8E6C9 100%) fixed;}
header[data-testid="stHeader"]{background:transparent;} #MainMenu,footer{visibility:hidden;}
.block-container{max-width:760px;padding:1rem 1rem 6rem;position:relative;z-index:1;}
h1,h2,h3,h4,p,label,span,div{color:#37474F;}
div[data-testid="stHorizontalBlock"]{flex-wrap:nowrap !important;gap:.4rem !important;}
div[data-testid="stColumn"],div[data-testid="column"]{min-width:0 !important;flex:1 1 0 !important;width:auto !important;}
.wb-bgfx{position:fixed;inset:0;overflow:hidden;pointer-events:none;z-index:0;}
.wb-bgfx i{position:absolute;bottom:-70px;border-radius:50%;background:rgba(255,255,255,.35);border:1.5px solid rgba(255,255,255,.8);animation:wkrise linear infinite;}
.wb-waves{position:absolute;bottom:0;left:0;width:200%;height:90px;animation:wkwave 12s linear infinite;opacity:.55;}
.wb-title{text-align:center;font-weight:800;font-size:2.3rem;margin:.2rem 0 0;}
.wb-sub{text-align:center;opacity:.8;margin-bottom:.6rem;}
.wb-card{background:rgba(255,255,255,.78);backdrop-filter:blur(6px);border-radius:22px;padding:14px;margin:12px 0;box-shadow:0 6px 18px rgba(55,71,79,.12);border:2px solid #fff;}
.wb-card h4{margin:0 0 8px;font-size:1rem;}
.wb-head{display:flex;justify-content:space-between;align-items:center;background:linear-gradient(135deg,#fff,#B3E5FC);border-radius:24px;padding:12px 16px;border:2px solid #fff;box-shadow:0 6px 18px rgba(55,71,79,.12);}
.wb-head b{font-size:1.5rem;display:block;} .wb-head span{font-size:.85rem;opacity:.8;}
.wb-chip{background:#fff;border-radius:20px;padding:6px 12px;font-weight:800;}
.wb-scene{position:relative;height:235px;border-radius:26px;overflow:hidden;border:3px solid #fff;box-shadow:0 6px 18px rgba(55,71,79,.18);margin:12px 0;}
.wb-wx{position:absolute;top:8px;right:14px;font-size:2.2rem;}
.wb-say{position:absolute;top:12px;left:12px;max-width:62%;background:#fff;border:2px solid #37474F;border-radius:16px;padding:6px 10px;font-weight:700;font-size:.85rem;z-index:3;}
.wb-hill{position:absolute;bottom:34px;height:90px;background:#A5D6A7;border-radius:50% 50% 0 0;}
.wb-trees{position:absolute;bottom:34px;left:0;width:max-content;white-space:nowrap;font-size:26px;letter-spacing:30px;animation:wktrees linear infinite;}
.wb-ground{position:absolute;bottom:0;left:0;right:0;height:42px;background:linear-gradient(#9CCC65 0 40%,#7CB342 40%);}
.wb-path{position:absolute;left:0;right:0;top:16px;height:6px;background:repeating-linear-gradient(90deg,#fff 0 26px,transparent 26px 56px);animation:wkpath linear infinite;opacity:.8;}
.wb-wick{position:absolute;left:50%;bottom:14px;margin-left:-105px;z-index:2;}
.wb-hero{display:flex;gap:12px;align-items:center;}
.wb-hl{flex:0 0 40%;max-width:220px;} .wb-hr{flex:1;min-width:0;}
.wb-bottle{width:100%;height:auto;display:block;}
.wb-big{font-size:2.4rem;font-weight:800;line-height:1;} .wb-big small{font-size:1rem;font-weight:600;}
.wb-bar{height:16px;background:#fff;border:2px solid #37474F;border-radius:12px;overflow:hidden;margin:8px 0 10px;}
.wb-bar>div{height:100%;background:linear-gradient(90deg,#81D4FA,#4FC3F7);transition:width .8s;}
.wb-tiles{display:grid;grid-template-columns:1fr 1fr;gap:8px;}
.wb-tile{background:#fff;border-radius:14px;padding:6px 8px;font-size:.72rem;} .wb-tile b{display:block;font-size:1.05rem;}
.wb-week{display:flex;justify-content:space-between;} .wb-day{text-align:center;font-size:.7rem;font-weight:700;}
.wb-ring{width:38px;height:38px;border-radius:50%;margin:0 auto 3px;display:flex;align-items:center;justify-content:center;}
.wb-ring u{width:28px;height:28px;border-radius:50%;background:#fff;text-decoration:none;display:flex;align-items:center;justify-content:center;font-size:.8rem;}
.wb-day.now .wb-ring{box-shadow:0 0 0 3px #37474F;}
.wb-row{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px dashed #B3E5FC;font-size:.85rem;}
.wb-mgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}
.wb-mile{background:#fff;border-radius:16px;padding:6px 2px;text-align:center;font-size:.72rem;font-weight:700;border:2px solid #C8E6C9;}
.wb-mile.off{opacity:.4;filter:grayscale(.7);}
.wb-tip{background:#FFF59D;border-radius:6px;padding:10px 14px;transform:rotate(-1.2deg);box-shadow:2px 3px 8px rgba(0,0,0,.15);font-style:italic;text-align:center;}
.stButton>button{border-radius:16px;font-weight:700;border:2px solid #37474F;background:#fff;color:#37474F;padding:.5rem .3rem;font-size:.88rem;transition:transform .12s;}
.stButton>button:hover{transform:translateY(-2px);border-color:#37474F;color:#37474F;} .stButton>button:active{transform:scale(.95);}
.stButton>button[kind="primary"]{background:#4FC3F7;}
.wb-wave{animation:wkw2 2.4s linear infinite;} .wb-drip{animation:wkdrip .9s ease-in;opacity:0;} .wk-sweat{animation:wksw 1.6s ease-in infinite;} .wk-line{animation:wkblink .3s linear infinite alternate;}
@keyframes wkA{0%,100%{transform:rotate(-30deg)}50%{transform:rotate(30deg)}}
@keyframes wkB{0%,100%{transform:rotate(30deg)}50%{transform:rotate(-30deg)}}
@keyframes wkAs{0%,100%{transform:rotate(-8deg)}50%{transform:rotate(8deg)}}
@keyframes wkBs{0%,100%{transform:rotate(8deg)}50%{transform:rotate(-8deg)}}
@keyframes wkstep{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
@keyframes wksag{0%,100%{transform:translateY(2px)}50%{transform:translateY(6px)}}
@keyframes wkjump{0%,100%{transform:translateY(0)}35%{transform:translateY(-34px) scale(1.05)}}
@keyframes wkpath{to{background-position-x:-56px}} @keyframes wktrees{to{transform:translateX(-50%)}}
@keyframes wkrise{from{transform:translateY(0)}to{transform:translateY(-115vh)}}
@keyframes wkwave{to{transform:translateX(-50%)}} @keyframes wkw2{to{transform:translateX(-100px)}}
@keyframes wkdrip{0%{transform:translateY(0);opacity:1}85%{transform:translateY(76px);opacity:1}100%{transform:translateY(80px);opacity:0}}
@keyframes wksw{0%{transform:translateY(0);opacity:1}100%{transform:translateY(22px);opacity:0}} @keyframes wkblink{to{opacity:.3}}
</style>"""


def background():
    bubbles = "".join(f'<i style="left:{l}%;width:{w}px;height:{w}px;animation-duration:{t}s;animation-delay:-{dl}s"></i>'
                      for l, w, t, dl in [(5, 26, 16, 2), (14, 14, 12, 7), (26, 34, 20, 4), (38, 18, 14, 9), (52, 28, 18, 1),
                                          (63, 12, 11, 5), (74, 30, 22, 8), (86, 20, 15, 3), (94, 36, 19, 10)])
    wave = ('<svg class="wb-waves" viewBox="0 0 1200 90" preserveAspectRatio="none"><path d="M0 40 Q150 0 300 40 T600 40 T900 40 T1200 40 V90H0Z" fill="#81D4FA"/>'
            '<path d="M0 55 Q150 20 300 55 T600 55 T900 55 T1200 55 V90H0Z" fill="#4FC3F7" opacity=".6"/></svg>')
    st.markdown(CSS + f'<div class="wb-bgfx">{bubbles}{wave}</div>', unsafe_allow_html=True)


# ---------------- screens ----------------
def screen_welcome():
    st.markdown("<div class='wb-title'>Water Buddy</div><div class='wb-sub'>Your body needs water!<br>Meet Wick, your hydration buddy 🐢</div>", unsafe_allow_html=True)
    st.markdown(scene_html("happy", f"Hi, I'm {MASCOT_NAME}! Let's drink up together 💧", False), unsafe_allow_html=True)
    st.button("Get Started", type="primary", on_click=go, args=("age",), width="stretch")


def screen_age():
    st.markdown("<div class='wb-title' style='font-size:1.8rem'>Select your age group</div>", unsafe_allow_html=True)
    age = st.radio("Age group", list(AGE_GROUPS), index=2, label_visibility="collapsed")
    rec = AGE_GROUPS[age]
    st.markdown(f"<div class='wb-card' style='text-align:center'>Recommended goal: <b>{rec} ml</b> (about {rec/250:.0f} cups)</div>", unsafe_allow_html=True)
    goal = st.slider("Adjust your daily goal (ml) if you want", 500, 4000, rec, 50, key=f"goal_{age}")
    if st.button("Let's Go!", type="primary", width="stretch"):
        st.session_state.age, st.session_state.goal = age, goal
        reset_day()
        go("home")
        st.rerun()


@st.dialog("Add a custom amount")
def custom_dialog():
    ml = st.number_input("Amount (ml)", 10, 1000, 150, 10)
    if st.button("Add water 💧", type="primary", width="stretch"):
        add_water(int(ml))
        st.rerun()


@st.dialog("Start a new day?")
def reset_dialog():
    st.write("Today's result is saved to your streak and the bottle starts empty.")
    c1, c2 = st.columns(2)
    if c1.button("Cancel", width="stretch"):
        st.rerun()
    if c2.button("Yes, new day", type="primary", width="stretch"):
        new_day()
        st.rerun()


def screen_home():
    s = st.session_state
    pct = min(100.0, s.total / s.goal * 100) if s.goal else 0
    mood, cur, best = mood_for(pct), *streaks()
    st.markdown(f"<div class='wb-head'><div><b>Stay hydrated 💧</b><span>{s.age} · goal {s.goal} ml</span></div><div class='wb-chip'>🔥 {cur}</div></div>", unsafe_allow_html=True)
    st.markdown(scene_html(mood, message_for(pct, len(s.log)), s.just_logged), unsafe_allow_html=True)
    tiles = "".join(f"<div class='wb-tile'>{i} {l}<b>{v}</b></div>" for i, l, v in [
        ("🎯", "Daily target", f"{s.goal} ml"), ("🥤", "Remaining", f"{max(0, s.goal - s.total)} ml"),
        ("🔥", "Current streak", f"{cur} day{'s' if cur != 1 else ''}"), ("🏆", "Best streak", f"{best} day{'s' if best != 1 else ''}")])
    st.markdown(html(f"""<div class='wb-card'><div class='wb-hero'><div class='wb-hl'>{bottle_svg(s.total, s.prev, s.goal, s.fills, s.just_logged)}</div>
    <div class='wb-hr'><div class='wb-big'>{s.total}<small> ml</small></div><div style='font-weight:700'>{pct:.0f}% of today's goal</div>
    <div class='wb-bar'><div style='width:{pct:.0f}%'></div></div><div class='wb-tiles'>{tiles}</div></div></div></div>"""), unsafe_allow_html=True)

    c = st.columns(4)
    c[0].button("💧 100", key="q100", on_click=add_water, args=(100,), width="stretch")
    c[1].button(f"💧 {QUICK_ML} ml", key="q250", type="primary", on_click=add_water, args=(QUICK_ML,), width="stretch")
    c[2].button("💧 500", key="q500", on_click=add_water, args=(500,), width="stretch")
    if c[3].button("✏️ Custom", key="cust", width="stretch"):
        custom_dialog()
    a = st.columns(3)
    a[0].button("↩️ Undo", on_click=undo_last, disabled=not s.log, width="stretch")
    if a[1].button("🌅 New day", width="stretch"):
        reset_dialog()
    a[2].button("🎂 Age", on_click=go, args=("age",), width="stretch")

    days = ""
    for i in range(6, -1, -1):
        d = s.today - timedelta(days=i)
        v = {"ml": s.total, "goal": s.goal} if i == 0 else s.history.get(d.isoformat())
        p = min(100, v["ml"] / v["goal"] * 100) if v and v["goal"] else 0
        days += (f"<div class='wb-day{' now' if i == 0 else ''}'><div class='wb-ring' style='background:conic-gradient({WATER} {p}%,#E3F2FD 0)'>"
                 f"<u>{'✔' if p >= 100 else ''}</u></div>{d.strftime('%a')}</div>")
    st.markdown(f"<div class='wb-card'><h4>🔥 Daily streak tracker</h4><div class='wb-week'>{days}</div>"
                f"<div style='font-size:.75rem;margin-top:8px;opacity:.8'>Hit your goal each day to grow your streak. Tap “New day” to try it.</div></div>", unsafe_allow_html=True)

    run, rows = 0, ""
    for i, ml in enumerate(s.log):
        run += ml
        rows += f"<div class='wb-row'><span>💧 Sip {i+1} · {ml} ml</span><span>{min(100, run*100//s.goal)}%</span></div>"
    st.markdown(f"<div class='wb-card'><h4>Today's progress</h4>{rows or 'No sips yet. Wick is waiting! 🐢'}</div>", unsafe_allow_html=True)

    mm = "".join(f"<div class='wb-mile{'' if pct >= m else ' off'}'>{m}%{wick_svg(md, 78, False)}<br>{t}</div>" for m, md, t in
                 [(50, "happy", "Halfway there!"), (75, "excited", "You're doing great!"), (100, "party", "Goal achieved!")])
    st.markdown(f"<div class='wb-card'><h4>🐢 Wick's milestones</h4><div class='wb-mgrid'>{mm}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='wb-tip'>💡 Tip: {TIPS[s.fills % len(TIPS)]}</div>", unsafe_allow_html=True)

    with st.expander("💾 Save / restore my progress (JSON)"):
        data = {"age": s.age, "goal": s.goal, "total": s.total, "log": s.log, "today": s.today.isoformat(), "history": s.history}
        st.download_button("Download progress", json.dumps(data), "waterbuddy_progress.json", "application/json")
        up = st.file_uploader("Restore from file", type="json")
        if up and s.restored != f"{up.name}{up.size}":
            try:
                x = json.loads(up.getvalue())
                s.update(age=x["age"], goal=int(x["goal"]), total=int(x["total"]), prev=int(x["total"]), log=list(x["log"]),
                         today=date.fromisoformat(x["today"]), history=dict(x["history"]), restored=f"{up.name}{up.size}")
                st.rerun()
            except Exception:
                st.error("That file doesn't look like WaterBuddy progress.")
    s.prev, s.just_logged = s.total, False
    if s.celebrate:
        st.balloons()
        s.celebrate = False


init_state()
background()
{"welcome": screen_welcome, "age": screen_age}.get(st.session_state.screen, screen_home)()
st.markdown("<p style='text-align:center;opacity:.6;font-size:.8rem'>WaterBuddy · Healthy Habits · Happy Users · A Brighter Tomorrow</p>", unsafe_allow_html=True)
