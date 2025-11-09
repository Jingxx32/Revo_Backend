from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    # Note: role field removed for security - all new users are created as 'customer' by default
    # Role is set server-side and cannot be specified by the client
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserLogin(BaseModel):
    """Login request schema."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password", min_length=1)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    """User information in login response."""
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    role: str = Field(..., description="User role (customer, admin, evaluator)")


class LoginSuccessResponse(BaseModel):
    """Successful login response schema."""
    success: bool = Field(True, description="Login success status")
    token: str = Field(..., description="JWT access token")
    user: UserInfo = Field(..., description="User information")


class LoginErrorResponse(BaseModel):
    """Failed login response schema."""
    success: bool = Field(False, description="Login success status")
    error: str = Field(..., description="Error message")


