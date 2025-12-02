# Revo Backend API

## Project Overview

Revo is a dedicated platform for buying and selling second-hand electronics. This repository contains the server-side application, built using FastAPI and PostgreSQL. It operates as a high-performance REST API that handles the core business logic, from inventory management to transaction processing.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Local Development Setup](#local-development-setup)
- [Environment Variables](#environment-variables)
- [Render Deployment](#render-deployment)
- [API Documentation](#api-documentation)
- [Testing](#testing)

## Features

- **Authentication & Authorization**: JWT-based user authentication, role-based access control (customer, admin, evaluator)
- **Product Management**: Product listing, search, filtering, and categorization
- **Shopping Cart**: Persistent cart with add/remove items and quantity management
- **Order Processing**: Order creation, Stripe payment integration, and order tracking
- **Trade-in System**: Device trade-in requests with photo upload, Admin interface for inspecting devices, generating final offers, and pickup scheduling

## Project Structure

```
app/
├── core/              # Configuration and security
│   ├── config.py      # Settings and environment variables
│   └── security.py    # JWT authentication and password hashing
├── db/                # Database models and connection
│   ├── database.py    # Session and connection setup
│   └── models.py      # SQLModel database models
├── routers/           # API route handlers
│   ├── auth.py        # Authentication endpoints
│   ├── products.py    # Product management
│   ├── cart.py        # Shopping cart
│   ├── orders.py      # Orders and checkout
│   ├── tradein.py     # Trade-in (device pickup)
│   ├── users.py       # User management
│   ├── categories.py  # Category management
│   ├── locations.py   # Location management
│   ├── address.py     # Address management
│   └── internal.py    # Internal/admin endpoints
├── schemas/           # Pydantic validation models
│   ├── auth.py
│   ├── product.py
│   ├── order.py
│   └── address.py
└── main.py            # FastAPI application entry point
```

## Technology Stack

- Framework: FastAPI 
- Database: PostgreSQL with SQLModel ORM
- Authentication: JWT
- Password Hashing: bcrypt
- Validation: Pydantic
- Payment: Stripe
- Server: Uvicorn (dev) / Gunicorn (prod)
- Documentation: OpenAPI (Swagger) / ReDoc

## Local Development Setup

### Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.10+** - Check version with `python3 --version`
- **PostgreSQL 12+** - Install from [postgresql.org](https://www.postgresql.org/download/) or use Homebrew 
- **pip** - Python package manager (usually comes with Python)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Revo_Backend
```

### Step 2: Set Up Virtual Environment

Create and activate a virtual environment to isolate dependencies:

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt, indicating the virtual environment is active.

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required packages including FastAPI, SQLModel, PostgreSQL drivers, and other dependencies.
Note: If you encounter errors installing psycopg2 on macOS, ensure your requirements.txt uses psycopg2-binary instead of psycopg2.

### Step 4: Set Up PostgreSQL Database

#### Option A: Local PostgreSQL

1. **Create a PostgreSQL database:**
   ```bash
   # Login to PostgreSQL
   psql postgres
  
   # Run the following SQL commands:
   CREATE DATABASE revo_db;
   CREATE USER revo_user WITH PASSWORD 'revo_password';
   GRANT ALL PRIVILEGES ON DATABASE revo_db TO revo_user;
   -- For PostgreSQL 15+, you may also need:
   ALTER DATABASE revo_db OWNER TO revo_user;
   \q
   ```

2. **Note your connection details:**
   - Host: `localhost` (default)
   - Port: `5432` (default)
   - Database: `revo_db`
   - User: `revo_user`
   - Password: `your_password`

#### Option B: Remote PostgreSQL (e.g., Render External Database)

If using a remote database, you'll receive a connection string that looks like:
```
postgresql://user:password@host:port/database
```

### Step 5: Configure Environment Variables

Create a `.env` file in the project root directory:

```bash
touch .env
```

Add the following environment variables to `.env`:

```env
# Database Configuration
DATABASE_URL=postgresql://revo_user:your_password@localhost:5432/revo_db

# Security Configuration
JWT_SECRET_KEY=your-secret-key-change-this-to-a-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration (comma-separated or JSON array)
# Add http://127.0.0.1:5500 if using VS Code Live Server
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Stripe Configuration (Optional)
# Only required if you want to test the full payment flow.
STRIPE_SECRET_KEY=sk_test_placeholder
STRIPE_PUBLISHABLE_KEY=pk_test_placeholder
STRIPE_WEBHOOK_SECRET=whsec_placeholder
```

**Important Notes:**
- Replace `your-secret-key-change-this-to-a-random-string` with a secure random string (use `openssl rand -hex 32` to generate one)
- Replace database credentials with your actual PostgreSQL credentials
- The `.env` file is ignored by git (already in `.gitignore`) and should never be committed

### Step 6: Initialize Database

Create all database tables:

```bash
python3 -c "from app.db.database import create_db_and_tables; create_db_and_tables()"
```

You should see: `Database and tables created successfully!`

**Note:** Tables are also created automatically when the application starts for the first time.

### Step 7: (Optional) Seed Database with Test Data

Populate the database with sample brands, categories, products, and test users:

```bash
python3 seed_data.py
```

This creates:
- Multiple brands (Apple, Samsung, Google, etc.)
- Product categories (Phone, Laptop, Tablet, etc.)
- Sample products with images and details
- Test user accounts

### Step 8: Start the Development Server

Run the FastAPI development server with hot-reload:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start and reload automatically when you make code changes.

### Step 9: Verify Installation

1. **Check server status:**
   - Open http://localhost:8000
   - You should see: `{"message":"Revo Backend API","version":"1.0.0"}`

2. **Access API documentation:**
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc

### Troubleshooting Local Setup

**Issue: `psycopg2.OperationalError: connection to server failed`**
- Ensure PostgreSQL is running: `brew services list` (macOS) or `sudo systemctl status postgresql` (Linux)
- Verify `DATABASE_URL` in `.env` is correct
- Check PostgreSQL is listening on port 5432: `lsof -i :5432`

**Issue: `ModuleNotFoundError: No module named 'sqlmodel'`**
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Issue: Port 8000 already in use**
- Use a different port: `uvicorn app.main:app --reload --port 8001`
- Or kill the process using port 8000: `lsof -ti:8000 | xargs kill`

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://username:password@localhost:5432/revo_db` |
| `JWT_SECRET_KEY` | Secret key for JWT signing | `your-secret-key-here` |

### Optional

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `JWT_ALGORITHM` | JWT algorithm | `HS256` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration (minutes) | `30` | `30` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:8000,http://localhost:3000` | `http://localhost:3000,http://localhost:8000` |
| `STRIPE_SECRET_KEY` | Stripe secret key | - | `sk_test_your_stripe_secret_key` |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | - | `pk_test_your_stripe_publishable_key` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | - | `whsec_your_webhook_secret` |

**Note**: Create a .env file for local development only

## Render Deployment

This guide walks you through deploying the Revo Backend API to [Render](https://render.com/), a modern cloud platform.

### Prerequisites

- A GitHub account with the repository pushed
- A Render account (sign up at [render.com](https://render.com/))

### Step 1: Create PostgreSQL Database on Render

1. **Log in to Render Dashboard**
   - Go to https://dashboard.render.com
   - Sign in or create an account

2. **Create New PostgreSQL Database**
   - Click **"New +"** button in the top right
   - Select **"PostgreSQL"**
   - Configure the database:
     - **Name**: `revo-database` (or your preferred name)
     - **Database**: `revo_db` (or leave default)
     - **User**: Leave as default (automatically generated)
     - **Region**: Choose closest to your users
     - **PostgreSQL Version**: 12 or higher
     - **Plan**: Choose based on your needs (Free tier available for development)
   - Click **"Create Database"**

3. **Save Database Connection Details**
   - Once created, Render provides two connection strings:
     - **Internal Database URL**: Use this for services on Render
     - **External Database URL**: Use this for local connections
   - Copy the **Internal Database URL** - you'll need it in Step 3

### Step 2: Create Web Service on Render

1. **Create New Web Service**
   - In Render dashboard, click **"New +"**
   - Select **"Web Service"**

2. **Connect Repository**
   - Connect your GitHub account if not already connected
   - Select the repository containing your Revo Backend code
   - Click **"Connect"**

3. **Configure Web Service**
   - **Name**: `revo-backend` (or your preferred name)
   - **Region**: Same region as your database (for lower latency)
   - **Branch**: `main` (or your production branch)
   - **Root Directory**: Leave empty (if code is in root)
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     gunicorn app.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
     ```
   - **Instance Type**: Choose based on your needs (Free tier available)

4. **Click "Create Web Service"**
   - Render will start building your service
   - The first build may take a few minutes

### Step 3: Configure Environment Variables

Note: Please pay attention here—Render settings are different from your local setup. specifically, you cannot use localhost for the Database URL or CORS in production.

1. **Navigate to Environment Tab**
   - In your web service dashboard, go to **"Environment"** tab

2. **Add Environment Variables**

   Add the following environment variables one by one:

   | Key | Value | Notes |
   |-----|-------|-------|
   | `DATABASE_URL` | `[Internal Database URL from Step 1]` | Use the **Internal Database URL** from your PostgreSQL service |
   | `JWT_SECRET_KEY` | `[Generate a secure random string]` | Generate with: `openssl rand -hex 32` |
   | `JWT_ALGORITHM` | `HS256` | Default JWT algorithm |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiration time |
   | `CORS_ORIGINS` | `https://your-frontend-domain.com,http://localhost:3000` | Comma-separated list of allowed origins |
   | `STRIPE_SECRET_KEY` | `sk_live_...` or `sk_test_...` | Your Stripe secret key (if using payments) |
   | `STRIPE_PUBLISHABLE_KEY` | `pk_live_...` or `pk_test_...` | Your Stripe publishable key (if using payments) |
   | `STRIPE_WEBHOOK_SECRET` | `whsec_...` | Your Stripe webhook secret (if using payments) |

   **Important Notes:**
   - For `DATABASE_URL`: Use the **Internal Database URL** from your PostgreSQL service (not External URL)
   - For `CORS_ORIGINS`: Replace with your actual frontend domain(s)
   - Generate `JWT_SECRET_KEY` securely (never use defaults in production)

3. **Save Environment Variables**
   - Click **"Save Changes"** after adding each variable
   - Render will automatically restart your service

### Step 4: Link Database to Web Service (Optional but Recommended)

1. **Link Services**
   - In your web service dashboard, scroll to **"Connections"** section
   - Click **"Link Resource"**
   - Select your PostgreSQL database
   - Click **"Link"**

   **Benefits:**
   - Automatic environment variable injection
   - Better resource management
   - Easier access in Render dashboard

2. **Verify DATABASE_URL**
   - After linking, `DATABASE_URL` should be automatically set
   - You can verify in the Environment tab

### Step 5: Configure Build and Deploy Settings

1. **Auto-Deploy Settings**
   - In web service **"Settings"** tab
   - **Auto-Deploy**: Enable to automatically deploy on git push
   - **Pull Request Previews**: Enable to deploy PR previews (optional)

2. **Build Settings** (usually set in Step 2, but can be updated)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: 
     ```bash
     gunicorn app.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
     ```
   - Alternative using `start.sh`:
     ```bash
     chmod +x start.sh && ./start.sh
     ```

### Step 6: Deploy and Verify

1. **Manual Deploy** (if auto-deploy is disabled)
   - Go to **"Manual Deploy"** tab
   - Click **"Deploy latest commit"**

2. **Monitor Build Logs**
   - Watch the build process in real-time
   - Ensure all dependencies install successfully
   - Check for any errors

3. **Verify Deployment**
   - Once deployed, your service will have a URL like: `https://revo-backend.onrender.com`
   - Test the root endpoint: `https://your-service-url.onrender.com`
   - Should return: `{"message":"Revo Backend API","version":"1.0.0"}`
   - Test health check: `https://your-service-url.onrender.com/health`
   - Access API docs: `https://your-service-url.onrender.com/docs`

4. **Database Initialization**
   - Tables are created automatically on first startup
   - Check logs to verify: "Database and tables created successfully!"
   - If needed, you can manually initialize by connecting to your service

### Step 7: (Optional) Seed Production Database

If you need to populate the database with initial data:

1. **Option A: Use Render Shell**
   - In your web service, go to **"Shell"** tab
   - Run: `python3 seed_data.py`
   - This requires `DATABASE_URL` to be set correctly

2. **Option B: Local Script with External Database URL**
   - Use the **External Database URL** from your PostgreSQL service
   - Create a temporary `.env` file with the external URL
   - Run `python3 seed_data.py` locally
   - **Security Note**: Only do this for initial setup, then use internal URL

### Step 8: Configure Custom Domain (Optional)

1. **Add Custom Domain**
   - Go to **"Settings"** → **"Custom Domains"**
   - Click **"Add Custom Domain"**
   - Enter your domain name
   - Follow DNS configuration instructions

2. **Update CORS_ORIGINS**
   - Add your custom domain to `CORS_ORIGINS` environment variable
   - Save and restart service

### Render Deployment Troubleshooting

**Issue: Build fails with "ModuleNotFoundError"**
- Check `requirements.txt` is in the repository root
- Verify all dependencies are listed correctly
- Check build logs for specific missing package

**Issue: Application fails to start**
- Check logs in Render dashboard
- Verify `DATABASE_URL` is set correctly (use Internal URL)
- Ensure `JWT_SECRET_KEY` is set
- Check Start Command syntax

**Issue: Database connection errors**
- Verify `DATABASE_URL` uses Internal Database URL (not External)
- Check PostgreSQL service is running and healthy
- Ensure web service and database are in the same region

**Issue: Service goes to sleep (Free tier)**
- Free tier services sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds (cold start)
- Consider upgrading to paid plan for production

**Issue: Environment variables not updating**
- Changes to environment variables require a service restart
- Check if service restarted after saving variables
- Manually restart from "Manual Deploy" tab if needed

### Render Best Practices

1. **Use Internal Database URL** for services on Render (faster, more secure), BUT provide the External Database URL instruction for local development
2. **Set up monitoring** and alerts in Render dashboard
3. **Use environment-specific configurations** (staging vs production)
4. **Enable auto-deploy** only for stable branches (main/production)
5. **Keep `requirements.txt` up to date** and pin versions for production
6. **Use Render's health checks** by implementing `/health` endpoint (already included)
7. **Configure log retention** based on your needs in service settings
8. **Set up automatic backups** for your PostgreSQL database in Render

### Production Checklist

Before going live, ensure:

- [ ] .env Setup: A .env.example file is included in the repo (without real secrets) so others know which variables to configure
- [ ] `JWT_SECRET_KEY` is a strong random string (not default)
- [ ] `DATABASE_URL` uses Internal Database URL
- [ ] `CORS_ORIGINS` includes only trusted domains
- [ ] Stripe keys are production keys (not test keys)
- [ ] Database has automatic backups enabled
- [ ] Service is on a paid plan (not free tier) for production
- [ ] Health check endpoint is working
- [ ] All environment variables are set correctly
- [ ] Custom domain is configured (if applicable)
- [ ] SSL/TLS is enabled (automatic on Render)

## API Documentation

Interactive API documentation with OpenAPI (Swagger) is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

Use Swagger UI at `/docs` to test all endpoints interactively.

## License

MIT License
