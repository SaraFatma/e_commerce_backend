from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.deps import get_db
from app.products import models, schemas

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=List[schemas.ProductOut])
def list_products(
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = Query(None, enum=["price", "name"]),
    page: int = 1,
    page_size: int = 10,
):
    query = db.query(models.Product)

    if category:
        query = query.filter(models.Product.category == category)
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    if sort_by == "price":
        query = query.order_by(models.Product.price)
    elif sort_by == "name":
        query = query.order_by(models.Product.name)

    products = query.offset((page - 1) * page_size).limit(page_size).all()
    return products


@router.get("/search", response_model=List[schemas.ProductOut])
def search_products(
    keyword: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    results = db.query(models.Product).filter(
        models.Product.name.ilike(f"%{keyword}%") |
        models.Product.description.ilike(f"%{keyword}%")
    ).all()

    return results


@router.get("/{id}", response_model=schemas.ProductOut)
def get_product_detail(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
