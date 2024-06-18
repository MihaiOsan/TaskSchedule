import streamlit as st
from api_functions import get_tasks_by_user, update_task_status

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = ""
    st.session_state.user_id = ""
    st.session_state.page = "Login"
    st.experimental_rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = ""
    st.session_state.user_id = ""
    st.session_state.page = "Login"
    st.experimental_rerun()

def user_page():
    st.title("User Dashboard")
    if st.button("Logout"):
        logout()

    user_id = st.session_state.user_id
    tasks = get_tasks_by_user(user_id)

    st.subheader("Assigned Tasks")
    for task in tasks:
        if task['status'] != "completed":
            with st.expander(f"**Task:** {task['title']}", expanded=False):
                st.markdown(f"### {task['title']}")
                st.write(f"**Status:** {task['status']}")
                st.write(f"**Description:** {task['description']}")
                col1, col2 = st.columns([1, 1])
                if col1.button("Complete", key=f"complete_{task['id']}"):
                    with st.spinner('Completing task...'):
                        update_task_status(task['id'], "completed")
                    st.experimental_rerun()

    st.subheader("Completed Tasks")
    for task in tasks:
        if task['status'] == "completed":
            with st.expander(f"**Task:** {task['title']}", expanded=False):
                st.markdown(f"### {task['title']}")
                st.write(f"**Status:** {task['status']}")
                st.write(f"**Description:** {task['description']}")
                col1 = st.columns(1)
                if col1[0].button("Reopen", key=f"reopen_{task['id']}"):
                    with st.spinner('Reopening task...'):
                        update_task_status(task['id'], "assigned")
                    st.experimental_rerun()

