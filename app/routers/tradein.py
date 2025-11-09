import json
import os
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlmodel import select

from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import Brand, PickupRequest, User


router = APIRouter(prefix="/api/tradein", tags=["Trade-in"])

# Directory to store uploaded photos
UPLOAD_DIR = "uploads/tradein_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class PickupRequestCreate(BaseModel):
    brand_id: Optional[int] = None
    brand_name: Optional[str] = None  # Alternative: provide brand name instead of ID
    model_text: Optional[str] = None
    storage: Optional[str] = None  # Storage capacity (e.g., "128GB", "256GB", "512GB")
    condition: Optional[str] = None
    additional_info: Optional[str] = None
    photos_json: Optional[list] = None  # List of photo URLs (if uploaded separately)
    address_json: Optional[dict] = None  # Address as dict
    scheduled_at: Optional[datetime] = None


class RespondPayload(BaseModel):
    action: str  # "accept" or "reject"


async def save_uploaded_photos(files: list[UploadFile], pickup_request_id: int) -> list[str]:
    """Save uploaded photos and return list of file paths/URLs."""
    photo_urls = []
    max_files = 5
    max_size = 5 * 1024 * 1024  # 5MB
    
    for idx, file in enumerate(files[:max_files]):  # Limit to 5 files
        if not file.filename:
            continue
        
        # Read file content to check size
        content = await file.read()
        if len(content) > max_size:
            continue
        
        # Generate filename
        file_extension = os.path.splitext(file.filename)[1] or ".jpg"
        filename = f"pickup_{pickup_request_id}_{idx}{file_extension}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(filepath, "wb") as f:
            f.write(content)
        
        # Store relative URL (you may want to use absolute URLs in production)
        photo_urls.append(f"/{UPLOAD_DIR}/{filename}")
    
    return photo_urls


@router.post("/pickup-requests", status_code=status.HTTP_201_CREATED)
async def create_pickup_request(
    brand_id: Optional[int] = Form(None),
    brand_name: Optional[str] = Form(None),
    model_text: str = Form(...),
    storage: Optional[str] = Form(None),
    condition: str = Form(...),
    additional_info: Optional[str] = Form(None),
    address_json: Optional[str] = Form(None),
    scheduled_at: Optional[str] = Form(None),
    photos: list[UploadFile] = File(default=[]),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    """Create a pickup request for trade-in estimate."""
    # Resolve brand_id from brand_name if provided
    resolved_brand_id = brand_id
    if not resolved_brand_id and brand_name:
        brand = session.exec(select(Brand).where(Brand.name == brand_name)).first()
        if brand:
            resolved_brand_id = brand.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Brand '{brand_name}' not found",
            )
    
    # Validate required fields
    if not resolved_brand_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand ID or brand name is required",
        )
    
    # Parse address_json if it's a string (legacy format)
    parsed_address = None
    if address_json:
        if isinstance(address_json, str):
            try:
                parsed_address = json.loads(address_json)
            except:
                # If parsing fails, treat as plain address string
                parsed_address = {"address": address_json}
        else:
            parsed_address = address_json
    
    # Parse scheduled_at from string to datetime if provided
    parsed_scheduled_at = None
    if scheduled_at:
        if isinstance(scheduled_at, str):
            try:
                # Try ISO format (e.g., "2025-01-15T10:00:00" or "2025-01-15T10:00:00Z")
                if scheduled_at.endswith('Z'):
                    scheduled_at = scheduled_at[:-1] + '+00:00'
                parsed_scheduled_at = datetime.fromisoformat(scheduled_at)
            except (ValueError, AttributeError):
                # If parsing fails, leave as None (database will handle validation)
                parsed_scheduled_at = None
        elif isinstance(scheduled_at, datetime):
            parsed_scheduled_at = scheduled_at
    
    # Create pickup request (without photos first to get ID)
    pr = PickupRequest(
        user_id=current_user.id,
        brand_id=resolved_brand_id,
        model_text=model_text,
        storage=storage,
        condition=condition,
        additional_info=additional_info,
        address_json=parsed_address,
        scheduled_at=parsed_scheduled_at,
        status="requested",
    )
    session.add(pr)
    session.commit()
    session.refresh(pr)
    
    # Handle photo uploads
    photo_urls = []
    if photos:
        photo_urls = await save_uploaded_photos(photos, pr.id)
        if photo_urls:
            # photos_json is now a List[str] type, no need for json.dumps()
            pr.photos_json = photo_urls
            session.add(pr)
            session.commit()
            session.refresh(pr)
    
    return {
        "id": pr.id,
        "user_id": pr.user_id,
        "brand_id": pr.brand_id,
        "model_text": pr.model_text,
        "storage": pr.storage,
        "condition": pr.condition,
        "additional_info": pr.additional_info,
        "photos": photo_urls,
        "status": pr.status,
        "created_at": pr.created_at if hasattr(pr, "created_at") else None,
    }


@router.post("/estimate", status_code=status.HTTP_200_OK)
def get_tradein_estimate(
    deviceData: dict,
    session=Depends(get_session),
    current_user: User = None,  # Make optional for estimate
):
    """Get trade-in estimate (compatible endpoint for frontend)."""
    # Extract device data
    if not deviceData:
        return {
            "success": False,
            "error": "Device data is required"
        }
    
    brand_name = deviceData.get("brand")
    model_text = deviceData.get("model")
    storage = deviceData.get("storage")
    condition = deviceData.get("condition")
    notes = deviceData.get("notes")
    
    if not brand_name or not model_text or not condition:
        return {
            "success": False,
            "error": "Brand, model, and condition are required"
        }
    
    # Simple estimation logic (you can enhance this)
    # Base prices by condition
    base_prices = {
        "A": 800,  # Excellent
        "B": 600,  # Great
        "C": 400,  # Like-new
    }
    
    base_price = base_prices.get(condition.upper(), 500)
    
    # Adjust by storage
    storage_multiplier = {
        "128GB": 1.0,
        "256GB": 1.2,
        "512GB": 1.5,
        "1TB": 2.0,
    }
    multiplier = storage_multiplier.get(storage, 1.0)
    
    estimated_price = base_price * multiplier
    service_fee = 50.0  # Fixed service fee
    
    return {
        "success": True,
        "data": {
            "estimated_price": round(estimated_price, 2),
            "service_fee": service_fee,
            "net_amount": round(estimated_price - service_fee, 2),
        }
    }


@router.post("/pickup/request", status_code=status.HTTP_201_CREATED)
async def request_pickup_compatible(
    request_data: dict,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    """Compatible pickup request endpoint for frontend."""
    # Extract data from request
    device_id = request_data.get("device_id")
    location = request_data.get("location")
    device = request_data.get("device", {})
    deposit_paid = request_data.get("deposit_paid")
    
    # Extract device data
    brand_name = device.get("brand") or device.get("brand_name")
    model_text = device.get("model") or device.get("model_text")
    storage = device.get("storage")
    condition = device.get("condition")
    notes = device.get("notes") or device.get("additional_info")
    
    # Resolve brand_id
    resolved_brand_id = None
    if brand_name:
        brand = session.exec(select(Brand).where(Brand.name == brand_name)).first()
        if brand:
            resolved_brand_id = brand.id
    
    if not resolved_brand_id:
        return {
            "success": False,
            "error": "Brand not found"
        }
    
    if not model_text or not condition:
        return {
            "success": False,
            "error": "Model and condition are required"
        }
    
    # Parse location to address_json (Dict format)
    parsed_address = None
    if location:
        if isinstance(location, dict):
            parsed_address = location
        elif isinstance(location, str):
            try:
                parsed_address = json.loads(location)
            except:
                # If parsing fails, treat as plain address string
                parsed_address = {"address": location}
        else:
            parsed_address = {"address": str(location)}
    
    # Create pickup request
    pr = PickupRequest(
        user_id=current_user.id,
        brand_id=resolved_brand_id,
        model_text=model_text,
        storage=storage,
        condition=condition,
        additional_info=notes,
        address_json=parsed_address,
        deposit_amount=deposit_paid,
        status="requested",
    )
    session.add(pr)
    session.commit()
    session.refresh(pr)
    
    # Return compatible response
    return {
        "success": True,
        "data": {
            "pickup_id": f"PICKUP{pr.id}",
            "engineer_assigned": "Engineer #001",
            "estimated_arrival": "2-3 business days",
            "pickup_location": location or "Address to be confirmed",
        }
    }


@router.post("/pickup-requests/json", status_code=status.HTTP_201_CREATED)
def create_pickup_request_json(
    payload: PickupRequestCreate,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    """Create a pickup request using JSON (alternative endpoint without file upload)."""
    # Resolve brand_id from brand_name if provided
    resolved_brand_id = payload.brand_id
    if not resolved_brand_id and payload.brand_name:
        brand = session.exec(select(Brand).where(Brand.name == payload.brand_name)).first()
        if brand:
            resolved_brand_id = brand.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Brand '{payload.brand_name}' not found",
            )
    
    # Validate required fields
    if not resolved_brand_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand ID or brand name is required",
        )
    
    if not payload.model_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model is required",
        )
    
    if not payload.condition:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Condition is required",
        )
    
    pr = PickupRequest(
        user_id=current_user.id,
        brand_id=resolved_brand_id,
        model_text=payload.model_text,
        storage=payload.storage,
        condition=payload.condition,
        additional_info=payload.additional_info,
        photos_json=payload.photos_json,
        address_json=payload.address_json,
        scheduled_at=payload.scheduled_at,
        status="requested",
    )
    session.add(pr)
    session.commit()
    session.refresh(pr)
    
    # Get photos (now a List[str] type, no need for json.loads())
    photos = pr.photos_json if pr.photos_json else []
    
    return {
        "id": pr.id,
        "user_id": pr.user_id,
        "brand_id": pr.brand_id,
        "model_text": pr.model_text,
        "storage": pr.storage,
        "condition": pr.condition,
        "additional_info": pr.additional_info,
        "photos": photos,
        "status": pr.status,
        "created_at": pr.created_at if hasattr(pr, "created_at") else None,
    }


@router.get("/pickup-requests/me")
def list_my_pickups(
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    """Get current user's pickup requests."""
    stmt = select(PickupRequest).where(PickupRequest.user_id == current_user.id)
    requests = session.exec(stmt).all()
    
    # Format response with brand information and parsed photos
    result = []
    for req in requests:
        brand = session.get(Brand, req.brand_id) if req.brand_id else None
        # photos_json is now a List[str] type, no need for json.loads()
        photos = req.photos_json if req.photos_json else []
        
        result.append({
            "id": req.id,
            "user_id": req.user_id,
            "brand_id": req.brand_id,
            "brand_name": brand.name if brand else None,
            "model_text": req.model_text,
            "storage": req.storage,
            "condition": req.condition,
            "additional_info": req.additional_info,
            "photos": photos,
            "address_json": req.address_json,
            "scheduled_at": req.scheduled_at,
            "deposit_amount": req.deposit_amount,
            "status": req.status,
        })
    
    return result


@router.get("/brands")
def list_brands(session=Depends(get_session)):
    """Get list of available brands for trade-in."""
    brands = session.exec(select(Brand)).all()
    return [{"id": brand.id, "name": brand.name} for brand in brands]


@router.post("/pickup-requests/{pickup_id}/respond")
def respond_to_offer(
    pickup_id: int,
    payload: RespondPayload,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    pr = session.get(PickupRequest, pickup_id)
    if not pr or pr.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pickup request not found")

    action = payload.action.lower().strip()
    if action not in {"accept", "reject"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action")

    pr.status = "accepted" if action == "accept" else "rejected"
    session.add(pr)
    session.commit()
    session.refresh(pr)
    return pr


