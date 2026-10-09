# Technical Interview & Code Walkthrough Guide

> **Prepared for Kanishka Software R&D Interview Round**  
> *Assessment Requirement (Section 9): "Candidates must understand, review, test, and be able to explain the code they submit if asked during the interview."*

---

## 1. System Architecture Overview

### Q: "Walk me through how your application is structured."
**Answer:**
> "I followed a modular separation of concerns based on production-grade FastAPI practices:
> - **API Layer (`app/api/`)**: Defines REST endpoints divided by domains (`auth` and `tasks`). It uses FastAPI routers with dependency injection for security and database sessions.
> - **Service Layer (`app/services/`)**: Encapsulates core business rules (RBAC checks, data manipulation, validation) separate from HTTP handling.
> - **Data Access Layer (`app/models/`, `app/database/`)**: SQLAlchemy 2.0 ORM models with Alembic schema migrations, utilizing connection pooling with `pool_pre_ping=True` to detect dropped connections.
> - **AI Integration Layer (`app/ai/`)**: An Abstract Factory pattern (`BaseAIProvider`) that allows hot-swapping between Google Gemini, OpenAI, Anthropic Claude, and an offline Mock provider without modifying business logic.
> - **Security Layer (`app/auth/`)**: Native 12-round bcrypt password hashing and PyJWT token generation and verification."

---

## 2. Authentication & Security (JWT & RBAC)

### Q: "How did you implement JWT authentication and password security?"
**Answer:**
> "Passwords are hashed using native `bcrypt` with a work factor of 12 salt rounds before hitting the database. I deliberately avoided deprecated libraries and used constant-time comparison via `bcrypt.checkpw` to protect against timing attacks.
> For authentication, successful logins return a signed JWT token using the `HS256` algorithm containing the user ID in the `sub` claim and role information. The token is validated on protected endpoints via FastAPI's `HTTPBearer` security scheme in `app/auth/permissions.py`."

### Q: "How is Role-Based Access Control (RBAC) enforced?"
**Answer:**
> "I implemented RBAC at both the dependency level and the service level:
> 1. **Endpoint Protection**: `get_current_user` extracts and decodes the token from `Authorization: Bearer <token>`, loading the active user from the database.
> 2. **Admin Restriction**: `require_admin` ensures only users with the `admin` role can access administrative endpoints.
> 3. **The Status Rule**: Regular users can create, view, and edit their own tasks, but are **strictly prevented from updating task status**. I enforced this across both dedicated status endpoints (`PATCH /api/tasks/{id}/status` and `PUT /api/tasks/{id}/status`) AND the general update endpoint (`PUT /api/tasks/{id}`). If a regular user sends a status field, it raises a `403 Forbidden` exception."

---

## 3. Database & Migrations

### Q: "Why use Alembic instead of just `Base.metadata.create_all()`?"
**Answer:**
> "While `create_all()` creates tables if they don't exist, it cannot manage schema evolutions (adding columns, updating constraints, or rolling back migrations).
> In `alembic/versions/0001_initial_schema.py`, I created formal `upgrade()` and `downgrade()` methods. This ensures consistent schema state across local environments, Docker containers, and production databases."

### Q: "How does your project handle multi-database support (PostgreSQL vs MySQL)?"
**Answer:**
> "SQLAlchemy abstracts SQL dialects. In `requirements.txt` and `pyproject.toml`, I included drivers for:
> - **PostgreSQL**: Modern `psycopg` (v3) and `psycopg2-binary`.
> - **MySQL**: Pure Python `pymysql`.
> - **SQLite**: Zero-dependency local evaluation.
> The database URL is configured dynamically via the `DATABASE_URL` environment variable loaded through Pydantic Settings."

---

## 4. AI LLM Integration

### Q: "How does the AI feature work, and how do you handle API failures?"
**Answer:**
> "I implemented both requested options:
> - **Option A (`POST /api/tasks/generate-description`)**: Takes a title and prompts the LLM to return structured objectives, action items, and acceptance criteria.
> - **Option B (`POST /api/tasks/{id}/summarize`)**: Takes an existing task ID, verifies ownership, and synthesizes a concise executive summary.
> 
> **Resilience & Error Handling**:
> 1. All LLM calls are wrapped in exception handlers that catch upstream API errors and translate them into standard HTTP `502 Bad Gateway` (`AIServiceException`) responses rather than uncaught 500 crashes.
> 2. An intelligent `MockProvider` automatically activates if an evaluator tests without an API key, preventing test suite failures or evaluation blockers."

---

## 5. Testing & Quality Assurance

### Q: "How did you test your application?"
**Answer:**
> "I implemented two layers of testing:
> 1. **Automated Pytest Suite (`tests/`)**: 34 unit and integration tests running against an isolated in-memory SQLite database (`StaticPool`). It achieves 100% test pass rate across auth, CRUD, RBAC boundary security, and AI fallback.
> 2. **Postman Collection (`postman_collection.json`)**: Postman v2.1 collection with 20 pre-configured requests containing JavaScript test assertions and automated environment variable capture (`{{userToken}}`, `{{adminToken}}`).
> 3. **CI/CD Pipeline (`.github/workflows/ci.yml`)**: Automated GitHub Actions workflow running tests on every push."
