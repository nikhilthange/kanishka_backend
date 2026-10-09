# AI-Powered Task Management System

[![CI Pipeline](https://github.com/nikhilthange/kanishka_backend/actions/workflows/ci.yml/badge.svg)](https://github.com/nikhilthange/kanishka_backend/actions)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20%7C%20MySQL%20%7C%20SQLite-336791.svg)](https://www.sqlalchemy.org/)
[![Migrations](https://img.shields.io/badge/Migrations-Alembic-red.svg)](https://alembic.sqlalchemy.org/)
[![Security](https://img.shields.io/badge/Auth-JWT%20%2B%20Bcrypt-orange.svg)](https://pyjwt.readthedocs.io/)
[![AI Integration](https://img.shields.io/badge/AI-Gemini%20%7C%20OpenAI%20%7C%20Claude-purple.svg)](https://ai.google.dev/)
[![Tests](https://img.shields.io/badge/Tests-34%2F34%20Passing-brightgreen.svg)](https://pytest.org/)

A production-ready **AI-Powered Task Management System** developed for the **Kanishka Software Python & AI Integration Intern Assessment**. 

This application provides a secure REST API backend built with **FastAPI**, featuring JWT authentication, strict role-based access control (RBAC), multi-database support (PostgreSQL / MySQL with Alembic schema migrations and seeders), and dual **AI capabilities** (generating actionable task descriptions and concise task summaries).

```mermaid
graph TD
    Client[HTTP Client / Postman / Swagger UI] -->|Bearer JWT| FastAPI[FastAPI REST API /api]
    FastAPI --> AuthMiddleware[Auth & Security Middleware]
    AuthMiddleware -->|Validate JWT| RBAC[RBAC Permission Validator]
    RBAC -->|Admin / User Authorized| Service[Task & Auth Service Layer]
    Service -->|SQLAlchemy ORM| DB[(PostgreSQL / MySQL / SQLite)]
    Service -->|Pluggable Interface| AIService[AI Service Layer]
    AIService -->|Google SDK| Gemini[Google Gemini LLM]
    AIService -->|OpenAI SDK| OpenAI[OpenAI GPT-4o-mini]
    AIService -->|Anthropic SDK| Claude[Anthropic Claude 3.5 / Haiku]
    AIService -->|Zero-Config Fallback| Mock[Intelligent Offline Mock Provider]
```

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Python Version & Tech Stack](#python-version--tech-stack)
3. [Project Structure](#project-structure)
4. [Setup & Installation](#setup--installation)
5. [Database Configuration & Migrations](#database-configuration--migrations)
6. [Database Seeding](#database-seeding)
7. [Environment Variables](#environment-variables)
8. [AI Configuration](#ai-configuration)
9. [How to Run the Application](#how-to-run-the-application)
10. [Test Credentials](#test-credentials)
11. [API Endpoints Reference](#api-endpoints-reference)
12. [Role-Based Access Control (RBAC) Matrix](#role-based-access-control-rbac-matrix)
13. [AI Features Implemented](#ai-features-implemented)
14. [Automated Test Suite (pytest)](#automated-test-suite-pytest)
15. [Postman Collection Guide](#postman-collection-guide)
16. [Key Architectural Decisions & Assumptions](#key-architectural-decisions--assumptions)

---

## Project Overview

The system allows authenticated users to create and manage development tasks with rigorous permission boundaries:
- **Regular Users** can register, authenticate, create tasks, view their own tasks, and modify their own task titles and descriptions. Regular users are strictly prevented from modifying other users' tasks and **cannot update task status**.
- **Administrators** possess full oversight: they can view all tasks across the platform, edit any task, and exclusively have authorization to update task statuses (`Pending`, `In Progress`, `Testing`, `Completed`).
- **AI Integration**: Implements **both Option A** (AI Task Description Generator) and **Option B** (AI Task Summarization), supporting Google Gemini and OpenAI with graceful fallback and structured response validation.

---

## Python Version & Tech Stack

- **Python Version**: `3.11.x` (compatible with `>=3.11`)
- **Web Framework**: FastAPI (`0.110.0+`)
- **ASGI Server**: Uvicorn (`0.28.0+`)
- **Data Validation & Settings**: Pydantic v2 & Pydantic-Settings
- **ORM**: SQLAlchemy 2.0 (Declarative Mapping)
- **Database Migrations**: Alembic
- **Database Drivers**:
  - PostgreSQL: `psycopg` (v3) & `psycopg2-binary`
  - MySQL: `pymysql`
  - SQLite: Built-in `sqlite3`
- **Security & Password Hashing**: Native `bcrypt` (12 rounds) & `PyJWT` (HS256)
- **AI SDKs**: `google-generativeai` (Google Gemini) & `openai` (GPT-4o-mini)
- **HTTP Client & Testing**: `httpx`, `pytest`, `pytest-asyncio`
- **Containerization**: Docker & Docker Compose

---

## Project Structure

Organized strictly following the modular separation requested in Section 7 of the specification:

```text
kanishka_python/
├── alembic/                      # Database migrations
│   ├── versions/
│   │   └── 0001_initial_schema.py # Initial tables migration
│   ├── env.py                   # Alembic environment config
│   └── script.py.mako
├── app/
│   ├── ai/                      # AI LLM Integration layer
│   │   ├── __init__.py
│   │   ├── base.py              # BaseAIProvider abstract class
│   │   ├── gemini_provider.py   # Google Gemini implementation
│   │   ├── openai_provider.py   # OpenAI implementation
│   │   ├── mock_provider.py     # Intelligent zero-cost fallback provider
│   │   └── service.py           # Pluggable AI Service factory
│   ├── api/                     # REST API Routing
│   │   ├── __init__.py
│   │   ├── deps.py              # Dependency injection helpers
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py          # /api/auth endpoints (register, login, me)
│   │       └── tasks.py         # /api/tasks & AI endpoints
│   ├── auth/                    # Security & Authentication logic
│   │   ├── __init__.py
│   │   ├── jwt_handler.py       # JWT creation, decode, & bcrypt hashing
│   │   └── permissions.py       # RBAC dependencies (get_current_user, require_admin)
│   ├── core/                    # Core configuration and exception handling
│   │   ├── __init__.py
│   │   ├── config.py            # Pydantic Settings
│   │   └── exceptions.py        # Centralized HTTP exceptions
│   ├── database/                # Database engine, session, & seeds
│   │   ├── __init__.py
│   │   ├── base.py              # DeclarativeBase
│   │   ├── session.py           # SQLAlchemy SessionLocal & get_db
│   │   └── seed.py              # Database seeding logic
│   ├── models/                  # SQLAlchemy ORM Models
│   │   ├── __init__.py
│   │   ├── user.py              # User model (id, name, email, password, role, timestamps)
│   │   └── task.py              # Task model (id, user_id, title, description, status, timestamps)
│   ├── schemas/                 # Pydantic v2 Request/Response DTOs
│   │   ├── __init__.py
│   │   ├── user.py              # UserRegister, UserLogin, UserResponse, TokenResponse
│   │   ├── task.py              # TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse
│   │   └── ai.py                # AI request and response schemas
│   └── main.py                  # FastAPI application entry point, CORS, and handlers
├── tests/                       # Automated pytest test suite (29 tests)
│   ├── __init__.py
│   ├── conftest.py              # In-memory DB fixtures & test tokens
│   ├── test_auth.py             # Auth & registration tests
│   ├── test_tasks.py            # Task CRUD tests
│   ├── test_permissions.py      # RBAC authorization failure tests
│   └── test_ai.py               # AI endpoints & permissions tests
├── .env.example                 # Environment configuration template
├── .gitignore                   # Git ignore (excludes secrets, .env, venv)
├── alembic.ini                  # Alembic CLI configuration
├── Dockerfile                   # Production Docker container image
├── docker-compose.yml           # 1-click PostgreSQL + API setup
├── postman_collection.json      # Postman v2.1 collection with automated tests
├── pyproject.toml               # Modern Python packaging configuration
├── requirements.txt             # Pinned pip dependencies
├── seed.py                      # Root convenience seeder runner
└── README.md                    # Comprehensive documentation
```

---

## Setup & Installation

### Option 1: Local Python Environment

1. **Clone or navigate into the repository**:
   ```bash
   cd kanishka_python
   ```

2. **Create a virtual environment (Python 3.11+)**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD)**:
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **macOS / Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create your `.env` configuration**:
   ```bash
   # Copy the sample file to .env
   cp .env.example .env     # (On Linux/macOS)
   copy .env.example .env   # (On Windows)
   ```

---

## Database Configuration & Migrations

The application natively supports **PostgreSQL**, **MySQL**, and **SQLite**.

### 1. PostgreSQL Configuration (Recommended)
Set `DATABASE_URL` in `.env`:
```env
DATABASE_URL="postgresql+psycopg://postgres:your_password@localhost:5432/taskdb"
```

### 2. MySQL Configuration
Set `DATABASE_URL` in `.env`:
```env
DATABASE_URL="mysql+pymysql://root:your_password@localhost:3306/taskdb"
```

### 3. SQLite Configuration (Instant zero-dependency evaluation)
```env
DATABASE_URL="sqlite:///./taskmanager.db"
```

### Run Migrations with Alembic
Execute the migration to build tables and indexes:
```bash
alembic upgrade head
```

---

## Database Seeding

To populate the database with initial users (Admin and Regular Users) and sample tasks across all supported statuses:

```bash
python seed.py
```
*(or via module: `python -m app.database.seed`)*

This creates:
- **1 Administrator**: `admin@example.com`
- **2 Regular Users**: `user1@example.com`, `user2@example.com`
- **6 Realistic Development Tasks** assigned to different users with various statuses (`Pending`, `In Progress`, `Testing`, `Completed`).

---

## Environment Variables

All variables are loaded via Pydantic Settings from `.env`:

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `PROJECT_NAME` | string | `AI-Powered Task Management System` | Application Title |
| `ENVIRONMENT` | string | `development` | Deployment environment (`development`, `production`, `testing`) |
| `DEBUG` | boolean | `True` | Debug mode toggle |
| `DATABASE_URL` | string | `postgresql+psycopg://...` | SQLAlchemy connection string |
| `JWT_SECRET_KEY` | string | `super-secret-kanishka...` | Secret key for signing JWTs |
| `JWT_ALGORITHM` | string | `HS256` | JWT signature algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | `1440` (24h) | JWT access token expiration duration |
| `AI_PROVIDER` | string | `gemini` | Active LLM (`gemini`, `openai`, `anthropic`, or `mock`) |
| `GEMINI_API_KEY` | string | `None` | Google Gemini API Key |
| `GEMINI_MODEL` | string | `gemini-1.5-flash` | Gemini model name |
| `OPENAI_API_KEY` | string | `None` | OpenAI API Key |
| `OPENAI_MODEL` | string | `gpt-4o-mini` | OpenAI model name |
| `ANTHROPIC_API_KEY` | string | `None` | Anthropic Claude API Key |
| `ANTHROPIC_MODEL` | string | `claude-3-haiku-20240307` | Anthropic model name |

> **Security Note**: As per assessment guidelines, no `.env` files containing secrets or real API keys are committed to version control. `.env` is listed in `.gitignore`.

---

## AI Configuration

The application includes an **Abstract Provider Architecture** (`app/ai/base.py`):

1. **Google Gemini (Default)**:
   - Provide your key in `.env`: `GEMINI_API_KEY="your-gemini-key"`
   - Uses `gemini-1.5-flash` for high speed and structured outputs.

2. **OpenAI**:
   - Set in `.env`:
     ```env
     AI_PROVIDER="openai"
     OPENAI_API_KEY="sk-..."
     OPENAI_MODEL="gpt-4o-mini"
     ```

3. **Anthropic Claude**:
   - Set in `.env`:
     ```env
     AI_PROVIDER="anthropic"
     ANTHROPIC_API_KEY="sk-ant-..."
     ANTHROPIC_MODEL="claude-3-haiku-20240307"
     ```

4. **Intelligent Offline Mock Provider (Zero-Cost Evaluation)**:
   - If no API key is specified, the application activates an intelligent built-in mock provider that delivers realistic, structured, professional task descriptions and summaries.
   - Evaluators can test both AI endpoints immediately **without needing an API key** or incurring charges.

---

## How to Run the Application

### Method A: Local Uvicorn Server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Once started, explore:
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Method B: 1-Click Docker Compose (PostgreSQL + API)
```bash
docker compose up --build
```
This automatically boots a PostgreSQL 16 container, runs Alembic migrations, seeds the database, and exposes the FastAPI service on port `8000`.

---

## Test Credentials

Use these pre-seeded accounts for testing and verification:

| Role | Email | Password | Allowed Capabilities |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@example.com` | `AdminPass123!` | View all tasks, Edit any task, **Update task status**, AI features |
| **User 1** | `user1@example.com` | `UserPass123!` | View own tasks, Create tasks, Edit own tasks, AI features |
| **User 2** | `user2@example.com` | `UserPass123!` | View own tasks, Create tasks, Edit own tasks, AI features |

---

## API Endpoints Reference

### 1. Authentication Endpoints (`/api/auth`)

| Method | Endpoint | Access | Description | Status Code |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Public | Register a new user (`name`, `email`, `password`, `role`) | `201 Created` |
| `POST` | `/api/auth/login` | Public | Authenticate user; returns Bearer JWT token | `200 OK` |
| `GET` | `/api/auth/me` | Authenticated | Retrieve profile of the current logged-in user | `200 OK` |

### 2. Task Management Endpoints (`/api/tasks`)

| Method | Endpoint | Access | Description | Status Code |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/tasks/` | Authenticated | Create a task (auto-assigned to current user, status `Pending`) | `201 Created` |
| `GET` | `/api/tasks/` | Authenticated | List tasks. Regular user: **only own tasks**. Admin: **all tasks**. | `200 OK` |
| `GET` | `/api/tasks/{id}` | Authenticated | View a task by ID. Regular user: only own task (403 if other's). | `200 OK` |
| `PUT` | `/api/tasks/{id}` | Authenticated | Edit task title/description. Regular user: only own task (403 if other's). | `200 OK` |
| `PATCH` | `/api/tasks/{id}/status` | **Admin Only** | Update task status (`Pending`, `In Progress`, `Testing`, `Completed`). | `200 OK` |
| `PUT` | `/api/tasks/{id}/status` | **Admin Only** | Alias for status update | `200 OK` |

### 3. AI Endpoints (`/api/tasks`)

| Method | Endpoint | Access | Description | Status Code |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/tasks/generate-description` | Authenticated | **Option A**: Generates a structured task description from a title | `200 OK` |
| `POST` | `/api/tasks/{id}/summarize` | Authenticated | **Option B**: Generates an executive summary of task `{id}` | `200 OK` |

---

## Role-Based Access Control (RBAC) Matrix

Strictly enforces access rules detailed in Section 3 of the assessment specification:

| Action | Regular User | Administrator | Error Response if Unauthorized |
| :--- | :---: | :---: | :--- |
| **Create Task** | Allowed | Allowed | `401 Unauthorized` (if not logged in) |
| **View Own Tasks** | Allowed | Allowed | - |
| **View Another User's Task** | **Denied** | Allowed | `403 Forbidden` |
| **Edit Own Task (Title/Desc)** | Allowed | Allowed | - |
| **Edit Another User's Task** | **Denied** | Allowed | `403 Forbidden` |
| **Update Task Status** | **Denied** | **Allowed** | `403 Forbidden: Regular users cannot update task status` |

---

## AI Features Implemented

Both requested AI options have been fully implemented:

### Option A: Generate Task Description
- **Endpoint**: `POST /api/tasks/generate-description`
- **Request Body**:
  ```json
  {
    "title": "Build Distributed Caching Layer with Redis"
  }
  ```
- **Response**:
  ```json
  {
    "title": "Build Distributed Caching Layer with Redis",
    "description": "### Task Overview...\n**Objective:** ...\n**Action Steps:** ...\n**Acceptance Criteria:** ...",
    "provider": "gemini"
  }
  ```

### Option B: Generate Task Summary
- **Endpoint**: `POST /api/tasks/{id}/summarize`
- **Response**:
  ```json
  {
    "task_id": 1,
    "title": "Setup FastAPI Architecture",
    "summary": "Executive Summary: Task 'Setup FastAPI Architecture' focuses on delivering core requirements...",
    "provider": "gemini"
  }
  ```

---

## Automated Test Suite (pytest)

The project includes **29 comprehensive automated tests** with 100% pass rate:

```bash
pytest -v
```

### Test Coverage Highlights:
- **Authentication (`tests/test_auth.py`)**:
  - User registration with valid data
  - Duplicate email rejection (409 Conflict)
  - Pydantic validation failures (422)
  - Login success with JWT issuance
  - Login rejection on bad password / bad email (401)
  - `/api/auth/me` profile retrieval
- **Task Management (`tests/test_tasks.py`)**:
  - Task creation and assignment
  - Regular user task isolation (only seeing own tasks)
  - Admin visibility over all tasks
  - Task retrieval and not-found handling (404)
  - Title and description editing
- **RBAC Security & Permissions (`tests/test_permissions.py`)**:
  - Regular user blocked from viewing another user's task (403)
  - Regular user blocked from modifying another user's task (403)
  - **Regular user blocked from updating task status (403)**
  - Admin permitted to update task status (200)
  - Admin permitted to edit any user's task (200)
  - Invalid task status values rejected (422)
  - Unauthenticated requests rejected (401)
- **AI Integration (`tests/test_ai.py`)**:
  - Option A: Description generation
  - Option B: Task summarization
  - Access control validation on AI endpoints

---

## Postman Collection Guide

A complete Postman Collection v2.1 is included in the root directory: [`postman_collection.json`](./postman_collection.json).

### How to Use:
1. Open **Postman**.
2. Click **Import** and select `postman_collection.json`.
3. The collection is pre-configured with the following test groups:
   - `1. Authentication`: Tests registration and logins for User and Admin, **automatically saving JWT tokens** to collection variables (`{{userToken}}`, `{{adminToken}}`).
   - `2. Regular User Task APIs`: Creates a task, stores `{{createdTaskId}}`, lists own tasks, views single task, and edits task details.
   - `3. Admin Task APIs`: Views all platform tasks, filters by status, updates task status to "In Progress" and "Completed", and edits tasks.
   - `4. Authorization Failures`: Tests that regular users receive `403 Forbidden` when attempting to update status or modify another user's task, and `401 Unauthorized` without a token.
   - `5. AI Integration Endpoints`: Tests `POST /api/tasks/generate-description` and `POST /api/tasks/{id}/summarize`.
   - `6. Health & System`: Checks service health.
4. Click **Run Collection** to execute all 16 tests sequentially with automated assertions!

---

## Key Architectural Decisions & Assumptions

1. **FastAPI & Async Support**: Selected FastAPI over Flask for automatic OpenAPI/Swagger interactive documentation, native Pydantic v2 data validation, and superior performance.
2. **Explicit RBAC Enforcement**: Task status updating is decoupled from general task editing. Even if a regular user passes `status` in an update payload, status changes are rejected with `403 Forbidden`, strictly fulfilling the assessment constraint: *"Regular User: Cannot update task status. Admin: Update task status."*
3. **Multi-Database Agility**: SQLAlchemy models and Alembic migrations are written dialect-agnostic, supporting PostgreSQL, MySQL, and SQLite.
4. **Pluggable AI with Zero-Config Fallback**: AI services are isolated behind an abstract interface (`BaseAIProvider`). Evaluators can test real LLMs (Gemini/OpenAI) by adding an API key, or test seamlessly offline without needing an API key.
5. **Secure Cryptography**: Password hashing uses native `bcrypt` with 12 salt rounds, avoiding deprecated wrapper libraries.
