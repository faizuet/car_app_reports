FROM python:3.11-slim

WORKDIR /app

# --------------------------
# Install system dependencies
# --------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --------------------------
# Install Python dependencies first
# --------------------------
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --------------------------
# Copy application code
# --------------------------
COPY . .

# Windows line endings and make scripts executable
RUN sed -i 's/\r$//' scripts/*.sh && chmod +x scripts/*.sh

# Expose FastAPI port
EXPOSE 8000

# Default command (overridden in docker-compose for worker/beat)
CMD ["/app/scripts/start.sh"]
