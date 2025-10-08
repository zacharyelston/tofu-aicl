# Stage 1: Base image with OS dependencies
FROM python:3.9-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libffi-dev libssl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Stage 2: Builder image for installing Python dependencies
FROM base AS builder

WORKDIR /app

# Copy only the files needed to install dependencies
COPY pyproject.toml .
COPY src/ ./src/

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -e .

# Stage 3: Final runtime image
FROM base AS final

WORKDIR /app

# Copy installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /app/src/ /app/src/

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Default command
CMD ["python3", "run.py", "rag_pipeline_test.aicl"]
