"""Hokies vs. Georgia Tech tailgate RSVP — Sat 10/17, German Club grass lot, 10:30 AM."""
import html
import json
import re
import threading
from datetime import datetime
from pathlib import Path

import streamlit as st

DATA = Path(__file__).with_name("rsvps.json")
LOCK = threading.Lock()
STATUS = {"in": "🔥 I'm in", "maybe": "🤔 Maybe", "out": "😔 Can't"}
GMAPS = "https://www.google.com/maps/search/?api=1&query=German+Club+Manor+Blacksburg+VA"
AMAPS = "https://maps.apple.com/?q=German+Club+Manor+Blacksburg+VA"

ANNOUNCEMENT = """🚀🦃 Unlocking the Ultimate Tailgate Experience 🦃🚀

In today's fast-paced world, it's more important than ever to pause, reflect, and come together to celebrate what truly matters: community, connection, and beating Georgia Tech. 🐝❌

It's not just a tailgate. It's a MOVEMENT. 💪✨

📅 Saturday 10/17
⏰ 10:30 AM sharp (greatness waits for no one)
📍 German Club parking lot, grass lot 🌱

🍔 Food: provided. Nourishing body AND soul 🙏
🍺 Drinks: mostly beer. If your journey calls for something different, feel empowered to bring it. Your hydration, your truth. 💧
📺 TV · 🔥 grill · 🎲 drinking games (fostering meaningful bonds)

Whether you're a seasoned veteran or just beginning your tailgate journey, there's a place for YOU at this table. 🫵❤️

RSVP + map here 👉 [paste link]

Let's. Go. Hokies. 🦃🔥🧡🤎

I hope this message finds you well. 🤖✨"""


# ---------- storage ----------
def load():
    try:
        return json.loads(DATA.read_text())
    except Exception:
        return {}


def save(rows):
    tmp = DATA.with_suffix(".tmp")
    tmp.write_text(json.dumps(rows, indent=2))
    tmp.replace(DATA)


def split_guests(text):
    return [g.strip() for g in re.split(r",|\band\b|&|\n", text or "") if g.strip()]


e = html.escape

st.set_page_config(page_title="GT Tailgate RSVP", page_icon="🦃", layout="centered")

# ---------- styles (same tokens as the artifact) ----------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bowlby+One+SC&family=Figtree:wght@400;600;800&family=JetBrains+Mono:wght@500&display=swap');
:root{
  --bg:#fbf6f2; --surface:#ffffff; --fg:#2a0d1a; --muted:#7a5b67; --line:#ead9d2;
  --maroon:#630031; --orange:#cf4420; --grass:#3f7d3a; --grass-2:#5d9b54;
  --in:#2f7d3b; --maybe:#b7791f; --out:#9b2c2c;
  --display:"Bowlby One SC","Impact","Arial Black",sans-serif;
  --body:"Figtree",system-ui,-apple-system,sans-serif;
  --mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
}
/* hide Streamlit chrome */
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"]{display:none!important}
.stApp{background:var(--bg)!important;color:var(--fg)!important}
.stApp, .stApp p, .stApp label, .stApp input, .stApp button{font-family:var(--body)!important}
.block-container{max-width:720px!important;padding-top:20px!important;padding-bottom:48px!important;padding-left:max(16px,env(safe-area-inset-left,0px))!important;padding-right:max(16px,env(safe-area-inset-right,0px))!important}
[data-testid="stVerticalBlock"]{gap:14px}

.tg h1,.tg h2{font-family:var(--display)!important;font-weight:400!important;margin:0!important;padding:0!important;text-wrap:balance;line-height:1.05!important}
.tg h1{font-size:clamp(2rem,8vw,3.4rem)!important;color:var(--maroon)!important}
.tg h1 .vs{color:var(--orange)}
.tg h2{font-size:1.5rem!important;color:var(--maroon)!important;margin-top:18px!important}
.tg a.anchor-link, .tg [data-testid="stHeaderActionElements"]{display:none!important}
.eyebrow{font-family:var(--mono);font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;color:var(--orange)}
.hero{display:flex;flex-direction:column;gap:12px}
.hype{font-size:1.05rem;max-width:62ch;margin:0;color:var(--fg);line-height:1.5}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:6px}
.fact{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.fact b{display:block;font-family:var(--mono);font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:500}
.fact span{font-weight:800;color:var(--fg)}
.tally{display:flex;gap:8px;flex-wrap:wrap}
.chip{font-family:var(--mono);font-size:.82rem;padding:4px 10px;border-radius:999px;border:1.5px solid currentColor;font-variant-numeric:tabular-nums}
.chip.in{color:var(--in)}.chip.maybe{color:var(--maybe)}.chip.out{color:var(--out)}.chip.heads{color:var(--maroon)}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px}
ul.list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}
ul.list li{display:flex;gap:10px;align-items:baseline;padding:10px 2px;border-bottom:1px solid var(--line);margin:0;flex-wrap:wrap}
ul.list li:last-child{border-bottom:0}
.dot{width:10px;height:10px;border-radius:50%;flex:none;align-self:center}
.dot.in{background:var(--in)}.dot.maybe{background:var(--maybe)}.dot.out{background:var(--out)}
.who{font-weight:800;color:var(--fg)}
.plus{font-weight:600;color:var(--maroon)}
.bring{color:var(--muted);font-size:.9rem;min-width:0;overflow-wrap:anywhere;flex:1 1 140px}
.empty{color:var(--muted);font-style:italic;padding:8px 2px}
.note{font-size:.88rem;color:var(--muted);margin:0}
.map{border-radius:14px;overflow:hidden;border:1px solid var(--line)}
.map svg{display:block;width:100%;height:auto}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.btn{font-family:var(--body);font-weight:800;padding:10px 16px;border-radius:10px;border:0;background:var(--orange);color:#fff!important;text-decoration:none!important;display:inline-block}
.btn.ghost{background:transparent;color:var(--maroon)!important;border:1.5px solid var(--line)}

/* RSVP form styled as the artifact's card */
[data-testid="stForm"]{background:var(--surface)!important;border:1px solid var(--line)!important;border-radius:14px!important;padding:16px!important}
.stApp label p{font-size:.85rem!important;color:var(--muted)!important;font-weight:600!important}
.stTextInput input{border-radius:10px!important;background:var(--bg)!important;color:var(--fg)!important;font-size:16px!important}
.stTextInput [data-baseweb="input"]{border:1.5px solid var(--line)!important;border-radius:10px!important;background:var(--bg)!important}
[data-testid="stRadioGroup"]{display:flex!important;flex-direction:row!important;gap:8px!important;flex-wrap:wrap!important}
[data-testid="stRadioGroup"] > div{flex:1 1 90px;display:flex}
[data-testid="stRadioOption"]{flex:1;border:2px solid var(--line);border-radius:10px;padding:10px 12px!important;margin:0!important;justify-content:center;background:transparent;cursor:pointer}
[data-testid="stRadioOption"] > div{justify-content:center;width:100%}
[data-testid="stRadioOption"] > div > div:first-child:not([data-testid]){display:none!important}
[data-testid="stRadioOption"] p{font-weight:800!important;color:var(--fg)!important;font-size:1rem!important;margin:0!important}
[data-testid="stRadioOption"][data-selected="true"]{border-color:var(--orange)}
[data-testid="stRadioOption"][data-selected="true"] p{color:var(--orange)!important}
.stFormSubmitButton button, .stButton button{background:var(--orange)!important;color:#fff!important;border:0!important;border-radius:10px!important;font-weight:800!important;padding:10px 16px!important}
.stFormSubmitButton button p, .stButton button p{color:#fff!important;font-weight:800!important}
[data-testid="stExpander"]{border:1px solid var(--line)!important;border-radius:14px!important;background:var(--surface)!important}
[data-testid="stExpander"] summary p{color:var(--muted)!important}
</style>
""",
    unsafe_allow_html=True,
)

# ---------- hero ----------
st.markdown(
    """
<div class="tg hero">
  <div class="eyebrow">🚀 A tailgate experience · Sat 10/17</div>
  <h1>Hokies <span class="vs">vs.</span> Georgia Tech Tailgate</h1>
  <p class="hype">In today's fast-paced world, it's more important than ever to come together and celebrate what truly matters: community, connection, and beating Georgia Tech. 🐝❌ This isn't just a tailgate. It's a movement. 💪✨</p>
  <div class="facts">
    <div class="fact"><b>When</b><span>Sat 10/17 · 10:30 AM</span></div>
    <div class="fact"><b>Where</b><span>German Club lot (grass)</span></div>
    <div class="fact"><b>Food</b><span>Provided 🍔</span></div>
    <div class="fact"><b>Drinks</b><span>Mostly beer 🍺 BYO else</span></div>
    <div class="fact"><b>Amenities</b><span>TV · grill · games 🎲</span></div>
  </div>
</div>
<div class="tg"><h2>RSVP: Are You Ready to Unlock Your Potential?</h2></div>
""",
    unsafe_allow_html=True,
)

tally_slot = st.empty()

# ---------- RSVP form ----------
with st.form("rsvp", clear_on_submit=True):
    status = st.radio("Your answer", list(STATUS), format_func=STATUS.get, horizontal=True,
                      label_visibility="collapsed")
    name = st.text_input("Your name", max_chars=40, placeholder="e.g. Gavin")
    guests = st.text_input("Who are you bringing? (names, separated by commas)", max_chars=120,
                           placeholder="e.g. Jake, Sam")
    bring = st.text_input("Bringing anything? (drinks, chairs, vibes)", max_chars=80,
                          placeholder="e.g. a 12-pack of seltzer and unmatched enthusiasm")
    sent = st.form_submit_button("Save my RSVP")

if sent:
    if not name.strip():
        st.error("Add your name so we know who's coming.")
    else:
        with LOCK:
            rows = load()
            rows[name.strip().lower()] = {
                "name": name.strip(), "status": status, "guests": split_guests(guests),
                "bring": bring.strip(), "at": datetime.now().isoformat(timespec="seconds"),
            }
            save(rows)
        st.success(f"Saved, {name.strip()}. Your journey begins. ✨ Submit again with the same name to change it.")
        if status == "in":
            st.balloons()

# ---------- list ----------
rows = load()
order = {"in": 0, "maybe": 1, "out": 2}
people = sorted(rows.values(), key=lambda r: (order.get(r["status"], 3), r["name"].lower()))
t = {k: sum(r["status"] == k for r in people) for k in STATUS}
heads = sum(1 + len(r.get("guests", [])) for r in people if r["status"] == "in")

tally_slot.markdown(
    f'<div class="tally"><span class="chip in">{t["in"]} in</span>'
    f'<span class="chip maybe">{t["maybe"]} maybe</span><span class="chip out">{t["out"]} out</span>'
    f'<span class="chip heads">{heads} total heads 🦃</span></div>',
    unsafe_allow_html=True,
)

if people:
    items = []
    for r in people:
        g = r.get("guests", [])
        plus = f'<span class="plus">+ {e(", ".join(g))}</span>' if g else ""
        detail = f"bringing {e(r['bring'])}" if r.get("bring") else e(STATUS.get(r["status"], ""))
        items.append(
            f'<li><span class="dot {e(r["status"])}"></span><span class="who">{e(r["name"])}</span>'
            f'{plus}<span class="bring">{detail}</span></li>'
        )
    list_html = "".join(items)
else:
    list_html = '<li class="empty">Nobody yet. Be the first to step into your tailgate era. 🫵</li>'
st.markdown(f'<div class="card"><ul class="list">{list_html}</ul></div>', unsafe_allow_html=True)

# ---------- map ----------
st.markdown(
    f"""
<div class="tg"><h2>The Destination 📍</h2></div>
<div class="map" role="img" aria-label="Illustrated grass lot with the tailgate spot marked">
<svg viewBox="0 0 600 260" xmlns="http://www.w3.org/2000/svg">
<rect width="600" height="260" fill="#3f7d3a"/>
<g fill="#5d9b54" opacity=".7"><rect x="0" y="0" width="600" height="20"/><rect x="0" y="60" width="600" height="20"/><rect x="0" y="120" width="600" height="20"/><rect x="0" y="180" width="600" height="20"/><rect x="0" y="240" width="600" height="20"/></g>
<rect x="0" y="210" width="600" height="50" fill="#ead9d2"/>
<text x="20" y="242" font-family="JetBrains Mono, monospace" font-size="14" fill="#7a5b67">ENTRANCE / ROAD</text>
<g fill="#ffffff" stroke="#ead9d2"><rect x="60" y="40" width="70" height="36" rx="6"/><rect x="160" y="40" width="70" height="36" rx="6"/><rect x="430" y="40" width="70" height="36" rx="6"/><rect x="80" y="130" width="70" height="36" rx="6"/><rect x="450" y="130" width="70" height="36" rx="6"/></g>
<circle cx="315" cy="115" r="62" fill="#cf4420" opacity=".18"/>
<rect x="270" y="88" width="90" height="54" rx="6" fill="#630031"/>
<text x="315" y="120" text-anchor="middle" font-family="Bowlby One SC, Impact, sans-serif" font-size="16" fill="#fbf6f2">US 🦃</text>
<text x="315" y="175" text-anchor="middle" font-family="Figtree, sans-serif" font-weight="800" font-size="15" fill="#fff">Look for the TV + grill</text>
</svg></div>
<p class="note">Not to scale. Spiritually accurate. German Club parking lot, grass side.</p>
<div class="row">
  <a class="btn" href="{GMAPS}" target="_blank" rel="noopener">Open in Google Maps</a>
  <a class="btn ghost" href="{AMAPS}" target="_blank" rel="noopener">Apple Maps</a>
</div>
<div class="tg"><h2>Copy This Into the Group Chat</h2></div>
""",
    unsafe_allow_html=True,
)

# ---------- group chat text (iframe so the copy button works) ----------
st.iframe(
    f"""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@800&family=JetBrains+Mono:wght@500&display=swap">
<style>
body{{margin:0;font-family:"Figtree",system-ui,sans-serif;background:transparent}}
.card{{background:#fff;border:1px solid #ead9d2;border-radius:14px;padding:16px;display:flex;flex-direction:column;gap:12px}}
.sms{{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:13px;white-space:pre-wrap;background:#fbf6f2;color:#2a0d1a;border:1px dashed #ead9d2;border-radius:10px;padding:12px;max-height:300px;overflow:auto}}
.row{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}}
.btn{{font:inherit;font-weight:800;padding:10px 16px;border-radius:10px;border:0;background:#cf4420;color:#fff;cursor:pointer}}
.toast{{font-size:14px;font-weight:700;color:#2f7d3b}}
.note{{font-size:14px;color:#7a5b67;margin:0}}
</style>
<div class="card">
  <div class="sms" id="sms">{e(ANNOUNCEMENT)}</div>
  <div class="row"><button class="btn" id="copy">Copy text</button><span class="toast" id="t"></span></div>
  <p class="note">Swap "[paste link]" for this app's link before sending.</p>
</div>
<script>
document.getElementById("copy").onclick=()=>{{
  const el=document.getElementById("sms"),t=document.getElementById("t");
  const sel=()=>{{const r=document.createRange();r.selectNodeContents(el);const s=getSelection();s.removeAllRanges();s.addRange(r);}};
  if(navigator.clipboard){{navigator.clipboard.writeText(el.textContent).then(()=>t.textContent="Copied. Go spread the movement. 🚀").catch(()=>{{sel();document.execCommand("copy");t.textContent="Copied. Go spread the movement. 🚀";}})}}
  else{{sel();document.execCommand("copy");t.textContent="Copied. Go spread the movement. 🚀";}}
}};
</script>
""",
    height=470,
)

# ---------- host tools ----------
try:
    admin_code = st.secrets.get("ADMIN_CODE", "")
except Exception:
    admin_code = ""
with st.expander("Host tools"):
    code = st.text_input("Host code", type="password")
    if admin_code and code == admin_code and people:
        who = st.selectbox("Remove someone", [r["name"] for r in people])
        if st.button("Remove"):
            with LOCK:
                rows = load()
                rows.pop(who.lower(), None)
                save(rows)
            st.rerun()
    elif code and code != admin_code:
        st.caption("That code doesn't match.")
