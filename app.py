import html as html_lib
from datetime import datetime

import requests
import streamlit as st
import streamlit.components.v1 as components

# ── Config ─────────────────────────────────────────────────────────────────────
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="MindMirror",
    page_icon="🪞",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global Streamlit CSS ───────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #FAF7F2;
    color: #2C2C2C;
}
section[data-testid="stSidebar"] {
    background: #F0EBE1;
    border-right: 1px solid #E0D8CC;
}
section[data-testid="stSidebar"] .block-container { padding-top: 2rem; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.main .block-container { padding: 2.5rem 3rem; max-width: 860px; }
div[data-testid="stSidebarContent"] .stButton > button {
    width: 100%; background: transparent; border: none;
    text-align: left; font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem; color: #5C5047;
    padding: 0.6rem 1rem; border-radius: 8px;
}
div[data-testid="stSidebarContent"] .stButton > button:hover {
    background: #E5DDD1; color: #1A1A1A;
}
textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.05rem !important;
    line-height: 1.8 !important;
    background: #FFFDF9 !important;
    border: 1.5px solid #DDD5C8 !important;
    border-radius: 12px !important;
    color: #2C2C2C !important;
}
textarea::placeholder { color: #B8AFA5 !important; }
textarea:focus {
    border-color: #C4956A !important;
    box-shadow: 0 0 0 3px rgba(196,149,106,0.12) !important;
}
.stButton > button[kind="primary"] {
    background: #2C2C2C !important;
    color: #FAF7F2 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
}
.stButton > button[kind="primary"]:hover { background: #1A1A1A !important; }
.stTextInput input {
    background: #FFFDF9 !important;
    border: 1.5px solid #DDD5C8 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    color: #2C2C2C !important;
}
.stTextInput input:focus {
    border-color: #C4956A !important;
    box-shadow: 0 0 0 3px rgba(196,149,106,0.12) !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── CSS injected into every iframe (components.html) ──────────────────────────
_IFRAME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'DM Sans', sans-serif; }
body { background: transparent; padding: 2px; }

/* card */
.card {
    background: #FFFDF9;
    border: 1px solid #E0D8CC;
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
}

/* typography */
.date { font-size: 0.76rem; color: #B8AFA5; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.55rem; }
.body-text { font-size: 0.95rem; color: #2C2C2C; line-height: 1.7; margin-bottom: 0.75rem; white-space: pre-wrap; word-break: break-word; }
.summary { font-family: 'DM Serif Display', serif; font-style: italic; font-size: 0.9rem; color: #8C7E6E; margin-bottom: 0.75rem; }
.insight-quote { font-family: 'DM Serif Display', serif; font-size: 1.1rem; font-style: italic; color: #3C3028; line-height: 1.6; border-left: 3px solid #C4956A; padding-left: 1rem; margin: 0.75rem 0; }
.lbl { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em; color: #B8AFA5; margin-bottom: 0.35rem; }

/* chips */
.chips { margin-bottom: 0.65rem; }
.chip { display: inline-block; font-size: 0.76rem; font-weight: 500; padding: 2px 9px; border-radius: 20px; margin: 2px 2px; background: #EDE8E0; color: #5C5047; }
.chip-warn { display: inline-block; font-size: 0.76rem; font-weight: 500; padding: 2px 9px; border-radius: 20px; margin: 2px 2px; background: #F5ECD7; color: #8B5E1A; }

/* valence pill */
.pill { display: inline-block; font-size: 0.76rem; font-weight: 500; padding: 2px 10px; border-radius: 20px; }

/* bar */
.bar-wrap { background: #EDE8E0; border-radius: 99px; height: 5px; width: 100%; margin-top: 4px; }
.bar-fill { height: 5px; border-radius: 99px; }

/* footer row inside card */
.card-footer { display: flex; align-items: center; gap: 1rem; margin-top: 0.7rem; flex-wrap: wrap; }
.intensity-lbl { font-size: 0.76rem; color: #B8AFA5; }

/* distortion box */
.dist-box {
    background: #FDF5E8; border: 1px solid #EDD5A3;
    border-radius: 10px; padding: 0.8rem 1rem;
    margin-top: 0.75rem; font-size: 0.85rem; color: #7A5220; line-height: 1.6;
}

/* metrics */
.metric-row { display: flex; gap: 0.8rem; }
.metric-card { flex: 1; background: #FFFDF9; border: 1px solid #E0D8CC; border-radius: 12px; padding: 1rem; text-align: center; }
.metric-val { font-family: 'DM Serif Display', serif; font-size: 1.9rem; color: #1A1A1A; }
.metric-lbl { font-size: 0.72rem; color: #8C7E6E; text-transform: uppercase; letter-spacing: 0.08em; }

/* bar rows (patterns) */
.bar-row { margin-bottom: 0.75rem; }
.bar-label { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 2px; }
.bar-count { color: #B8AFA5; }

/* valence tiles */
.valence-grid { display: flex; gap: 0.7rem; }
.valence-tile { flex: 1; text-align: center; padding: 0.9rem 0.4rem; border-radius: 12px; }
.valence-pct { font-family: 'DM Serif Display', serif; font-size: 1.5rem; }
.valence-lbl { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; }

/* report cards */
.report-card { background: #FFFDF9; border: 1px solid #E0D8CC; border-radius: 14px; padding: 1.3rem 1.5rem; margin-bottom: 0.75rem; }
.report-text { font-size: 0.97rem; color: #2C2C2C; line-height: 1.7; }

/* empty state */
.empty { text-align: center; padding: 2.5rem 1rem; color: #B8AFA5; }
.empty-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.empty-title { font-family: 'DM Serif Display', serif; font-size: 1.15rem; color: #8C7E6E; margin-bottom: 0.3rem; }
</style>
"""


# ── Pure helper functions ──────────────────────────────────────────────────────

def esc(text) -> str:
    """HTML-escape any value before injecting into an HTML string."""
    return html_lib.escape(str(text))


def fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%B %d, %Y · %H:%M")
    except Exception:
        return iso[:10]


def valence_colors(valence: str):
    """Return (bg_color, text_color) for a valence string."""
    palette = {
        "positive": ("#E3EDDE", "#3A6B30"),
        "negative": ("#F5E0E0", "#B04040"),
        "mixed":    ("#F5ECD7", "#8B5E1A"),
        "neutral":  ("#EDE8E0", "#5C5047"),
    }
    return palette.get(valence, ("#EDE8E0", "#5C5047"))


def make_chips(items: list, warn: bool = False) -> str:
    cls = "chip-warn" if warn else "chip"
    return "".join(f'<span class="{cls}">{esc(i)}</span>' for i in items if i)


def make_bar(pct: int, color: str = "#C4956A") -> str:
    return (
        f'<div class="bar-wrap">'
        f'<div class="bar-fill" style="width:{pct}%;background:{color}"></div>'
        f'</div>'
    )


def render_iframe(body: str, height: int = 200) -> None:
    """Render HTML inside a sandboxed iframe — immune to Streamlit's sanitizer."""
    components.html(
        f"<!DOCTYPE html><html><head>{_IFRAME_CSS}</head><body>{body}</body></html>",
        height=height,
        scrolling=False,
    )


# ── API helpers ────────────────────────────────────────────────────────────────

def api_get(path: str, params: dict = None):
    try:
        r = requests.get(f"{API_URL}{path}", params=params, timeout=10)
        return r.json(), None
    except Exception as ex:
        return None, str(ex)


def api_post(path: str, body: dict):
    try:
        r = requests.post(f"{API_URL}{path}", json=body, timeout=30)
        return r.json(), None
    except Exception as ex:
        return None, str(ex)


def api_delete(path: str):
    try:
        r = requests.delete(f"{API_URL}{path}", timeout=10)
        return r.json(), None
    except Exception as ex:
        return None, str(ex)


@st.cache_data(ttl=30,show_spinner=False)
def cached_stats():
    return api_get("/stats")


@st.cache_data(ttl=30,show_spinner=False)
def cached_entries(days: int = 90):
    return api_get("/entries/recent", {"days": days})


def bust_cache():
    cached_stats.clear()
    cached_entries.clear()


# ── Sidebar nav ────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        '<p style="font-family:\'DM Serif Display\',serif;font-size:2rem;'
        'color:#1A1A1A;line-height:1.1;margin:0">Mind<br>Mirror</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-size:0.78rem;color:#8C7E6E;letter-spacing:0.08em;'
        'text-transform:uppercase;margin-bottom:1.5rem">Your private AI journal</p>',
        unsafe_allow_html=True,
    )

    NAV = {
        "✍️  Write":         "write",
        "📖  My Journal":    "journal",
        "🔍  Search":        "search",
        "📊  Patterns":      "patterns",
        "📋  Weekly Report": "report",
    }

    if "page" not in st.session_state:
        st.session_state.page = "write"

    for label, key in NAV.items():
        if st.button(label, key=f"nav_{key}"):
            st.session_state.page = key

    st.markdown("---")
    _stats, _ = cached_stats()
    if _stats:
        st.markdown(
            f'<p style="font-size:0.78rem;color:#8C7E6E;line-height:2;margin:0">'
            f'📝 {_stats.get("total_entries", 0)} entries<br>'
            f'⚡ Avg intensity: {_stats.get("avg_intensity", 0)}/10</p>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<p style="font-size:0.73rem;color:#B8AFA5;margin-top:1.5rem;'
        'padding-top:1rem;border-top:1px solid #E0D8CC;line-height:1.6">'
        'MindMirror is a self-reflection tool.<br>'
        'Not a substitute for professional mental health support.</p>',
        unsafe_allow_html=True,
    )

_page = st.session_state.page


# ══════════════════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════════════════
if _page == "write":
    now_str = datetime.now().strftime("%A, %B %d")
    st.markdown(
        f'<div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #E0D8CC">'
        f'<h1 style="font-family:\'DM Serif Display\',serif;font-size:2rem;margin:0 0 0.2rem">'
        f'Today&#39;s Entry</h1>'
        f'<p style="color:#8C7E6E;font-size:0.88rem;margin:0">{esc(now_str)}</p></div>',
        unsafe_allow_html=True,
    )

    text = st.text_area(
        "What's on your mind?",
        height=260,
        placeholder="Write freely — there's no right or wrong way to journal...",
        label_visibility="collapsed",
        key="write_text",
    )

    col_a, col_b = st.columns([1, 3])
    with col_a:
        submitted = st.button("Analyze & Save →", type="primary")
    with col_b:
        st.markdown(
            '<p style="color:#B8AFA5;font-size:0.82rem;padding-top:0.65rem">'
            'Stored privately on your machine.</p>',
            unsafe_allow_html=True,
        )

    if submitted:
        if len(text.strip()) < 10:
            st.warning("Write at least a sentence or two before analyzing.")
        else:
            with st.spinner("Reflecting on your words…"):
                result, err = api_post("/entry", {"text": text})

            if err:
                st.error(f"Cannot reach the API. Is `uvicorn api.main:app --reload` running?\n\n{err}")
            else:
                a = result.get("analysis", {})
                emotions    = a.get("emotions", [])
                distortions = a.get("distortions", [])
                intensity   = int(a.get("intensity", 5))
                valence     = a.get("valence", "neutral")
                summary     = a.get("summary", "")
                bg, fg      = valence_colors(valence)

                dist_html = ""
                if distortions:
                    dist_html = (
                        f'<div class="dist-box">'
                        f'<strong>Thinking patterns noticed:</strong>&nbsp;'
                        f'{make_chips(distortions, warn=True)}<br>'
                        f'<span style="font-size:0.82rem;opacity:0.8">'
                        f'Common cognitive patterns worth gently reflecting on — not diagnoses.</span>'
                        f'</div>'
                    )

                body = f"""
                <div class="card">
                    <div class="lbl">What I noticed</div>
                    <div class="insight-quote">{esc(summary)}</div>
                    <div class="chips">{make_chips(emotions)}</div>
                    <div style="display:flex;gap:1rem;align-items:flex-start;margin-top:0.6rem">
                        <div style="flex:1">
                            <div class="lbl">Tone</div>
                            <span class="pill" style="background:{bg};color:{fg};margin-top:4px">
                                {esc(valence.capitalize())}
                            </span>
                        </div>
                        <div style="flex:2">
                            <div class="lbl">Intensity &middot; {intensity}/10</div>
                            {make_bar(intensity * 10)}
                        </div>
                    </div>
                    {dist_html}
                </div>
                """
                render_iframe(body, height=230 + (90 if distortions else 0))
                bust_cache()


# ── Replace your ENTIRE "MY JOURNAL" section with this ────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
# MY JOURNAL
# ══════════════════════════════════════════════════════════════════════════════
elif _page == "journal":

    # ── Extra CSS for cards + delete button ─────────────────────────────────
    st.markdown("""
    <style>

    .journal-card {
        background: #FFFDF9;
        border: 1px solid #E0D8CC;
        border-radius: 14px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 1rem;
        position: relative;
    }

    .journal-date {
        font-size: 0.76rem;
        color: #B8AFA5;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.55rem;
    }

    .journal-text {
        font-size: 0.95rem;
        color: #2C2C2C;
        line-height: 1.7;
        margin-bottom: 0.75rem;
        white-space: pre-wrap;
    }

    .journal-summary {
        font-family: 'DM Serif Display', serif;
        font-style: italic;
        font-size: 0.95rem;
        color: #8C7E6E;
        margin-bottom: 0.8rem;
    }

    .journal-chip {
        display: inline-block;
        font-size: 0.76rem;
        font-weight: 500;
        padding: 2px 9px;
        border-radius: 20px;
        margin: 2px;
        background: #EDE8E0;
        color: #5C5047;
    }

    .journal-chip-warn {
        display: inline-block;
        font-size: 0.76rem;
        font-weight: 500;
        padding: 2px 9px;
        border-radius: 20px;
        margin: 2px;
        background: #F5ECD7;
        color: #8B5E1A;
    }

    .journal-footer {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-top: 0.8rem;
        flex-wrap: wrap;
    }

    .journal-pill {
        display: inline-block;
        font-size: 0.76rem;
        font-weight: 500;
        padding: 2px 10px;
        border-radius: 20px;
    }

    .journal-bar-wrap {
        background: #EDE8E0;
        border-radius: 999px;
        height: 5px;
        width: 110px;
    }

    .journal-bar-fill {
        height: 5px;
        border-radius: 999px;
        background: #C4956A;
    }

    .delete-btn button {
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        padding: 0 !important;
        background: #FFF5F5 !important;
        color: #B04040 !important;
        border: 1px solid #F0D0D0 !important;
        margin-top: 12px;
    }

    .delete-btn button:hover {
        background: #FFEAEA !important;
        border-color: #E8BBBB !important;
        color: #902D2D !important;
    }

    .distortion-box {
        margin-top: 0.7rem;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        """
        <div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #E0D8CC">
            <h1 style="font-family:'DM Serif Display',serif;font-size:2rem;margin:0 0 0.2rem">
                My Journal
            </h1>
            <p style="color:#8C7E6E;font-size:0.88rem;margin:0">
                All your entries with their emotional analysis
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    data, err = cached_entries(90)

    if err:
        st.error(f"Cannot reach API: {err}")

    elif not data or not data.get("entries"):

        st.markdown("""
        <div style="
            text-align:center;
            padding:3rem 1rem;
            color:#B8AFA5;
        ">
            <div style="font-size:2.5rem">🪞</div>

            <div style="
                font-family:'DM Serif Display',serif;
                font-size:1.2rem;
                color:#8C7E6E;
                margin-top:0.5rem;
            ">
                Your journal is empty
            </div>

            <div style="margin-top:0.3rem">
                Write your first entry to get started.
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:

        entries = data["entries"]

        # ── Top controls ─────────────────────────────────────────────────────
        top_col1, top_col2 = st.columns([5, 1])

        with top_col1:
            st.markdown(
                f"""
                <p style="color:#8C7E6E;font-size:0.85rem;margin:0 0 1rem">
                    {len(entries)} entries
                </p>
                """,
                unsafe_allow_html=True,
            )

        with top_col2:
            if st.button("🗑 Clear all", key="clear_all_btn"):
                st.session_state["confirm_clear_all"] = True

        # ── Confirm delete all ──────────────────────────────────────────────
        if st.session_state.get("confirm_clear_all"):
            st.warning("Delete ALL journal entries permanently?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Yes, delete all", type="primary"):
                    api_delete("/entries/all")
                    bust_cache()
                    st.session_state["confirm_clear_all"] = False
                    st.rerun()
            with c2:
                if st.button("Cancel"):
                    st.session_state["confirm_clear_all"] = False
                    st.rerun()

        # ── Render entries ──────────────────────────────────────────────────
        for entry in entries:

            meta         = entry["metadata"]
            entry_id     = entry["id"]
            text_body    = entry["text"]

            emotions     = [x.strip() for x in meta.get("emotions", "").split(",") if x.strip()]
            distortions  = [x.strip() for x in meta.get("distortions", "").split(",") if x.strip()]
            valence      = meta.get("valence", "neutral")
            intensity    = int(meta.get("intensity", 5))
            summary      = meta.get("summary", "")
            date_str     = fmt_date(meta.get("date", ""))
            bg, fg       = valence_colors(valence)
            short        = len(text_body) > 300
            display_text = text_body[:300] + ("\u2026" if short else "")

            # chips — inline styles only, no CSS classes (avoids st.markdown scoping issues)
            _cs  = "display:inline-block;font-size:0.76rem;font-weight:500;padding:2px 9px;border-radius:20px;margin:2px;background:#EDE8E0;color:#5C5047;"
            _cws = "display:inline-block;font-size:0.76rem;font-weight:500;padding:2px 9px;border-radius:20px;margin:2px;background:#F5ECD7;color:#8B5E1A;"
            emotion_html    = "".join(f'<span style="{_cs}">{esc(e)}</span>' for e in emotions)
            distortion_html = "".join(f'<span style="{_cws}">{esc(d)}</span>' for d in distortions)

            # card column + delete button column
            card_col, btn_col = st.columns([20, 1])

            with card_col:
                summary_block = (
                    f'<div style="font-family:\'DM Serif Display\',serif;font-style:italic;'
                    f'font-size:0.95rem;color:#8C7E6E;margin:0.6rem 0;">'
                    f'\u201c{esc(summary)}\u201d</div>'
                ) if summary else ''
                dist_block = f'<div style="margin-top:0.5rem">{distortion_html}</div>' if distortions else ''
                bar_w = intensity * 10
                st.markdown(
                    f'<div style="background:#FFFDF9;border:1px solid #E0D8CC;border-radius:14px;padding:1.3rem 1.5rem;margin-bottom:0.25rem;">'
                    f'<div style="font-size:0.76rem;color:#B8AFA5;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.55rem;">{esc(date_str)}</div>'
                    f'<div style="font-size:0.95rem;color:#2C2C2C;line-height:1.7;margin-bottom:0.6rem;white-space:pre-wrap;">{esc(display_text)}</div>'
                    f'{summary_block}'
                    f'<div style="margin-bottom:0.4rem">{emotion_html}</div>'
                    f'{dist_block}'
                    f'<div style="display:flex;align-items:center;gap:1rem;margin-top:0.8rem;flex-wrap:wrap;">'
                    f'<span style="background:{bg};color:{fg};padding:2px 10px;border-radius:20px;font-size:0.76rem;font-weight:500;">{esc(valence.capitalize())}</span>'
                    f'<span style="font-size:0.8rem;color:#8C7E6E;">Intensity {intensity}/10</span>'
                    f'<div style="background:#EDE8E0;border-radius:99px;height:5px;width:110px;">'
                    f'<div style="height:5px;border-radius:99px;background:#C4956A;width:{bar_w}%;"></div></div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

            with btn_col:
                st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
                if st.button("✕", key=f"delete_{entry_id}", help="Delete this entry"):
                    api_delete(f"/entry/{entry_id}")
                    bust_cache()
                    st.rerun()

            # expand full entry if truncated
            if short:
                with st.expander("Read full entry"):
                    st.write(text_body)

# ══════════════════════════════════════════════════════════════════════════════
# SEARCH
# ══════════════════════════════════════════════════════════════════════════════
elif _page == "search":
    st.markdown(
        '<div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #E0D8CC">'
        '<h1 style="font-family:\'DM Serif Display\',serif;font-size:2rem;margin:0 0 0.2rem">'
        'Search</h1>'
        '<p style="color:#8C7E6E;font-size:0.88rem;margin:0">'
        'Describe a feeling — not just a keyword</p></div>',
        unsafe_allow_html=True,
    )

    query = st.text_input(
        "search_input",
        label_visibility="collapsed",
        placeholder="e.g.  times I felt overwhelmed at work  ·  entries where I was hard on myself",
    )

    s_col, n_col = st.columns([1, 4])
    with s_col:
        do_search = st.button("Search →", type="primary")
    with n_col:
        n_results = st.select_slider(
            "n_results", options=[3, 5, 10], value=5, label_visibility="collapsed"
        )

    if do_search and query.strip():
        with st.spinner("Searching your journal…"):
            data, err = api_get("/search", {"q": query.strip(), "n": n_results})

        if err:
            st.error(f"API error: {err}")
        elif not data or not data.get("results"):
            render_iframe(
                '<div class="empty"><div class="empty-icon">🔍</div>'
                '<div class="empty-title">No matching entries found</div>'
                '<div>Try different words, or write more entries first.</div></div>',
                height=160,
            )
        else:
            results = data["results"]
            st.markdown(
                f'<p style="color:#8C7E6E;font-size:0.85rem;margin:0 0 1rem">'
                f'{len(results)} entries found for &#8220;{esc(query)}&#8221;</p>',
                unsafe_allow_html=True,
            )

            for r in results:
                meta        = r["metadata"]
                txt         = r["text"]
                emotions    = [x.strip() for x in meta.get("emotions", "").split(",") if x.strip()]
                distortions = [x.strip() for x in meta.get("distortions", "").split(",") if x.strip()]
                valence     = meta.get("valence", "neutral")
                intensity   = int(meta.get("intensity", 5))
                summary     = meta.get("summary", "")
                date_str    = fmt_date(meta.get("date", ""))
                similarity  = round((1 - r.get("distance", 0.5)) * 100)
                bg, fg      = valence_colors(valence)

                short_txt    = txt[:300] + ("…" if len(txt) > 300 else "")
                summary_html = (
                    f'<div class="summary">&#8220;{esc(summary)}&#8221;</div>'
                    if summary else ""
                )
                dist_html = (
                    f'<div style="margin-top:0.5rem">{make_chips(distortions, warn=True)}</div>'
                    if distortions else ""
                )

                card_body = f"""
                <div class="card">
                    <div style="display:flex;justify-content:space-between;
                                align-items:center;margin-bottom:0.5rem">
                        <div class="date">{esc(date_str)}</div>
                        <span style="font-size:0.74rem;color:#B8AFA5">{similarity}% match</span>
                    </div>
                    <div class="body-text">{esc(short_txt)}</div>
                    {summary_html}
                    <div class="chips">{make_chips(emotions)}</div>
                    {dist_html}
                    <div class="card-footer">
                        <span class="pill" style="background:{bg};color:{fg}">
                            {esc(valence.capitalize())}
                        </span>
                        <span class="intensity-lbl">Intensity {intensity}/10</span>
                        <div style="flex:1;max-width:110px">{make_bar(intensity * 10)}</div>
                    </div>
                </div>
                """
                h = 210 + (30 if summary else 0) + (28 if distortions else 0)
                render_iframe(card_body, height=h)
                st.markdown('<div style="margin-bottom:0.5rem"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PATTERNS
# ══════════════════════════════════════════════════════════════════════════════
elif _page == "patterns":
    st.markdown(
        '<div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #E0D8CC">'
        '<h1 style="font-family:\'DM Serif Display\',serif;font-size:2rem;margin:0 0 0.2rem">'
        'Your Patterns</h1>'
        '<p style="color:#8C7E6E;font-size:0.88rem;margin:0">'
        'Emotional trends across all your entries</p></div>',
        unsafe_allow_html=True,
    )

    data, err = cached_stats()

    if err:
        st.error(f"API error: {err}")
    elif not data or data.get("total_entries", 0) == 0:
        render_iframe(
            '<div class="empty"><div class="empty-icon">📊</div>'
            '<div class="empty-title">Not enough data yet</div>'
            '<div>Write a few entries to start seeing patterns.</div></div>',
            height=160,
        )
    else:
        valence_dist = data.get("valence_distribution", {})
        dominant     = max(valence_dist, key=valence_dist.get) if valence_dist else "neutral"
        dom_bg, dom_fg = valence_colors(dominant)

        render_iframe(
            f'<div class="metric-row">'
            f'<div class="metric-card">'
            f'<div class="metric-val">{data["total_entries"]}</div>'
            f'<div class="metric-lbl">Total entries</div></div>'
            f'<div class="metric-card">'
            f'<div class="metric-val">{data["avg_intensity"]}</div>'
            f'<div class="metric-lbl">Avg intensity /10</div></div>'
            f'<div class="metric-card">'
            f'<div class="metric-val" style="font-size:1.35rem;color:{dom_fg}">'
            f'{esc(dominant.capitalize())}</div>'
            f'<div class="metric-lbl">Dominant tone</div></div></div>',
            height=108,
        )

        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown(
                '<p style="font-family:\'DM Serif Display\',serif;font-size:1.3rem;'
                'margin:1rem 0 0.75rem">Most felt emotions</p>',
                unsafe_allow_html=True,
            )
            top_emotions = data.get("top_emotions", [])
            if top_emotions:
                max_c  = top_emotions[0][1] or 1
                bars   = "".join(
                    f'<div class="bar-row">'
                    f'<div class="bar-label"><span>{esc(em)}</span>'
                    f'<span class="bar-count">{c}×</span></div>'
                    f'{make_bar(int(c / max_c * 100), "#C4956A")}'
                    f'</div>'
                    for em, c in top_emotions
                )
                render_iframe(bars, height=42 * len(top_emotions) + 8)
            else:
                st.markdown('<p style="color:#B8AFA5">No data yet.</p>', unsafe_allow_html=True)

        with col_r:
            st.markdown(
                '<p style="font-family:\'DM Serif Display\',serif;font-size:1.3rem;'
                'margin:1rem 0 0.75rem">Cognitive patterns</p>',
                unsafe_allow_html=True,
            )
            top_dist = data.get("top_distortions", [])
            if top_dist:
                max_c = top_dist[0][1] or 1
                bars  = "".join(
                    f'<div class="bar-row">'
                    f'<div class="bar-label"><span>{esc(d)}</span>'
                    f'<span class="bar-count">{c}×</span></div>'
                    f'{make_bar(int(c / max_c * 100), "#E8A84E")}'
                    f'</div>'
                    for d, c in top_dist
                )
                render_iframe(bars, height=42 * len(top_dist) + 8)
            else:
                st.markdown(
                    '<p style="color:#8C7E6E;font-size:0.9rem">✓ No distortions detected yet.</p>',
                    unsafe_allow_html=True,
                )

        st.markdown(
            '<p style="font-family:\'DM Serif Display\',serif;font-size:1.3rem;'
            'margin:1.2rem 0 0.75rem">Emotional tone breakdown</p>',
            unsafe_allow_html=True,
        )
        total = sum(valence_dist.values()) or 1
        tiles = "".join(
            f'<div class="valence-tile" style="background:{valence_colors(v)[0]}">'
            f'<div class="valence-pct" style="color:{valence_colors(v)[1]}">'
            f'{round(c / total * 100)}%</div>'
            f'<div class="valence-lbl" style="color:{valence_colors(v)[1]}">{esc(v)}</div>'
            f'</div>'
            for v, c in valence_dist.items()
        )
        render_iframe(f'<div class="valence-grid">{tiles}</div>', height=100)


# ══════════════════════════════════════════════════════════════════════════════
# WEEKLY REPORT
# ══════════════════════════════════════════════════════════════════════════════
elif _page == "report":
    st.markdown(
        '<div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #E0D8CC">'
        '<h1 style="font-family:\'DM Serif Display\',serif;font-size:2rem;margin:0 0 0.2rem">'
        'Weekly Insight</h1>'
        '<p style="color:#8C7E6E;font-size:0.88rem;margin:0">'
        'Your AI coach reflects on the past 7 days</p></div>',
        unsafe_allow_html=True,
    )

    if st.button("Generate this week&#39;s report →", type="primary"):
        with st.spinner("Reflecting on your week…"):
            data, err = api_get("/report/weekly")

        if err:
            st.error(f"API error: {err}")
        else:
            trend       = data.get("intensity_trend", "stable")
            trend_label = {
                "improving": "📈 Improving",
                "worsening": "📉 Needs attention",
                "stable":    "➡️ Stable",
            }.get(trend, "➡️ Stable")

            body = f"""
            <div style="display:inline-block;font-size:0.8rem;padding:3px 13px;
                border-radius:20px;background:#EDE8E0;color:#5C5047;margin-bottom:1rem">
                Intensity trend: {esc(trend_label)}
            </div>

            <div class="report-card">
                <div class="lbl">This week&#39;s theme</div>
                <div class="report-text"
                     style="font-family:'DM Serif Display',serif;font-size:1.1rem;font-style:italic">
                    {esc(data.get('dominant_theme', ''))}
                </div>
            </div>

            <div class="report-card">
                <div class="lbl">Pattern to notice</div>
                <div class="report-text">{esc(data.get('pattern_to_notice', ''))}</div>
            </div>

            <div class="report-card" style="border-color:#D4EACB;background:#F4FAF2">
                <div class="lbl" style="color:#5A8C50">Suggestion for next week</div>
                <div class="report-text">{esc(data.get('suggestion', ''))}</div>
            </div>

            <div class="report-card" style="border-color:#E8D5C4;background:#FDF6F0">
                <div class="lbl" style="color:#A06040">Encouragement</div>
                <div class="report-text"
                     style="font-family:'DM Serif Display',serif;font-style:italic">
                    {esc(data.get('encouragement', ''))}
                </div>
            </div>
            """
            render_iframe(body, height=530)
    else:
        render_iframe(
            '<div class="empty"><div class="empty-icon">📋</div>'
            '<div class="empty-title">Ready when you are</div>'
            '<div>Best after journaling for at least 3–4 days.</div></div>',
            height=180,
        )