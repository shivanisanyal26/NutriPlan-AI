
import streamlit as st
from core.ui import setup_page, init_theme, inject_css, sidebar
from core.auth import require_login, current_user
from core.db import load_profile, save_profile

setup_page("NutriPlan AI — Profile", "👤")
init_theme()
require_login()
inject_css()
route = sidebar("pages/02_Profile.py")
if route and route != "pages/02_Profile.py":
    st.switch_page(route)

user = current_user()
existing = load_profile(user["id"]) or {}

st.markdown('<div class="section-title">Your nutrition profile</div>', unsafe_allow_html=True)
st.write("These are the inputs used by the trained diet-classification model. The extra goal field is used to turn the prediction into calorie targets.")

with st.form("profile"):
    c1, c2 = st.columns(2)

    with c1:
        name = st.text_input("Name", value=existing.get("name", user["name"]))
        age = st.number_input("Age", 13, 100, int(existing.get("age", 25)))
        gender = st.selectbox("Gender", ["Female", "Male"], index=["Female","Male"].index(existing.get("gender","Female")))
        height = st.number_input("Height (cm)", 100.0, 230.0, float(existing.get("height", 165)))
        weight = st.number_input("Weight (kg)", 30.0, 250.0, float(existing.get("weight", 60)))

        disease_options = ["Obesity", "Diabetes", "Hypertension"]
        disease = st.selectbox("Health context / disease type", disease_options,
                               index=disease_options.index(existing.get("disease","Obesity")) if existing.get("disease") in disease_options else 0)
        severity_options = ["Mild", "Moderate", "Severe"]
        severity = st.selectbox("Severity", severity_options,
                                index=severity_options.index(existing.get("severity","Mild")) if existing.get("severity") in severity_options else 0)

    with c2:
        activity_options = ["Sedentary", "Moderate", "Active"]
        activity = st.selectbox("Physical activity level", activity_options,
                                index=activity_options.index(existing.get("activity","Moderate")) if existing.get("activity") in activity_options else 1)
        cholesterol = st.number_input("Cholesterol (mg/dL)", 80.0, 400.0, float(existing.get("cholesterol", 190)))
        blood_pressure = st.number_input("Systolic blood pressure (mmHg)", 80.0, 220.0, float(existing.get("blood_pressure", 120)))
        glucose = st.number_input("Glucose (mg/dL)", 50.0, 350.0, float(existing.get("glucose", 100)))
        restriction_options = ["None", "Low_Sugar", "Low_Sodium"]
        restriction = st.selectbox("Dietary restriction", restriction_options,
                                   index=restriction_options.index(existing.get("dietary_restriction","None")) if existing.get("dietary_restriction") in restriction_options else 0)
        allergy_options = ["None", "Peanuts", "Gluten"]
        allergy = st.selectbox("Allergy / avoidance", allergy_options,
                               index=allergy_options.index(existing.get("allergy","None")) if existing.get("allergy") in allergy_options else 0)
        cuisine_options = ["Indian", "Mexican", "Chinese", "Italian"]
        cuisine = st.selectbox("Preferred cuisine", cuisine_options,
                               index=cuisine_options.index(existing.get("cuisine","Indian")) if existing.get("cuisine") in cuisine_options else 0)
        weekly_exercise = st.number_input("Weekly exercise hours", 0.0, 30.0, float(existing.get("weekly_exercise", 3.0)), step=0.5)
        goal_options = ["Weight Loss", "Maintain Weight", "Weight Gain"]
        goal = st.selectbox("Personal goal", goal_options,
                            index=goal_options.index(existing.get("goal","Maintain Weight")) if existing.get("goal") in goal_options else 1)

    submitted = st.form_submit_button("💾 Save profile", use_container_width=True)

if submitted:
    bmi = weight / (height / 100) ** 2
    profile = {
        "name": name.strip(),
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "bmi": round(bmi, 2),
        "disease": disease,
        "severity": severity,
        "activity": activity,
        "cholesterol": cholesterol,
        "blood_pressure": blood_pressure,
        "glucose": glucose,
        "dietary_restriction": restriction,
        "allergy": allergy,
        "cuisine": cuisine,
        "weekly_exercise": weekly_exercise,
        "goal": goal,
    }
    save_profile(user["id"], profile)
    st.success("Profile saved successfully.")
    


