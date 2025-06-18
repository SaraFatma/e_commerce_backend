from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.deps import get_db
from app.auth import schemas, models, utils
from app.core.deps import get_current_user
import logging
from app.auth.schemas import ForgotPasswordRequest, ResetPasswordRequest
from app.auth.email_utils import send_email  

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.Token)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db), status_code=201):
    try:
        existing = db.query(models.User).filter(models.User.email == user.email).first()
        if existing:
            logger.warning(f"Signup failed - Email already registered: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_pw = utils.hash_password(user.password)
        db_user = models.User(
            name=user.name,
            email=user.email,
            hashed_password=hashed_pw,
            role=user.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"User signed up successfully: {user.email}, Role: {user.role}")
        token = utils.create_access_token({"sub": db_user.email, "role": db_user.role})
        return {"access_token": token, "token_type": "bearer"}

    except SQLAlchemyError as e:
        logger.error(f"Database error during signup: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logger.exception(f"Unexpected error in signup: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@router.post("/signin", response_model=schemas.Token)
def signin(user: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if not db_user or not utils.verify_password(user.password, db_user.hashed_password):
            logger.warning(f"Failed login attempt: {user.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        logger.info(f"User logged in: {db_user.email}, Role: {db_user.role}")
        token = utils.create_access_token({"sub": db_user.email, "role": db_user.role})
        return {"access_token": token, "token_type": "bearer"}

    except SQLAlchemyError as e:
        logger.error(f"Database error during signin: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logger.exception(f"Unexpected error in signin: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@router.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    try:
        logger.info(f"Current user fetched: {current_user.email}")
        return current_user

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logger.exception("Error fetching current user")
        raise HTTPException(status_code=500, detail="Error retrieving user info")


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    try:
        token = utils.create_password_reset_token(payload.email, db)
        if not token:
            logger.warning(f"Password reset attempted for non-existent email: {payload.email}")
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"Password reset token created for: {payload.email}")
        reset_link = f"http://localhost:3000/reset-password?token={token}" 
        subject = "Password Reset Request"
        body = f"""
        Hi {payload.email},

        We received a request to reset your password.

        Click the link below to reset your password:
        {reset_link}

        If you did not request this, please ignore this email.

        Regards,
        Your Team
        """

        try:
            send_email(payload.email, subject, body)
            logger.info(f"Password reset email sent to: {payload.email}")
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")

        return {"message": "If the email is registered, a reset link has been sent."}

    except SQLAlchemyError as e:
        logger.error(f"DB error during forgot-password: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logger.exception(f"Unexpected error in forgot-password: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        token_entry = utils.verify_password_reset_token(payload.token, db)
        if not token_entry:
            logger.warning(f"Invalid or expired reset token used: {payload.token}")
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user = db.query(models.User).filter(models.User.id == token_entry.user_id).first()
        if not user:
            logger.error("Token points to a non-existent user.")
            raise HTTPException(status_code=404, detail="User not found")

        user.hashed_password = utils.hash_password(payload.new_password)
        utils.mark_token_as_used(payload.token, db)
        db.commit()

        logger.info(f"Password reset successful for user: {user.email}")
        return {"message": "Password reset successful"}

    except SQLAlchemyError as e:
        logger.error(f"Database error during password reset: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logger.exception(f"Unexpected error in reset-password: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")
