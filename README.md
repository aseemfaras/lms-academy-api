# LMS System Documentation & Business Requirements Document (BRD)

## 1. Executive Summary

The LMS System is a robust, modular, and RESTful web application designed to manage educational content, student enrollments, and live sessions. The system is split into a **React Frontend** and a **Django+DRF Backend**. The backend provides a powerful API layer, utilizes **PostgreSQL** for relational data storage, and employs **SimpleJWT** for stateless authentication. Role-Based Access Control (RBAC) securely separates operations and data visibility among Students, Trainers, and Administrators.

---

## 2. Tech Stack & Infrastructure

- **Frontend Runtime**: Node.js + Vite (React)
- **Backend Runtime**: Python 3.10+
- **Backend Framework**: Django 6.0.2 + Django REST Framework (DRF)
- **Database**: PostgreSQL
- **Authentication**: `djangorestframework-simplejwt` (JSON Web Tokens)
- **CORS Handling**: `django-cors-headers`

---

## 3. Detailed Folder Structure

The backend follows a service-oriented Django Application pattern to separate concerns tightly. It relies on a central config project and modularized apps.

### Project Root: `lms-backend/`

```text
lms-backend/
│
├── apps/                        # The core logic of the application, separated by domain
│   ├── users/                   # Authentication, User definitions, Roles
│   │   ├── models.py            # Definition of custom User model (`login_users` table)
│   │   ├── serializers.py       # Serializes Auth/JWT payloads
│   │   ├── urls.py              # Auth endpoints (/login/, /register/)
│   │   └── views.py             # CustomTokenObtainPairView (Login logic)
│   │
│   ├── trainers/                # Course creation, Module definitions, Live Sessions
│   │   ├── models.py            # Course, Module, and Session schemas
│   │   ├── serializers.py       # Transforms Course/Session objects to JSON
│   │   ├── urls.py              # Instructor API routes
│   │   └── views.py             # Logic for managing courses and sessions
│   │
│   ├── students/                # Enrollment tracking and student portals
│   │   ├── models.py            # Enrollment relations
│   │   ├── urls.py              # Student portal routes
│   │   └── views.py             # Logic for fetching enrolled courses & progress
│   │
│   ├── admins/                  # Administrative system oversight logic
│   └── supporters/              # Optional support portal
│
├── config/                      # Global server configurations
│   ├── settings.py              # Master settings (DB keys, CORS, App Registrations)
│   ├── urls.py                  # Master URL routing table (Root router)
│   └── wsgi.py / asgi.py        # Gateway interface for Gunicorn/Uvicorn
│
├── env/                         # Isolated Python Virtual Environment
├── db.sqlite3                   # Legacy/Fallback local database
├── manage.py                    # Django CLI for server operations and migrations
├── error.log                    # Centralized rotating diagnostic log file
└── sql_queries.log              # Log of executed database queries for debugging
```

---

## 4. Connection Architecture

This section details how the three pillars of the system (Frontend, Backend, Database) interconnect.

### A. Frontend to Backend Connection (CORS & APIs)

The React frontend communicates securely cross-origin with the Django backend. This connection is now managed via environment variables in the `.env` file for better security and smoother deployment.

**Backend Configuration (`config/settings.py`):**
The backend reads the `FRONTEND_URL` from `.env` to allow cross-origin requests.
```python
# config/settings.py
FRONTEND_URL = env('FRONTEND_URL', default='http://localhost:5173')
CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:5177",
    "http://127.0.0.1:5177",
]
CORS_ALLOW_CREDENTIALS = True
```

**Frontend call (Environment Variable):**
Instead of hardcoding the URL, the frontend should use an environment variable.
```javascript
// Example: Using Vite environment variable
const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000/api/";
const response = await axios.post(`${apiUrl}users/login/`, { ... });
```

### B. Backend to Database Connection (PostgreSQL)

The Django ORM handles all database transactions. The explicit connection credentials are now managed via the `.env` file.

```python
# config/settings.py
DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE'),
        'NAME': env('DB_NAME'),          # Target Database (lms_aideas)
        'USER': env('DB_USER'),          # Database User (postgres)
        'PASSWORD': env('DB_PASSWORD'),  # Master DB Password (tiger)
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}
```

By changing these parameters, the system can seamlessly swap between local environments and cloud-hosted databases (e.g., AWS RDS).

---

## 5. System Workflow (Step-by-Step API Execution)

To understand the core backend flow, here is the lifecycle of a single HTTP request, using the User Login process as an example.

### Step 1: URL Routing (Master to App)
The incoming request (`POST /api/users/login/`) first hits the Master URL configuration.
```python
# config/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')), # Request routed to Users App
    path('api/students/', include('students.urls')),
    path('api/', include('trainers.urls')),
]
```

### Step 2: App URL Resolution
Inside the `users` app, the specific endpoint is bound to a View.
```python
# apps/users/urls.py
urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
]
```

### Step 3: View Processing & Serialization
The `CustomTokenObtainPairView` intercepts the JSON payload. It passes the payload to a Serializer to validate the credentials against the PostgreSQL database.
If valid, the system provisions a JWT and returns the User's explicit Role.

```python
# apps/users/views.py (Conceptual Extract)
class CustomTokenObtainPairView(TokenObtainPairView):
    # Transforms payload and overrides default JWT behavior
    # Returns: { "access": "...", "refresh": "...", "role": "STUDENT" }
    pass
```

### Step 4: Subsequent Authenticated Requests
Once the client has the token, they include it in the Header of future requests.
`Authorization: Bearer <access_token>`

Django REST Framework validates this automatically globally:
```python
# config/settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}
```

---

## 6. Core Modules & Data Relationships

### A. Users Module (`apps/users`)
- Serves as the identity foundation.
- Extends the baseline `AbstractUser` to use `email` as the absolute primary key instead of the traditional username.
- Handles Role assignments (`ADMIN`, `TRAINER`, `STUDENT`).

### B. Trainers (Core Academic) Module (`apps/trainers`)
- Handles syllabus configurations.
- `Course`: The overarching subject. Attached to a specific `instructor_id`.
- `Module`: Chapters or sub-sections belonging to a specific Course.

### C. Students (Enrollment) Module (`apps/students`)
- Defines the many-to-many relationship between Users and Courses.
- Maintains completion metrics and timeline statuses (e.g., dropping out or graduating).

---

## 7. Database Schema Reference

### Core Tables

| Table Name | Source Model | Core Purpose | Important Relations |
| :--- | :--- | :--- | :--- |
| `users_user` | `users.User` | Identity Management | PK: `id`, Unique: `email` |
| `trainers_course` | `trainers.Course` | Course Catalog | FK: `instructor_id` -> `users_user.id` |
| `trainers_module` | `trainers.Module` | Course Syllabus | FK: `course_id` -> `trainers_course.id` |
| `students_enroll` | `students.Enrollment` | Track Student Activity| FK `student_id` -> `users_user.id`, FK `course_id` -> `trainers_course.id` |

---

## 8. Setup & Diagnostics

### Standard Environment Initialization
```bash
# Set up isolated Python env
python -m venv env
source env/Scripts/activate

# Install Django & DB tools
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers psycopg2-binary

# Apply Table Schemas to PostgreSQL
python manage.py makemigrations
python manage.py migrate
```

### Running Server & Logs
To run the server locally:
```bash
python manage.py runserver 0.0.0.0:8000
```

**Diagnostics**: The system is configured to actively log all SQL queries inside `sql_queries.log` and standard application exceptions inside `error.log`. These should be monitored during active frontend development to trace API payload bottlenecks.
