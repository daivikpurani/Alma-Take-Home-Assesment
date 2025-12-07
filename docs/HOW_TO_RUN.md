# How to Run the Application

A simple step-by-step guide to get the Alma Lead Management API running on your computer.

---

## What You Need First

Before starting, make sure you have:
- **Python 3.10 or newer** (check with `python3 --version`)
- **PostgreSQL database** (we'll use Docker to run it easily)
- **pip** (comes with Python)

---

## Step 1: Get the Code and Install Packages

1. Open your terminal and go to the project folder:
   ```bash
   cd Alma-Take-Home-Assesment
   ```

2. Create a virtual environment (this keeps packages separate):
   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   # On Mac/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

4. Install all required packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## Step 2: Start the Database

We'll use Docker to run PostgreSQL easily. Just run:

```bash
docker-compose up -d
```

This starts a PostgreSQL database with these settings:
- Username: `leads_user`
- Password: `leads_pass`
- Database name: `leads_db`
- Port: `5432`

**Don't have Docker?** You can use your own PostgreSQL database instead. Just make sure to update the connection string in the next step.

---

## Step 3: Create Configuration File

Create a file named `.env` in the project root folder (same folder as `requirements.txt`).

Copy and paste this into the `.env` file:

```env
DATABASE_URL=postgresql://leads_user:leads_pass@localhost:5432/leads_db
INTERNAL_API_TOKEN=super-secret-token
SENDGRID_API_KEY=your-sendgrid-api-key-here
COMPANY_NOTIFICATION_EMAIL=your-email@example.com
COMPANY_NAME=Alma
```

### What each setting does:

- **DATABASE_URL**: How to connect to your database (use the one above if you used Docker)
- **INTERNAL_API_TOKEN**: A secret password to access internal endpoints (change this to something secure)
- **SENDGRID_API_KEY**: Your SendGrid API key for sending emails (optional - leave empty if you don't have one)
- **COMPANY_NOTIFICATION_EMAIL**: The email address that will send emails (needed if using SendGrid)
- **COMPANY_NAME**: Your company name (used in emails)

**Important notes:**
- If you don't have a SendGrid API key, that's okay! The app will still work, but emails will just be printed to the console instead of being sent.
- All settings are read from this `.env` file only (not from your computer's environment variables).
- **Email sending is asynchronous** - emails are sent in the background, so the API responds immediately without waiting for emails to be sent.

---

## Step 4: Start the Application

Run this command:

```bash
uvicorn app.main:app --reload
```

The `--reload` flag means the app will automatically restart when you change code (useful for development).

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Your API is now running at: **http://localhost:8000**

---

## Step 5: Check if It's Working

Open your web browser and go to:
```
http://localhost:8000/health
```

Or use curl in your terminal:
```bash
curl http://localhost:8000/health
```

You should see:
```json
{"status":"ok","app":"Leads Service"}
```

If you see this, everything is working!

---

## Viewing API Documentation

The app comes with built-in documentation. Once it's running, visit:

- **Swagger UI** (interactive): http://localhost:8000/docs
- **ReDoc** (readable format): http://localhost:8000/redoc

These pages show you all available endpoints and let you test them directly.

### What endpoints are available?

**Public endpoints** (anyone can use):
- `POST /public/leads` - Submit a new lead with resume
- `GET /public/leads/ping` - Check if public API is working

**Internal endpoints** (need a password/token):
- `GET /api/internal/leads` - See all leads (with pagination support)
- `GET /api/internal/leads/{lead_id}` - See one specific lead
- `PATCH /api/internal/leads/{lead_id}/state` - Change a lead's status

To use internal endpoints, you need to include your token. Example:
```bash
curl -H "Authorization: Bearer super-secret-token" http://localhost:8000/api/internal/leads
```

### Pagination

The `GET /api/internal/leads` endpoint supports pagination with the following query parameters:

- `page` (optional, default: 1) - Page number (1-indexed, minimum: 1)
- `page_size` (optional, default: 10) - Number of items per page (minimum: 1, maximum: 100)

**Example requests:**

```bash
# Get first page with default page size (10 items)
curl -H "Authorization: Bearer super-secret-token" http://localhost:8000/api/internal/leads

# Get first page with 20 items per page
curl -H "Authorization: Bearer super-secret-token" "http://localhost:8000/api/internal/leads?page=1&page_size=20"

# Get second page with 5 items per page
curl -H "Authorization: Bearer super-secret-token" "http://localhost:8000/api/internal/leads?page=2&page_size=5"
```

**Response format:**

The paginated response includes:
- `items` - Array of lead objects
- `total` - Total number of leads in the database
- `page` - Current page number
- `page_size` - Number of items per page
- `total_pages` - Total number of pages

Example response:
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "resume_path": "uploads/abc123.pdf",
      "state": "PENDING",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```

---

## Running Tests

To run all tests:

```bash
pytest
```

To see how much of the code is tested:

```bash
pytest --cov=app --cov-report=html
```

This creates an HTML report showing test coverage.

---

## Stopping the Application

**To stop the API server:**
- Press `Ctrl+C` in the terminal where it's running

**To stop the database (if using Docker):**
```bash
docker-compose down
```

---

## Common Problems and Solutions

### Problem: Can't connect to database

**Check if database is running:**
```bash
docker-compose ps
```

**Check your `.env` file** - make sure `DATABASE_URL` matches your database settings.

**Test database connection:**
```bash
docker-compose exec postgres psql -U leads_user -d leads_db
```

### Problem: Emails aren't sending

**Check your `.env` file:**
- Make sure `SENDGRID_API_KEY` is set (if you want real emails)
- Make sure `COMPANY_NOTIFICATION_EMAIL` is set

**Remember:** 
- If you don't have a SendGrid API key, emails will just be printed to the console. This is normal and the app will still work!
- Emails are sent asynchronously in the background, so they may take a moment to be delivered after the API responds. Check the application logs to see email sending status.

### Problem: Port 8000 is already in use

**Option 1:** Stop whatever is using port 8000

**Option 2:** Run on a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

Then access it at `http://localhost:8001`

---

## Need Help?

- Check the logs in your terminal - they usually show what went wrong
- Make sure all steps above were completed correctly
- Verify your `.env` file has all required settings
