
import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nutriplan.db")
COOKIE_NAME = "remember_token"
COOKIE_PASSWORD = os.environ.get(
    "NUTRIPLAN_COOKIE_PASSWORD",
    "NutriPlan-AI-change-this-cookie-secret"
)

def db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_auth_db():
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS login_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def _hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000
    )
    return salt, digest.hex()

def verify_password(password, salt, stored_hash):
    _, digest = _hash_password(password, salt)
    return hmac.compare_digest(digest, stored_hash)

def register_user(name, email, password):
    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password:
        return False, "Please fill in all fields."
    if len(password) < 6:
        return False, "Password must contain at least 6 characters."

    salt, password_hash = _hash_password(password)
    conn = db()
    try:
        conn.execute(
            "INSERT INTO users(name,email,password_hash,salt,created_at) VALUES(?,?,?,?,?)",
            (name, email, password_hash, salt, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False, "An account with this email already exists."
    conn.close()
    return True, "Account created. You can now log in."

def authenticate(email, password):
    email = email.strip().lower()
    conn = db()
    row = conn.execute(
        "SELECT id,name,email,password_hash,salt FROM users WHERE email=?",
        (email,)
    ).fetchone()
    conn.close()

    if not row or not verify_password(password, row[4], row[3]):
        return None

    return {"id": row[0], "name": row[1], "email": row[2]}

def get_cookie_manager():
    return EncryptedCookieManager(
        prefix="nutriplan_ai/",
        password=COOKIE_PASSWORD
    )

def remember_user(user_id, cookies, days=30):
    raw_token = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires = datetime.now(timezone.utc) + timedelta(days=days)

    conn = db()
    conn.execute(
        "INSERT INTO login_tokens(user_id,token_hash,expires_at) VALUES(?,?,?)",
        (user_id, token_hash, expires.isoformat())
    )
    conn.commit()
    conn.close()

    cookies[COOKIE_NAME] = raw_token
    cookies.save()

def restore_user_from_cookie(cookies):
    try:
        raw_token = cookies.get(COOKIE_NAME)
    except Exception:
        return None

    if not raw_token:
        return None

    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    now = datetime.now(timezone.utc)

    conn = db()
    row = conn.execute("""
        SELECT u.id,u.name,u.email,t.expires_at
        FROM login_tokens t
        JOIN users u ON u.id=t.user_id
        WHERE t.token_hash=?
    """, (token_hash,)).fetchone()

    if not row:
        conn.close()
        return None

    try:
        expires = datetime.fromisoformat(row[3])
    except ValueError:
        conn.close()
        return None

    if expires <= now:
        conn.execute("DELETE FROM login_tokens WHERE token_hash=?", (token_hash,))
        conn.commit()
        conn.close()
        return None

    conn.close()
    return {"id": row[0], "name": row[1], "email": row[2]}

def clear_remembered_login(cookies):
    try:
        raw_token = cookies.get(COOKIE_NAME)
        if raw_token:
            token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
            conn = db()
            conn.execute("DELETE FROM login_tokens WHERE token_hash=?", (token_hash,))
            conn.commit()
            conn.close()
        cookies[COOKIE_NAME] = ""
        cookies.save()
    except Exception:
        pass

def login_into_session(user):
    st.session_state["user"] = user

def logout():
    st.session_state.pop("user", None)
    st.session_state.pop("profile", None)
    st.session_state.pop("plan", None)
    st.session_state.pop("prediction", None)
    st.session_state.pop("targets", None)

def current_user():
    return st.session_state.get("user")

def require_login():
    if not st.session_state.get("user"):
        st.switch_page("app.py")
        st.stop()
