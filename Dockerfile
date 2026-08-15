# Use official Python lightweight base image
FROM python:3.13-slim

# Prevent Python from writing .pyc files and buffer output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set working directory inside container
WORKDIR /app

# Install basic system requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure directories for persistent memory exist
RUN mkdir -p memory reports

# Expose server port
EXPOSE 8000

# Launch server
CMD python main.py web --host=0.0.0.0 --port=$PORT
