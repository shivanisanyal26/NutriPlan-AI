
"""
Optional model retraining script.

Run:
    python train_model.py

It trains the same classifier used by the app and writes:
    models/diet_model.joblib
"""
from core.model import make_model, MODEL_PATH
import os
import joblib

model = make_model()
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(model, MODEL_PATH)
print(f"Saved trained model to: {MODEL_PATH}")
