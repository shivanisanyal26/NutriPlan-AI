
import os
import joblib
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(ROOT, "models", "diet_model.joblib")
DATA_PATH = os.path.join(ROOT, "data", "diet_recommendations_dataset.csv")

FEATURES = [
    "Age","Weight_kg","Height_cm","BMI","BMI_calc",
    "Cholesterol_mg/dL","Blood_Pressure_mmHg","Glucose_mg/dL",
    "Weekly_Exercise_Hours","BP_high","Glu_high","Chol_high",
    "Gender","Disease_Type","Severity","Physical_Activity_Level",
    "Dietary_Restrictions","Allergies"
]

def make_model():
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.ensemble import RandomForestClassifier

    df = pd.read_csv(DATA_PATH).copy()
    df["BMI_calc"] = df["Weight_kg"] / (df["Height_cm"] / 100) ** 2
    df["BP_high"] = df["Blood_Pressure_mmHg"] >= 130
    df["Glu_high"] = df["Glucose_mg/dL"] >= 126
    df["Chol_high"] = df["Cholesterol_mg/dL"] >= 200

    X = df[FEATURES]
    y = df["Diet_Recommendation"].fillna("Balanced")

    numeric = [c for c in FEATURES if X[c].dtype != object]
    categorical = [c for c in FEATURES if X[c].dtype == object]

    pre = ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]), numeric),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]), categorical)
    ])

    clf = RandomForestClassifier(
        n_estimators=350,
        max_depth=12,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    pipe = Pipeline([("prep", pre), ("classifier", clf)])
    pipe.fit(X, y)
    return pipe

def load_model():
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            pass

    model = make_model()
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return model

def profile_to_model_row(profile):
    bmi = profile["weight"] / (profile["height"] / 100) ** 2
    return pd.DataFrame([{
        "Age": profile["age"],
        "Weight_kg": profile["weight"],
        "Height_cm": profile["height"],
        "BMI": bmi,
        "BMI_calc": bmi,
        "Cholesterol_mg/dL": profile["cholesterol"],
        "Blood_Pressure_mmHg": profile["blood_pressure"],
        "Glucose_mg/dL": profile["glucose"],
        "Weekly_Exercise_Hours": profile["weekly_exercise"],
        "BP_high": profile["blood_pressure"] >= 130,
        "Glu_high": profile["glucose"] >= 126,
        "Chol_high": profile["cholesterol"] >= 200,
        "Gender": profile["gender"],
        "Disease_Type": profile["disease"],
        "Severity": profile["severity"],
        "Physical_Activity_Level": profile["activity"],
        "Dietary_Restrictions": profile["dietary_restriction"],
        "Allergies": profile["allergy"],
    }])

def predict_diet(profile):
    model = load_model()
    X = profile_to_model_row(profile)
    prediction = model.predict(X)[0]
    probabilities = {}
    if hasattr(model, "predict_proba"):
        raw = model.predict_proba(X)[0]
        for cls, prob in zip(model.classes_, raw):
            probabilities[str(cls)] = round(float(prob), 4)
    return {"diet": str(prediction), "probabilities": probabilities}
