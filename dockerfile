# Use official Python slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_NO_ANSI=1

# Set working directory
WORKDIR /app

# Install system deps (for building some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Install pip + poetry
RUN pip install --upgrade pip \
    && pip install poetry

# Copy only pyproject + lock file first (better Docker caching)
COPY pyproject.toml poetry.lock* README.md ./

# Install dependencies with poetry (disable parallel to avoid DNS issues)
RUN poetry config installer.parallel false \
    && poetry install --only main --no-root

# Copy application code
COPY app ./app

# Expose API port
EXPOSE 8000

# Set environment for production
ENV ENVIRONMENT=production

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
