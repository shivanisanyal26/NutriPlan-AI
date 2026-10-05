
import os
import re
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(__file__))
INDIAN_PATH = os.path.join(ROOT, "data", "Indian_Food_Nutrition_Processed.csv")
USDA_PATH = os.path.join(ROOT, "data", "comprehensive_foods_usda.csv")

ACTIVITY_FACTORS = {
    "Sedentary": 1.20,
    "Moderate": 1.55,
    "Active": 1.725,
}

def calculate_targets(profile, predicted_diet):
    if profile["gender"] == "Male":
        bmr = 10 * profile["weight"] + 6.25 * profile["height"] - 5 * profile["age"] + 5
    else:
        bmr = 10 * profile["weight"] + 6.25 * profile["height"] - 5 * profile["age"] - 161

    tdee = bmr * ACTIVITY_FACTORS.get(profile["activity"], 1.55)

    if profile["goal"] == "Weight Loss":
        kcal = tdee - 400
    elif profile["goal"] == "Weight Gain":
        kcal = tdee + 300
    else:
        kcal = tdee

    kcal = int(max(1200, round(kcal)))

    if predicted_diet == "Low_Carb":
        p, c, f = .30, .20, .50
        sodium = 2300
    elif predicted_diet == "Low_Sodium":
        p, c, f = .25, .45, .30
        sodium = 1500
    else:
        p, c, f = .20, .50, .30
        sodium = 2300

    return {
        "target_kcal": kcal,
        "protein_g": round(kcal * p / 4),
        "carbs_g": round(kcal * c / 4),
        "fat_g": round(kcal * f / 9),
        "sodium_mg_limit": sodium,
        "bmr": round(bmr),
        "tdee": round(tdee),
    }

def _meal_type(name):
    n = str(name).lower()

    # Desserts, biscuits and drinks are safer as snacks than as lunch/dinner.
    if any(k in n for k in [
        "juice","lassi","milkshake","fruit","nuts","chikki","chaat","snack",
        "biscuit","cookie","puffed","lemonade","cooler","sweet","halwa",
        "laddu","ladoo","barfi","burfi","kheer","murki","cake","candy"
    ]):
        return "Snack"

    if any(k in n for k in [
        "tea","coffee","sandwich","porridge","oatmeal","cornflakes","poha",
        "chiwda","murmura","egg omelette","omelette","idli","dosa","upma",
        "parantha","paratha","poori","puri","pancake","appam","pongal","cheela",
        "breakfast"
    ]):
        return "Breakfast"

    # Lunch-oriented dishes.
    if any(k in n for k in [
        "rice","biryani","pulao","pulav","thali","sambar","rajma","chole",
        "chana","dal","curry","khichdi","meal","vegetable rice"
    ]):
        return "Lunch"

    # Dinner-oriented dishes.
    if any(k in n for k in [
        "soup","salad","tikka","kebab","grilled","roti","chapati",
        "paneer","fish","chicken","mutton","meat","dinner"
    ]):
        return "Dinner"

    return "Lunch"

def load_indian_foods():
    df = pd.read_csv(INDIAN_PATH)
    df = df.rename(columns={
        "Dish Name":"food",
        "Calories (kcal)":"kcal",
        "Carbohydrates (g)":"carbs_g",
        "Protein (g)":"protein_g",
        "Fats (g)":"fat_g",
        "Sodium (mg)":"sodium_mg",
        "Fibre (g)":"fiber_g",
    })
    df["source"] = "indian"
    df["meal"] = df["food"].map(_meal_type)
    for c in ["kcal","carbs_g","protein_g","fat_g","sodium_mg","fiber_g"]:
        if c not in df:
            df[c] = 0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df

def load_usda_foods(limit=5000):
    df = pd.read_csv(USDA_PATH, nrows=limit)
    df = df.rename(columns={"food_name":"food"})
    df["source"] = "USDA"
    df["meal"] = df["food"].map(_meal_type)
    for c in ["calories","carbs_g","protein_g","fat_g","sodium_mg","fiber_g"]:
        if c not in df:
            df[c] = 0
    df = df.rename(columns={"calories":"kcal"})
    return df[["food","kcal","carbs_g","protein_g","fat_g","sodium_mg","fiber_g","source","meal"]]

def load_foods(source="Indian"):
    if source == "USDA":
        return load_usda_foods()
    return load_indian_foods()

def _blocked(food, allergy):
    allergy = str(allergy or "").lower()
    if allergy in ("", "none", "nan"):
        return False

    terms = {
        "Peanuts": ["peanut","groundnut","moongfali"],
        "Gluten": ["wheat","bread","roti","chapati","maida","paratha","parantha","pasta"],
    }
    return any(term in str(food).lower() for term in terms.get(allergy, [allergy]))

def _score(row, kcal_target, p_target, c_target, f_target, low_sodium):
    kcal = max(float(row["kcal"]), 1)
    serving = float(np.clip(kcal_target / kcal, .5, 2.25))

    actual_k = kcal * serving
    actual_p = float(row["protein_g"]) * serving
    actual_c = float(row["carbs_g"]) * serving
    actual_f = float(row["fat_g"]) * serving
    actual_s = float(row["sodium_mg"]) * serving

    score = (
        abs(actual_k-kcal_target) * 0.9
        + abs(actual_p-p_target) * 2.2
        + abs(actual_c-c_target) * 0.8
        + abs(actual_f-f_target) * 1.2
    )

    if low_sodium:
        score += actual_s * 0.65

    return score, serving

def generate_plan(profile, targets, source="Indian"):
    df = load_foods(source)
    daily = targets["target_kcal"]

    meal_targets = {
        "Breakfast": daily * .25,
        "Lunch": daily * .35,
        "Snack": daily * .15,
        "Dinner": daily * .25,
    }

    macro = {
        "protein": targets["protein_g"],
        "carbs": targets["carbs_g"],
        "fat": targets["fat_g"],
    }

    plan = []
    used = set()

    for meal, meal_kcal in meal_targets.items():
        candidates = df[df["meal"] == meal].copy()

        if candidates.empty:
            continue

        candidates = candidates[~candidates["food"].isin(used)]
        candidates = candidates[~candidates["food"].map(lambda x: _blocked(x, profile["allergy"]))]

        if candidates.empty:
            candidates = df[df["meal"] == meal].copy()

        # Prefer lower-sodium foods for the Low_Sodium model output.
        if targets["sodium_mg_limit"] <= 1500:
            candidates = candidates.sort_values("sodium_mg").head(250)

        p_target = macro["protein"] * meal_kcal / daily
        c_target = macro["carbs"] * meal_kcal / daily
        f_target = macro["fat"] * meal_kcal / daily

        scored = []
        for _, row in candidates.iterrows():
            score, servings = _score(
                row, meal_kcal, p_target, c_target, f_target,
                targets["sodium_mg_limit"] <= 1500
            )
            scored.append((score, servings, row))

        scored.sort(key=lambda x: x[0])
        _, servings, row = scored[0]

        used.add(row["food"])
        plan.append({
            "meal": meal,
            "food": str(row["food"]),
            "source": str(row["source"]),
            "servings": round(servings, 2),
            "kcal": round(float(row["kcal"]) * servings, 1),
            "protein_g": round(float(row["protein_g"]) * servings, 1),
            "carbs_g": round(float(row["carbs_g"]) * servings, 1),
            "fat_g": round(float(row["fat_g"]) * servings, 1),
            "sodium_mg": round(float(row["sodium_mg"]) * servings, 1),
        })

    actual = {
        "kcal": round(sum(x["kcal"] for x in plan), 1),
        "protein_g": round(sum(x["protein_g"] for x in plan), 1),
        "carbs_g": round(sum(x["carbs_g"] for x in plan), 1),
        "fat_g": round(sum(x["fat_g"] for x in plan), 1),
        "sodium_mg": round(sum(x["sodium_mg"] for x in plan), 1),
    }

    return plan, actual
