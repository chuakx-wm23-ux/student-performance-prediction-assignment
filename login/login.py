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

    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def get_image(path):
    if path.exists():
        return base64.b64encode(
            path.read_bytes()
        ).decode()
    return ""


def login_screen():

    users = load_users()

    bg = get_image(BG_FILE)
    head = get_image(HEAD_FILE)


    st.markdown(
        f"""
        <style>

        .stApp {{
            background-image:
            linear-gradient(
            rgba(3,10,35,0.75),
            rgba(10,20,60,0.85)
            ),
            url("data:image/png;base64,{bg}");

            background-size:cover;
            background-position:center;
        }}


        .title {{
            text-align:center;
            color:white;
            font-size:42px;
            font-weight:700;
        }}


        .subtitle {{
            text-align:center;
            color:#cbd5e1;
            font-size:18px;
        }}


        .box {{
            background:rgba(255,255,255,0.95);
            padding:35px;
            border-radius:25px;
            box-shadow:
            0 20px 60px rgba(0,0,0,.3);
        }}


        .head {{
            width:230px;
            height:230px;
            border-radius:50%;
            object-fit:cover;
            box-shadow:
            0 0 50px #38bdf8;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


    col1,col2 = st.columns(
        [1,1],
        gap="large"
    )


    with col1:

        st.markdown(
            f"""
            <div style="
            text-align:center;
            padding-top:80px;
            ">

            <img class="head"
            src="data:image/png;base64,{head}">

            <h1 class="title">
            Student AI
            </h1>

            <p class="subtitle">
            Intelligent Performance Prediction System
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            '<div class="box">',
            unsafe_allow_html=True
        )


        tab1,tab2 = st.tabs(
            [
                "🔐 Login",
                "📝 Register"
            ]
        )


        with tab1:

            role = st.selectbox(
                "Login As",
                [
                    "Student",
                    "Educator"
                ]
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

                if username in users:

                    if users[username]["password"] == hash_password(password):

                        if users[username]["role"] == role:

                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.session_state.role = role

                            st.rerun()

                        else:
                            st.error(
                                "Wrong account type"
                            )

                    else:
                        st.error(
                            "Wrong password"
                        )

                else:
                    st.error(
                        "User not found"
                    )


        with tab2:

            username = st.text_input(
                "Create Username"
            )

            password = st.text_input(
                "Create Password",
                type="password"
            )


            role = st.selectbox(
                "Register As",
                [
                    "Student",
                    "Educator"
                ]
            )


            if st.button(
                "Create Account",
                use_container_width=True
            ):

                if username in users:

                    st.warning(
                        "Username already exists"
                    )

                else:

                    users[username]={
                        "password":
                        hash_password(password),

                        "role":
                        role
                    }

                    save_users(users)

                    st.success(
                        "Account created"
                    )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )
