# Leads Service (FastAPI Take-Home)

A production-style FastAPI backend that supports public lead submissions and internal lead management.  
The service persists data using PostgreSQL and separates public vs. internal APIs using Bearer token authentication.

This project is structured as a realistic backend service with:
- FastAPI + SQLAlchemy
- PostgreSQL (local or Docker)
- Environment-based configuration
- Separate public and internal API routers
- Auth guard for internal APIs
- Minimal logging
- Optional Docker setup for database

---

## 🚀 Tech Stack

| Component | Technology |
|-----------|------------|
| API Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Auth | Bearer Token |
| Runtime | Uvicorn |
| Container (optional) | Docker Compose |

---

## 📦 Requirements

- Python 3.10+
- PostgreSQL (either local or via Docker)
- pip / virtual environment

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```bash
DATABASE_URL=postgresql+psycopg2://leads_user:leads_pass@localhost:5432/leads_db
INTERNAL_API_TOKEN=super-secret-token
APP_NAME=Leads Service
UPLOAD_ROOT=uploads
LOG_LEVEL=INFO
