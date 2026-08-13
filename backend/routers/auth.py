"""
Authentication Router for AgroControl Pro
Handles user login, registration, and token management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import jwt
import crud
import schemas
from database import get_db
from config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    email: str,
    nombre_usuario: str,
    password: str,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    """
    # Check if user already exists
    db_user_email = crud.get_user_by_email(db, email)
    if db_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    db_user_username = crud.get_user_by_username(db, nombre_usuario)
    if db_user_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create new user
    user = crud.create_user(
        db=db,
        email=email,
        nombre_usuario=nombre_usuario,
        password=password,
        rol="secretary"
    )
    return user


@router.post("/login", response_model=schemas.TokenResponse)
def login(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    Returns access token and user info
    """
    user = crud.get_user_by_email(db, email)
    if not user or not crud.verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"user_id": user.id_usuario, "email": user.email}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/logout")
def logout(current_user = Depends(get_current_user)):
    """
    Logout user (token invalidation on frontend)
    """
    return {"message": "Successfully logged out"}


@router.get("/verify", response_model=schemas.UserResponse)
def verify_token(current_user = Depends(get_current_user)):
    """
    Verify if token is valid and return current user
    """
    return current_user


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user
