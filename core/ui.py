
import streamlit as st
from .auth import current_user, get_cookie_manager, clear_remembered_login, logout

BG = "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=2200&q=85"

def setup_page(title, icon="🥗"):
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")

def init_theme():
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = True

def inject_css():
    dark = st.session_state.get("dark_mode", True)
    if dark:
        overlay = "rgba(7,14,11,.78), rgba(7,14,11,.88)"
        text = "#f5f8f4"
        muted = "#b9c5bd"
        card = "rgba(19,29,24,.88)"
        border = "rgba(255,255,255,.12)"
        heading = "#ffffff"
    else:
        overlay = "rgba(247,249,244,.88), rgba(247,249,244,.94)"
        text = "#17241b"
        muted = "#637067"
        card = "rgba(255,255,255,.92)"
        border = "rgba(40,80,55,.12)"
        heading = "#173d28"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

    html, body, [class*="css"] {{
        font-family:'DM Sans',sans-serif;
        color:{text};
    }}
    .stApp {{
        background:
          linear-gradient({overlay}),
          url("{BG}") center/cover fixed;
    }}
    .block-container {{
        max-width:1200px;
        padding-top:1.2rem;
        padding-bottom:3rem;
    }}
    [data-testid="stSidebar"] {{
        background:rgba(8,18,13,.88);
        backdrop-filter:blur(18px);
        border-right:1px solid rgba(255,255,255,.08);
    }}
    .hero {{
        border-radius:28px;
        padding:42px 44px;
        color:white;
        background:
          linear-gradient(90deg,rgba(10,33,21,.94),rgba(34,83,54,.62)),
          url("{BG}") center/cover;
        box-shadow:0 16px 50px rgba(0,0,0,.28);
        margin-bottom:28px;
    }}
    .hero h1 {{
        font-family:'Playfair Display',serif;
        font-size:48px;
        margin:0 0 8px;
        letter-spacing:-1px;
        color:white;
    }}
    .hero p {{font-size:17px;max-width:780px;line-height:1.65;color:white;}}
    .section-title {{
        font-family:'Playfair Display',serif;
        color:{heading};
        font-size:31px;
        margin:22px 0 9px;
    }}
    .card,.food-card,.metric-card,.glass {{
        background:{card};
        border:1px solid {border};
        border-radius:20px;
        padding:21px;
        box-shadow:0 10px 30px rgba(0,0,0,.10);
        backdrop-filter:blur(12px);
    }}
    .metric-card {{text-align:center;}}
    .metric-value {{font-size:29px;font-weight:700;color:#7ed69b;}}
    .metric-label {{font-size:13px;color:{muted};margin-top:3px;}}
    .badge {{
        display:inline-block;padding:5px 10px;border-radius:999px;
        background:rgba(65,155,95,.18);color:#9be0ad;font-size:12px;
        font-weight:600;margin:2px;
    }}
    .muted {{color:{muted};}}
    .food-card {{margin-bottom:12px;}}
    .small {{font-size:13px;color:{muted};}}
    .login-box {{
        max-width:980px;margin:5vh auto;
        padding:38px;border-radius:30px;
        background:rgba(8,17,12,.78);
        border:1px solid rgba(255,255,255,.12);
        box-shadow:0 24px 80px rgba(0,0,0,.35);
        backdrop-filter:blur(16px);
    }}
    .login-box h1,.login-box h2,.login-box p,.login-box label {{color:white !important;}}
    div.stButton > button {{
        border-radius:12px;border:0;background:#2f7b4c;color:white;
        font-weight:700;padding:10px 18px;
    }}
    div.stButton > button:hover {{background:#3b9660;color:white;}}
    [data-baseweb="input"]>div,[data-baseweb="select"]>div {{
        border-radius:10px;
    }}
    hr {{border-color:{border};}}
    </style>
    """, unsafe_allow_html=True)

def sidebar(current_page="pages/01_Dashboard.py"):
    user = current_user()
    if not user:
        return

    routes = {
        "🏠 Dashboard": "pages/01_Dashboard.py",
        "👤 My Profile": "pages/02_Profile.py",
        "✨ Diet Plan": "pages/03_Diet_Plan.py",
        "🍎 Food Explorer": "pages/04_Food_Explorer.py",
        "📋 History": "pages/05_History.py",
    }

    page_names = list(routes.keys())

    # Select the correct sidebar item for the page currently being viewed
    current_index = 0

    for i, route in enumerate(routes.values()):
        if route == current_page:
            current_index = i
            break

    with st.sidebar:
        st.markdown("## 🥗 NutriPlan AI")
        st.caption(f"Welcome, {user['name']}")
        st.divider()

        page = st.radio(
            "Navigation",
            page_names,
            index=current_index,
            label_visibility="collapsed"
        )

        st.divider()

        dark = st.toggle(
            "Dark theme",
            value=st.session_state.get("dark_mode", True)
        )
        st.session_state["dark_mode"] = dark

        if st.button("Log out", use_container_width=True):
            try:
                clear_remembered_login(get_cookie_manager())
            except Exception:
                pass

            logout()
            st.switch_page("app.py")

        st.caption("AI nutrition project • Streamlit")

    selected_route = routes[page]

    # Only navigate when the user actually selects another page
    if selected_route != current_page:
        return selected_route

    return None