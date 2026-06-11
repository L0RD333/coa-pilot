"""Light / dark theme CSS for the Streamlit app.

Visual language mirrors the rahul357.netlify.app portfolio: a dark-first palette
with a matching light mode, ambient radial glows, Sora / Inter / JetBrains Mono
typography, glass cards, a tri-colour gradient (indigo -> teal -> purple) and
glowing pill buttons. Both palettes are kept so the day/night toggle keeps
working.
"""

PALETTES = {
    "dark": {
        "bg": "#070912", "bg2": "#0b0f1c", "card": "#10131f",
        "surface": "rgba(255,255,255,.045)", "surface2": "rgba(255,255,255,.07)",
        "text": "#eef1fb", "muted": "#aab2cf", "text3": "#6f7798",
        "border": "rgba(255,255,255,.10)", "borderglow": "rgba(120,140,255,.35)",
        "accent": "#7c84ff", "accent2": "#4ad6c4", "accent3": "#b07cff",
        "good": "#4ad6c4", "bad": "#ff7b8a",
        "glow1": "rgba(124,132,255,.22)", "glow2": "rgba(74,214,196,.14)",
        "shadow": "0 20px 50px -20px rgba(0,0,0,.7)",
    },
    "light": {
        "bg": "#f5f7fc", "bg2": "#eef1f9", "card": "#ffffff",
        "surface": "rgba(255,255,255,.75)", "surface2": "#ffffff",
        "text": "#141a2e", "muted": "#46506e", "text3": "#828aa6",
        "border": "rgba(20,30,70,.10)", "borderglow": "rgba(90,100,220,.35)",
        "accent": "#4b53e0", "accent2": "#0fa593", "accent3": "#8a4bd6",
        "good": "#0fa593", "bad": "#dc2626",
        "glow1": "rgba(75,83,224,.14)", "glow2": "rgba(15,165,147,.10)",
        "shadow": "0 20px 50px -24px rgba(40,50,120,.25)",
    },
}

# Tri-colour gradient used for headline text, primary buttons and accents.
GRADIENT = ("linear-gradient(110deg, var(--accent), var(--accent2) 60%, "
            "var(--accent3))")


def css(mode: str) -> str:
    p = PALETTES["dark" if mode == "dark" else "light"]
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sora:wght@600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
:root {{
  --bg:{p['bg']}; --bg2:{p['bg2']}; --card:{p['card']};
  --surface:{p['surface']}; --surface2:{p['surface2']};
  --text:{p['text']}; --muted:{p['muted']}; --text3:{p['text3']};
  --border:{p['border']}; --borderglow:{p['borderglow']};
  --accent:{p['accent']}; --accent2:{p['accent2']}; --accent3:{p['accent3']};
  --good:{p['good']}; --bad:{p['bad']};
  --glow1:{p['glow1']}; --glow2:{p['glow2']}; --shadow:{p['shadow']};
  --grad:{GRADIENT};
}}
html, body, .stApp, [class*="css"] {{
  font-family:'Inter','Segoe UI',system-ui,-apple-system,sans-serif;
}}
.stApp {{ background: var(--bg); color: var(--text); }}
[data-testid="stHeader"] {{ background: transparent; }}

/* Ambient radial glow background */
.stApp::before {{
  content:""; position:fixed; inset:0; z-index:0; pointer-events:none;
  background:
    radial-gradient(620px circle at 12% 8%, var(--glow1), transparent 60%),
    radial-gradient(560px circle at 88% 22%, var(--glow2), transparent 55%),
    radial-gradient(700px circle at 50% 110%, var(--glow1), transparent 60%);
}}
.block-container {{ padding-top: 1.4rem; max-width: 1080px; position:relative;
  z-index:1; }}

.stApp, .stApp p, .stApp label, .stApp span, .stApp li,
.stMarkdown, [data-testid="stWidgetLabel"] {{ color: var(--text); }}
.stCaption, small, .stApp .st-emotion-cache p small {{ color: var(--muted) !important; }}
h1, h2, h3 {{ font-family:'Sora','Inter',sans-serif; letter-spacing:-.02em;
  font-weight:700; }}

/* Hero header */
.hero {{
  background: var(--surface); border:1px solid var(--border);
  border-radius: 24px; padding: 34px 36px; margin-bottom: 22px;
  backdrop-filter: blur(14px); box-shadow: var(--shadow);
  position: relative; overflow: hidden;
}}
.hero::after {{
  content:""; position:absolute; left:0; top:0; right:0; height:4px;
  background: var(--grad);
}}
.status-pill {{
  display:inline-flex; align-items:center; gap:9px; font-size:13px;
  font-weight:500; color:var(--accent2); background:var(--surface2);
  border:1px solid var(--border); padding:7px 15px; border-radius:100px;
  margin-bottom:20px; font-family:'JetBrains Mono',monospace;
}}
.status-pill .live {{
  width:8px; height:8px; border-radius:50%; background:var(--accent2);
  box-shadow:0 0 0 0 var(--accent2); animation:ping 2s infinite;
}}
@keyframes ping {{
  0% {{ box-shadow:0 0 0 0 rgba(74,214,196,.5); }}
  70% {{ box-shadow:0 0 0 8px rgba(74,214,196,0); }}
  100% {{ box-shadow:0 0 0 0 rgba(74,214,196,0); }}
}}
.hero h1 {{
  margin:0; font-size:clamp(34px,5vw,52px); font-weight:800;
  line-height:1.04; font-family:'Sora','Inter',sans-serif;
}}
.hero h1 .grad {{
  background: var(--grad); -webkit-background-clip:text;
  background-clip:text; -webkit-text-fill-color:transparent;
}}
.hero p, .hero .sub {{ color: var(--muted) !important; margin:.6rem 0 0;
  font-size:1.05rem; max-width:660px; line-height:1.6; }}
.badges {{ margin-top:18px; }}
.badge {{ display:inline-block; background: var(--surface2); color: var(--accent);
  border:1px solid var(--border); padding:6px 14px; border-radius:999px;
  font-size:.75rem; font-weight:600; margin-right:8px; margin-top:6px;
  font-family:'JetBrains Mono',monospace; }}

/* Glass cards / bordered containers */
[data-testid="stVerticalBlockBorderWrapper"] {{
  background: var(--surface); border:1px solid var(--border) !important;
  border-radius:18px; backdrop-filter: blur(14px); box-shadow: var(--shadow);
  transition:.3s;
}}
[data-testid="stVerticalBlockBorderWrapper"]:hover {{
  border-color: var(--borderglow) !important;
}}

/* Metrics — gradient value text */
[data-testid="stMetric"] {{
  background: var(--surface2); border:1px solid var(--border);
  border-radius:16px; padding:16px 18px;
}}
[data-testid="stMetricValue"] {{
  font-family:'Sora','Inter',sans-serif; font-weight:800;
  background: var(--grad); -webkit-background-clip:text; background-clip:text;
  -webkit-text-fill-color:transparent;
}}
[data-testid="stMetricLabel"] {{ color: var(--text3); font-size:.8rem;
  font-weight:500; }}

/* Download buttons = primary gradient */
.stDownloadButton > button {{
  background: linear-gradient(120deg, var(--accent), var(--accent3));
  color:#fff; border:0; border-radius:12px; padding:.7rem 1.4rem;
  font-weight:600; font-size:.92rem;
  box-shadow:0 10px 28px -10px var(--accent); transition:.25s;
}}
.stDownloadButton > button:hover {{
  transform: translateY(-3px); box-shadow:0 16px 34px -10px var(--accent);
}}

/* Plain buttons (theme toggle) = ghost */
.stButton > button {{
  background: var(--surface2); color: var(--text);
  border:1px solid var(--border); border-radius:12px; padding:.6rem 1.1rem;
  font-weight:600; transition:.25s;
}}
.stButton > button:hover {{
  border-color: var(--borderglow); transform: translateY(-2px);
  color: var(--text);
}}

/* Inputs / uploader / tabs */
[data-testid="stFileUploaderDropzone"] {{
  background: var(--surface); border:1.5px dashed var(--border);
  border-radius:16px;
}}
.stTextInput input, .stTextArea textarea {{
  background: var(--surface2); color: var(--text); border:1px solid var(--border);
  border-radius:12px;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
  border-color: var(--accent);
  box-shadow:0 0 0 3px var(--glow1);
}}
[data-baseweb="tab-list"] {{ gap:8px; }}
[data-baseweb="tab"] {{ background: var(--surface2); border-radius:12px 12px 0 0;
  font-weight:600; }}
[data-baseweb="tab"][aria-selected="true"] {{ color: var(--accent); }}

/* Dataframe / editor */
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {{
  border:1px solid var(--border); border-radius:14px; overflow:hidden;
}}
hr {{ border-color: var(--border); }}

/* Sidebar */
[data-testid="stSidebar"] {{ background: var(--bg2);
  border-right:1px solid var(--border); }}
</style>
"""
