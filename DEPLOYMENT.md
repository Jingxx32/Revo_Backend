# Deployment Guide - Render Platform

## PostgreSQL Database Setup

### 1. Create PostgreSQL Database on Render

1. Log in to Render dashboard
2. Create a new PostgreSQL database service
3. Note the connection string (sets `DATABASE_URL` automatically)

### 2. Environment Variables

Set these environment variables in Render Web Service:

```bash
# Database connection (provided by Render)
DATABASE_URL=postgresql://user:password@host:port/database

# JWT configuration
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS configuration
CORS_ORIGINS=https://your-frontend-domain.com

# Stripe configuration (if needed)
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Optional AWS configuration
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_BUCKET_NAME=
AWS_REGION=us-east-1
```

### 3. Render Deployment Settings

#### Option 1: Use startup script

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `./start.sh`

#### Option 2: Use gunicorn directly

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

### 4. Database Migration

After initial deployment, initialize database tables:

**Using Render Shell**:
```bash
python -c "from app.db.database import create_db_and_tables; create_db_and_tables()"
```

Tables can also be created automatically on app startup (implemented in current code).

### 5. Local Development

#### PostgreSQL

Create `.env` file:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/revo_db
JWT_SECRET_KEY=your-local-secret-key
```

#### SQLite

If `DATABASE_URL` is not set or uses SQLite URL, the app falls back to SQLite (local development only).

## Dependencies

- **psycopg2-binary**: PostgreSQL adapter
- **gunicorn**: Production WSGI server
- **uvicorn[standard]**: ASGI server (UvicornWorker for gunicorn)

## Configuration Notes

1. **Connection pool**: PostgreSQL pool_size=5, max_overflow=10
2. **Connection health check**: pool_pre_ping=True enabled
3. **Port**: Render sets `PORT` automatically
4. **Logging**: Set appropriate log level for production

## Troubleshooting

### Database Connection Issues

Check:
1. `DATABASE_URL` is set correctly
2. PostgreSQL service is running
3. Network connectivity
4. Database user permissions

### Application Startup Issues

Check:
1. Dependencies installed from `requirements.txt`
2. Start command is correct
3. Render logs for detailed errors
