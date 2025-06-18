from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from app.core.deps import get_db, require_admin
from . import models, schemas
from app.orders.models import OrderItem
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/products", tags=["Admin Products"])


@router.post("/create", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    try:
        db_product = models.Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info(f"Product created: {db_product.name} (ID: {db_product.id})")
        return db_product
    except SQLAlchemyError as e:
        logger.exception("Database error while creating product")
        raise HTTPException(status_code=500, detail="Database error")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception("Unexpected error while creating product")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@router.get("/list", response_model=List[schemas.ProductOut])
def list_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), admin=Depends(require_admin)):
    try:
        products = db.query(models.Product).offset(skip).limit(limit).all()
        logger.info(f"{len(products)} products fetched (skip={skip}, limit={limit})")
        return products
    except SQLAlchemyError:
        logger.exception("Database error while listing products")
        raise HTTPException(status_code=500, detail="Database error")
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        logger.exception("Unexpected error while listing products")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    try:
        product = db.query(models.Product).get(product_id)
        if not product:
            logger.warning(f"Product not found (ID: {product_id})")
            raise HTTPException(status_code=404, detail="Product not found")
        logger.info(f"Product fetched: {product.name} (ID: {product.id})")
        return product
    except SQLAlchemyError:
        logger.exception("Database error while fetching product")
        raise HTTPException(status_code=500, detail="Database error")
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        logger.exception("Unexpected error while fetching product")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, updates: schemas.ProductUpdate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    try:
        product = db.query(models.Product).get(product_id)
        if not product:
            logger.warning(f"Product not found for update (ID: {product_id})")
            raise HTTPException(status_code=404, detail="Product not found")

        for key, value in updates.dict(exclude_unset=True).items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)
        logger.info(f"Product updated: {product.name} (ID: {product.id})")
        return product
    except SQLAlchemyError:
        logger.exception("Database error while updating product")
        raise HTTPException(status_code=500, detail="Database error")
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        logger.exception("Unexpected error while updating product")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(product_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    try:
        product = db.query(models.Product).get(product_id)
        if not product:
            logger.warning(f"Product not found for deletion (ID: {product_id})")
            raise HTTPException(status_code=404, detail="Product not found")

        if db.query(OrderItem).filter(OrderItem.product_id == product_id).first():
            logger.warning(f"Attempt to delete product in use (ID: {product_id})")
            raise HTTPException(status_code=400, detail="Product cannot be deleted as it is part of an order")

        db.delete(product)
        db.commit()
        logger.info(f"Product deleted successfully (ID: {product_id})")
        return {"message": "Product deleted successfully"}
    except SQLAlchemyError:
        logger.exception("Database error while deleting product")
        raise HTTPException(status_code=500, detail="Database error")
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        logger.exception("Unexpected error while deleting product")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")
