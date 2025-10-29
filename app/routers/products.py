from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.db.database import get_session
from app.db.models import Product


router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("/")
def list_products(session=Depends(get_session)):
    products = session.exec(select(Product)).all()
    return products


@router.get("/{product_id}")
def get_product(product_id: int, session=Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


