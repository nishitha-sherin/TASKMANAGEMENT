# test_api.py
# Run this script to test the API endpoints
# Usage: python test_api.py

import requests
import json

BASE_URL = "http://localhost:8000/api"

# ------------------ LOGIN ------------------ #
def test_login(username="user1", password="user123"):
    """Test user login and get JWT token"""
    print("\n=== Testing Login ===")
    url = f"{BASE_URL}/login/"
    data = {
        "username": username,
        "password": password
    }

    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        token_data = response.json()
        print(f"Access Token: {token_data['access'][:50]}...")
        return token_data['access']
    else:
        print(f"Error: {response.json()}")
        return None
# ------------------ SUPERADMIN LOGIN ------------------ #
def test_admin_login(username="superadmin", password="123456"):
    """Test superadmin login"""
    print("\n=== Testing Super Admin Login ===")
    return test_login(username, password)

# ------------------ GET TASKS ------------------ #
def test_get_tasks(token):
    """Fetch tasks for the logged-in user"""
    print("\n=== Testing Get Tasks ===")
    url = f"{BASE_URL}/tasks/"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        tasks = response.json()
        print(f"Found {len(tasks)} task(s)")
        for task in tasks:
            print(f"  - Task #{task['id']}: {task['title']} (Status: {task['status']})")
        return tasks
    else:
        print(f"Error: {response.json()}")
        return []

# ------------------ UPDATE TASK ------------------ #
def test_update_task(token, task_id):
    """Update task with status, worked hours, and completion report"""
    print(f"\n=== Testing Update Task #{task_id} ===")
    url = f"{BASE_URL}/tasks/update/{task_id}/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "status": "completed",
        "worked_hours": 8.0,
        "completion_report": "Task completed successfully with all requirements met."
    }

    response = requests.put(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        task = response.json()
        print(f"Task updated successfully!")
        print(f"  Status: {task['status']}")
        print(f"  Worked Hours: {task['worked_hours']}")
        print(f"  Report: {task['completion_report'][:100]}...")
    else:
        print(f"Error: {response.json()}")

# ------------------ ADMIN LOGIN ------------------ #
def test_admin_login(username="admin1", password="123456"):
    """Test admin login"""
    print("\n=== Testing Admin Login ===")
    return test_login(username, password)

# ------------------ GET TASK REPORT ------------------ #
def test_get_task_report(token, task_id):
    """Admin/SuperAdmin can get task report"""
    print(f"\n=== Testing Get Task Report #{task_id} ===")
    url = f"{BASE_URL}/tasks/report/"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        report = response.json()
        print(f"Task Report Retrieved:")
        print(f"  Title: {report['title']}")
        print(f"  Assigned To: {report['assigned_to_name']}")
        print(f"  Worked Hours: {report['worked_hours']}")
        print(f"  status: {report['status']}")
        print(f"  Due date: {report['due_date']}...")
    else:
        print(f"Error: {response.json()}")

# ------------------ MAIN ------------------ #
if __name__ == "__main__":
    print("="*60)
    print("Task Management API Test Script")
    print("="*60)

    # User login
    user_token = test_login()
    if user_token:
        tasks = test_get_tasks(user_token)
        if tasks:
            test_update_task(user_token, tasks[0]['id'])

            # Admin login to fetch report
            admin_token = test_admin_login()
            if admin_token:
                test_get_task_report(admin_token, tasks[0]['id'])

    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)
