#!/bin/bash
# Production startup script for Render deployment

# Run database migrations (if needed)
# python -m alembic upgrade head

# Start the application with gunicorn
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

