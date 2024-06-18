import streamlit as st
from auth import login_page
from admin_pages import admin_page
from user_pages import user_page

def main():
    st.markdown(
        """
        <style>
        .centered {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        </style>
        """, unsafe_allow_html=True
    )

    st.markdown('<div class="centered"><h1>Task Management System</h1></div>', unsafe_allow_html=True)

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = ""
        st.session_state.user_id = ""
        st.session_state.page = "Login"

    if st.session_state.logged_in:
        if st.session_state.user_role == "admin":
            admin_page()
        else:
            user_page()
    else:
        login_page()

if __name__ == "__main__":
    main()
