# Revo Backend API

Backend API for Revo C2B2C Electronics Trade-in Platform.

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/revo_db

# Security
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

```

3. Initialize database:
```bash
python -c "from app.db.database import create_db_and_tables; create_db_and_tables()"
```
Tables are created automatically on first run.

4. Run server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Access API documentation at http://localhost:8000/docs

## API Documentation

Interactive API documentation with OpenAPI (Swagger) is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc 

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

## Features

### Authentication & Authorization
- User registration with email and password
- JWT-based authentication
- OAuth2 password flow
- Password hashing with bcrypt
- Role-based access control (customer, admin, evaluator)

### Product Management
- Product listing with filtering and pagination
- Product details and search
- Category and brand management
- Product image handling

### Shopping Cart
- Add/remove items
- Update quantities
- Persistent cart per user

### Order Management
- Order creation and processing
- Stripe payment integration
- Order history and tracking
- Order status management
- Inventory deduction

### Trade-in
- Device trade-in requests
- Pickup request creation
- Device condition assessment
- Photo upload for evaluation
- Trade-in valuation
- Pickup scheduling

### User Management
- User profile management
- User information retrieval
- User role management

### Address Management
- CRUD operations for shipping addresses
- Default address management

### Location Management
- Location listing and details
- Multi-city support

## Security

- JWT token-based authentication
- bcrypt password hashing
- Configurable CORS
- Pydantic input validation
- SQL injection protection via SQLModel ORM
- Role-based access control
- Environment variable configuration

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

## Technology Stack

- Framework: FastAPI 0.104+
- Database: PostgreSQL with SQLModel ORM
- Authentication: JWT
- Password Hashing: bcrypt
- Validation: Pydantic
- Payment: Stripe
- Server: Uvicorn (dev) / Gunicorn (prod)
- Documentation: OpenAPI (Swagger) / ReDoc

## Deployment

### Deployment Example: Render

1. Create PostgreSQL database on Render (connection string sets `DATABASE_URL` automatically)

2. Set environment variables in Render dashboard Environment tab (see [Environment Variables](#environment-variables))

3. Configure deployment settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

4. Database tables are created automatically on application startup (configured in `main.py`).


## Testing

Use Swagger UI at `/docs` to test all endpoints interactively.

## License

MIT License