FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq5 \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies (cached unless requirements.txt changes)
RUN pip install --no-cache-dir -r requirements.txt

# Install essential packages separately
RUN pip install --no-cache-dir uvicorn fastapi

# Now copy the full app source
COPY . .

ENV PYTHONPATH="/app:$PYTHONPATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
