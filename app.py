import streamlit as st
import streamlit.components.v1 as components
import requests
import html as html_lib
from datetime import datetime

API_URL = "http://localhost:8000"

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MindMirror",
    page_icon="🪞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Shared fonts + body style (injected once) ──────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #FAF7F2; color: #2C2C2C; }
section[data-testid="stSidebar"] { background: #F0EBE1; border-right: 1px solid #E0D8CC; }
section[data-testid="stSidebar"] .block-container { padding-top: 2rem; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
h1, h2, h3 { font-family: 'DM Serif Display', serif; color: #1A1A1A; }
.sidebar-title { font-family: 'DM Serif Display', serif; font-size: 2rem; color: #1A1A1A; line-height: 1.1; margin-bottom: 0.2rem; }
.sidebar-subtitle { font-size: 0.8rem; color: #8C7E6E; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 2rem; }
div[data-testid="stSidebarContent"] .stButton > button { width: 100%; background: transparent; border: none; text-align: left; font-family: 'DM Sans', sans-serif; font-size: 0.95rem; color: #5C5047; padding: 0.6rem 1rem; border-radius: 8px; cursor: pointer; transition: background 0.15s; }
div[data-testid="stSidebarContent"] .stButton > button:hover { background: #E5DDD1; color: #1A1A1A; }
.main .block-container { padding: 2.5rem 3rem; max-width: 860px; }
textarea { font-family: 'DM Sans', sans-serif !important; font-size: 1.05rem !important; line-height: 1.8 !important; background: #FFFDF9 !important; border: 1.5px solid #DDD5C8 !important; border-radius: 12px !important; padding: 1.2rem !important; color: #2C2C2C !important; }
textarea:focus { border-color: #C4956A !important; box-shadow: 0 0 0 3px rgba(196,149,106,0.12) !important; }
textarea::placeholder { color: #B8AFA5 !important; }
.stButton > button[kind="primary"] { background: #2C2C2C !important; color: #FAF7F2 !important; border: none !important; border-radius: 8px !important; padding: 0.6rem 2rem !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important; font-weight: 500 !important; }
.stButton > button[kind="primary"]:hover { background: #1A1A1A !important; }
.stTextInput input { background: #FFFDF9 !important; border: 1.5px solid #DDD5C8 !important; border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important; color: #2C2C2C !important; }
.stTextInput input:focus { border-color: #C4956A !important; box-shadow: 0 0 0 3px rgba(196,149,106,0.12) !important; }
</style>
""", unsafe_allow_html=True)

# ── Shared CSS string injected into every components.html() call ───────────────
CARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'DM Sans', sans-serif; }
body { background: transparent; padding: 0; }
.card { background: #FFFDF9; border: 1px solid #E0D8CC; border-radius: 14px; padding: 1.4rem 1.6rem; margin-bottom: 2px; }
.date { font-size: 0.78rem; color: #B8AFA5; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.6rem; }
.entry-text { font-size: 0.95rem; color: #2C2C2C; line-height: 1.7; margin-bottom: 0.8rem; white-space: pre-wrap; word-break: break-word; }
.summary { font-family: 'DM Serif Display', serif; font-style: italic; font-size: 0.92rem; color: #8C7E6E; margin-bottom: 0.8rem; }
.chip { display: inline-block; font-size: 0.78rem; font-weight: 500; padding: 3px 10px; border-radius: 20px; margin: 2px 3px; background: #EDE8E0; color: #5C5047; }
.chip-warn { display: inline-block; font-size: 0.78rem; font-weight: 500; padding: 3px 10px; border-radius: 20px; margin: 2px 3px; background: #F5ECD7; color: #8B5E1A; }
.chips { margin-bottom: 0.7rem; }
.footer { display: flex; align-items: center; gap: 1rem; margin-top: 0.6rem; }
.valence-pill { font-size: 0.78rem; padding: 2px 10px; border-radius: 20px; font-weight: 500; }
.intensity { font-size: 0.78rem; color: #B8AFA5; }
.bar-wrap { background: #EDE8E0; border-radius: 99px; height: 5px; width: 100%; margin-top: 4px; }
.bar-fill { height: 5px; border-radius: 99px; background: linear-gradient(90deg, #9FC48A, #E8A84E, #D96B5A); }
.distortion-box { background: #FDF5E8; border: 1px solid #EDD5A3; border-radius: 10px; padding: 0.9rem 1.1rem; margin-top: 0.8rem; font-size: 0.87rem; color: #7A5220; line-height: 1.6; }
.insight-quote { font-family: 'DM Serif Display', serif; font-size: 1.1rem; font-style: italic; color: #3C3028; line-height: 1.6; border-left: 3px solid #C4956A; padding-left: 1rem; margin: 0.8rem 0; }
.section-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #B8AFA5; margin-bottom: 0.4rem; }
.report-card { background: #FFFDF9; border: 1px solid #E0D8CC; border-radius: 14px; padding: 1.4rem 1.6rem; margin-bottom: 0.8rem; }
.report-text { font-size: 1rem; color: #2C2C2C; line-height: 1.7; }
.metric-row { display: flex; gap: 1rem; margin-bottom: 1.2rem; }
.metric-card { flex: 1; background: #FFFDF9; border: 1px solid #E0D8CC; border-radius: 12px; padding: 1.1rem; text-align: center; }
.metric-val { font-family: 'DM Serif Display', serif; font-size: 2rem; color: #1A1A1A; }
.metric-lbl { font-size: 0.75rem; color: #8C7E6E; text-transform: uppercase; letter-spacing: 0.08em; }
.bar-row { margin-bottom: 0.8rem; }
.bar-label { display: flex; justify-content: space-between; font-size: 0.87rem; margin-bottom: 3px; }
.bar-count { color: #B8AFA5; }
.valence-grid { display: flex; gap: 0.8rem; }
.valence-tile { flex: 1; text-align: center; padding: 1rem 0.5rem; border-radius: 12px; }
.valence-pct { font-family: 'DM Serif Display', serif; font-size: 1.6rem; }
.valence-lbl { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; }
.empty { text-align: center; padding: 3rem 1rem; color: #B8AFA5; }
.empty-title { font-family: 'DM Serif Display', serif; font-size: 1.2rem; color: #8C7E6E; margin: 0.5rem 0; }
.match-pct { font-size: 0.75rem; color: #B8AFA5; }
.page-header { margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #E0D8CC; }
.page-header h1 { font-family: 'DM Serif Display', serif; font-size: 2rem; color: #1A1A1A; margin-bottom: 0.2rem; }
.page-header p { color: #8C7E6E; font-size: 0.88rem; margin: 0; }
</style>
"""

# ── Helpers ────────────────────────────────────────────────────────────────────

def e(text) -> str:
    """HTML-escape any value. Always call this before injecting into HTML."""
    return html_lib.escape(str(text))

def valence_colors(valence: str):
    colors = {
        "positive": ("#E3EDDE", "#3A6B30"),
        "negative": ("#F5E0E0", "#B04040"),
        "mixed":    ("#F5ECD7", "#8B5E1A"),
        "neutral":  ("#EDE8E0", "#5C5047"),
    }
    return colors.get(valence, ("#EDE8E0", "#5C5047"))

def chips_html(items: list, warn=False) -> str:
    cls = "chip-warn" if warn else "chip"
    return "".join(f'<span class="{cls}">{e(i)}</span>' for i in items if i)

def bar_html(pct: int, color: str = "#C4956A") -> str:
    return f'<div class="bar-wrap"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div>'

def fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%B %d, %Y · %H:%M")
    except:
        return iso[:10]

def render(html_body: str, height: int = 200):
    """Render HTML safely inside an iframe via components.html()."""
    components.html(f"<!DOCTYPE html><html><head>{CARD_CSS}</head><body>{html_body}</body></html>",
                    height=height, scrolling=False)

def api_get(path, params=None):
    try:
        r = requests.get(f"{API_URL}{path}", params=params, timeout=10)
        return r.json(), None
    except Exception as ex:
        return None, str(ex)

def api_post(path, body):
    try:
        r = requests.post(f"{API_URL}{path}", json=body, timeout=30)
        return r.json(), None
    except Exception as ex:
        return None, str(ex)

@st.cache_data(ttl=30, show_spinner=False)
def cached_stats():
    return api_get("/stats")

@st.cache_data(ttl=30, show_spinner=False)
def cached_entries(days=90):
    return api_get("/entries/recent", {"days": days})

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">Mind<br>Mirror</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Your private AI journal</div>', unsafe_allow_html=True)

    pages = {"✍️  Write": "write", "📖  My Journal": "journal",
             "🔍  Search": "search", "📊  Patterns": "patterns", "📋  Weekly Report": "report"}

    if "page" not in st.session_state:
        st.session_state.page = "write"

    for label, key in pages.items():
        if st.button(label, key=f"nav_{key}"):
            st.session_state.page = key

    st.markdown("---")
    stats_data, _ = cached_stats()
    if stats_data:
        st.markdown(f"""<div style="font-size:0.78rem;color:#8C7E6E;line-height:2">
            📝 {stats_data.get('total_entries',0)} entries<br>
            ⚡ Avg intensity: {stats_data.get('avg_intensity',0)}/10</div>""",
            unsafe_allow_html=True)

    st.markdown("""<div style="font-size:0.75rem;color:#B8AFA5;margin-top:2rem;padding-top:1rem;
        border-top:1px solid #E0D8CC;line-height:1.6">
        MindMirror is a self-reflection tool.<br>Not a substitute for professional mental health support.
        </div>""", unsafe_allow_html=True)

page = st.session_state.page

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: WRITE
# ══════════════════════════════════════════════════════════════════════════════
if page == "write":
    now = datetime.now().strftime("%A, %B %d")
    st.markdown(f"""<div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #E0D8CC">
        <h1 style="font-family:'DM Serif Display',serif;font-size:2rem;margin-bottom:0.2rem">Today&#39;s Entry</h1>
        <p style="color:#8C7E6E;font-size:0.88rem;margin:0">{e(now)}</p></div>""",
        unsafe_allow_html=True)

    text = st.text_area("entry_input", height=260,
        placeholder="What's on your mind today? Write freely — there's no right or wrong way to journal...",
        label_visibility="collapsed", key="journal_text")

    col_btn, col_hint = st.columns([1, 3])
    with col_btn:
        submit = st.button("Analyze & Save →", type="primary")
    with col_hint:
        st.markdown('<p style="color:#B8AFA5;font-size:0.82rem;padding-top:0.6rem">'
                    'Analyzed locally and stored privately.</p>', unsafe_allow_html=True)

    if submit:
        if len(text.strip()) < 10:
            st.warning("Write a little more — at least a sentence or two.")
        else:
            with st.spinner("Reflecting on your words..."):
                result, err = api_post("/entry", {"text": text})
            if err:
                st.error(f"Could not reach the API. Is `uvicorn api.main:app --reload` running?\n\n{err}")
            else:
                a = result["analysis"]
                emotions    = a.get("emotions", [])
                distortions = a.get("distortions", [])
                intensity   = int(a.get("intensity", 5))
                valence     = a.get("valence", "neutral")
                summary     = a.get("summary", "")
                bg, fg      = valence_colors(valence)

                dist_block = ""
                if distortions:
                    dist_block = f"""<div class="distortion-box">
                        <strong>Thinking patterns noticed:</strong> {chips_html(distortions, warn=True)}<br>
                        <span style="font-size:0.82rem;opacity:0.8">Common cognitive patterns worth gently reflecting on — not diagnoses.</span>
                    </div>"""

                html_body = f"""
                <div class="card">
                    <div class="section-label">What I noticed</div>
                    <div class="insight-quote">{e(summary)}</div>
                    <div class="chips">{chips_html(emotions)}</div>
                    <div style="display:flex;gap:1rem;align-items:center;margin-top:0.6rem">
                        <div style="flex:1">
                            <div class="section-label">Tone</div>
                            <span class="valence-pill" style="background:{bg};color:{fg};margin-top:4px;display:inline-block">
                                {e(valence.capitalize())}
                            </span>
                        </div>
                        <div style="flex:2">
                            <div class="section-label">Intensity · {intensity}/10</div>
                            {bar_html(intensity * 10)}
                        </div>
                    </div>
                    {dist_block}
                </div>"""

                h = 220 + (80 if distortions else 0)
                render(html_body, height=h)

                cached_stats.clear()
                cached_entries.clear()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MY JOURNAL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "journal":
    st.markdown("""<div class="page-header" style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #E0D8CC">
        <h1 style="font-family:'DM Serif Display',serif;font-size:2rem;margin-bottom:0.2rem">My Journal</h1>
        <p style="color:#8C7E6E;font-size:0.88rem;margin:0">All your entries with their emotional analysis</p>
    </div>""", unsafe_allow_html=True)

    data, err = cached_entries(90)
    if err:
        st.error(f"Could not reach API: {err}")
    elif not data or not data.get("entries"):
        render('<div class="empty"><div style="font-size:3rem">🪞</div>'
               '<div class="empty-title">Your journal is empty</div>'
               '<div>Write your first entry to get started.</div></div>', height=180)
    else:
        entries = data["entries"]
        st.markdown(f'<p style="color:#8C7E6E;font-size:0.85rem;margin-bottom:1rem">{len(entries)} entries</p>',
                    unsafe_allow_html=True)

        for entry in entries:
            meta        = entry["metadata"]
            text_body   = entry["text"]
            emotions    = [x.strip() for x in meta.get("emotions","").split(",") if x.strip()]
            distortions = [x.strip() for x in meta.get("distortions","").split(",") if x.strip()]
            valence     = meta.get("valence","neutral")
            intensity   = int(meta.get("intensity", 5))
            summary     = meta.get("summary","")
            date_str    = fmt_date(meta.get("date",""))
            bg, fg      = valence_colors(valence)

            short        = len(text_body) > 300
            display_text = text_body[:300] + ("…" if short else "")

            summary_block = f'<div class="summary">&#8220;{e(summary)}&#8221;</div>' if summary else ""
            dist_block    = f'<div style="margin-top:0.4rem">{chips_html(distortions,warn=True)}</div>' if distortions else ""

            html_body = f"""
            <div class="card">
                <div class="date">{e(date_str)}</div>
                <div class="entry-text">{e(display_text)}</div>
                {summary_block}
                <div class="chips">{chips_html(emotions)}</div>
                {dist_block}
                <div class="footer">
                    <span class="valence-pill" style="background:{bg};color:{fg}">{e(valence.capitalize())}</span>
                    <span class="intensity">Intensity {intensity}/10</span>
                    <div style="flex:1;max-width:120px">{bar_html(intensity*10)}</div>
                </div>
            </div>"""

            h = 200 + (30 if summary else 0) + (25 if distortions else 0) + (50 if short else 0)
            render(html_body, height=h)

            if short:
                with st.expander("Read full entry"):
                    st.write(text_body)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SEARCH
# ══════════════════════════════════════════════════════════════════════════════
elif page == "search":
    st.markdown("""<div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #E0D8CC">
        <h1 style="font-family:'DM Serif Display',serif;font-size:2rem;margin-bottom:0.2rem">Search</h1>
        <p style="color:#8C7E6E;font-size:0.88rem;margin:0">Describe a feeling — not just a keyword</p>
    </div>""", unsafe_allow_html=True)

    query = st.text_input("search_q", label_visibility="collapsed",
        placeholder="e.g.  times I felt overwhelmed at work  ·  entries where I was hard on myself")

    col1, col2 = st.columns([1, 4])
    with col1:
        search_btn = st.button("Search →", type="primary")
    with col2:
        n = st.select_slider("Results", options=[3, 5, 10], value=5, label_visibility="collapsed")

    if search_btn and query:
        with st.spinner("Searching your journal..."):
            data, err = api_get("/search", {"q": query, "n": n})
        if err:
            st.error(f"API error: {err}")
        elif not data or not data.get("results"):
            render('<div class="empty"><div style="font-size:2rem">🔍</div>'
                   '<div class="empty-title">No matching entries found</div>'
                   '<div>Try different words, or write more entries first.</div></div>', height=160)
        else:
            results = data["results"]
            st.markdown(f'<p style="color:#8C7E6E;font-size:0.85rem;margin-bottom:1rem">'
                        f'{len(results)} entries found for &#8220;{e(query)}&#8221;</p>',
                        unsafe_allow_html=True)

            for r in results:
                meta        = r["metadata"]
                txt         = r["text"]
                emotions    = [x.strip() for x in meta.get("emotions","").split(",") if x.strip()]
                distortions = [x.strip() for x in meta.get("distortions","").split(",") if x.strip()]
                valence     = meta.get("valence","neutral")
                intensity   = int(meta.get("intensity",5))
                summary     = meta.get("summary","")
                date_str    = fmt_date(meta.get("date",""))
                similarity  = round((1 - r.get("distance", 0.5)) * 100)
                bg, fg      = valence_colors(valence)

                short_txt    = txt[:300] + ("…" if len(txt) > 300 else "")
                summary_html = f'<div class="summary">&#8220;{e(summary)}&#8221;</div>' if summary else ""
                dist_html    = f'<div style="margin-top:0.4rem">{chips_html(distortions,warn=True)}</div>' if distortions else ""

                html_body = f"""
                <div class="card">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem">
                        <div class="date">{e(date_str)}</div>
                        <span class="match-pct">{similarity}% match</span>
                    </div>
                    <div class="entry-text">{e(short_txt)}</div>
                    {summary_html}
                    <div class="chips">{chips_html(emotions)}</div>
                    {dist_html}
                    <div class="footer">
                        <span class="valence-pill" style="background:{bg};color:{fg}">{e(valence.capitalize())}</span>
                        <span class="intensity">Intensity {intensity}/10</span>
                        <div style="flex:1;max-width:120px">{bar_html(intensity*10)}</div>
                    </div>
                </div>"""

                h = 200 + (30 if summary else 0) + (25 if distortions else 0)
                render(html_body, height=h)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PATTERNS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "patterns":
    st.markdown("""<div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #E0D8CC">
        <h1 style="font-family:'DM Serif Display',serif;font-size:2rem;margin-bottom:0.2rem">Your Patterns</h1>
        <p style="color:#8C7E6E;font-size:0.88rem;margin:0">Emotional trends across all your entries</p>
    </div>""", unsafe_allow_html=True)

    data, err = cached_stats()
    if err:
        st.error(f"API error: {err}")
    elif not data or data.get("total_entries", 0) == 0:
        render('<div class="empty"><div style="font-size:2rem">📊</div>'
               '<div class="empty-title">Not enough data yet</div>'
               '<div>Write a few entries to start seeing patterns.</div></div>', height=160)
    else:
        # Metric row
        valence_dist = data.get("valence_distribution", {})
        dominant = max(valence_dist, key=valence_dist.get) if valence_dist else "neutral"
        dom_bg, dom_fg = valence_colors(dominant)

        render(f"""<div class="metric-row">
            <div class="metric-card">
                <div class="metric-val">{data['total_entries']}</div>
                <div class="metric-lbl">Total entries</div>
            </div>
            <div class="metric-card">
                <div class="metric-val">{data['avg_intensity']}</div>
                <div class="metric-lbl">Avg intensity /10</div>
            </div>
            <div class="metric-card">
                <div class="metric-val" style="font-size:1.4rem;color:{dom_fg}">{e(dominant.capitalize())}</div>
                <div class="metric-lbl">Dominant tone</div>
            </div>
        </div>""", height=110)

        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown("### Most felt emotions")
            top_emotions = data.get("top_emotions", [])
            if top_emotions:
                max_c = top_emotions[0][1] or 1
                bars = "".join(f"""<div class="bar-row">
                    <div class="bar-label"><span>{e(em)}</span><span class="bar-count">{c}×</span></div>
                    {bar_html(int(c/max_c*100), "#C4956A")}
                </div>""" for em, c in top_emotions)
                render(bars, height=40 * len(top_emotions) + 10)
            else:
                st.markdown('<p style="color:#B8AFA5">No data yet</p>', unsafe_allow_html=True)

        with col_r:
            st.markdown("### Cognitive patterns")
            top_dist = data.get("top_distortions", [])
            if top_dist:
                max_c = top_dist[0][1] or 1
                bars = "".join(f"""<div class="bar-row">
                    <div class="bar-label"><span>{e(d)}</span><span class="bar-count">{c}×</span></div>
                    {bar_html(int(c/max_c*100), "#E8A84E")}
                </div>""" for d, c in top_dist)
                render(bars, height=40 * len(top_dist) + 10)
            else:
                st.markdown('<p style="color:#8C7E6E;font-size:0.9rem">✓ No distortions detected yet</p>',
                            unsafe_allow_html=True)

        st.markdown("### Emotional tone breakdown")
        total = sum(valence_dist.values()) or 1
        tiles = "".join(f"""<div class="valence-tile" style="background:{valence_colors(v)[0]}">
            <div class="valence-pct" style="color:{valence_colors(v)[1]}">{round(c/total*100)}%</div>
            <div class="valence-lbl" style="color:{valence_colors(v)[1]}">{e(v)}</div>
        </div>""" for v, c in valence_dist.items())
        render(f'<div class="valence-grid">{tiles}</div>', height=100)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: WEEKLY REPORT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "report":
    st.markdown("""<div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #E0D8CC">
        <h1 style="font-family:'DM Serif Display',serif;font-size:2rem;margin-bottom:0.2rem">Weekly Insight</h1>
        <p style="color:#8C7E6E;font-size:0.88rem;margin:0">Your AI coach reflects on the past 7 days</p>
    </div>""", unsafe_allow_html=True)

    if st.button("Generate this week's report →", type="primary"):
        with st.spinner("Reflecting on your week..."):
            data, err = api_get("/report/weekly")
        if err:
            st.error(f"API error: {err}")
        else:
            trend = data.get("intensity_trend", "stable")
            trend_label = {"improving": "📈 Improving", "worsening": "📉 Needs attention",
                           "stable": "➡️ Stable"}.get(trend, "➡️ Stable")

            html_body = f"""
            <div style="display:inline-block;font-size:0.8rem;padding:4px 14px;border-radius:20px;
                background:#EDE8E0;color:#5C5047;margin-bottom:1.2rem">
                Intensity trend: {e(trend_label)}
            </div>
            <div class="report-card">
                <div class="section-label">This week&#39;s theme</div>
                <div class="report-text" style="font-family:'DM Serif Display',serif;font-size:1.15rem;font-style:italic">
                    {e(data.get('dominant_theme',''))}
                </div>
            </div>
            <div class="report-card">
                <div class="section-label">Pattern to notice</div>
                <div class="report-text">{e(data.get('pattern_to_notice',''))}</div>
            </div>
            <div class="report-card" style="border-color:#D4EACB;background:#F4FAF2">
                <div class="section-label" style="color:#5A8C50">Suggestion for next week</div>
                <div class="report-text">{e(data.get('suggestion',''))}</div>
            </div>
            <div class="report-card" style="border-color:#E8D5C4;background:#FDF6F0">
                <div class="section-label" style="color:#A06040">Encouragement</div>
                <div class="report-text" style="font-family:'DM Serif Display',serif;font-style:italic">
                    {e(data.get('encouragement',''))}
                </div>
            </div>"""

            render(html_body, height=520)
    else:
        render("""<div class="empty" style="padding:2.5rem 1rem">
            <div style="font-size:2.5rem">📋</div>
            <div class="empty-title">Ready when you are</div>
            <div>Best after journaling for at least 3–4 days.</div>
        </div>""", height=180)