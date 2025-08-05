FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y gcc libpq-dev && apt-get clean

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose Flask port
EXPOSE 5000
