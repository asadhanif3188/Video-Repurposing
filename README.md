# Video Repurposing Service

## Overview
The **Video Repurposing Service** constitutes a full-stack application designed to transform existing video content into various formats automatically. By leveraging AI (OpenAI/Gemini), it extracts transcripts from YouTube videos and repurposes them into Tweets, LinkedIn posts, Blog articles, and more.

## Architecture

The system is composed of two main applications orchestrated together:

1.  **Frontend (`/frontend`)**: A **Next.js 14** application providing an interactive UI for users to input video URLs, view generated content, and manage their dashboard.
2.  **Backend (`/backend`)**: A **FastAPI** service handling business logic, database operations, and AI orchestration. It uses **Celery** with **Redis** for asynchronous task processing to handle long-running operations like transcript fetching and content generation.

### High-Level Architecture

```text
          +--------+
          |  User  |
          +---+----+
              |
+-------------v---------------+
|     Frontend (Next.js)      |
+-------------+---------------+
              | HTTP
              v
+-----------------------------+       +------------------+
|    Backend API (FastAPI)    +------>|   Redis (Queue)  |
+-------------+---------------+       +--------+---------+
              |                                ^
              | SQL                            | Poll
              v                                |
+-----------------------------+       +--------+---------+
|    PostgreSQL Database      |<------+  Celery Worker   |
+-----------------------------+       +--------+---------+
                                               |
                                               | API Calls
                                      +--------v---------+
                                      | External Services|
                                      | (OpenAI, YouTube)|
                                      +------------------+
```

## Project Structure

```bash
.
├── backend/            # FastAPI application, Workers, and DB models
├── frontend/           # Next.js frontend application
├── docker-compose.yml  # Root orchestration for all services
└── README.md           # This file
```

## Getting Started

### Prerequisites
- [Docker](https://www.docker.com/) and Docker Compose
- (Optional) Node.js & Python 3.10+ for local development without Docker

### Quick Start (Docker)
The easiest way to run the entire stack is using Docker Compose from the root directory.

1.  **Configure Environment Variables**:
    *   Backend: Copy `backend/.env.example` to `backend/.env` and populate it (DB creds, OpenAI Key).
    *   Frontend: content is usually static or client-side configured, but check `frontend/.env.local` if needed.

2.  **Run Services**:
    ```bash
    docker-compose up --build
    ```
    This command starts:
    *   Frontend: `http://localhost:3000`
    *   Backend API: `http://localhost:8000`
    *   PostgreSQL & Redis containers

### Manual Development
If you prefer to run services individually, please refer to the specific README files:
*   [Backend Documentation](./backend/README.md)
*   [Frontend Documentation](./frontend/README.md)
