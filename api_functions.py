import requests
import streamlit as st

API_URL = "https://jz6rlgqo2g.execute-api.eu-west-3.amazonaws.com"  # Înlocuiește cu URL-ul tău

def login(email, password):
    response = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
    if response.status_code == 200:
        return response.json()
    else:
        return {"message": "Invalid email or password"}

def get_task_by_id(task_id):
    response = requests.get(f"{API_URL}/tasks/{task_id}")
    return response.json()

def get_tasks():
    response = requests.get(f"{API_URL}/tasks")
    return response.json()

def get_unassigned_tasks():
    response = requests.get(f"{API_URL}/tasks")
    tasks = response.json()
    unassigned_tasks = [task for task in tasks if task['status'] == 'created']
    return unassigned_tasks

def get_tasks_by_user(user_id):
    response = requests.get(f"{API_URL}/tasks/user/{user_id}")
    return response.json()

def create_task(task):
    response = requests.post(f"{API_URL}/tasks", json=task)
    return response.json()

def create_user(user):
    response = requests.post(f"{API_URL}/users", json=user)
    return response.json()

def get_non_admin_users():
    response = requests.get(f"{API_URL}/users")
    users = response.json()
    non_admin_users = [user for user in users if user['role'] == 'user']
    return non_admin_users

def assign_task(task_id, user_id):
    payload = {
        "idUser": user_id,
        "status": "assigned"
    }
    response = requests.put(f"{API_URL}/tasks/{task_id}", json=payload)
    if response.status_code == 200:
        return {"statusCode": response.status_code, "message": response.text}
    else:
        return {"statusCode": response.status_code, "message": response.text}

def update_task_status(task_id, status):
    response = requests.put(f"{API_URL}/tasks/{task_id}", json={"status": status})
    return response.json()

def update_task(task_id, title=None, description=None):
    data = {}
    if title is not None:
        data['title'] = title
    if description is not None:
        data['description'] = description

    if not data:
        st.write("no data")
        return {"message": "No updates provided"}

    st.write(f"Updating task {task_id} with data: {data}")
    response = requests.put(f"{API_URL}/tasks/{task_id}", json=data)

    try:
        response.raise_for_status()
        st.write(f"Update successful: {response.json()}")
        return response.json()
    except requests.exceptions.HTTPError as err:
        st.write(f"Update failed: {str(err)}, {response.text}")
        return {"message": str(err), "response": response.json()}
    except Exception as e:
        st.write(f"Unexpected error: {e}, {response.text}")
        return {"message": "Unexpected error", "response": response.text}

def delete_task(task_id):
    response = requests.delete(f"{API_URL}/tasks/{task_id}")
    return response.json()

def get_tasks_by_user(user_id):
    response = requests.get(f"{API_URL}/tasks/user/{user_id}")
    return response.json()

def update_task(task_id, **kwargs):
    response = requests.put(f"{API_URL}/tasks/{task_id}", json=kwargs)
    return response.json()

def delete_user(user_id):
    response = requests.delete(f"{API_URL}/users/{user_id}")
    return response.json()
