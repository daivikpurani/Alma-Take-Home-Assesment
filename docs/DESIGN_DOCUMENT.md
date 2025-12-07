# Design Document – Alma Lead Management API

This document explains how the Alma Lead Management API is built and why we made certain choices. It's written in simple terms to help anyone understand the system.

---

## What Problem Are We Solving?

The system needs to:
- Let people submit their information and resume through a public website
- Save all submissions in a database
- Send emails to both the person who submitted and to an internal team member
- Provide a private area where team members can:
  - See all submissions
  - Mark submissions as "reached out" when they contact someone

---

## How the System is Organized

### The Big Picture

The system follows a standard layered architecture:
- **Routers** - Handle HTTP requests and responses
- **Services** - Contain the business logic
- **Database** - Stores persistent data
- **Storage** - Manages file uploads

### Main Parts of the System

| Part | What It Does |
|------|-------------|
| FastAPI Routers | Handles incoming web requests (like "submit a lead" or "show me all leads") |
| Services | Contains the business logic (saving leads, sending emails, updating status) |
| Database (PostgreSQL) | Stores all lead information permanently |
| File Storage | Saves uploaded resume files to disk |
| Email Service | Sends emails using SendGrid (or just logs them if SendGrid isn't configured) |
| Authentication | Protects internal endpoints with a password token |

### Folder Structure

Here's how the code is organized:

```
app/
├── api/              # Handles web requests
│   ├── public/       # Public endpoints (anyone can use)
│   ├── internal/     # Private endpoints (need password)
│   └── deps.py       # Helper functions for database, auth, etc.
├── models/            # Database table definitions
├── schemas/          # Data validation rules
├── services/         # Business logic
├── db/               # Database connection setup
├── core/             # Configuration and settings
├── storage/          # File storage handling
└── main.py           # Application startup
```

**Why organize it this way?**
- Each part has a clear job
- Easy to find and change code
- Easy to test each part separately
- If we need to change something (like switch email providers), we only change one place

---

## How Data is Stored

### Why PostgreSQL?

PostgreSQL is a reliable database that:
- Keeps data safe and permanent
- Works well for production systems
- Can grow with your needs
- Works easily with Docker

### Why Store Resumes as Files (Not in Database)?

**Resumes are stored on disk, not in the database.**

Why?
- Keeps the database smaller and faster
- Easier to move files to cloud storage (like AWS S3) later if needed
- The database only stores the file path (like `uploads/abc123.pdf`)

Files are saved in the `uploads/` folder. You can change this location in the `.env` file with `UPLOAD_ROOT`.

---

## How Emails Work

### The Goal

- Send real emails when possible
- Don't break the app if email fails
- Send emails to both the person who submitted and to the team

### How It Works

**Email Service:**
- Uses SendGrid to send real emails
- If SendGrid isn't configured, emails are just logged to the console (app still works!)
- Emails are formatted as HTML (looks nice)
- **Emails are sent asynchronously** using FastAPI's BackgroundTasks - the API responds immediately without waiting for emails to be sent

**Who Gets Emails?**

1. **The person who submitted** - Gets a "thank you" email
2. **The team member** - Gets notified about the new submission
   - Configured via `ATTORNEY_EMAIL` in `.env` (default: `shuo@tryalma.ai`)
   - The sender email is hardcoded to `daiiviikpurani2@gmail.com` (cannot be configured)

**What Happens if Email Fails?**

- The error is logged
- The lead submission still succeeds (doesn't fail)
- This way, we don't lose submissions even if email is temporarily broken
- Since emails are sent asynchronously, email failures don't affect API response time

---

## Security for Internal Endpoints

### How It Works

Internal endpoints (like viewing all leads) are protected with a password token.

**Why use token authentication?**
- Simple to set up and test
- Meets the requirement of protecting internal areas
- Easy to replace with more advanced auth later if needed

**How it works:**
1. You put a token in your `.env` file (`INTERNAL_API_TOKEN`)
2. When making requests to internal endpoints, you include this token in the header
3. The app checks if your token matches
4. If it matches, you get access. If not, you get an "unauthorized" error

**Example:**
```bash
curl -H "Authorization: Bearer your-token-here" http://localhost:8000/api/internal/leads
```

---

## Lead Status Management

Leads have two possible statuses:

| Status | Meaning |
|--------|---------|
| `PENDING` | Just submitted, no one has contacted them yet |
| `REACHED_OUT` | Team member has contacted this person |

**Why control this in the service layer?**
- Prevents unauthorized changes
- Makes it easy to add features later (like tracking who changed it, when, etc.)

---

## Future Improvements

Here are some things that could be added later:

| Feature | Why It Would Help |
|---------|-------------------|
| ~~Background tasks for emails~~ | ~~Makes the API respond faster (emails sent in background)~~ **Implemented** |
| Database migrations | Safer way to change database structure |
| Cloud file storage (S3/GCS) | Better for scaling across multiple servers |
| User accounts with OAuth2 | Support multiple team members with their own accounts |
| ~~Pagination for leads list~~ | ~~Better performance when there are many leads~~ **Implemented** |
| CRM integration | Automatically sync leads with other systems |

---

## Trade-offs I Made

Every design decision has pros and cons. Here's what we chose and why:

| Decision | Downside | Why We Did It |
|----------|----------|---------------|
| Store files locally | Can't share files across multiple servers | Simple for this project, easy to change later |
| No database migrations | Database structure created automatically | Faster to build, migrations can be added later |
| Log emails if SendGrid missing | Real emails won't be sent | App still works for testing without SendGrid |
| Simple token auth | Not good for many users | Meets requirements, easy to upgrade later |
| Only use `.env` file | Less flexible for deployment | Simpler for reviewers, consistent behavior |
| Hardcoded attorney email | Can't change without code | Meets requirement, can be made configurable later |

---

## Summary

This system is built like a real production application, not just a quick demo. It has:

- **Clear organization** - Easy to understand and modify
- **Scalable design** - Can grow as needs change
- **Real integrations** - Actually sends emails and saves to database
- **Error handling** - Doesn't break if email fails
- **Security** - Protects internal endpoints

These choices make the system work well today, while making it easy to add new features in the future.
