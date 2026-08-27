
from pathlib import Path
import json
import hashlib
import base64
import streamlit as st

ROOT = Path(__file__).resolve().parent
USERS_FILE = ROOT.parent / "users.json"

BG_FILE = ROOT / "login_background.png"
HEAD_FILE = ROOT / "ai_head.png"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    if not USERS_FILE.exists():
        users = {
            "educator": {
                "password": hash_password("educator123"),
                "role": "Educator"
            }
        }
        save_users(users)

    return json.loads(USERS_FILE.read_text())


def save_users(users):
    USERS_FILE.write_text(json.dumps(users, indent=4))


def img64(path):
    if path.exists():
        return base64.b64encode(path.read_bytes()).decode()
    return ""


def login_screen():

    bg = img64(BG_FILE)
    head = img64(HEAD_FILE)

    st.markdown(f"""
    <style>

    .stApp {{
        background:
        linear-gradient(
            rgba(2,6,23,.78),
            rgba(15,23,42,.82)
        ),
        url("data:image/png;base64,{bg}");

        background-size:cover;
        background-position:center;
    }}

    .login-wrap {{
        min-height:85vh;
        display:flex;
        justify-content:center;
        align-items:center;
        gap:50px;
    }}

    .ai-card {{
        width:420px;
        height:500px;
        border-radius:35px;
        background:
        linear-gradient(145deg,#020617,#1e3a8a,#4c1d95);
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        color:white;
        box-shadow:0 30px 80px rgba(0,0,0,.45);
    }}

    .ai-head {{
        width:220px;
        height:220px;
        border-radius:50%;
        object-fit:cover;
        box-shadow:0 0 60px #38bdf8;
    }}

    .login-card {{
        width:380px;
        background:rgba(255,255,255,.93);
        padding:35px;
        border-radius:30px;
        box-shadow:0 30px 70px rgba(0,0,0,.3);
    }}

    </style>
    """, unsafe_allow_html=True)

    users = load_users()

    st.markdown(f"""
    <div class="login-wrap">

    <div class="ai-card">
        <img class="ai-head"
        src="data:image/png;base64,{head}">
        <h1>Student AI</h1>
        <p>Intelligent Performance Prediction System</p>
    </div>

    <div class="login-card">

    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        role = st.selectbox(
            "Login As",
            ["Student", "Educator"]
        )

        username = st.text_input("Username")
        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("🚀 Login", use_container_width=True):

            if username in users and users[username]["password"] == hash_password(password):

                if users[username]["role"] == role:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.rerun()

                else:
                    st.error("Wrong account type.")

            else:
                st.error("Invalid username or password.")

    with tab2:
        username = st.text_input("New Username")
        password = st.text_input(
            "New Password",
            type="password"
        )

        role = st.selectbox(
            "Account Type",
            ["Student", "Educator"],
            key="register_role"
        )

        if st.button("Create Account", use_container_width=True):

            if username in users:
                st.warning("Username exists.")

            else:
                users[username] = {
                    "password": hash_password(password),
                    "role": role
                }

                save_users(users)
                st.success("Account created.")

    st.markdown("</div></div>", unsafe_allow_html=True)
