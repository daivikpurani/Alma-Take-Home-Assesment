# PROJECT SUMMARY — Alma Lead Management API

**GitHub Repo:** https://github.com/daivikpurani/Alma-Take-Home-Assesment

---

## Overview  
A production-style FastAPI backend to collect prospect leads through a public form, store uploaded resumes, notify both the prospect and an internal attorney via email, and expose secure internal APIs for reviewing and updating lead status.

---

## Core Features  

### Public Lead Submission
- Multipart file upload: first name, last name, email, resume/CV  
- Resume stored locally (`uploads/`), path saved in DB  
- Pydantic validation  

### Persistent Storage
- PostgreSQL with SQLAlchemy ORM  
- UUID primary keys  
- Automatic created/updated timestamps  

### Email Notifications (Async)
- Prospect acknowledgment + attorney notification  
- Real emails sent via SendGrid  
- If no key is provided → gracefully logs instead of failing  
- Email delivery handled using **FastAPI Background Tasks**

### Internal API (Bearer Protected)
- List leads with pagination → `GET /api/internal/leads?limit=<n>`  
- Update state from `PENDING` → `REACHED_OUT`  
- Must include header: `Authorization: Bearer <token>`  

### Production-Style Project Structure
- Routers, Models, Schemas, Services, Storage, Email, DB separated  
- Business logic lives in services (thin routing layer)  
- Easier maintenance + testability  

---

## Tech Stack & Design Choices

| Component | Technology / Strategy | Reason |
|-----------|----------------------|--------|
| Framework | FastAPI | Async, typed, automatic docs |
| DB | PostgreSQL + SQLAlchemy | Persistent + scalable |
| Resume Storage | Local file system w/ abstraction | Easy future migration to S3 |
| Email | SendGrid + async fallback logging | Real emails + fault tolerance |
| Auth | Static Bearer Token | Lightweight for internal UI |
| ID Type | UUID | Safer than incremental IDs |
| Pagination | `limit` parameter | Scales for large datasets |

---

## Security
- Internal APIs require `Authorization: Bearer <token>` from `.env`  
- Public form remains open for users (as required)  
- Resume files are not publicly served, only path stored  

---

## Lead State Machine

| State | Meaning |
|-------|--------|
| `PENDING` | Lead just submitted, no outreach yet |
| `REACHED_OUT` | Updated manually after internal contact |

Only internal users can update lead state.

---

##  How It Runs
1. Clone repo & install dependencies  
2. Create `.env` using `.env.example`  
3. Run PostgreSQL (Docker preferred)  
4. Start API with `uvicorn`  
5. Access docs at `/docs` and test endpoints  

---

##  Future Scalability Improvements
- Offload file uploads + emails into task queues (Celery/RQ)  
- Switch storage layer to S3/GCS  
- JWT-based roles for multi-user internal UI  
- Advanced filtering, search & pagination  
- Alembic DB migrations  
- CRM webhook automation for follow-up workflows  

---

**Author:** Daivik Purani  
**Project:** Alma Take-Home Assessment — Backend API
