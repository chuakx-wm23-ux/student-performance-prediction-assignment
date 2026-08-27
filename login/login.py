
from pathlib import Path
import json
import hashlib
import base64
import streamlit as st


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
USERS_FILE = ROOT / "users.json"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    if not USERS_FILE.exists():
        USERS_FILE.write_text(
            json.dumps(
                {
                    "admin": {
                        "password": hash_password("admin123"),
                        "role": "Lecturer"
                    }
                },
                indent=4
            )
        )

    return json.loads(USERS_FILE.read_text())


def save_users(users):
    USERS_FILE.write_text(json.dumps(users, indent=4))


def image_base64(path):
    if path.exists():
        return base64.b64encode(path.read_bytes()).decode()
    return ""


def login_style():
    bg = image_base64(ASSETS / "login_background.png")
    head = image_base64(ASSETS / "ai_head.png")

    st.markdown(
        f"""
        <style>

        .stApp {{
            background:
            linear-gradient(
                rgba(2,6,23,.78),
                rgba(15,23,42,.78)
            ),
            url("data:image/png;base64,{bg}");

            background-size:cover;
            background-position:center;
        }}

        .login-wrapper {{
            min-height:85vh;
            display:flex;
            align-items:center;
            justify-content:center;
            gap:50px;
        }}

        .ai-panel {{
            width:420px;
            height:520px;
            border-radius:35px;
            background:
            linear-gradient(
                145deg,
                rgba(15,23,42,.95),
                rgba(30,64,175,.85)
            );

            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;

            color:white;
            box-shadow:
            0 30px 80px rgba(0,0,0,.45);
        }}

        .ai-head {{
            width:220px;
            height:220px;
            border-radius:50%;
            object-fit:cover;

            box-shadow:
            0 0 60px rgba(56,189,248,.8);
        }}

        .login-card {{
            width:380px;
            padding:35px;

            border-radius:30px;

            background:
            rgba(255,255,255,.92);

            backdrop-filter:blur(20px);

            box-shadow:
            0 30px 70px rgba(0,0,0,.25);
        }}

        .login-title {{
            font-size:28px;
            font-weight:900;
            color:#1e3a8a;
            text-align:center;
        }}

        .login-subtitle {{
            text-align:center;
            color:#64748b;
            margin-bottom:25px;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

    return head


def login_screen():

    login_style()

    users = load_users()

    head = image_base64(ASSETS / "ai_head.png")

    st.markdown(
        f"""
        <div class="login-wrapper">

            <div class="ai-panel">

                {"<img class='ai-head' src='data:image/png;base64," + head + "'>" if head else "🤖"}

                <h1>Student AI</h1>
                <p>
                Intelligent Performance Prediction System
                </p>

            </div>

            <div class="login-card">

        """,
        unsafe_allow_html=True
    )


    tab1, tab2 = st.tabs(
        ["🔐 Login", "📝 Register"]
    )


    with tab1:

        role = st.selectbox(
            "Login As",
            ["Student", "Lecturer"]
        )

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )


        if st.button(
            "🚀 Login",
            use_container_width=True
        ):

            if (
                username in users
                and users[username]["password"] == hash_password(password)
            ):

                if users[username]["role"] == role:

                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = role

                    st.rerun()

                else:
                    st.error(
                        "Wrong account role selected."
                    )

            else:
                st.error(
                    "Invalid username or password."
                )


    with tab2:

        new_user = st.text_input(
            "New Username"
        )

        new_pass = st.text_input(
            "New Password",
            type="password"
        )

        new_role = st.selectbox(
            "Account Type",
            ["Student", "Lecturer"],
            key="register_role"
        )


        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if new_user in users:
                st.warning(
                    "Username already exists."
                )

            elif not new_user or not new_pass:
                st.warning(
                    "Complete all fields."
                )

            else:

                users[new_user] = {
                    "password": hash_password(new_pass),
                    "role": new_role
                }

                save_users(users)

                st.success(
                    "Account created. Please login."
                )


    st.markdown(
        """
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
