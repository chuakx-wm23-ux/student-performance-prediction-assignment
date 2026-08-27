from pathlib import Path
import json
import hashlib
import streamlit as st

ROOT = Path(__file__).resolve().parent
USERS_FILE = ROOT / "users.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not USERS_FILE.exists():
        USERS_FILE.write_text(json.dumps({
            "admin": {
                "password": hash_password("admin123"),
                "role": "Lecturer"
            }
        }, indent=4))
    return json.loads(USERS_FILE.read_text())

def save_users(users):
    USERS_FILE.write_text(json.dumps(users, indent=4))

def login_screen():
    st.markdown("""
    <div class="login-premium">
        <div class="login-ai-card">
            <div class="login-ai-head">🤖</div>
            <h2 style="color:white;margin-top:25px;">Student AI</h2>
            <p style="color:#cbd5e1;">Intelligent Performance Prediction System</p>
        </div>
        <div class="login-role-card">
    """, unsafe_allow_html=True)

    users = load_users()
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        role = st.selectbox("Login As", ["Student", "Lecturer"])
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("🚀 Login", use_container_width=True):
            if username in users and users[username]["password"] == hash_password(password):
                if users[username]["role"] == role:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.rerun()
                else:
                    st.error("Account role does not match selected login type.")
            else:
                st.error("Invalid username or password.")

    with tab2:
        new_user = st.text_input("Create Username", key="reg_user")
        new_pass = st.text_input("Create Password", type="password", key="reg_pass")
        new_role = st.selectbox("Register As", ["Student", "Lecturer"], key="reg_role")

        if st.button("Create Account", use_container_width=True):
            if new_user in users:
                st.warning("Username already exists.")
            elif not new_user or not new_pass:
                st.warning("Please complete all fields.")
            else:
                users[new_user] = {
                    "password": hash_password(new_pass),
                    "role": new_role
                }
                save_users(users)
                st.success("Account created. Please login.")

    st.markdown("</div></div>", unsafe_allow_html=True)
