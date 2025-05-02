FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Install Python dependencies directly
RUN pip install --no-cache-dir -r requirements.txt

# Make sure uvicorn is installed
RUN pip install --no-cache-dir uvicorn fastapi

# Set Python path
ENV PYTHONPATH="/app:$PYTHONPATH"

EXPOSE 8000

# Use simple command that doesn't rely on module resolution
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
