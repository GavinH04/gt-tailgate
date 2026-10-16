"""Hokies vs. Georgia Tech tailgate RSVP — Sat 10/17, German Club grass lot, 10:30 AM."""
import json
import threading
from datetime import datetime
from pathlib import Path

import streamlit as st

DATA = Path(__file__).with_name("rsvps.json")
LOCK = threading.Lock()
STATUS = {"in": "🔥 I'm in", "maybe": "🤔 Maybe", "out": "😔 Can't make it"}
MAPS = "https://www.google.com/maps/search/?api=1&query=German+Club+Manor+Blacksburg+VA"

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

RSVP here 👉 [paste app link]

Let's. Go. Hokies. 🦃🔥🧡🤎

I hope this message finds you well. 🤖✨"""


def load():
    try:
        return json.loads(DATA.read_text())
    except Exception:
        return {}


def save(rows):
    tmp = DATA.with_suffix(".tmp")
    tmp.write_text(json.dumps(rows, indent=2))
    tmp.replace(DATA)


st.set_page_config(page_title="GT Tailgate RSVP", page_icon="🦃", layout="centered")
st.markdown(
    """<style>
    h1, h2, h3 {color:#861F41 !important;}
    div.stButton > button, div.stFormSubmitButton > button {background:#E5751F;color:white;border:0;font-weight:700;}
    </style>""",
    unsafe_allow_html=True,
)

st.caption("🚀 A TAILGATE EXPERIENCE · SAT 10/17")
st.title("Hokies vs. Georgia Tech Tailgate 🦃")
st.write(
    "In today's fast-paced world, it's more important than ever to come together and celebrate "
    "what truly matters: community, connection, and beating Georgia Tech. 🐝❌ "
    "This isn't just a tailgate. It's a **movement**. 💪✨"
)

c1, c2, c3 = st.columns(3)
c1.metric("When", "Sat 10:30 AM")
c2.metric("Where", "German Club")
c3.metric("Food", "Provided 🍔")
st.write("🍺 **Drinks:** mostly beer, so bring anything else you want. Your hydration, your truth. 💧  \n"
         "📺 TV · 🔥 grill · 🎲 drinking games")

# ---------- RSVP ----------
st.header("RSVP: Are You Ready to Unlock Your Potential?")
with st.form("rsvp", clear_on_submit=True):
    name = st.text_input("Your name", max_chars=40)
    status = st.radio("Are you coming?", list(STATUS), format_func=STATUS.get, horizontal=True)
    bring = st.text_input("Bringing anything? (drinks, chairs, vibes)", max_chars=80,
                          placeholder="a 12-pack of seltzer and unmatched enthusiasm")
    sent = st.form_submit_button("Save my RSVP")

if sent:
    if not name.strip():
        st.error("Add your name so we know who's coming.")
    else:
        with LOCK:
            rows = load()
            rows[name.strip().lower()] = {
                "name": name.strip(), "status": status, "bring": bring.strip(),
                "at": datetime.now().isoformat(timespec="seconds"),
            }
            save(rows)
        st.success(f"Saved, {name.strip()}. Your journey begins. ✨ (Submit again with the same name to change it.)")
        if status == "in":
            st.balloons()

rows = load()
order = {"in": 0, "maybe": 1, "out": 2}
people = sorted(rows.values(), key=lambda r: (order.get(r["status"], 3), r["name"].lower()))
tally = {k: sum(r["status"] == k for r in people) for k in STATUS}

t1, t2, t3 = st.columns(3)
t1.metric("🔥 In", tally["in"])
t2.metric("🤔 Maybe", tally["maybe"])
t3.metric("😔 Out", tally["out"])

if people:
    for r in people:
        extra = f" · bringing {r['bring']}" if r["bring"] else ""
        st.markdown(f"- {STATUS[r['status']].split(' ')[0]} **{r['name']}**{extra}")
else:
    st.info("Nobody yet. Be the first to step into your tailgate era. 🫵")

# ---------- Map ----------
st.header("The Destination 📍")
st.write("German Club parking lot, **grass side**. Look for the TV and the grill.")
st.link_button("Open in Google Maps", MAPS)

# ---------- Group chat text ----------
st.header("Copy This Into the Group Chat")
st.code(ANNOUNCEMENT, language=None, wrap_lines=True)
st.caption("Use the copy icon in the corner of the box. Swap in this app's link first.")

# ---------- Host tools ----------
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
