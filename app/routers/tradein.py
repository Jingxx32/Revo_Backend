import json
import os
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlmodel import select

from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import Brand, Evaluation, PickupRequest, User


router = APIRouter(prefix="/api/tradein", tags=["Trade-in"])

# Directory to store uploaded photos
UPLOAD_DIR = "uploads/tradein_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)


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
    brand_id: Optional[int] = Form(
        None,
        description="Brand ID of the device. Either brand_id or brand_name must be provided.",
        example=1
    ),
    brand_name: Optional[str] = Form(
        None,
        description="Brand name of the device (e.g., 'Apple', 'Samsung', 'Huawei'). Either brand_id or brand_name must be provided. If brand_name is provided, it will be resolved to brand_id automatically.",
        example="Apple"
    ),
    model_text: str = Form(
        ...,
        description="Model name or description of the device. This is a required field.",
        example="iPhone 14 Pro",
        min_length=1,
        max_length=200
    ),
    storage: Optional[str] = Form(
        None,
        description="Storage capacity of the device. Common values: '128GB', '256GB', '512GB', '1TB'. This field is optional but recommended for accurate valuation.",
        example="256GB"
    ),
    condition: str = Form(
        ...,
        description="Condition of the device. Required field. Common values: 'A' (Excellent), 'B' (Great), 'C' (Like-new), 'D' (Good), 'E' (Fair). The condition affects the trade-in valuation.",
        example="A",
        min_length=1,
        max_length=10
    ),
    additional_info: Optional[str] = Form(
        None,
        description="Additional information about the device condition, damage, or special notes. This is an optional field that can help with accurate valuation.",
        example="Minor scratches on screen, battery health at 85%",
        max_length=1000
    ),
    address_json: Optional[str] = Form(
        None,
        description="Pickup address in JSON format. Can be a JSON string or plain address string. If JSON, it should contain address fields like 'street', 'city', 'postal_code', etc. Example: '{\"street\": \"123 Main St\", \"city\": \"Shanghai\", \"postal_code\": \"200000\"}' or simply a plain address string.",
        example='{"street": "123 Main St", "city": "Shanghai", "district": "Pudong", "postal_code": "200000"}'
    ),
    scheduled_at: Optional[str] = Form(
        None,
        description="Scheduled pickup date and time in ISO 8601 format (e.g., '2025-01-15T10:00:00' or '2025-01-15T10:00:00Z'). This field is optional. If not provided, the pickup will be scheduled based on availability.",
        example="2025-01-15T10:00:00"
    ),
    estimated_price: Optional[float] = Form(
        None,
        description="Estimated trade-in price at the time of request (from estimation API).",
        example=750.0,
    ),
    photos: list[UploadFile] = File(
        default=[],
        description="Photos of the device (up to 5 files). Each file must be under 5MB. Supported formats: JPEG, PNG, etc. Photos help with accurate device condition assessment. Files are uploaded as multipart/form-data. Note: Only the first 5 files will be processed if more are provided."
    ),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    """
    Create a pickup request for trade-in estimate.
    
    This endpoint allows authenticated users to create a pickup request for their device trade-in.
    The request requires device information such as brand, model, condition, and optional details
    like storage capacity, photos, and pickup address.
    
    **Request Format:**
    - Content-Type: `multipart/form-data`
    - Authentication: Required (Bearer token)
    
    **Required Parameters:**
    - `model_text`: Device model name (required)
    - `condition`: Device condition (required)
    - Either `brand_id` OR `brand_name` (at least one is required)
    
    **Optional Parameters:**
    - `storage`: Storage capacity (recommended for accurate valuation)
    - `additional_info`: Additional notes about the device
    - `address_json`: Pickup address (JSON string or plain text)
    - `scheduled_at`: Preferred pickup date/time (ISO 8601 format)
    - `photos`: Device photos (up to 5 files, each < 5MB)
    
    **Response (201 Created):**
    Returns a JSON object containing the created pickup request details:
    - `id` (int): Unique pickup request ID
    - `user_id` (int): ID of the user who created the request
    - `brand_id` (int): Brand ID of the device
    - `model_text` (str): Device model name
    - `storage` (str, optional): Storage capacity
    - `condition` (str): Device condition
    - `additional_info` (str, optional): Additional device information
    - `photos` (list[str]): URLs of uploaded photos
    - `status` (str): Request status (typically "requested")
    - `created_at` (datetime, optional): Creation timestamp
    
    **Error Responses:**
    - `400 Bad Request`: Missing required fields (brand_id/brand_name, model_text, or condition)
    - `401 Unauthorized`: Invalid or missing authentication token
    - `404 Not Found`: Brand not found (if brand_name is provided but doesn't exist)
    
    **Example Request:**
    ```
    POST /api/tradein/pickup-requests
    Content-Type: multipart/form-data
    Authorization: Bearer <token>
    
    brand_name=Apple
    model_text=iPhone 14 Pro
    storage=256GB
    condition=A
    additional_info=Minor scratches on screen
    address_json={"street": "123 Main St", "city": "Shanghai"}
    scheduled_at=2025-01-15T10:00:00
    photos=@device_photo1.jpg
    photos=@device_photo2.jpg
    ```
    
    **Example Response:**
    ```json
    {
        "id": 123,
        "user_id": 45,
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
    """
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
        estimated_price=estimated_price,
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
        "estimated_price": pr.estimated_price,
    }


@router.post("/estimate", status_code=status.HTTP_200_OK)
def get_tradein_estimate(
    deviceData: dict = Body(...),
    session=Depends(get_session),
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


@router.get("/pickup-requests/me")
def list_my_pickups(
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    """Get current user's pickup requests."""
    # LEFT OUTER JOIN evaluations so we can show final_offer/notes if available
    stmt = (
        select(PickupRequest, Evaluation)
        .where(PickupRequest.user_id == current_user.id)
        .join(Evaluation, Evaluation.pickup_id == PickupRequest.id, isouter=True)
    )
    rows = session.exec(stmt).all()

    result = []
    for req, ev in rows:
        brand = session.get(Brand, req.brand_id) if req.brand_id else None
        photos = req.photos_json if req.photos_json else []

        evaluation_data = (
            {
                "id": ev.id,
                "pickup_id": ev.pickup_id,
                "final_offer": ev.final_offer,
                "notes": ev.notes,
                "created_at": ev.created_at,
            }
            if ev
            else None
        )

        result.append(
            {
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
                "evaluation": evaluation_data,
            }
        )

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


