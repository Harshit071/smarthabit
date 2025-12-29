#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Executing database setup script..."
python run_migrations.py
echo "Database setup script complete."

# Start the Uvicorn server
echo "Starting FastAPI application..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
