# How to Run

Simple guide to get the Alma Lead Management API up and running.

## Prerequisites

- Python 3.10 or higher
- PostgreSQL (or Docker for running PostgreSQL)
- pip

## Quick Start

### 1. Navigate to Project Directory

```bash
cd Alma-Take-Home-Assesment
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start PostgreSQL Database

Using Docker Compose (recommended):

```bash
docker-compose up -d
```

Or use your own PostgreSQL instance.

### 5. Create `.env` File

Create a `.env` file in the project root with the following:

```env
DATABASE_URL=postgresql+psycopg2://leads_user:leads_pass@localhost:5432/leads_db
INTERNAL_API_TOKEN=super-secret-token
SENDGRID_API_KEY=your-sendgrid-api-key-here
COMPANY_NOTIFICATION_EMAIL=your-email@example.com
```

**Note:** The `SENDGRID_API_KEY` is optional. If not provided, email functionality will be disabled.

### 6. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

### 7. Verify It's Running

Open your browser or use curl:

```bash
curl http://localhost:8000/health
```

You should see:
```json
{"status":"ok","app":"Leads Service"}
```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running Tests

```bash
pytest
```

## Stopping the Application

Press `Ctrl+C` in the terminal where the server is running.

To stop the database (if using Docker):

```bash
docker-compose down
```
