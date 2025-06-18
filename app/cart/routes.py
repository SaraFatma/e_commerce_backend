import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.deps import get_db, require_user
from app.cart import models, schemas
from app.products.models import Product

router = APIRouter(prefix="/cart", tags=["cart"])
logger = logging.getLogger(__name__)


@router.post("/add", response_model=schemas.CartItemOut, status_code=status.HTTP_201_CREATED)
def add_to_cart(item: schemas.CartItemCreate, db: Session = Depends(get_db), current_user=Depends(require_user)):
    try:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        
        if product.stock <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{product.name}' is currently out of stock."
        )

        existing = db.query(models.Carts).filter_by(user_id=current_user.id, product_id=item.product_id).first()
        existing_quantity = existing.quantity if existing else 0
        new_quantity = existing_quantity + item.quantity

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot add {item.quantity} more units of '{product.name}'. "
                    f"You already have {existing_quantity} in your cart. "
                    f"Only {product.stock} units are available in stock."
                )
            )

        if existing:
            existing.quantity = new_quantity
        else:
            existing = models.Carts(
                user_id=current_user.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            db.add(existing)

        db.commit()
        db.refresh(existing)
        logger.info(f"User {current_user.id} added product {product.id} to cart with quantity {existing.quantity}")
        return existing

    except HTTPException as e:
        raise e
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while adding to cart")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        logger.exception("Unexpected error while adding to cart")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error occurred")


@router.get("", response_model=list[schemas.CartItemOut])
def view_cart(db: Session = Depends(get_db), current_user=Depends(require_user)):
    try:
        cart_items = db.query(models.Carts).filter_by(user_id=current_user.id).all()
        logger.info(f"User {current_user.id} viewed their cart with {len(cart_items)} items")
        return cart_items
    except HTTPException as e:
        raise e
    except SQLAlchemyError:
        logger.exception("Database error while viewing cart")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        logger.exception("Unexpected error while viewing cart")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error occurred")


@router.put("/{item_id}", response_model=schemas.CartItemOut)
def update_cart_item(item_id: int, payload: schemas.CartItemUpdate, db: Session = Depends(get_db), current_user=Depends(require_user)):
    try:
        item = db.query(models.Carts).filter_by(id=item_id, user_id=current_user.id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

        item.quantity = payload.quantity
        db.commit()
        db.refresh(item)
        logger.info(f"User {current_user.id} updated cart item {item_id} to quantity {item.quantity}")
        return item
    except HTTPException as e:
        raise e
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while updating cart item")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        logger.exception("Unexpected error while updating cart item")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error occurred")


@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def remove_cart_item(item_id: int, db: Session = Depends(get_db), current_user=Depends(require_user)):
    try:
        item = db.query(models.Carts).filter_by(id=item_id, user_id=current_user.id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

        db.delete(item)
        db.commit()
        logger.info(f"User {current_user.id} removed cart item {item_id}")
        return {"message": "Item removed from cart"}

    except HTTPException as e:
        raise e
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while deleting cart item")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception:
        logger.exception("Unexpected error while deleting cart item")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error occurred")
