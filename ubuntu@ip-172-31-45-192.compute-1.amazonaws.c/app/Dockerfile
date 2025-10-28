FROM mcr.microsoft.com/playwright/python:v1.47.0-focal

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Docker client
RUN apt-get update && apt-get install -y \
    curl \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 sharkbrowser && chown -R sharkbrowser:sharkbrowser /app
USER sharkbrowser

# Expose the API port and CDP port range
EXPOSE 8000
EXPOSE 9000-9020

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
