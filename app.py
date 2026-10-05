
import streamlit as st
from core.auth import (
    init_auth_db, register_user, authenticate, get_cookie_manager,
    restore_user_from_cookie, remember_user, login_into_session
)
from core.db import init_db
from core.ui import setup_page, init_theme, inject_css

setup_page("NutriPlan AI — Login", "🥗")
init_theme()
inject_css()
init_auth_db()
init_db()

cookies = get_cookie_manager()
if not cookies.ready():
    st.stop()

# Restore remembered login before showing the login screen.
# Do not restore the previous cookie immediately after logout.
if not st.session_state.get("user") and not st.session_state.pop("logged_out", False):
    remembered = restore_user_from_cookie(cookies)

    if remembered:
        login_into_session(remembered)
        st.switch_page("pages/01_Dashboard.py")
        st.stop()

st.markdown("""
<div class="login-box">
    <div style="font-size:42px;">🥗</div>
    <h1 style="font-family:Playfair Display,serif;font-size:46px;margin-bottom:6px;">
        NutriPlan AI
    </h1>
    <p style="font-size:17px;line-height:1.6;">
        Personalized diet recommendations powered by your profile, nutrition data
        and a machine-learning diet classifier.
    </p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.1, 1], gap="large")

with left:
    st.markdown("""
    <div class="glass">
      <h2 style="color:white;">Eat smarter. Live better.</h2>
      <p class="small" style="color:#d5ded8;">
        Your account keeps your profile and generated diet plans available
        across sessions. Select “Remember me” when logging in from your own device.
      </p>
      <span class="badge">AI Diet Type</span>
      <span class="badge">Calories & Macros</span>
      <span class="badge">Indian Food Data</span>
      <span class="badge">Saved History</span>
    </div>
    """, unsafe_allow_html=True)

with right:
    login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            remember = st.checkbox("Remember me for 30 days", value=True)
            submit = st.form_submit_button("Login", use_container_width=True)

        if submit:
            user = authenticate(email, password)

        if user:
            login_into_session(user)

            if remember:
                remember_user(user["id"], cookies)

            st.session_state["login_success"] = True
            st.switch_page("pages/01_Dashboard.py")

        else:
            st.error("Incorrect email or password.")

    with register_tab:
        with st.form("register_form"):
            name = st.text_input("Full name")
            new_email = st.text_input("Email address")
            new_password = st.text_input("Create password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            submit_register = st.form_submit_button("Create account", use_container_width=True)

        if submit_register:
            if new_password != confirm:
                st.error("The passwords do not match.")
            else:
                ok, message = register_user(name, new_email, new_password)
                if ok:
                    st.success(message)
                else:
                    st.error(message)

st.markdown(
    '<div style="text-align:center;color:#b9c5bd;font-size:12px;margin-top:25px;">'
    'Educational project — not medical advice.</div>',
    unsafe_allow_html=True
)
