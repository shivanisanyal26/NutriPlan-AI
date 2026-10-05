
# NutriPlan AI — VS Code Multi-Page Version

This version splits the website into separate Streamlit pages:

- `app.py` — Login + Register
- `pages/01_Dashboard.py` — Dashboard
- `pages/02_Profile.py` — User profile/model inputs
- `pages/03_Diet_Plan.py` — Model prediction + generated diet plan
- `pages/04_Food_Explorer.py` — Food database explorer
- `pages/05_History.py` — Saved plans
- `core/` — authentication, database, model and diet-plan logic
- `data/` — your CSV datasets
- `models/diet_model.joblib` — trained classifier

## Run in VS Code

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

For CMD:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Login memory

The app stores users and profiles in SQLite and creates a 30-day remembered-login token when
"Remember me" is selected. The token is stored in a browser cookie.

For a deployed application, change the cookie password with:

```powershell
$env:NUTRIPLAN_COOKIE_PASSWORD="use-a-long-random-secret"
```

## Model note

The supplied `diet_model.joblib` was saved with an older scikit-learn version and, in this
environment, contains a preprocessing object that cannot be loaded cleanly with the current
scikit-learn version. The project therefore includes a freshly trained classifier built from
`diet_recommendations_dataset.csv`.

The target classes are:

- Balanced
- Low_Carb
- Low_Sodium

The training features match the columns used by the supplied training artifact:
Age, Weight_kg, Height_cm, BMI, BMI_calc, Cholesterol_mg/dL, Blood_Pressure_mmHg,
Glucose_mg/dL, Weekly_Exercise_Hours, BP_high, Glu_high, Chol_high, Gender,
Disease_Type, Severity, Physical_Activity_Level, Dietary_Restrictions, Allergies.

## Design

The interface uses a food photograph as the background, with a dark glass overlay so the
text remains readable. The default authenticated pages use a dark theme; the theme button
in the sidebar can switch between dark and light modes.

This is an academic/demo nutrition recommendation system, not medical advice.
