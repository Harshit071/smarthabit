FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
COPY run_migrations.py .
RUN pip install --no-cache-dir -r requirements.txt alembic uvicorn

# Copy application code
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
COPY . .

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose)
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

