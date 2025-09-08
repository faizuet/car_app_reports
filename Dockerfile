FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for MySQL and cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Make scripts executable
RUN chmod +x scripts/*.sh

CMD ["/app/scripts/start.sh"]

