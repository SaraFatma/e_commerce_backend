from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional
from dotenv import load_dotenv
from app.core.config import settings

import uuid
from app.core.database import SessionLocal
from app.auth.models import PasswordResetToken, User
import logging
from sqlalchemy.orm import Session




load_dotenv()
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str): 
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logging.getLogger(__name__).info(f"Access token created for: {data.get('sub')}")
    return encoded_jwt

def generate_reset_token():
    return str(uuid.uuid4())

def create_password_reset_token(email: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    token = generate_reset_token()
    reset_entry = PasswordResetToken(
        user_id=user.id,
        token=token
    )
    db.add(reset_entry)
    db.commit()
    return token

def verify_password_reset_token(token: str, db: Session):
    entry = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used == False
    ).first()

    if not entry or entry.expiration_time < datetime.utcnow():
        return None
    return entry

def mark_token_as_used(token: str, db: Session):
    db.query(PasswordResetToken).filter(PasswordResetToken.token == token).update({"used": True})
    db.commit()
