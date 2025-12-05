import streamlit as st
from auth_db import user_exists, register_user, verify_user

# ---------- Initialise session state ----------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

st.title("🔐 Welcome")

# If already logged in, go straight to dashboard
if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}**.")
    if st.button("Go to Dashboard"):
        st.switch_page("pages/1_Dashboard.py")
    st.stop()

# ---------- Tabs ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", type="primary"):
       if verify_user(login_username, login_password):
         st.session_state.logged_in = True
         st.session_state.username = login_username
         st.success(f"Welcome back, {login_username}! ")
         st.switch_page("pages/1_Dashboard.py")
       else:
         st.error("Invalid username or password.")
# ----- REGISTER TAB -----
with tab_register:
    st.subheader("Register")

    new_username = st.text_input("Choose a username", key="register_username")
    new_password = st.text_input("Choose a password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")

    if st.button("Create account"):
     if not new_username or not new_password:
        st.warning("Please fill in all fields.")
     elif new_password != confirm_password:
        st.error("Passwords do not match.")
     elif user_exists(new_username):
        st.error("Username already exists.")
     else:
        register_user(new_username, new_password)
        st.success("Account created! You can now log in.")


