from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.deps import get_db, require_user
from app.orders import models as order_models, schemas as order_schemas

router = APIRouter(prefix="/orders", tags=["orders"])

logger = logging.getLogger(__name__)


@router.get("", response_model=list[order_schemas.OrderSummary])
def get_order_history(db: Session = Depends(get_db), current_user=Depends(require_user)):
    try:
        orders = (
            db.query(order_models.Order)
            .filter_by(user_id=current_user.id)
            .order_by(order_models.Order.created_at.desc())
            .all()
        )

        logger.info("Fetched %d orders for user_id=%s", len(orders), current_user.id)
        return orders

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.exception("Unexpected error while fetching order history for user_id=%s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{order_id}", response_model=order_schemas.OrderOut)
def get_order_detail(order_id: int, db: Session = Depends(get_db), current_user=Depends(require_user)):
    try:
        order = (
            db.query(order_models.Order)
            .filter_by(id=order_id, user_id=current_user.id)
            .first()
        )

        if not order:
            logger.info("Order not found: order_id=%s, user_id=%s", order_id, current_user.id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        logger.info("Fetched order details for order_id=%s, user_id=%s", order_id, current_user.id)
        return order

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.exception("Unexpected error while retrieving order detail: order_id=%s, user_id=%s", order_id, current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

