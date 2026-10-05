
import streamlit as st
from core.ui import setup_page, init_theme, inject_css, sidebar
from core.auth import require_login, current_user
from core.db import load_profile, load_latest_plan

setup_page("NutriPlan AI — Dashboard", "🏠")
init_theme()
require_login()
inject_css()
route = sidebar("pages/01_Dashboard.py")
if route and route != "pages/01_Dashboard.py":
    st.switch_page(route)

user = current_user()
profile = load_profile(user["id"])
latest = load_latest_plan(user["id"])

st.markdown(f"""
<div class="hero">
  <h1>Welcome back, {user['name']}.</h1>
  <p>Your personalized nutrition workspace. Update your profile, run the model,
  and view the generated diet plan whenever you need it.</p>
</div>
""", unsafe_allow_html=True)

if not profile:
    st.markdown('<div class="section-title">Let’s set up your profile</div>', unsafe_allow_html=True)
    st.info("You have not entered your nutrition profile yet. The model needs those values before it can generate a diet plan.")
    if st.button("Setup My Profile", use_container_width=True):
        st.switch_page("pages/02_Profile.py")
else:
    st.markdown('<div class="section-title">Your profile snapshot</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    values = [
        (f"{profile['age']}", "Age"),
        (f"{profile['weight']:.1f} kg", "Weight"),
        (f"{profile['bmi']:.1f}", "BMI"),
        (profile["disease"], "Health context"),
    ]
    for col, (value, label) in zip(cols, values):
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{value}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">What would you like to do?</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card"><h3>👤 Update profile</h3><p class="muted">Change measurements, health data, activity, restrictions or goal.</p></div>', unsafe_allow_html=True)
        if st.button("Open profile", key="profile", use_container_width=True):
            st.switch_page("pages/02_Profile.py")
    with c2:
        st.markdown('<div class="card"><h3>✨ Generate plan</h3><p class="muted">Run the trained classifier and create a nutrition plan from the food datasets.</p></div>', unsafe_allow_html=True)
        if st.button("Create diet plan", key="plan", use_container_width=True):
            st.switch_page("pages/03_Diet_Plan.py")
    with c3:
        st.markdown('<div class="card"><h3>🍎 Explore foods</h3><p class="muted">Search nutrition values and inspect foods available to the planner.</p></div>', unsafe_allow_html=True)
        if st.button("Explore foods", key="foods", use_container_width=True):
            st.switch_page("pages/04_Food_Explorer.py")

if latest:
    st.markdown('<div class="section-title">Latest generated result</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    vals = [
        (latest["diet"], "Predicted diet"),
        (latest["targets"]["target_kcal"], "Target kcal"),
        (latest["actual"]["kcal"], "Plan kcal"),
        (latest["actual"]["sodium_mg"], "Plan sodium mg"),
    ]
    for col, (v, l) in zip([c1,c2,c3,c4], vals):
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{v}</div><div class="metric-label">{l}</div></div>', unsafe_allow_html=True)

    st.caption(f"Generated: {latest['created_at']}")
else:
    st.info("No diet plan has been generated yet.")
