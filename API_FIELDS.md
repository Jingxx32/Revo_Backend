# API Fields Reference

This document provides a detailed reference of all API endpoints with their request and response fields. This is designed to help frontend developers integrate with the backend API.

## Table of Contents

- [Authentication](#authentication)
- [Products](#products)
- [Cart](#cart)
- [Orders](#orders)
- [Trade-in](#trade-in)
- [Categories](#categories)
- [Locations](#locations)
- [Users](#users)

---

## Authentication

### POST /api/auth/register

Register a new user.

**Authentication:** Not required

**Request Body (JSON):**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Request Fields:**
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| email | string (email) | Yes | User email address | "user@example.com" |
| password | string | Yes | User password (min 8 characters) | "password123" |

**Response (201 Created):**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "customer"
  }
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Registration success status |
| token | string | JWT access token |
| user | object | User information |
| user.id | integer | User ID |
| user.email | string | User email |
| user.role | string | User role (always "customer" for new users) |

**Error Response (400):**
```json
{
  "success": false,
  "error": "Email already registered"
}
```

---

### POST /api/auth/token

Login and get JWT token (OAuth2 password flow).

**Authentication:** Not required

**Request Body (form-data):**
```
username=user@example.com
password=password123
```

**Request Fields:**
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| username | string | Yes | User email address | "user@example.com" |
| password | string | Yes | User password | "password123" |

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| access_token | string | JWT access token |
| token_type | string | Token type (always "bearer") |

**Error Response (401):**
```json
{
  "detail": "Incorrect email or password"
}
```

---

### GET /api/auth/me

Get current authenticated user information.

**Authentication:** Required (Bearer token)

**Request Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "customer",
  "created_at": "2025-01-15T10:00:00"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| id | integer | User ID |
| email | string | User email |
| role | string | User role (customer, admin, evaluator) |
| created_at | string (datetime) | Account creation timestamp |

---

## Products

### GET /api/products

Get list of products with optional filters.

**Authentication:** Not required

**Query Parameters:**
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| category | string | No | Filter by category name | "Phone" |
| brand | string | No | Filter by brand name | "Apple" |
| condition | string | No | Filter by condition (A, B, C) | "A" |
| min_price | float | No | Minimum price filter | 100.0 |
| max_price | float | No | Maximum price filter | 1000.0 |
| city | string | No | Filter by city availability | "Vancouver" |

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "brand": "Apple",
    "model": "iPhone 14 Pro",
    "name": "iPhone 14 Pro 256GB",
    "price": 899.99,
    "originalPrice": 1099.99,
    "condition": "Excellent",
    "rating": 4.5,
    "reviews": 120,
    "location": "Vancouver Hub",
    "image": "https://example.com/image.jpg",
    "highlights": ["Certified inspection", "Store warranty"],
    "cityAvailability": ["Vancouver", "Ottawa"],
    "updatedAt": 20250115
  }
]
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Product ID |
| brand | string | Brand name |
| model | string | Product model |
| name | string | Product title/name |
| price | float | Current selling price |
| originalPrice | float | Original price |
| condition | string | Condition (Excellent, Great, Like-new) |
| rating | float | Product rating (0-5) |
| reviews | integer | Number of reviews |
| location | string | Product location |
| image | string | Product image URL |
| highlights | array[string] | Product highlights |
| cityAvailability | array[string] | Available cities |
| updatedAt | integer | Update date (YYYYMMDD format) |

---

### GET /api/products/search

Search products by keyword.

**Authentication:** Not required

**Query Parameters:**
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| q | string | Yes | Search keyword | "iPhone" |
| category | string | No | Filter by category | "Phone" |
| brand | string | No | Filter by brand | "Apple" |
| min_price | float | No | Minimum price | 100.0 |
| max_price | float | No | Maximum price | 1000.0 |

**Response (200 OK):** Same as GET /api/products

---

### GET /api/products/deals

Get products with discounts.

**Authentication:** Not required

**Query Parameters:**
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| limit | integer | No | Maximum number of deals (default: 10) | 20 |
| min_discount | float | No | Minimum discount percentage | 10.0 |

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "brand": "Apple",
    "model": "iPhone 14 Pro",
    "name": "iPhone 14 Pro 256GB",
    "price": 899.99,
    "originalPrice": 1099.99,
    "condition": "Excellent",
    "rating": 4.5,
    "reviews": 120,
    "location": "Vancouver Hub",
    "image": "https://example.com/image.jpg",
    "highlights": ["Certified inspection"],
    "cityAvailability": ["Vancouver"],
    "updatedAt": 20250115,
    "discount_percent": 18.2,
    "voucher_label": "+18% Voucher"
  }
]
```

**Additional Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| discount_percent | float | Discount percentage |
| voucher_label | string | Voucher label text |

---

### GET /api/products/{product_id}

Get single product by ID.

**Authentication:** Not required

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| product_id | integer | Yes | Product ID |

**Response (200 OK):** Same as GET /api/products (single object)

**Error Response (404):**
```json
{
  "detail": "Product not found"
}
```

---

## Cart

### GET /api/cart

Get user's shopping cart.

**Authentication:** Required (Bearer token)

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "items": [
    {
      "product_id": 1,
      "title": "iPhone 14 Pro 256GB",
      "qty": 2,
      "unit_price": 899.99,
      "line_total": 1799.98
    }
  ],
  "subtotal": 1799.98
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Cart ID |
| user_id | integer | User ID |
| items | array[object] | Cart items |
| items[].product_id | integer | Product ID |
| items[].title | string | Product title |
| items[].qty | integer | Quantity |
| items[].unit_price | float | Unit price |
| items[].line_total | float | Line total (qty * unit_price) |
| subtotal | float | Cart subtotal |

---

### GET /api/cart/count

Get cart item count.

**Authentication:** Required (Bearer token)

**Response (200 OK):**
```json
{
  "count": 3,
  "total_items": 5
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| count | integer | Number of unique products |
| total_items | integer | Total quantity of all items |

---

### POST /api/cart/items

Add item to cart.

**Authentication:** Required (Bearer token)

**Request Body (JSON):**
```json
{
  "product_id": 1,
  "qty": 2
}
```

**Request Fields:**
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| product_id | integer | Yes | Product ID | 1 |
| qty | integer | No | Quantity (default: 1) | 2 |

**Response (201 Created):** Same as GET /api/cart

**Error Response (404):**
```json
{
  "detail": "Product not found"
}
```

---

### PUT /api/cart/items/{product_id}

Update cart item quantity.

**Authentication:** Required (Bearer token)

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| product_id | integer | Yes | Product ID |

**Request Body (JSON):**
```json
{
  "qty": 3
}
```

**Request Fields:**
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| qty | integer | Yes | New quantity | 3 |

**Response (200 OK):** Same as GET /api/cart

**Note:** If qty is 0 or negative, the item will be removed from cart.

**Error Response (404):**
```json
{
  "detail": "Item not in cart"
}
```

---

### DELETE /api/cart/items/{product_id}

Remove item from cart.

**Authentication:** Required (Bearer token)

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| product_id | integer | Yes | Product ID |

**Response (204 No Content):** No response body

**Error Response (404):**
```json
{
  "detail": "Item not in cart"
}
```

---

## Orders

### POST /api/orders

Create a new order from cart.

**Authentication:** Required (Bearer token)

**Response (200 OK):**
```json
{
  "order_id": 1,
  "client_secret": "pi_xxxxx_secret_xxxxx"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| order_id | integer | Order ID |
| client_secret | string | Stripe PaymentIntent client secret |

**Error Responses:**
- `400 Bad Request`: Cart is empty
- `500 Internal Server Error`: Stripe not configured

---

### POST /api/orders/checkout

Checkout with payment (compatible endpoint).

**Authentication:** Required (Bearer token)

**Request Body (JSON):**
```json
{
  "items": [
    {
      "id": 1,
      "name": "iPhone 14 Pro",
      "price": 899.99,
      "quantity": 2
    }
  ],
  "total": 1799.98,
  "paymentMethod": "card"
}
```

**Request Fields:**
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| items | array[object] | Yes | Order items | - |
| items[].id | integer | Yes | Product ID | 1 |
| items[].name | string | No | Product name | "iPhone 14 Pro" |
| items[].price | float | Yes | Product price | 899.99 |
| items[].quantity | integer | Yes | Quantity | 2 |
| total | float | No | Total amount | 1799.98 |
| paymentMethod | string | No | Payment method (card/wallet) | "card" |

**Response (200 OK):**
```json
{
  "success": true,
  "orderId": "ORD1",
  "order_id": 1,
  "client_secret": "pi_xxxxx_secret_xxxxx"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Checkout success status |
| orderId | string | Order ID string (format: ORD{id}) |
| order_id | integer | Order ID |
| client_secret | string | Stripe PaymentIntent client secret (if paymentMethod is "card") |

**Error Response:**
```json
{
  "success": false,
  "error": "Cart is empty"
}
```

---

### GET /api/orders/me

Get current user's orders.

**Authentication:** Required (Bearer token)

**Query Parameters:**
| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| status | string | No | Filter by status | "paid" |
| limit | integer | No | Maximum results (default: 50) | 20 |
| offset | integer | No | Offset for pagination (default: 0) | 0 |

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "status": "paid",
    "subtotal": 1799.98,
    "tax": 0.0,
    "shipping_fee": 0.0,
    "total": 1799.98,
    "created_at": "2025-01-15T10:00:00",
    "items": [
      {
        "product_id": 1,
        "title": "iPhone 14 Pro 256GB",
        "unit_price": 899.99,
        "qty": 2,
        "line_total": 1799.98,
        "product": {
          "id": 1,
          "title": "iPhone 14 Pro 256GB",
          "image": "https://example.com/image.jpg"
        }
      }
    ],
    "payment": {
      "status": "succeeded",
      "amount": 1799.98,
      "currency": "usd"
    }
  }
]
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Order ID |
| user_id | integer | User ID |
| status | string | Order status (pending, paid, shipped, completed, cancelled) |
| subtotal | float | Order subtotal |
| tax | float | Tax amount |
| shipping_fee | float | Shipping fee |
| total | float | Total amount |
| created_at | string (datetime) | Order creation timestamp |
| items | array[object] | Order items |
| items[].product_id | integer | Product ID |
| items[].title | string | Product title snapshot |
| items[].unit_price | float | Unit price |
| items[].qty | integer | Quantity |
| items[].line_total | float | Line total |
| items[].product | object | Product information (if available) |
| items[].product.id | integer | Product ID |
| items[].product.title | string | Product title |
| items[].product.image | string | Product image URL |
| payment | object | Payment information |
| payment.status | string | Payment status |
| payment.amount | float | Payment amount |
| payment.currency | string | Currency code |

---

### POST /api/orders/stripe-webhook

Stripe webhook endpoint (for payment status updates).

**Authentication:** Not required (uses Stripe signature)

**Request Headers:**
```
stripe-signature: <stripe_signature>
```

**Request Body:** Raw Stripe webhook payload

**Response (200 OK):**
```json
{
  "received": true
}
```

---

## Trade-in

### POST /api/tradein/pickup-requests

Create a pickup request for trade-in.

**Authentication:** Required (Bearer token)

**Request Format:** multipart/form-data

**Request Fields:**
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| brand_id | integer | No* | Brand ID | 1 |
| brand_name | string | No* | Brand name | "Apple" |
| model_text | string | Yes | Device model name | "iPhone 14 Pro" |
| storage | string | No | Storage capacity | "256GB" |
| condition | string | Yes | Device condition (A, B, C, D, E) | "A" |
| additional_info | string | No | Additional device information | "Minor scratches" |
| address_json | string | No | Pickup address (JSON string or plain text) | '{"street": "123 Main St", "city": "Shanghai"}' |
| scheduled_at | string | No | Scheduled pickup date/time (ISO 8601) | "2025-01-15T10:00:00" |
| photos | file[] | No | Device photos (up to 5 files, each < 5MB) | - |

**Note:** Either `brand_id` OR `brand_name` must be provided.

**Response (201 Created):**
```json
{
  "id": 123,
  "user_id": 1,
  "brand_id": 1,
  "model_text": "iPhone 14 Pro",
  "storage": "256GB",
  "condition": "A",
  "additional_info": "Minor scratches on screen",
  "photos": [
    "/uploads/tradein_photos/pickup_123_0.jpg",
    "/uploads/tradein_photos/pickup_123_1.jpg"
  ],
  "status": "requested",
  "created_at": "2025-01-15T10:00:00"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Pickup request ID |
| user_id | integer | User ID |
| brand_id | integer | Brand ID |
| model_text | string | Device model name |
| storage | string | Storage capacity |
| condition | string | Device condition |
| additional_info | string | Additional information |
| photos | array[string] | Photo URLs |
| status | string | Request status (requested, accepted, rejected, offered) |
| created_at | string (datetime) | Creation timestamp |

**Error Responses:**
- `400 Bad Request`: Missing required fields or brand not found
- `401 Unauthorized`: Invalid or missing authentication token

---

### GET /api/tradein/pickup-requests/me

Get current user's pickup requests.

**Authentication:** Required (Bearer token)

**Response (200 OK):**
```json
[
  {
    "id": 123,
    "user_id": 1,
    "brand_id": 1,
    "brand_name": "Apple",
    "model_text": "iPhone 14 Pro",
    "storage": "256GB",
    "condition": "A",
    "additional_info": "Minor scratches",
    "photos": [
      "/uploads/tradein_photos/pickup_123_0.jpg"
    ],
    "address_json": {
      "street": "123 Main St",
      "city": "Shanghai"
    },
    "scheduled_at": "2025-01-15T10:00:00",
    "deposit_amount": null,
    "status": "requested"
  }
]
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Pickup request ID |
| user_id | integer | User ID |
| brand_id | integer | Brand ID |
| brand_name | string | Brand name |
| model_text | string | Device model name |
| storage | string | Storage capacity |
| condition | string | Device condition |
| additional_info | string | Additional information |
| photos | array[string] | Photo URLs |
| address_json | object | Pickup address |
| scheduled_at | string (datetime) | Scheduled pickup time |
| deposit_amount | float | Deposit amount (if any) |
| status | string | Request status |

---

### POST /api/tradein/estimate

Get trade-in estimate.

**Authentication:** Not required

**Request Body (JSON):**
```json
{
  "brand": "Apple",
  "model": "iPhone 14 Pro",
  "storage": "256GB",
  "condition": "A",
  "notes": "Minor scratches"
}
```

**Request Fields:**
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| brand | string | Yes | Brand name | "Apple" |
| model | string | Yes | Device model | "iPhone 14 Pro" |
| storage | string | No | Storage capacity | "256GB" |
| condition | string | Yes | Device condition (A, B, C) | "A" |
| notes | string | No | Additional notes | "Minor scratches" |

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "estimated_price": 960.0,
    "service_fee": 50.0,
    "net_amount": 910.0
  }
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Estimation success status |
| data | object | Estimation data |
| data.estimated_price | float | Estimated trade-in price |
| data.service_fee | float | Service fee |
| data.net_amount | float | Net amount (estimated_price - service_fee) |

**Error Response:**
```json
{
  "success": false,
  "error": "Brand, model, and condition are required"
}
```

---

### GET /api/tradein/brands

Get list of available brands for trade-in.

**Authentication:** Not required

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Apple"
  },
  {
    "id": 2,
    "name": "Samsung"
  }
]
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Brand ID |
| name | string | Brand name |

---

### POST /api/tradein/pickup-requests/{pickup_id}/respond

Respond to pickup offer (accept or reject).

**Authentication:** Required (Bearer token)

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| pickup_id | integer | Yes | Pickup request ID |

**Request Body (JSON):**
```json
{
  "action": "accept"
}
```

**Request Fields:**
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| action | string | Yes | Action (accept or reject) | "accept" |

**Response (200 OK):**
```json
{
  "id": 123,
  "user_id": 1,
  "brand_id": 1,
  "model_text": "iPhone 14 Pro",
  "status": "accepted",
  ...
}
```

**Error Responses:**
- `400 Bad Request`: Invalid action
- `404 Not Found`: Pickup request not found

---

## Categories

### GET /api/categories

Get list of categories.

**Authentication:** Not required

**Response (200 OK):**
```json
[
  {
    "id": "phones",
    "name": "Phones",
    "icon": "📱"
  },
  {
    "id": "laptops",
    "name": "Laptops",
    "icon": "💻"
  }
]
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| id | string | Category ID |
| name | string | Category name |
| icon | string | Category icon (emoji) |

---

## Locations

### GET /api/locations

Get list of available locations.

**Authentication:** Not required

**Response (200 OK):**
```json
[
  {
    "id": "vancouver",
    "name": "Vancouver",
    "code": "VAN",
    "hub_name": "Vancouver Hub"
  },
  {
    "id": "ottawa",
    "name": "Ottawa",
    "code": "OTT",
    "hub_name": "Ottawa Lab"
  }
]
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| id | string | Location ID |
| name | string | Location name |
| code | string | Location code |
| hub_name | string | Hub name |

---

### GET /api/locations/{location_id}

Get location details by ID.

**Authentication:** Not required

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| location_id | string | Yes | Location ID |

**Response (200 OK):** Same as GET /api/locations (single object)

**Error Response (404):**
```json
{
  "detail": "Location 'invalid_id' not found"
}
```

---

## Users

### GET /api/users/me/items

**Note:** This endpoint has been removed. Please use `GET /api/tradein/pickup-requests/me` instead.

---

## Authentication Header

Most endpoints require authentication using a Bearer token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

To get a token:
1. Register: `POST /api/auth/register`
2. Login: `POST /api/auth/token`

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message"
}
```

### Common HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no response body
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required or invalid token
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Custom Error Format (Some Endpoints)

Some endpoints return errors in a custom format:

```json
{
  "success": false,
  "error": "Error message"
}
```

---

## Notes for Frontend Developers

1. **Authentication**: Always include the Bearer token in the Authorization header for protected endpoints.

2. **Content-Type**: 
   - Use `application/json` for JSON requests
   - Use `multipart/form-data` for file uploads (e.g., trade-in photos)
   - Use `application/x-www-form-urlencoded` for OAuth2 token endpoint

3. **File Uploads**: 
   - Maximum 5 files per request
   - Each file must be under 5MB
   - Supported formats: JPEG, PNG, etc.

4. **Pagination**: Some endpoints support pagination using `limit` and `offset` query parameters.

5. **Filtering**: Many endpoints support filtering via query parameters. Check individual endpoint documentation.

6. **Date Formats**: 
   - Use ISO 8601 format for datetime: `2025-01-15T10:00:00`
   - Use YYYYMMDD format for dates: `20250115`

7. **Price Fields**: All price fields are in the base currency (typically USD) and are floating-point numbers.

8. **Condition Values**: 
   - `A`: Excellent
   - `B`: Great
   - `C`: Like-new
   - `D`: Good
   - `E`: Fair

---

## Base URL

Development: `http://localhost:8000`
Production: Update based on your deployment

---

## Support

For API support or questions, please refer to the main README.md or contact the development team.

