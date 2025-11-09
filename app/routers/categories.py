from fastapi import APIRouter, Depends
from sqlmodel import select

from app.db.database import get_session
from app.db.models import Category


router = APIRouter(prefix="/api/categories", tags=["Categories"])


DEFAULT_CATEGORIES = [
    {"id": "phones", "name": "Phones", "icon": "📱"},
    {"id": "laptops", "name": "Laptops", "icon": "💻"},
    {"id": "tablets", "name": "Tablets", "icon": "📱"},
    {"id": "accessories", "name": "Accessories", "icon": "🎧"},
]

# Category name mapping for compatibility
CATEGORY_NAME_MAP = {
    "Phone": "phones",
    "Laptop": "laptops",
    "Tablet": "tablets",
    "Accessory": "accessories",
}

CATEGORY_ICON_MAP = {
    "Phone": "📱",
    "Laptop": "💻",
    "Tablet": "📱",
    "Accessory": "🎧",
}


@router.get("/")
def list_categories(session=Depends(get_session)):
    """Get categories list with icon support for frontend compatibility."""
    categories = session.exec(select(Category)).all()
    
    if categories:
        # Format categories with icon
        result = []
        for cat in categories:
            # Map category name to frontend format
            category_id = CATEGORY_NAME_MAP.get(cat.name, cat.name.lower())
            icon = CATEGORY_ICON_MAP.get(cat.name, "📦")
            
            result.append({
                "id": category_id,
                "name": cat.name + "s" if not cat.name.endswith("s") else cat.name,  # Pluralize
                "icon": icon,
            })
        return result
    
    # If DB is empty, return the default navigation set
    return DEFAULT_CATEGORIES




