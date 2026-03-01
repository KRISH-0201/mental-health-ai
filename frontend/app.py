import streamlit as st
import requests
import plotly.graph_objects as go
import os

BACKEND_URL = os.getenv("BACKEND_URL", "https://mental-health-ai-production-e9e7.up.railway.app")

st.set_page_config(
    page_title="Mental Health AI Chatbot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================
# SESSION STATE INIT
# =============================
for key, val in {
    "token": None,
    "username": None,
    "messages": [],
    "burnout_score": 5,
    "streak": 2,
    "dominant_emotion": "Calm",
    "emotion_percent": 72,
    "weekly_data": [65, 70, 58, 80, 72, 85, 78],
    "theme": "light",
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def fetch_weekly_data():
    """Fetch real per-day average intensity for last 7 days from backend."""
    try:
        r = requests.get(f"{BACKEND_URL}/weekly-wellness", headers=auth_headers(), timeout=4)
        if r.status_code == 200:
            raw = r.json()          # [{"day":"Mon","value":42.0}, ...]
            # Fill None (no data that day) with previous day's value or 50
            values = []
            last = 50
            for item in raw:
                v = item.get("value")
                if v is None:
                    values.append(last)
                else:
                    last = int(v)
                    values.append(last)
            return values
    except Exception:
        pass
    return st.session_state.weekly_data   # fallback: keep current

is_dark = st.session_state.theme == "dark"

# ==============================
# THEME TOKENS
# ==============================
T = {
    "bg_base":      "#0d0b1a"        if is_dark else "#f0eeff",
    "sidebar_bg":   "#100d24"        if is_dark else "#ffffff",
    "glass":        "rgba(255,255,255,0.07)"  if is_dark else "rgba(255,255,255,0.82)",
    "glass_border": "rgba(255,255,255,0.13)"  if is_dark else "rgba(139,92,246,0.18)",
    "glass_hover":  "rgba(255,255,255,0.11)"  if is_dark else "rgba(255,255,255,0.96)",
    "text_primary":   "#f1f0fe" if is_dark else "#1e1340",
    "text_secondary": "#a89ed4" if is_dark else "#5b4b8a",
    "text_muted":     "#6b5f8c" if is_dark else "#9580c4",
    "input_bg":     "rgba(255,255,255,0.07)" if is_dark else "#ffffff",
    "input_border": "rgba(255,255,255,0.13)" if is_dark else "rgba(139,92,246,0.28)",
    "mesh1":        "rgba(139,92,246,0.18)"  if is_dark else "rgba(167,139,250,0.20)",
    "mesh2":        "rgba(99,102,241,0.15)"  if is_dark else "rgba(196,181,253,0.28)",
    "mesh3":        "rgba(147,197,253,0.08)" if is_dark else "rgba(224,231,255,0.48)",
    "grid_color":   "rgba(255,255,255,0.05)" if is_dark else "rgba(139,92,246,0.08)",
    "tick_color":   "#6b5f8c" if is_dark else "#9c87c2",
    "emotion_card": ("linear-gradient(135deg,rgba(109,40,217,0.38) 0%,rgba(99,102,241,0.28) 100%)"
                     if is_dark else
                     "linear-gradient(135deg,rgba(167,139,250,0.3) 0%,rgba(196,181,253,0.24) 100%)"),
    "streak_bg":    ("linear-gradient(135deg,rgba(110,231,183,0.13) 0%,rgba(96,165,250,0.13) 100%)"
                     if is_dark else
                     "linear-gradient(135deg,rgba(110,231,183,0.22) 0%,rgba(147,197,253,0.2) 100%)"),
    "chip_bg":      "rgba(196,181,253,0.08)" if is_dark else "rgba(196,181,253,0.15)",
    "chip_border":  "rgba(196,181,253,0.2)"  if is_dark else "rgba(139,92,246,0.28)",
    "chip_color":   "#c4b5fd" if is_dark else "#6d28d9",
    "burnout_card": "rgba(255,255,255,0.05)" if is_dark else "rgba(255,255,255,0.88)",
    "emo_tag_bg":   "rgba(255,255,255,0.05)" if is_dark else "rgba(196,181,253,0.14)",
    "header_bg":    "#1a1040"                if is_dark else "#5b3fd4",
    "bubble_ai_bg": "rgba(255,255,255,0.08)" if is_dark else "#ffffff",
}

# ==============================
# GLOBAL CSS
# ==============================
st.markdown(f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap" rel="stylesheet">

<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, .stApp {{
    font-family: 'DM Sans', sans-serif !important;
    background: {T['bg_base']} !important;
    color: {T['text_primary']} !important;
    min-height: 100vh;
}}

/* ── Styled top header bar ── */
header[data-testid="stHeader"] {{
    background: {T['header_bg']} !important;
    border-bottom: 1px solid rgba(255,255,255,0.1) !important;
    height: 48px !important;
}}

/* Push main content below the styled header */
.block-container {{
    padding: 4.5rem 2.25rem 3rem !important;
    max-width: 1440px !important;
    margin-top: 0 !important;
}}

/* Mesh background */
.stApp::before {{
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 15%  10%, {T['mesh1']} 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 85%  85%, {T['mesh2']} 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 55%  45%, {T['mesh3']} 0%, transparent 60%);
    pointer-events: none; z-index: 0;
}}

/* Sidebar */
div[data-testid="stSidebar"] {{
    background: {T['sidebar_bg']} !important;
    border-right: 1px solid {T['glass_border']} !important;
}}
div[data-testid="stSidebar"] > div:first-child {{ padding-top: 1.5rem; }}

/* Hide default chrome */
#MainMenu, footer, .stDeployButton {{ visibility:hidden; display:none; }}

/* Scrollbar */
::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {T['text_muted']}; border-radius: 8px; }}

/* ─ Glass Card ─ */
.glass-card {{
    background: {T['glass']};
    backdrop-filter: blur(22px) saturate(160%);
    -webkit-backdrop-filter: blur(22px) saturate(160%);
    border: 1px solid {T['glass_border']};
    border-radius: 22px;
    padding: 1.4rem;
    transition: all 0.28s ease;
}}
.glass-card:hover {{
    background: {T['glass_hover']};
    border-color: rgba(196,181,253,0.38);
    box-shadow: 0 8px 32px rgba(139,92,246,0.16);
}}

/* ─ Sidebar user block ─ */
.sidebar-user {{
    display:flex; align-items:center; gap:0.75rem;
    padding: 1rem 1.2rem;
    background: {T['glass']};
    border: 1px solid {T['glass_border']};
    border-radius: 18px; margin-bottom: 1.25rem;
    backdrop-filter: blur(12px);
}}
.avatar {{
    width:40px; height:40px; border-radius:50%;
    background: linear-gradient(135deg,#7c3aed,#6366f1);
    display:flex; align-items:center; justify-content:center;
    font-size:1rem; font-weight:700; color:white; flex-shrink:0;
    box-shadow: 0 0 14px rgba(139,92,246,0.5);
}}
.user-name  {{ font-size:0.9rem; font-weight:600; color:{T['text_primary']}; }}
.user-status {{ font-size:0.7rem; color:#6ee7b7; display:flex; align-items:center; gap:0.3rem; margin-top:2px; }}
.status-dot  {{ width:6px; height:6px; background:#6ee7b7; border-radius:50%; box-shadow:0 0 6px #6ee7b7; }}

.s-label {{
    font-size:0.63rem; font-weight:700; letter-spacing:0.12em;
    text-transform:uppercase; color:{T['text_muted']};
    margin: 1rem 0 0.45rem;
}}

/* ─ Emotion card ─ */
.emotion-card {{
    background: {T['emotion_card']};
    backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(196,181,253,0.28);
    border-radius: 20px; padding: 1.4rem;
    position:relative; overflow:hidden;
}}
.emotion-card::after {{
    content:''; position:absolute; top:-40px; right:-40px;
    width:130px; height:130px;
    background:radial-gradient(circle,rgba(196,181,253,0.16) 0%,transparent 70%);
    border-radius:50%; pointer-events:none;
}}
.emo-label  {{ font-size:0.63rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:#c4b5fd; margin-bottom:0.4rem; }}
.emo-value  {{ font-family:'DM Serif Display',serif; font-size:2.1rem; color:{T['text_primary']}; line-height:1; margin-bottom:0.7rem; }}
.emo-pct    {{ font-family:Consolas,monospace; font-size:0.85rem; font-weight:700; color:#c4b5fd; }}
.prog-track {{ width:100%; height:5px; background:rgba(255,255,255,0.12); border-radius:99px; overflow:hidden; margin-top:0.6rem; }}
.prog-fill  {{ height:100%; border-radius:99px; background:linear-gradient(90deg,#7c3aed,#c4b5fd); box-shadow:0 0 10px rgba(139,92,246,0.45); }}

/* ─ Streak card ─ */
.streak-card {{
    background: {T['streak_bg']};
    border: 1px solid rgba(110,231,183,0.25);
    border-radius: 16px; padding:1rem; text-align:center;
}}
.streak-num {{ font-family:Consolas,monospace; font-size:2.1rem; font-weight:700; color:#6ee7b7; line-height:1; }}
.streak-sub {{ font-size:0.67rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:{T['text_muted']}; margin-top:0.3rem; }}

/* ─ Burnout mini card ─ */
.burnout-mini {{
    background: {T['burnout_card']};
    border: 1px solid {T['glass_border']};
    border-radius: 16px; padding:1rem; text-align:center;
    backdrop-filter:blur(12px);
}}

.hdivider {{ height:1px; background:linear-gradient(90deg,transparent,{T['glass_border']},transparent); margin:0.9rem 0; }}

/* ─ Page title ─ */
.page-title {{
    font-family: 'DM Serif Display', serif;
    font-size: 1.95rem;
    background: linear-gradient(135deg, {T['text_primary']} 40%, #c4b5fd 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    line-height:1.15; margin-bottom:0.15rem;
}}
.page-sub {{ color:{T['text_muted']}; font-size:0.82rem; margin-bottom:1.4rem; }}

/* ─ Section header ─ */
.sec-hdr {{ display:flex; align-items:center; gap:0.5rem; margin-bottom:0.8rem; }}
.sec-dot {{ width:7px; height:7px; border-radius:50%; background:#8b5cf6; box-shadow:0 0 8px #8b5cf6; }}
.sec-title {{ font-family:'DM Serif Display',serif; font-size:1.1rem; color:{T['text_primary']}; }}

/* ─ Chat messages ─ */
.msg-row-user {{ display:flex; justify-content:flex-end; margin-bottom:0.65rem; }}
.msg-row-ai   {{ display:flex; justify-content:flex-start; margin-bottom:0.65rem; }}
.bubble-user {{
    max-width:74%; background:linear-gradient(135deg,#7c3aed 0%,#6366f1 100%);
    color:white; padding:0.78rem 1rem;
    border-radius:18px 18px 4px 18px;
    font-size:0.875rem; line-height:1.55;
    box-shadow:0 4px 14px rgba(124,58,237,0.32);
    word-break:break-word;
}}
.bubble-ai {{
    max-width:74%;
    background: {T['bubble_ai_bg']};
    backdrop-filter:blur(12px);
    border:1px solid {T['glass_border']};
    color:{T['text_primary']};
    padding:0.78rem 1rem;
    border-radius:18px 18px 18px 4px;
    font-size:0.875rem; line-height:1.55;
    box-shadow:0 4px 16px rgba(0,0,0,0.08);
    word-break:break-word;
}}
.bubble-ai-name {{ font-size:0.63rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:#c4b5fd; margin-bottom:0.3rem; }}

.chat-empty {{
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    padding: 3rem 1rem;
    gap:0.55rem;
    opacity:0.45; color:{T['text_muted']}; font-size:0.83rem; text-align:center;
}}

/* ─ Quick chips ─ */
.chips-row {{ display:flex; flex-wrap:wrap; gap:0.42rem; margin:0.65rem 0 0.25rem; }}
.chip {{
    background:{T['chip_bg']}; border:1px solid {T['chip_border']};
    border-radius:99px; padding:0.38rem 0.82rem;
    font-size:0.75rem; font-weight:500; color:{T['chip_color']};
    white-space:nowrap;
}}

/* ─ Emotion tags ─ */
.emo-tag {{
    display:inline-flex; align-items:center; gap:0.3rem;
    background:{T['emo_tag_bg']}; border:1px solid {T['glass_border']};
    border-radius:99px; padding:0.27rem 0.62rem;
    font-size:0.73rem; color:{T['text_secondary']}; margin:0.2rem;
}}

/* ─ Text inputs ─ */
.stTextInput input {{
    background: {T['input_bg']} !important;
    border: 1px solid {T['input_border']} !important;
    border-radius: 12px !important;
    color: {T['text_primary']} !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    transition: all 0.25s ease !important;
}}
.stTextInput input:focus {{
    border-color: rgba(139,92,246,0.6) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.12) !important;
    outline: none !important;
}}
.stTextInput label {{
    color: {T['text_secondary']} !important;
    font-size: 0.78rem !important; font-weight: 500 !important;
    font-family: 'DM Sans', sans-serif !important;
}}

/* ─ All Buttons ─ */
.stButton > button {{
    background: linear-gradient(135deg,#7c3aed 0%,#6366f1 100%) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important; font-size: 0.875rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 14px rgba(139,92,246,0.3) !important;
}}
.stButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(139,92,246,0.44) !important;
}}

/* ─ Theme toggle button (top-right) ─ */
.theme-toggle-wrap {{
    display: flex;
    justify-content: flex-end;
    padding-top: 0.6rem;
}}

/* Sidebar sign-out button */
div[data-testid="stSidebar"] .stButton > button {{
    background: {T['glass']} !important;
    border: 1px solid {T['glass_border']} !important;
    color: {T['text_secondary']} !important;
    box-shadow: none !important;
    font-size: 0.8rem !important;
}}
div[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(239,68,68,0.1) !important;
    border-color: rgba(239,68,68,0.35) !important;
    color: #fca5a5 !important;
    transform: none !important;
}}

/* ─ Radio buttons — clean pill tab style ─ */
div[data-testid="stRadio"] > label,
div[data-testid="stRadio"] > div:first-child:not([role="radiogroup"]) {{
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}}
div[data-testid="stRadio"] {{
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}
div[role="radiogroup"] {{
    display: flex !important;
    flex-direction: row !important;
    align-items: stretch !important;
    gap: 0.25rem !important;
    background: {T['glass']} !important;
    border: 1px solid {T['glass_border']} !important;
    border-radius: 14px !important;
    padding: 0.25rem !important;
    backdrop-filter: blur(12px) !important;
    width: 100% !important;
}}
div[role="radiogroup"] label {{
    flex: 1 !important;
    border-radius: 10px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 38px !important;
    cursor: pointer !important;
    margin: 0 !important;
    padding: 0 0.5rem !important;
    position: relative !important;
    transition: background 0.2s ease !important;
}}
/* Selected tab highlight */
div[role="radiogroup"] label[data-checked="true"],
div[role="radiogroup"] label:has(input:checked) {{
    background: linear-gradient(135deg,#7c3aed,#6366f1) !important;
    box-shadow: 0 2px 8px rgba(124,58,237,0.35) !important;
}}
div[role="radiogroup"] label[data-checked="true"] p,
div[role="radiogroup"] label:has(input:checked) p {{
    color: #ffffff !important;
    font-weight: 600 !important;
}}
/* Hide ALL circle dot indicators — both the outer ring and inner fill */
div[role="radiogroup"] label > div:first-child,
div[role="radiogroup"] label > div:first-child > *,
div[role="radiogroup"] label input[type="radio"],
div[role="radiogroup"] label svg,
div[role="radiogroup"] label span:empty {{
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    visibility: hidden !important;
    position: absolute !important;
}}
/* Make second div (the text container) fill full width */
div[role="radiogroup"] label > div:last-child {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
}}
div[role="radiogroup"] label p {{
    color: {T['text_secondary']} !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-align: center !important;
    padding: 0 !important;
    margin: 0 !important;
    white-space: nowrap !important;
    line-height: 1 !important;
    display: block !important;
}}

/* ─ Chat input — white like text boxes ─ */
div[data-testid="stChatInput"],
div[data-testid="stChatInput"] > div,
div[data-testid="stChatInput"] > div > div,
div[data-testid="stChatInput"] [data-baseweb="textarea"],
div[data-testid="stChatInput"] [data-baseweb="base-input"] {{
    background: {T['input_bg']} !important;
    border: 1px solid {T['input_border']} !important;
    border-radius: 14px !important;
    box-shadow: none !important;
    padding: 0 !important;
}}
div[data-testid="stChatInput"] textarea,
div[data-testid="stChatInput"] textarea:focus {{
    color: {T['text_primary']} !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.875rem !important;
    background: {T['input_bg']} !important;
    outline: none !important;
    box-shadow: none !important;
    caret-color: {'#f1f0fe' if is_dark else '#1e1340'} !important;
}}
div[data-testid="stChatInput"] textarea::placeholder {{
    color: {T['text_muted']} !important;
}}

/* ─ Text input caret color (cursor) ─ */
.stTextInput input {{
    caret-color: {'#f1f0fe' if is_dark else '#1e1340'} !important;
}}
div[data-testid="stChatInput"] button {{
    background: linear-gradient(135deg,#7c3aed,#6366f1) !important;
    border-radius: 8px !important;
    border: none !important;
}}

/* ─ Auth card — style middle column's stVerticalBlock directly ─ */
/* Hide ghost element container Streamlit injects before radio widget */
.auth-card .stElementContainer:first-child:not(:has([data-testid="stRadio"])) {{
    display: none !important;
    height: 0 !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
}}
/* Catch-all: any empty div inside auth area */
div[data-testid="stVerticalBlock"] > div:empty {{
    display: none !important;
}}

/* ─ Auth form card — targeted via JS-injected class ─ */
.auth-form-area {{
    background: {T['glass']} !important;
    backdrop-filter: blur(24px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(160%) !important;
    border: 1px solid {T['glass_border']} !important;
    border-radius: 24px !important;
    padding: 1.75rem !important;
    box-shadow: 0 20px 60px rgba(139,92,246,0.12) !important;
}}

/* Hide any stElementContainer that wraps a single empty/invisible element */
div[data-testid="stElementContainer"]:has(> div:empty),
div[data-testid="stElementContainer"]:has(> p:empty),
div[data-testid="stElementContainer"]:has(> span:empty),
div[data-testid="stElementContainer"]:has(.auth-form-start) {{
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}}
.auth-logo {{
    font-family: 'DM Serif Display', serif; font-size: 2.4rem;
    background: {'linear-gradient(135deg,#c4b5fd 0%,#93c5fd 100%)' if is_dark else 'linear-gradient(135deg,#5b21b6 0%,#4338ca 100%)'};
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    text-align:center; line-height:1.15;
}}
.auth-tagline {{
    color: {'#a89ed4' if is_dark else '#4c3a8a'}; font-size: 0.92rem; font-weight: 500;
    text-align: center; letter-spacing: 0.02em; margin: 0.5rem 0 2rem;
}}

@keyframes fadeUp {{
    from {{ opacity:0; transform:translateY(10px); }}
    to   {{ opacity:1; transform:translateY(0); }}
}}
.glass-card, .emotion-card, .streak-card, .auth-card {{
    animation: fadeUp 0.38s ease both;
}}
</style>
""", unsafe_allow_html=True)


# ==============================
# AUTH PAGE
# ==============================
if not st.session_state.token:

    # Theme toggle — inside header area, top right
    th_col1, th_col2 = st.columns([14, 1])
    with th_col2:
        st.markdown('<div class="theme-toggle-wrap">', unsafe_allow_html=True)
        tog_icon = "☀️" if is_dark else "🌙"
        if st.button(tog_icon, key="theme_btn_auth"):
            st.session_state.theme = "light" if is_dark else "dark"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Auth layout — logo above, form below styled via CSS on column
    a1, a2, a3 = st.columns([1, 1.35, 1])
    with a2:
        # Logo & tagline
        st.markdown(f"""
        <div style="text-align:center; padding: 2rem 0 1.75rem;">
            <div class="auth-logo">Mental Health AI Chatbot</div>
            <div class="auth-tagline">Your private space to feel, reflect, and grow.</div>
        </div>
        """, unsafe_allow_html=True)

        # Invisible marker — JS finds this and adds 'auth-form-area' class to the parent stVerticalBlock
        st.markdown("""
        <script>
        (function() {
            var markers = window.parent.document.querySelectorAll('.auth-form-start');
            markers.forEach(function(m) {
                var block = m.closest('[data-testid="stVerticalBlock"]');
                if (block) block.classList.add('auth-form-area');
            });
        })();
        </script>
        <span class="auth-form-start" style="display:none"></span>
        """, unsafe_allow_html=True)
        mode = st.radio(
            "Mode", ["Login", "Sign Up"],
            horizontal=True,
            label_visibility="collapsed",
            key="auth_mode"
        )

        username = st.text_input("Username", placeholder="your username", key="auth_user")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="auth_pass")

        btn_label = "Continue →" if mode == "Login" else "Create Account →"
        if st.button(btn_label, use_container_width=True, key="auth_submit"):
            endpoint = "/login" if mode == "Login" else "/signup"
            try:
                res = requests.post(
                    BACKEND_URL + endpoint,
                    json={"username": username, "password": password}
                )
                if res.status_code == 200:
                    data = res.json()
                    if mode == "Login":
                        # Login response contains access_token
                        st.session_state.token    = data["access_token"]
                        st.session_state.username = username
                        st.success("Welcome ♡")
                        st.rerun()
                    else:
                        # Signup response is {"message": "User registered successfully"}
                        # — there is NO access_token, redirect user to login
                        st.success("Account created! Please log in. ♡")
                        st.session_state["auth_mode"] = "Login"
                        st.rerun()
                else:
                    detail = res.json().get("detail", "Authentication failed — please check your credentials.")
                    st.error(detail)
            except Exception:
                st.error("Cannot connect to server. Make sure the backend is running.")


# ==============================
# MAIN APP
# ==============================
else:
    # ── Header row: title + theme toggle ──────────────────
    h1, h2 = st.columns([12, 1])
    with h1:
        name = st.session_state.username or "there"
        st.markdown(f"""
        <div class="page-title">Good to see you, {name}.</div>
        <div class="page-sub">Your private wellness space — no judgement, just presence.</div>
        """, unsafe_allow_html=True)
    with h2:
        st.markdown("<div style='padding-top:0.55rem;display:flex;justify-content:flex-end;'>", unsafe_allow_html=True)
        tog_icon = "☀️" if is_dark else "🌙"
        if st.button(tog_icon, key="theme_btn_main"):
            st.session_state.theme = "light" if is_dark else "dark"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Sidebar ──────────────────────────────────────────
    init     = (st.session_state.username or "U")[0].upper()
    emo      = st.session_state.dominant_emotion
    pct      = st.session_state.emotion_percent
    emo_icons = {"Calm":"🌿","Anxious":"🌀","Happy":"☀️","Sad":"🌧","Stressed":"⚡","Peaceful":"🍃"}
    emo_icon  = emo_icons.get(emo, "💜")
    bscore    = st.session_state.burnout_score
    b_color   = "#6ee7b7" if bscore < 40 else ("#facc15" if bscore < 70 else "#f87171")

    st.sidebar.markdown(f"""
    <div class="sidebar-user">
        <div class="avatar">{init}</div>
        <div>
            <div class="user-name">{st.session_state.username}</div>
            <div class="user-status"><div class="status-dot"></div> Active session</div>
        </div>
    </div>

    <div class="s-label">Current State</div>
    <div class="emotion-card">
        <div class="emo-label">Dominant Emotion</div>
        <div class="emo-value">{emo_icon} {emo}</div>
        <div class="emo-pct">{pct}% intensity</div>
        <div class="prog-track"><div class="prog-fill" style="width:{pct}%"></div></div>
    </div>

    <div class="s-label">Consistency</div>
    <div class="streak-card">
        <div class="streak-num">🔥 {st.session_state.streak}</div>
        <div class="streak-sub">Day Streak</div>
    </div>

    <div class="s-label">Burnout Index</div>
    <div class="burnout-mini">
        <div style="font-family:Consolas,monospace;font-size:2rem;font-weight:700;color:{b_color};">{bscore}</div>
        <div style="font-size:0.67rem;letter-spacing:0.1em;text-transform:uppercase;
                    color:{T['text_muted']};margin-top:0.22rem;">out of 100</div>
    </div>
    <div class="hdivider"></div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("← Sign Out", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    # ── Two-column layout ─────────────────────────────────
    col_l, col_r = st.columns([1, 1.45], gap="large")

    # ── LEFT: Analytics ───────────────────────────────────
    with col_l:

        # Weekly Wellness spline chart
        st.markdown("""<div class="sec-hdr">
            <div class="sec-dot"></div>
            <div class="sec-title">Weekly Wellness</div>
        </div>""", unsafe_allow_html=True)

        days     = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        wellness = st.session_state.weekly_data

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=days, y=wellness,
            fill='tozeroy',
            fillcolor="rgba(139,92,246,0.11)" if is_dark else "rgba(139,92,246,0.07)",
            line=dict(color='#8b5cf6', width=2.5, shape='spline', smoothing=1.3),
            mode='lines+markers',
            marker=dict(size=7, color='#c4b5fd', line=dict(color='#8b5cf6', width=2)),
            hovertemplate='<b>%{x}</b>: %{y}<extra></extra>'
        ))
        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=8, b=0), height=170,
            font=dict(family='DM Sans', color=T['tick_color'], size=11),
            xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=T['tick_color'], size=10)),
            yaxis=dict(showgrid=True, zeroline=False, gridcolor=T['grid_color'],
                       range=[0,100], tickfont=dict(color=T['tick_color'], size=10)),
            showlegend=False,
            hoverlabel=dict(bgcolor='#1e1340', font_color='white', bordercolor='#8b5cf6')
        )
        st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})

        st.markdown('<div class="hdivider"></div>', unsafe_allow_html=True)

        # Burnout gauge
        st.markdown("""<div class="sec-hdr">
            <div class="sec-dot" style="background:#f87171;box-shadow:0 0 8px #f87171;"></div>
            <div class="sec-title">Burnout Index</div>
        </div>""", unsafe_allow_html=True)

        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=bscore,
            number={'suffix':'/100','font':{'size':20,'family':'Consolas','color':T['text_primary']}},
            gauge={
                'axis':{'range':[0,100],'tickfont':{'color':T['tick_color'],'size':9},
                        'tickwidth':1,'tickcolor':T['glass_border']},
                'bar':{'color':'#8b5cf6','thickness':0.18},
                'bgcolor':'rgba(255,255,255,0.03)', 'borderwidth':0,
                'steps':[
                    {'range':[0,40], 'color':'rgba(110,231,183,0.13)'},
                    {'range':[40,70],'color':'rgba(250,204,21,0.11)'},
                    {'range':[70,100],'color':'rgba(248,113,113,0.13)'},
                ],
                'threshold':{'line':{'color':'#c4b5fd','width':2},'thickness':0.75,'value':bscore}
            }
        ))
        fig_g.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=8, b=0), height=190,
            font=dict(family='DM Sans', color=T['text_secondary'])
        )
        st.plotly_chart(fig_g, use_container_width=True, config={'displayModeBar': False})



    # ── RIGHT: Chat ───────────────────────────────────────
    with col_r:

        st.markdown("""<div class="sec-hdr">
            <div class="sec-dot" style="background:#93c5fd;box-shadow:0 0 8px #93c5fd;"></div>
            <div class="sec-title">Therapy Session</div>
        </div>""", unsafe_allow_html=True)

        # Render messages (no outer blank box — messages render directly)
        if not st.session_state.messages:
            st.markdown("""
            <div class="chat-empty">
                <div style="font-size:2rem;">💜</div>
                <div>Start a conversation — We are here to listen.</div>
            </div>""", unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="msg-row-user">
                        <div class="bubble-user">{msg['content']}</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="msg-row-ai">
                        <div class="bubble-ai">
                            <div class="bubble-ai-name">🤖</div>
                            {msg['content']}
                        </div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        # Quick action chips
        st.markdown(f"""
        <div>
            <div style="font-size:0.63rem;letter-spacing:0.1em;text-transform:uppercase;
                        color:{T['text_muted']};margin-bottom:0.42rem;font-weight:700;">
                Quick Prompts
            </div>
            <div class="chips-row">
                <span class="chip">I'm feeling anxious</span>
                <span class="chip">I need to vent</span>
                <span class="chip">Help me relax</span>
                <span class="chip">I can't sleep</span>
                <span class="chip">I feel overwhelmed</span>
                <span class="chip">I'm grateful today</span>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # Chat input — styled white like text inputs
        user_input = st.chat_input("How are you feeling right now…", key="chat_in")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner("Solace is thinking…"):
                try:
                    resp = requests.post(
                        f"{BACKEND_URL}/chat",
                        headers=auth_headers(),
                        json={"text": user_input},
                        timeout=30
                    )
                    if resp.status_code == 200:
                        result = resp.json()
                        st.session_state.burnout_score    = result.get("burnout_score",    st.session_state.burnout_score)
                        st.session_state.streak           = result.get("streak",           st.session_state.streak)
                        st.session_state.dominant_emotion = result.get("emotion",           st.session_state.dominant_emotion)
                        st.session_state.emotion_percent  = result.get("emotion_score",     st.session_state.emotion_percent)
                        st.session_state.weekly_data      = fetch_weekly_data()
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result.get("response", "")
                        })
                    elif resp.status_code == 400:
                        st.warning(resp.json().get("detail", "Invalid message."))
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "I'm having trouble connecting right now. Please try again."
                        })
                except requests.exceptions.Timeout:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Response is taking too long. Please try again."
                    })
                except Exception:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Backend unreachable. Make sure the server is running on port 8000."
                    })
            st.rerun()# Trigger rebuild for Streamlit URL
