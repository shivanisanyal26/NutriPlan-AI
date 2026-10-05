
import streamlit as st
from core.ui import setup_page, init_theme, inject_css, sidebar
from core.auth import require_login
from core.diet import load_indian_foods, load_usda_foods

setup_page("NutriPlan AI — Food Explorer", "🍎")
init_theme()
require_login()
inject_css()
route = sidebar("pages/04_Food_Explorer.py")

if route and route != "pages/04_Food_Explorer.py":
    st.switch_page(route)

st.markdown('<div class="section-title">Food Explorer</div>', unsafe_allow_html=True)

source = st.radio("Dataset", ["Indian", "USDA"], horizontal=True)
search = st.text_input("🔎 Search food", placeholder="Search for rice, paneer, chicken, fruit...")

with st.spinner("Loading nutrition data..."):
    df = load_indian_foods() if source == "Indian" else load_usda_foods()

if search.strip():
    q = search.lower()
    df = df[df["food"].str.lower().str.contains(q, na=False)]

df = df[["food","source","meal","kcal","protein_g","carbs_g","fat_g","sodium_mg"]].head(100)

st.caption(f"Showing {len(df)} matching items.")
st.dataframe(df, use_container_width=True, hide_index=True)
