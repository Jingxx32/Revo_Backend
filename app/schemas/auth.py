from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str | None = None  # defaults to customer in model if None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


