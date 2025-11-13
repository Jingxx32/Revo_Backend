from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from typing import List

from app.core.security import get_current_user
from app.db.database import get_session
from app.db.models import Address, User
from app.schemas.address import AddressCreate, AddressUpdate, AddressRead


router = APIRouter(prefix="/api/addresses", tags=["Addresses"])


@router.get("/", response_model=List[AddressRead])
def list_addresses(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get all addresses for the current user.
    
    Returns a list of all addresses belonging to the authenticated user,
    ordered by default address first, then by creation date.
    """
    # Query all addresses for the current user
    statement = select(Address).where(Address.user_id == current_user.id)
    addresses = session.exec(statement).all()
    
    # Sort: default address first, then by creation date (newest first)
    addresses = sorted(
        addresses,
        key=lambda a: (not a.is_default, -(a.created_at.timestamp() if a.created_at else 0)),
    )
    
    return addresses


@router.post("/", response_model=AddressRead, status_code=status.HTTP_201_CREATED)
def create_address(
    address_in: AddressCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new address for the current user.
    
    If this is set as the default address (is_default=True), or if this is
    the user's first address, all other addresses will be set to is_default=False.
    """
    # Check if this is the user's first address
    existing_addresses = session.exec(
        select(Address).where(Address.user_id == current_user.id)
    ).all()
    
    is_first_address = len(existing_addresses) == 0
    
    # If setting as default or this is the first address, unset other defaults
    if address_in.is_default or is_first_address:
        # Set all other addresses to is_default=False
        for addr in existing_addresses:
            addr.is_default = False
            session.add(addr)
        
        # If this is the first address, automatically set it as default
        is_default = True if is_first_address else address_in.is_default
    else:
        is_default = address_in.is_default
    
    # Create new address
    address = Address(
        user_id=current_user.id,
        full_name=address_in.full_name,
        phone_number=address_in.phone_number,
        address_line1=address_in.address_line1,
        address_line2=address_in.address_line2,
        city=address_in.city,
        state=address_in.state,
        postal_code=address_in.postal_code,
        country=address_in.country,
        is_default=is_default,
    )
    
    session.add(address)
    session.commit()
    session.refresh(address)
    
    return address


@router.put("/{address_id}", response_model=AddressRead)
def update_address(
    address_id: int,
    address_in: AddressUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update an existing address.
    
    Only the address owner can update their own address.
    If updating to set as default address, all other addresses will be set to is_default=False.
    """
    # Find the address
    address = session.get(Address, address_id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    # Check if the address belongs to the current user
    if address.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own addresses"
        )
    
    # Get all update data (exclude None values)
    update_data = address_in.model_dump(exclude_unset=True)
    
    # If setting as default, unset other defaults
    if update_data.get("is_default") is True:
        existing_addresses = session.exec(
            select(Address).where(
                Address.user_id == current_user.id,
                Address.id != address_id
            )
        ).all()
        
        for addr in existing_addresses:
            addr.is_default = False
            session.add(addr)
    
    # Update address fields
    for field, value in update_data.items():
        setattr(address, field, value)
    
    session.add(address)
    session.commit()
    session.refresh(address)
    
    return address


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete an address.
    
    Only the address owner can delete their own address.
    """
    # Find the address
    address = session.get(Address, address_id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    # Check if the address belongs to the current user
    if address.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own addresses"
        )
    
    # Delete the address
    session.delete(address)
    session.commit()
    
    return None

