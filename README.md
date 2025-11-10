# Revo Backend API

Backend API for Revo C2B2C Electronics Trade-in Platform - A comprehensive e-commerce platform for buying, selling, and trading electronic devices.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/revo_db

# Security
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (comma-separated list of allowed origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Stripe (for payment processing)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# AWS S3 (optional, for file storage)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_BUCKET_NAME=your_bucket_name
AWS_REGION=us-east-1
```

### 3. Initialize Database

The database tables will be created automatically on first run. Alternatively, you can initialize them manually:

```bash
python -c "from app.db.database import create_db_and_tables; create_db_and_tables()"
```

### 4. Run the Server

**Development Environment:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production Environment:**
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 5. Access API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📚 API Documentation

The API documentation is automatically generated using OpenAPI (Swagger) and is available at `/docs` endpoint. The documentation includes:

- Interactive API testing interface
- Request/response schemas
- Authentication requirements
- Example requests and responses
- Error codes and messages

## 🔧 Project Structure

```
app/
├── core/              # Core configuration and security
│   ├── config.py      # Application settings and environment variables
│   └── security.py    # JWT authentication and password hashing
├── db/                # Database models and connection
│   ├── database.py    # Database session and connection setup
│   └── models.py      # SQLModel database models
├── routers/           # API route handlers
│   ├── auth.py        # Authentication endpoints (register, login, token)
│   ├── products.py    # Product management endpoints
│   ├── cart.py        # Shopping cart endpoints
│   ├── orders.py      # Order management and checkout endpoints
│   ├── tradein.py     # Trade-in (device pickup) endpoints
│   ├── users.py       # User management endpoints
│   ├── categories.py  # Category management endpoints
│   ├── locations.py   # Location management endpoints
│   └── internal.py    # Internal/admin endpoints
├── schemas/           # Pydantic models for request/response validation
│   ├── auth.py        # Authentication schemas
│   └── product.py     # Product schemas
└── main.py            # FastAPI application entry point
```

## 📋 Main Features

### Authentication & Authorization
- ✅ User registration with email and password
- ✅ JWT-based authentication
- ✅ OAuth2 password flow
- ✅ Password hashing with bcrypt
- ✅ Role-based access control (customer, admin, evaluator)

### Product Management
- ✅ Product listing with filtering and pagination
- ✅ Product details and search
- ✅ Category management
- ✅ Brand management
- ✅ Product image handling

### Shopping Cart
- ✅ Add/remove items from cart
- ✅ Update item quantities
- ✅ Cart persistence per user
- ✅ Cart item management

### Order Management
- ✅ Order creation and processing
- ✅ Stripe payment integration
- ✅ Order history and tracking
- ✅ Order status management

### Trade-in Functionality
- ✅ Device trade-in requests
- ✅ Pickup request creation
- ✅ Device condition assessment
- ✅ Photo upload for device evaluation
- ✅ Trade-in valuation
- ✅ Pickup scheduling

### User Management
- ✅ User profile management
- ✅ User information retrieval
- ✅ User role management

### Location Management
- ✅ Location listing
- ✅ Location details
- ✅ Multi-city support

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt password hashing for secure storage
- **CORS Support**: Configurable CORS for cross-origin requests
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Protection**: SQLModel ORM with parameterized queries
- **Role-based Access Control**: User roles and permissions
- **Environment Variables**: Secure configuration management

## 📝 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL database connection string | `postgresql://user:pass@localhost:5432/revo_db` |
| `JWT_SECRET_KEY` | Secret key for JWT token signing | `your-secret-key-change-this` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time (minutes) | `30` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:8000,http://localhost:3000` |
| `STRIPE_SECRET_KEY` | Stripe secret key for payments | - |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | - |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | - |
| `AWS_ACCESS_KEY_ID` | AWS access key for S3 | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key for S3 | - |
| `AWS_BUCKET_NAME` | AWS S3 bucket name | - |
| `AWS_REGION` | AWS region | `us-east-1` |

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt
- **Validation**: Pydantic
- **Payment Processing**: Stripe
- **Server**: Uvicorn (development) / Gunicorn (production)
- **API Documentation**: OpenAPI (Swagger) / ReDoc

## 🚢 Deployment

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).

### Quick Deployment Guide

1. Set up PostgreSQL database
2. Configure environment variables
3. Install dependencies: `pip install -r requirements.txt`
4. Run database migrations (if applicable)
5. Start the server with Gunicorn:
   ```bash
   gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

## 📖 API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/token` - Login and get JWT token
- `GET /api/auth/me` - Get current user information

### Products
- `GET /api/products` - List all products (with filtering)
- `GET /api/products/{id}` - Get product details

### Cart
- `GET /api/cart` - Get user's cart
- `POST /api/cart/items` - Add item to cart
- `PUT /api/cart/items/{product_id}` - Update cart item
- `DELETE /api/cart/items/{product_id}` - Remove item from cart
- `GET /api/cart/count` - Get cart item count

### Orders
- `POST /api/orders` - Create new order
- `POST /api/orders/checkout` - Checkout with payment
- `GET /api/orders` - Get user's orders

### Trade-in
- `POST /api/tradein/pickup-requests` - Create pickup request
- `GET /api/tradein/pickup-requests/me` - Get user's pickup requests
- `POST /api/tradein/estimate` - Get trade-in estimate
- `GET /api/tradein/brands` - List available brands
- `POST /api/tradein/pickup-requests/{id}/respond` - Respond to pickup offer

### Categories
- `GET /api/categories` - List all categories

### Locations
- `GET /api/locations` - List all locations
- `GET /api/locations/{id}` - Get location details

### Health Check
- `GET /` - API root endpoint
- `GET /health` - Health check endpoint
- `GET /api/health` - API health check endpoint

## 🧪 Testing

To test the API endpoints, you can use:

1. **Swagger UI**: Interactive testing at `/docs`
2. **cURL**: Command-line tool for API testing
3. **Postman**: API testing tool
4. **Python requests**: Programmatic API testing

Example using cURL:

```bash
# Register a new user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Login and get token
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"

# Get products (with authentication)
curl -X GET "http://localhost:8000/api/products" \
  -H "Authorization: Bearer <your-token>"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support, please open an issue in the GitHub repository or contact the development team.

## 🎯 Roadmap

- [ ] Add unit tests and integration tests
- [ ] Implement Redis caching
- [ ] Add email notifications
- [ ] Implement file upload to S3
- [ ] Add API rate limiting
- [ ] Implement websocket support for real-time updates
- [ ] Add comprehensive logging and monitoring

---

**Built with ❤️ using FastAPI**
