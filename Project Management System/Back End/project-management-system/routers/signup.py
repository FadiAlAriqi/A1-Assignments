from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse
from database import get_db


router = APIRouter(prefix="/signup", tags=["Sign UP"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Create a new user
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    errors = []

    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        errors.append("Username already exists")

    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        errors.append("Email already exists")

    if errors:
        raise HTTPException(
            status_code=400,
            detail=errors
        )
    

    hashed_password = pwd_context.hash(user.password)
    # db_user = User(**user.dict())
    db_user = User(
        name=user.name, 
        username=user.username, 
        email=user.email, 
        password=hashed_password, 
        is_active=user.is_active
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
