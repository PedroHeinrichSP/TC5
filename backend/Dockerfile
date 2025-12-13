# Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set Python path
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p /tmp/uploads

# Expose port
EXPOSE 8000

# Run the application
CMD ["bash", "-c", "export PYTHONPATH=/app:$PYTHONPATH && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
