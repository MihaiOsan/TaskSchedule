import streamlit as st
from api_functions import login

def login_page():
    st.markdown('<div class="centered"><h2>Login</h2></div>', unsafe_allow_html=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        with st.spinner('Logging in...'):
            user = login(email, password)
        if "id" in user:
            st.session_state.logged_in = True
            st.session_state.user_role = user["role"]
            st.session_state.user_id = user["id"]
            st.success("Logged in successfully")
            st.session_state.page = "Manage Tasks" if user["role"] == "admin" else "User Dashboard"
            st.rerun()
        else:
            st.error(user["message"])
