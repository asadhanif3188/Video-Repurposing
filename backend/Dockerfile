# Python 3.10 Slim with uv
FROM python:3.10-slim

# Install uv (latest version)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies using uv with requirements.txt
# --system installs into the system python environment
RUN uv pip install --system --no-cache -r requirements.txt

# Copy App
COPY . .

# Expose Port
EXPOSE 8000

# Run Command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
