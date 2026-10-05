
import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nutriplan.db")

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT,
            age INTEGER,
            gender TEXT,
            height REAL,
            weight REAL,
            bmi REAL,
            disease TEXT,
            severity TEXT,
            activity TEXT,
            cholesterol REAL,
            blood_pressure REAL,
            glucose REAL,
            dietary_restriction TEXT,
            allergy TEXT,
            cuisine TEXT,
            weekly_exercise REAL,
            goal TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            predicted_diet TEXT,
            probabilities_json TEXT,
            target_json TEXT,
            actual_json TEXT,
            plan_json TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

def save_profile(user_id, profile):
    conn = get_conn()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    existing = conn.execute(
        "SELECT id FROM profiles WHERE user_id=? ORDER BY id DESC LIMIT 1",
        (user_id,)
    ).fetchone()

    values = (
        user_id, profile["name"], profile["age"], profile["gender"],
        profile["height"], profile["weight"], profile["bmi"],
        profile["disease"], profile["severity"], profile["activity"],
        profile["cholesterol"], profile["blood_pressure"], profile["glucose"],
        profile["dietary_restriction"], profile["allergy"], profile["cuisine"],
        profile["weekly_exercise"], profile["goal"], now, now
    )

    if existing:
        conn.execute("""
            UPDATE profiles SET
                name=?,age=?,gender=?,height=?,weight=?,bmi=?,disease=?,severity=?,
                activity=?,cholesterol=?,blood_pressure=?,glucose=?,
                dietary_restriction=?,allergy=?,cuisine=?,weekly_exercise=?,goal=?,
                updated_at=?
            WHERE user_id=?
        """, values[1:-2] + (now, user_id))
        profile_id = existing[0]
    else:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO profiles(
                user_id,name,age,gender,height,weight,bmi,disease,severity,activity,
                cholesterol,blood_pressure,glucose,dietary_restriction,allergy,
                cuisine,weekly_exercise,goal,created_at,updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, values)
        profile_id = cur.lastrowid

    conn.commit()
    conn.close()
    return profile_id

def load_profile(user_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT name,age,gender,height,weight,bmi,disease,severity,activity,
               cholesterol,blood_pressure,glucose,dietary_restriction,allergy,
               cuisine,weekly_exercise,goal
        FROM profiles WHERE user_id=? ORDER BY id DESC LIMIT 1
    """, (user_id,)).fetchone()
    conn.close()

    if not row:
        return None

    keys = [
        "name","age","gender","height","weight","bmi","disease","severity",
        "activity","cholesterol","blood_pressure","glucose",
        "dietary_restriction","allergy","cuisine","weekly_exercise","goal"
    ]
    return dict(zip(keys, row))

def save_plan(user_id, prediction, targets, actual, plan):
    conn = get_conn()
    conn.execute("""
        INSERT INTO plans(
            user_id,predicted_diet,probabilities_json,target_json,actual_json,
            plan_json,created_at
        ) VALUES(?,?,?,?,?,?,?)
    """, (
        user_id,
        prediction["diet"],
        json.dumps(prediction["probabilities"]),
        json.dumps(targets),
        json.dumps(actual),
        json.dumps(plan),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def load_latest_plan(user_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT id,predicted_diet,probabilities_json,target_json,actual_json,plan_json,created_at
        FROM plans WHERE user_id=? ORDER BY id DESC LIMIT 1
    """, (user_id,)).fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "diet": row[1],
        "probabilities": json.loads(row[2]),
        "targets": json.loads(row[3]),
        "actual": json.loads(row[4]),
        "plan": json.loads(row[5]),
        "created_at": row[6],
    }

def load_history(user_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT id,predicted_diet,target_json,actual_json,created_at
        FROM plans WHERE user_id=? ORDER BY id DESC LIMIT 30
    """, (user_id,)).fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "diet": r[1],
            "targets": json.loads(r[2]),
            "actual": json.loads(r[3]),
            "created_at": r[4],
        }
        for r in rows
    ]
