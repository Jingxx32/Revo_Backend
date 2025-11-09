from pydantic import BaseModel
from typing import Optional, List


class ProductResponse(BaseModel):
    id: int
    brand: str
    model: str
    name: str
    price: float
    originalPrice: float
    condition: str
    rating: float = 4.5
    reviews: int = 0
    location: str = "Vancouver Hub"
    image: str
    highlights: List[str] = []
    cityAvailability: List[str] = ["Vancouver"]
    updatedAt: Optional[int] = None

    class Config:
        from_attributes = True

