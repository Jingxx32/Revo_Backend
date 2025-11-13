from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ShippingAddressSchema(BaseModel):
    """Shipping address schema matching frontend structure."""
    
    # Contact information
    fullName: Optional[str] = Field(None, description="Full name of the recipient")
    phone: Optional[str] = Field(None, description="Phone number of the recipient")
    email: Optional[str] = Field(None, description="Email address of the recipient")
    
    # Address information
    street: Optional[str] = Field(None, description="Street address (e.g., '123 Main Street')")
    city: Optional[str] = Field(None, description="City name (e.g., 'Vancouver')")
    province: Optional[str] = Field(None, description="Province/State code (e.g., 'BC', 'ON')")
    postalCode: Optional[str] = Field(None, description="Postal/ZIP code (e.g., 'V6B 1A1')")
    country: Optional[str] = Field(None, description="Country name (e.g., 'Canada')")
    
    # Additional address fields (alternative field names)
    address: Optional[str] = Field(None, description="Full address string (alternative to street)")
    zipCode: Optional[str] = Field(None, description="ZIP code (alternative to postalCode)")
    state: Optional[str] = Field(None, description="State (alternative to province)")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "fullName": "John Doe",
                "phone": "+1 (604) 555-0123",
                "email": "john.doe@example.com",
                "street": "123 Main Street",
                "city": "Vancouver",
                "province": "BC",
                "postalCode": "V6B 1A1",
                "country": "Canada"
            }
        }


class CartItemSchema(BaseModel):
    """Cart item schema matching frontend structure."""
    
    id: int = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    price: float = Field(..., description="Unit price")
    quantity: int = Field(..., description="Quantity")
    image: Optional[str] = Field(None, description="Product image URL")
    brand: Optional[str] = Field(None, description="Brand name")
    model: Optional[str] = Field(None, description="Product model")
    condition: Optional[str] = Field(None, description="Product condition")
    rating: Optional[float] = Field(None, description="Product rating")
    reviews: Optional[int] = Field(None, description="Number of reviews")
    location: Optional[str] = Field(None, description="Product location")
    originalPrice: Optional[float] = Field(None, description="Original price")
    highlights: Optional[List[str]] = Field(None, description="Product highlights")
    cityAvailability: Optional[List[str]] = Field(None, description="Available cities")
    updatedAt: Optional[int] = Field(None, description="Update timestamp")


class CheckoutRequest(BaseModel):
    """Checkout request schema matching frontend structure."""
    
    items: List[CartItemSchema] = Field(..., description="List of cart items")
    total: str = Field(..., description="Total amount (as string)")
    paymentMethod: str = Field(..., description="Payment method: 'card', 'wallet', or 'cod'")
    timestamp: Optional[str] = Field(None, description="Order timestamp (ISO 8601 format)")
    shippingAddress: Optional[ShippingAddressSchema] = Field(None, description="Shipping address information")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 1001,
                        "name": "iPhone 14 128GB Midnight",
                        "price": 899.00,
                        "quantity": 2,
                        "image": "https://via.placeholder.com/480x360.png?text=iPhone+14",
                        "brand": "Apple",
                        "model": "iPhone 14",
                        "condition": "Excellent"
                    }
                ],
                "total": "1234.56",
                "paymentMethod": "card",
                "timestamp": "2025-01-15T10:00:00.000Z",
                "shippingAddress": {
                    "fullName": "John Doe",
                    "phone": "+1 (604) 555-0123",
                    "street": "123 Main Street",
                    "city": "Vancouver",
                    "province": "BC",
                    "postalCode": "V6B 1A1",
                    "country": "Canada"
                }
            }
        }


class OrderCreate(BaseModel):
    """Order creation request schema for POST /api/orders/ endpoint."""
    
    shippingAddress: Optional[ShippingAddressSchema] = Field(None, description="Shipping address information")
    
    class Config:
        from_attributes = True

