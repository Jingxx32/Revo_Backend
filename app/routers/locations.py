from fastapi import APIRouter

router = APIRouter(prefix="/api/locations", tags=["Locations"])

# Predefined locations
LOCATIONS = [
    {"id": "vancouver", "name": "Vancouver", "code": "VAN", "hub_name": "Vancouver Hub"},
    {"id": "ottawa", "name": "Ottawa", "code": "OTT", "hub_name": "Ottawa Lab"},
    {"id": "edmonton", "name": "Edmonton", "code": "EDM", "hub_name": "Edmonton Studio"},
]


@router.get("/")
def list_locations():
    """Get list of available locations."""
    return LOCATIONS


@router.get("/{location_id}")
def get_location(location_id: str):
    """Get location details by ID."""
    location = next((loc for loc in LOCATIONS if loc["id"] == location_id), None)
    if not location:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location '{location_id}' not found"
        )
    return location

