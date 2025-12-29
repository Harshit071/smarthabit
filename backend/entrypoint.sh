#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Running database migrations..."
alembic upgrade head
echo "Database migrations complete."

# Start the Uvicorn server
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000
