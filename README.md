# Project Management Tool - Backend

A Django-based backend for managing tasks and subtasks with user authentication and profile management.

---

## Features

- **User Management**: 
  - User registration, login, and logout.
  - Token-based authentication.
  - User profiles with customizable fields (e.g., phone number, color).

- **Task Management**:
  - Create, update, and delete tasks.
  - Support for subtasks, linked to main tasks.
  - Priority management for tasks.

- **API**:
  - RESTful API endpoints for interacting with tasks, subtasks, and user profiles.
  - Token-based authentication for secure access.
  - JSON responses for seamless integration with frontends.

---

## Installation

### Prerequisites

1. Python 3.8 or higher.
2. `pip` for installing Python packages.
3. SQLite (default database) or an alternative database (e.g., PostgreSQL).

---

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/velizarganchev/join-backend.git
   cd join-backend
2. Set up a virtual environment:
   ```bash
    python -m venv env
    env\Scripts\activate
4. Install dependencies:
    ```bash
    pip install -r requirements.txt
6. Apply migrations:
    ```bash
    python manage.py migrate
8. Create a superuser for admin access:
    ```bash
    python manage.py createsuperuser
10. Run the development server:
    ```bash
    python manage.py runserver
    
---

### API Endpoints

- **Authentication**
  - Register: POST /api/register/
  - Login: POST /api/login/
  - Logout: POST /api/logout/

- **User Profiles**
  - Get Profile: GET /api/user-profile/id/
  - Update Profile: PUT /api/user-profile/id/
  - Delete User and Profile: DELETE /api/user-profile/id/

- **Tasks**
  - Get All Tasks: GET /api/tasks/
  - Get Task by ID: GET /api/tasks/id/
  - Create Task: POST /api/tasks/
  - Update Task: PUT /api/tasks/id/
  - Delete Task: DELETE /api/tasks/id/

- **Subtasks**
  - Get Subtasks for a Task: GET /api/tasks/id/subtasks/
  - Create Subtask: POST /api/tasks/id/subtasks/
  - Update Subtask: PUT /api/subtasks/id/
  - Delete Subtask: DELETE /api/subtasks/id/

---

### Notes
The BASE_URL for all API endpoints is typically http://127.0.0.1:8000 during development.
Make sure to configure CORS settings in settings.py to allow your frontend to communicate with the backend.

---

### Contact
For questions or feedback, please reach out via GitHub: velizarganchev.
