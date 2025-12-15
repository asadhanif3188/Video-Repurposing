# Video Repurposing Backend

## Overview
This is the backend service for the Video Repurposing application. It is built with **FastAPI** and is responsible for handling content generation, transcript processing, and communicating with AI services (OpenAI). It uses **Celery** for background task processing (e.g., long-running transcript extraction or content generation) and **PostgreSQL** for data persistence.

## Tech Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL (with SQLAlchemy & AsyncPG)
- **Task Queue:** Celery (with Redis)
- **AI/ML:** OpenAI API
- **Dependency Management:** uv / pip

## Project Structure
```
backend/
├── app/
│   ├── api/            # API route handlers
│   ├── core/           # Core configuration (settings, db)
│   ├── models/         # SQLAlchemy database models
│   ├── schemas/        # Pydantic models for validation
│   ├── services/       # Business logic services
│   ├── utils/          # Utility functions
│   ├── workers/        # Celery tasks and app configuration
│   └── main.py         # Application entry point
├── scripts/            # Helper scripts
├── .env.example        # Environment variable template
├── docker-compose.yml  # Docker services configuration
├── pyproject.toml      # Project configuration and dependencies
└── requirements.txt    # Python dependencies
```

## Getting Started

### Prerequisites
- Python 3.10 or higher
- PostgreSQL
- Redis (for background tasks)

### Installation

1. **Clone the repository** and navigate to the backend directory.

2. **Set up a virtual environment:**
   It is recommended to use `uv` for fast package management, but standard `pip` works as well.

   ```bash
   # Using standard venv
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   Copy the example environment file and configure your secrets.
   ```bash
   cp .env.example .env
   ```
   Update `.env` with your database credentials, OpenAI API key, and Redis URL.

### Running the Application

1. **Start the API Server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.
   API Documentation (Swagger UI) is available at `http://localhost:8000/docs`.

2. **Start the Celery Worker:**
   To process background tasks, you need to run a Celery worker.
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info --pool=solo
   ```
   *Note: `--pool=solo` is often required on Windows to avoid issues.*

### Docker Support
You can also run the entire stack (Database, Redis, Backend) using Docker Compose if available in the root or backend directory.

```bash
docker-compose up --build
```

## APIs
- **Health Check:** `GET /health`
- **Content Operations:** `app/api/routes/content.py` handles content creation and retrieval.
