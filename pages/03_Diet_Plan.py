
import streamlit as st
import pandas as pd

from core.ui import setup_page, init_theme, inject_css, sidebar
from core.auth import require_login, current_user
from core.db import load_profile, save_plan
from core.model import predict_diet
from core.diet import calculate_targets, generate_plan

setup_page("NutriPlan AI — Diet Plan", "✨")
init_theme()
require_login()
inject_css()
route = sidebar("pages/03_Diet_Plan.py")

if route and route != "pages/03_Diet_Plan.py":
    st.switch_page(route)

user = current_user()
profile = load_profile(user["id"])

st.markdown('<div class="section-title">AI-generated diet plan</div>', unsafe_allow_html=True)

if not profile:
    st.warning("Please complete your profile first.")
    if st.button("Open profile", use_container_width=True):
        st.switch_page("pages/02_Profile.py")
    st.stop()

if st.button("✨ Run model & generate new plan", use_container_width=True):
    with st.spinner("Running the diet classifier and building your meal plan..."):
        prediction = predict_diet(profile)
        targets = calculate_targets(profile, prediction["diet"])
        plan, actual = generate_plan(profile, targets, source="Indian")

        save_plan(user["id"], prediction, targets, actual, plan)

        st.session_state["prediction"] = prediction
        st.session_state["targets"] = targets
        st.session_state["plan"] = plan
        st.session_state["actual"] = actual

if "prediction" not in st.session_state:
    st.info("Click the button above to generate your first plan.")
    st.stop()

prediction = st.session_state["prediction"]
targets = st.session_state["targets"]
plan = st.session_state.get("plan")

if not plan:
    st.info("No diet plan has been generated yet.")
    st.stop()
actual = st.session_state["actual"]

st.markdown(f"""
<div class="hero">
  <h1>Your predicted diet type: {prediction['diet'].replace('_',' ')}</h1>
  <p>The classifier combines your profile variables and returns a diet category.
  The planner then uses the predicted category to set calorie/macronutrient priorities
  and selects foods from the Indian nutrition dataset.</p>
</div>
""", unsafe_allow_html=True)

if prediction["probabilities"]:
    st.markdown('<div class="section-title">Model probabilities</div>', unsafe_allow_html=True)
    prob_cols = st.columns(len(prediction["probabilities"]))
    for col, (label, value) in zip(prob_cols, prediction["probabilities"].items()):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{value*100:.1f}%</div>'
                f'<div class="metric-label">{label.replace("_"," ")}</div></div>',
                unsafe_allow_html=True
            )

st.markdown('<div class="section-title">Target vs actual</div>', unsafe_allow_html=True)

target_df = pd.DataFrame([
    {"Metric":"Calories (kcal)", "Target":targets["target_kcal"], "Plan":actual["kcal"]},
    {"Metric":"Protein (g)", "Target":targets["protein_g"], "Plan":actual["protein_g"]},
    {"Metric":"Carbs (g)", "Target":targets["carbs_g"], "Plan":actual["carbs_g"]},
    {"Metric":"Fat (g)", "Target":targets["fat_g"], "Plan":actual["fat_g"]},
    {"Metric":"Sodium (mg)", "Target":targets["sodium_mg_limit"], "Plan":actual["sodium_mg"]},
])
st.dataframe(target_df, use_container_width=True, hide_index=True)

st.markdown('<div class="section-title">Recommended meals</div>', unsafe_allow_html=True)

if plan:
    meal_df = pd.DataFrame(plan)[[
        "meal","food","source","servings","kcal","protein_g","carbs_g","fat_g","sodium_mg"
    ]].rename(columns={
        "meal":"Meal","food":"Food","source":"Source","servings":"Servings",
        "kcal":"kcal","protein_g":"protein_g","carbs_g":"carbs_g",
        "fat_g":"fat_g","sodium_mg":"sodium_mg"
    })
    st.dataframe(meal_df, use_container_width=True, hide_index=True)
else:
    st.error("The food dataset did not return a usable meal plan.")

st.caption(
    f"Estimated BMR: {targets['bmr']} kcal/day • "
    f"Estimated maintenance (TDEE): {targets['tdee']} kcal/day"
)

st.warning(
    "This is an educational recommendation system. Nutrition values are dataset estimates "
    "and should not be used as medical treatment."
)
