
import streamlit as st
from core.ui import setup_page, init_theme, inject_css, sidebar
from core.auth import require_login, current_user
from core.db import load_history

setup_page("NutriPlan AI — History", "📋")
init_theme()
require_login()
inject_css()
route = sidebar("pages/05_History.py")

if route and route != "pages/05_History.py":
    st.switch_page(route)

user = current_user()
history = load_history(user["id"])

st.markdown('<div class="section-title">Your saved diet plans</div>', unsafe_allow_html=True)

if not history:
    st.info("No plans yet. Generate your first plan from the Diet Plan page.")
else:
    for item in history:
        with st.expander(
            f"{item['diet'].replace('_',' ')} • {item['targets']['target_kcal']} kcal • {item['created_at']}"
        ):
            c1, c2, c3, c4 = st.columns(4)
            vals = [
                (item["targets"]["target_kcal"], "Target kcal"),
                (item["actual"]["kcal"], "Actual kcal"),
                (item["actual"]["protein_g"], "Protein g"),
                (item["actual"]["sodium_mg"], "Sodium mg"),
            ]
            for col, (v, label) in zip([c1,c2,c3,c4], vals):
                with col:
                    st.markdown(
                        f'<div class="metric-card"><div class="metric-value">{v}</div>'
                        f'<div class="metric-label">{label}</div></div>',
                        unsafe_allow_html=True
                    )
