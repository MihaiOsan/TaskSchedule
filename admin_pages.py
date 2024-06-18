import time
import re
import uuid
import streamlit as st
from api_functions import get_unassigned_tasks, get_non_admin_users, assign_task, get_tasks, update_task_status, \
    delete_task, create_task, create_user, update_task, get_task_by_id, login, get_tasks_by_user, delete_user


def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = ""
    st.session_state.user_id = ""
    st.session_state.page = "Login"
    st.experimental_rerun()

def admin_page():
    st.markdown('<div class="centered"><h2>Admin Dashboard</h2></div>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
    with col1:
        if st.button("Manage Tasks", key="manage_tasks"):
            st.session_state.page = "Manage Tasks"
    with col2:
        if st.button("Create Task", key="create_task"):
            st.session_state.page = "Create Task"
    with col3:
        if st.button("Create User", key="create_user"):
            st.session_state.page = "Create User"
    with col4:
        if st.button("Assign Task", key="assign_task"):
            st.session_state.page = "Assign Task"
    with col5:
        if st.button("Logout", key="logout"):
            logout()

    st.write("---")

    if st.session_state.page == "Create Task":
        create_task_page()
    elif st.session_state.page == "Assign Task":
        assign_task_page()
    elif st.session_state.page == "Create User":
        create_user_page()
    elif st.session_state.page == "Manage Tasks":
        manage_tasks_page()


def assign_task_page():
    st.subheader("Assign Task to User")

    # Fetch unassigned tasks and non-admin users
    tasks = get_unassigned_tasks()
    users = get_non_admin_users()
    assigned_tasks = [task for task in get_tasks() if task['status'] == 'assigned']
    user_dict = {user['id']: user['email'] for user in users}  # Map user IDs to emails

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Unassigned Tasks")
        for task in tasks:
            is_selected = st.session_state.get('selected_task_id') == task['id']
            task_button_label = f"{task['title']}" + (" (Selected)" if is_selected else "")
            if st.button(task_button_label, key=f"select_task_{task['id']}", use_container_width=True):
                if is_selected:
                    del st.session_state['selected_task_id']
                    del st.session_state['selected_task_title']
                else:
                    st.session_state['selected_task_id'] = task['id']
                    st.session_state['selected_task_title'] = task['title']
                st.experimental_rerun()

    with col2:
        st.write("### Users")
        for user in users:
            is_selected = st.session_state.get('selected_user_id') == user['id']
            user_button_label = f"{user['email']}" + (" (Selected)" if is_selected else "")
            if st.button(user_button_label, key=f"assign_user_{user['id']}", use_container_width=True):
                if is_selected:
                    del st.session_state['selected_user_id']
                else:
                    st.session_state['selected_user_id'] = user['id']
                st.experimental_rerun()

    st.write("---")

    # Caseta pentru afișarea taskului și utilizatorului selectat
    if 'selected_task_id' in st.session_state and 'selected_user_id' in st.session_state:
        st.write("### Selected Task and User")
        selected_user_email = user_dict.get(st.session_state['selected_user_id'], 'Unknown')
        st.info(f"Task: {st.session_state['selected_task_title']}\nUser: {selected_user_email}")

        if st.button("Complete Assignment", use_container_width=True):
            task_id = st.session_state['selected_task_id']
            user_id = st.session_state['selected_user_id']
            st.write(f"Attempting to assign Task ID: {task_id} to User ID: {user_id}")  # Debug message
            try:
                response = assign_task(task_id, user_id)
                st.write(f"API Response: {response}")  # Debug message
                if isinstance(response, dict) and response.get('statusCode', 200) == 200:
                    st.success(f"Task {task_id} assigned to user {user_id}")
                    del st.session_state['selected_task_id']
                    del st.session_state['selected_task_title']
                    del st.session_state['selected_user_id']
                    time.sleep(2)  # Așteaptă 2 secunde pentru a permite afișarea mesajului de succes
                    st.experimental_rerun()
                else:
                    st.error("Failed to assign task. Please try again.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.write(f"Exception details: {e}")  # Debug message

    st.write("---")

    st.write("### Assigned Tasks")
    for task in assigned_tasks:
        user_email = user_dict.get(task['idUser'], 'Unknown')
        task_info = f"{task['title']} - {user_email}"
        task_container = st.container()
        with task_container:
            col_task, col_unassign, col_delete = st.columns([3, 1, 1])
            col_task.write(task_info)
            if col_unassign.button("Unassign", key=f"unassign_{task['id']}", use_container_width=True):
                response = update_task_status(task['id'], "created")
                if response:
                    st.success(f"Task {task['id']} unassigned")
                    st.experimental_rerun()
            if col_delete.button("Delete", key=f"delete_{task['id']}", use_container_width=True):
                response = delete_task(task['id'])
                if response:
                    st.success(f"Task {task['id']} deleted")
                    st.experimental_rerun()

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
            st.session_state.page = "Admin Dashboard" if user["role"] == "admin" else "User Dashboard"
            st.experimental_rerun()
        else:
            st.error(user["message"])

def create_task_page():
    st.subheader("Create a New Task")
    title_new = st.text_input("Title", key="title_new")
    description_new = st.text_area("Description", key="description_new")
    if st.button("Create Task", key="create_task_button"):
        with st.spinner('Creating task...'):
            task_id = str(uuid.uuid4())
            task = {
                "id": task_id,
                "title": title_new,
                "description": description_new
            }
            response = create_task(task)
            st.text_area
        st.write(response)
        

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def create_user_page():
    st.subheader("Create a New User")
    email = st.text_input("Email", key="email")
    password = st.text_input("Password", type="password", key="password")
    role = st.selectbox("Role", ["user","admin"], key="role")

    if st.button("Create User", key="create_user_button"):
        if not is_valid_email(email):
            st.error("Invalid email format")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters long")
        else:
            with st.spinner('Creating user...'):
                user_id = str(uuid.uuid4())
                user = {
                    "id": user_id,
                    "email": email,
                    "password": password,
                    "role": role
                }
                response = create_user(user)
                st.write(response)

    st.write("---")

    st.subheader("Existing Users")
    users = get_non_admin_users()

    for user in users:
        st.write(user['email'])
        if st.button("Delete", key=f"delete_user_{user['id']}"):
            with st.spinner('Deleting user...'):
                tasks = get_tasks_by_user(user['id'])
                for task in tasks:
                    update_task_status(task['id'], "created")
                    # Remove user ID from the task
                    update_task(task['id'], idUser=None)
                response = delete_user(user['id'])
                if response:
                    st.success(f"User {user['email']} deleted")
                    st.experimental_rerun()


def manage_tasks_page():
    st.subheader("Manage Tasks")

    # Filter tasks by status
    status_filter = st.selectbox("Filter by Status", options=["All", "created", "assigned", "completed"], index=0)

    tasks = get_tasks()
    if status_filter != "All":
        tasks = [task for task in tasks if task["status"] == status_filter]

    # CSS styles for better appearance
    st.markdown("""
        <style>
        .task-row {
            padding: 10px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        .task-title {
            font-size: 16px;
            font-weight: bold;
        }
        .edit-btn, .delete-btn, .update-btn, .cancel-btn {
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
            margin: 0 5px;
        }
        .edit-btn {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
        }
        .delete-btn {
            background-color: #f44336;
            color: white;
            border: none;
            border-radius: 5px;
        }
        .update-btn {
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 5px;
        }
        .cancel-btn {
            background-color: #f44336;
            color: white;
            border: none;
            border-radius: 5px;
        }
        .button-container {
            display: flex;
            justify-content: flex-end;
            margin-top: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

    # Display tasks with edit and delete buttons
    for task in tasks:
        st.markdown("<div class='task-row'>", unsafe_allow_html=True)
        col_task, col_edit, col_delete = st.columns([3, 1, 1])
        col_task.markdown(f"<span class='task-title'>{task['title']} - {task['status']}</span>", unsafe_allow_html=True)

        if task['status'] == "created":
            if col_edit.button("Edit", key=f"edit_{task['id']}", help="Edit Task"):
                st.session_state[f"edit_mode_{task['id']}"] = True
        else:
            col_edit.write("Cannot Edit")

        if col_delete.button("Delete", key=f"delete_{task['id']}", help="Delete Task"):
            response = delete_task(task['id'])
            if response:
                st.success(f"Task {task['id']} deleted")
                st.experimental_rerun()

        if st.session_state.get(f"edit_mode_{task['id']}", False):
            task_details = get_task_by_id(task['id'])
            st.markdown("**Editing Task**")
            title = st.text_input("Title", value=task_details.get('title', ''), key=f"title_{task['id']}")
            description = st.text_area("Description", value=task_details.get('description', ''), key=f"description_{task['id']}")

            st.markdown('<div class="button-container">', unsafe_allow_html=True)
            col3, col4 = st.columns([1, 1])
            if col3.button("Update Task", key=f"update_{task['id']}", help="Update Task", use_container_width=True):
                try:
                    st.write("Updating task...")  # Debug message
                    data = {
                        "title": title if title != task_details.get('title') else None,
                        "description": description if description != task_details.get('description') else None
                    }
                    # Remove None values from data
                    data = {k: v for k, v in data.items() if v is not None}
                    st.write(f"Updating task {task['id']} with data: {data}")  # Debug message
                    response = update_task(task['id'], **data)
                    st.write(f"Response: {response}")  # Debug message
                    time.sleep(3)  # Wait 3 seconds after submit
                    if isinstance(response, dict) and "message" in response and response["message"] == "No updates provided":
                        st.warning("No updates provided.")
                    elif isinstance(response, dict) and response.get("statusCode", 200) == 200:
                        st.success(f"Task {task['id']} updated successfully.")
                        st.session_state[f"edit_mode_{task['id']}"] = False
                        st.experimental_rerun()
                    else:
                        st.success(response)  # If the response is a string, consider the update successful
                        st.session_state[f"edit_mode_{task['id']}"] = False
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

            if col4.button("Cancel", key=f"cancel_{task['id']}", help="Cancel Update", use_container_width=True):
                st.session_state[f"edit_mode_{task['id']}"] = False
                st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# Testarea funcției
if __name__ == "__main__":
    if 'session_initialized' not in st.session_state:
        st.session_state.session_initialized = True
        # Initialize edit_mode for all tasks to False
        tasks = get_tasks()
        for task in tasks:
            st.session_state[f"edit_mode_{task['id']}"] = False

    manage_tasks_page()



if __name__ == "__main__":
    admin_page()
