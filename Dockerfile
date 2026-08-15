# Use an official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Set the working directory inside the container
WORKDIR /app

# Install basic system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY . .

# Ensure storage directories exist
RUN mkdir -p memory reports

# Expose the web port
EXPOSE 8000

# Launch uvicorn web server dynamically using the PORT environment variable
CMD ["sh", "-c", "uvicorn web.app:app --host 0.0.0.0 --port ${PORT}"]
