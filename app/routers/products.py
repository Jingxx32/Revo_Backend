import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select

from app.db.database import get_session
from app.db.models import Brand, Category, Product
from app.schemas.product import ProductResponse


router = APIRouter(prefix="/api/products", tags=["Products"])


# Condition mapping
CONDITION_MAP = {
    "A": "Excellent",
    "B": "Great",
    "C": "Like-new",
}


def _parse_images_json(images_json: Optional[str]) -> str:
    """Extract first image URL from JSON string, or return placeholder."""
    if not images_json:
        return "https://via.placeholder.com/480x360.png?text=Product"
    try:
        images = json.loads(images_json)
        if isinstance(images, list) and len(images) > 0:
            return images[0] if isinstance(images[0], str) else images[0].get("url", "")
        elif isinstance(images, dict):
            return images.get("url", "") or images.get("primary", "")
    except:
        pass
    return "https://via.placeholder.com/480x360.png?text=Product"


def _parse_highlights(product: Product) -> list[str]:
    """Extract highlights from description or cost_components_json."""
    highlights = []
    if product.description:
        # Try to extract from description (simple approach)
        desc_lower = product.description.lower()
        common_highlights = [
            "certified inspection",
            "unlocked",
            "includes charger",
            "battery health",
            "warranty",
            "apple pencil",
            "liquid retina",
            "dynamic amoled",
            "fast charger",
            "s pen",
            "120hz display",
        ]
        for hl in common_highlights:
            if hl in desc_lower:
                highlights.append(hl.title())
    
    # Also check cost_components_json
    if product.cost_components_json:
        try:
            components = json.loads(product.cost_components_json)
            if isinstance(components, dict):
                if components.get("warranty"):
                    highlights.append("Store warranty")
                if components.get("charger_included"):
                    highlights.append("Includes charger")
        except:
            pass
    
    # Default highlights if none found
    if not highlights:
        highlights = ["Certified inspection", "Store warranty"]
    
    return highlights[:5]  # Limit to 5 highlights


def _parse_json_array(json_str: Optional[str], default: list = None) -> list:
    """Parse JSON array string, return default if invalid."""
    if default is None:
        default = []
    if not json_str:
        return default
    try:
        parsed = json.loads(json_str)
        if isinstance(parsed, list):
            return parsed
    except:
        pass
    return default


def _format_product_response(product: Product, brand: Optional[Brand] = None) -> ProductResponse:
    """Convert Product model to ProductResponse format."""
    # Get brand name
    brand_name = brand.name if brand else "Unknown"
    
    # Get model from database field, or extract from title as fallback
    model = product.model
    if not model:
        if brand:
            # Try to extract model by removing brand name
            title_parts = product.title.replace(brand.name, "").strip().split()
            if title_parts:
                model = " ".join(title_parts[:3])  # Take first 3 words as model
        else:
            # Fallback: use first few words of title
            title_parts = product.title.split()
            model = " ".join(title_parts[:3]) if len(title_parts) > 1 else product.title
    
    # Map condition
    condition = CONDITION_MAP.get(product.condition, "Good") if product.condition else "Good"
    
    # Get prices
    price = product.resale_price or product.list_price or product.base_price or 0.0
    original_price = product.base_price or product.list_price or price * 1.15  # Fallback: 15% markup
    
    # Parse image
    image = _parse_images_json(product.images_json)
    
    # Get highlights from database field, or parse from description as fallback
    highlights = _parse_json_array(product.highlights_json)
    if not highlights:
        highlights = _parse_highlights(product)
    
    # Get city availability from database field, or use default
    city_availability = _parse_json_array(product.city_availability_json, ["Vancouver", "Ottawa", "Edmonton"])
    
    # Get location from database field, or use default
    location = product.location or "Vancouver Hub"
    
    # Get rating and reviews from database, or use defaults
    rating = product.rating if product.rating is not None else 4.5
    reviews = product.reviews if product.reviews is not None else 0
    
    # Parse updated_at to YYYYMMDD format
    updated_at_int = None
    if product.updated_at:
        try:
            # Assume format like "2025-01-04" or "2025-01-04 12:00:00"
            date_str = product.updated_at[:10].replace("-", "")
            updated_at_int = int(date_str)
        except:
            pass
    
    return ProductResponse(
        id=product.id or 0,
        brand=brand_name,
        model=model,
        name=product.title,
        price=round(price, 2),
        originalPrice=round(original_price, 2),
        condition=condition,
        rating=rating,
        reviews=reviews,
        location=location,
        image=image,
        highlights=highlights,
        cityAvailability=city_availability,
        updatedAt=updated_at_int,
    )


@router.get("/", response_model=list[ProductResponse])
def list_products(
    category: Optional[str] = Query(None, description="Filter by category name (e.g., 'Phone', 'Laptop')"),
    brand: Optional[str] = Query(None, description="Filter by brand name (e.g., 'Apple', 'Samsung')"),
    condition: Optional[str] = Query(None, description="Filter by condition: 'A' (Excellent), 'B' (Great), 'C' (Like-new)"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    city: Optional[str] = Query(None, description="Filter by city (e.g., 'Vancouver', 'Ottawa', 'Edmonton')"),
    session=Depends(get_session),
):
    """Get products list with optional filters: category, brand, condition, price range."""
    # Build query
    stmt = select(Product)
    
    # Filter by category if provided
    if category:
        cat = session.exec(select(Category).where(Category.name == category)).first()
        if cat:
            stmt = stmt.where(Product.category_id == cat.id)
        else:
            # If category not found, return empty list
            return []
    
    # Filter by brand if provided
    if brand:
        brand_obj = session.exec(select(Brand).where(Brand.name == brand)).first()
        if brand_obj:
            stmt = stmt.where(Product.brand_id == brand_obj.id)
        else:
            # If brand not found, return empty list
            return []
    
    # Filter by condition if provided
    if condition:
        condition_upper = condition.upper()
        if condition_upper in ["A", "B", "C"]:
            stmt = stmt.where(Product.condition == condition_upper)
        else:
            # Invalid condition, return empty list
            return []
    
    # Execute query to get products
    products = session.exec(stmt).all()
    
    # Filter by price range (applied after query for flexibility with price fields)
    if min_price is not None or max_price is not None:
        filtered_products = []
        for product in products:
            # Use resale_price, list_price, or base_price as the price
            price = product.resale_price or product.list_price or product.base_price or 0.0
            
            # Apply price filters
            if min_price is not None and price < min_price:
                continue
            if max_price is not None and price > max_price:
                continue
            
            filtered_products.append(product)
        products = filtered_products
    
    # Format responses with brand information
    products_response = []
    for product in products:
        brand_obj = session.get(Brand, product.brand_id) if product.brand_id else None
        product_response = _format_product_response(product, brand_obj)
        
        # Filter by city if provided (check cityAvailability)
        if city:
            city_availability = product_response.cityAvailability or []
            city_normalized = city.lower()
            if not any(c.lower() == city_normalized for c in city_availability):
                continue
        
        products_response.append(product_response)
    
    return products_response


@router.get("/search", response_model=list[ProductResponse])
def search_products(
    q: str = Query(..., description="Search keyword"),
    category: Optional[str] = Query(None, description="Filter by category name"),
    brand: Optional[str] = Query(None, description="Filter by brand name"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    session=Depends(get_session),
):
    """Search products by keyword in title, model, or description."""
    # Build search query - search in title, model, and description (case-insensitive)
    search_lower = q.lower()
    
    # Get all products first, then filter in Python (SQLite doesn't support ILIKE well)
    stmt = select(Product)
    
    # Apply category filter first (more efficient)
    if category:
        cat = session.exec(select(Category).where(Category.name == category)).first()
        if cat:
            stmt = stmt.where(Product.category_id == cat.id)
        else:
            return []
    
    # Apply brand filter
    if brand:
        brand_obj = session.exec(select(Brand).where(Brand.name == brand)).first()
        if brand_obj:
            stmt = stmt.where(Product.brand_id == brand_obj.id)
        else:
            return []
    
    # Execute query
    products = session.exec(stmt).all()
    
    # Filter by search keyword (case-insensitive search in title, model, description)
    filtered_products = []
    for product in products:
        # Check if keyword matches in title, model, or description
        matches = (
            (product.title and search_lower in product.title.lower()) or
            (product.model and search_lower in product.model.lower()) or
            (product.description and search_lower in product.description.lower())
        )
        if matches:
            filtered_products.append(product)
    
    products = filtered_products
    
    # Filter by price range if provided
    if min_price is not None or max_price is not None:
        price_filtered = []
        for product in products:
            price = product.resale_price or product.list_price or product.base_price or 0.0
            if min_price is not None and price < min_price:
                continue
            if max_price is not None and price > max_price:
                continue
            price_filtered.append(product)
        products = price_filtered
    
    # Format responses
    products_response = []
    for product in products:
        brand_obj = session.get(Brand, product.brand_id) if product.brand_id else None
        products_response.append(_format_product_response(product, brand_obj))
    
    return products_response


@router.get("/deals")
def get_deals(
    limit: Optional[int] = Query(10, description="Maximum number of deals to return"),
    min_discount: Optional[float] = Query(None, description="Minimum discount percentage"),
    session=Depends(get_session),
):
    """Get products with discounts (deals)."""
    # Get all products
    products = session.exec(select(Product)).all()
    
    # Calculate discounts and filter
    deals = []
    for product in products:
        # Current selling price (resale_price or list_price)
        price = product.resale_price or product.list_price or 0.0
        # Original price (base_price or list_price)
        original_price = product.base_price or product.list_price or 0.0
        
        # Skip if no valid pricing or if price >= original_price (no discount)
        if price <= 0 or original_price <= 0 or price >= original_price:
            continue
        
        # Calculate discount percentage
        discount_percent = ((original_price - price) / original_price) * 100
        
        # Skip if discount is too small
        if discount_percent <= 0:
            continue
        
        if min_discount is not None and discount_percent < min_discount:
            continue
        
        deals.append((product, discount_percent))
    
    # Sort by discount percentage (highest first)
    deals.sort(key=lambda x: x[1], reverse=True)
    
    # Limit results
    deals = deals[:limit] if limit else deals
    
    # Format responses
    products_response = []
    for product, discount_percent in deals:
        brand_obj = session.get(Brand, product.brand_id) if product.brand_id else None
        product_response = _format_product_response(product, brand_obj)
        # Add discount information
        product_dict = product_response.model_dump()
        product_dict["discount_percent"] = round(discount_percent, 1)
        product_dict["voucher_label"] = f"+{int(discount_percent)}% Voucher"
        products_response.append(product_dict)
    
    return products_response


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, session=Depends(get_session)):
    """Get a single product by ID."""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    brand = session.get(Brand, product.brand_id) if product.brand_id else None
    return _format_product_response(product, brand)


