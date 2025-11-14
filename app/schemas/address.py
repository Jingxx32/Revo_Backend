from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AddressBase(BaseModel):
    """Base address schema with common fields."""
    
    full_name: str = Field(..., description="Recipient full name", min_length=1, max_length=100)
    phone_number: str = Field(..., description="Contact phone number", min_length=1, max_length=20)
    address_line1: str = Field(..., description="Street address / Building", min_length=1, max_length=200)
    address_line2: Optional[str] = Field(None, description="Apartment / Suite / Additional info", max_length=200)
    city: str = Field(..., description="City name", min_length=1, max_length=100)
    state: str = Field(..., description="Province / State", min_length=1, max_length=100)
    postal_code: str = Field(..., description="Postal / ZIP code", min_length=1, max_length=20)
    country: str = Field(default="Canada", description="Country name", max_length=100)
    is_default: bool = Field(default=False, description="Is this the default address")


class AddressCreate(AddressBase):
    """Schema for creating a new address."""
    pass


class AddressUpdate(BaseModel):
    """Schema for updating an address - all fields are optional."""
    
    full_name: Optional[str] = Field(None, description="Recipient full name", min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, description="Contact phone number", min_length=1, max_length=20)
    address_line1: Optional[str] = Field(None, description="Street address / Building", min_length=1, max_length=200)
    address_line2: Optional[str] = Field(None, description="Apartment / Suite / Additional info", max_length=200)
    city: Optional[str] = Field(None, description="City name", min_length=1, max_length=100)
    state: Optional[str] = Field(None, description="Province / State", min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, description="Postal / ZIP code", min_length=1, max_length=20)
    country: Optional[str] = Field(None, description="Country name", max_length=100)
    is_default: Optional[bool] = Field(None, description="Is this the default address")


class AddressRead(AddressBase):
    """Schema for reading an address - includes id."""
    
    id: int = Field(..., description="Address ID")
    user_id: int = Field(..., description="User ID who owns this address")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True

