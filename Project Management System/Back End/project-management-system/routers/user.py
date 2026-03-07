from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse
from database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

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


# Get all users
@router.get("/", response_model=List[UserResponse])
def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# Get a user by ID
@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# Update a user
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user.dict(exclude_unset=True)

    errors = []

    # Check if the new username or email already exists for another user
    if "username" in update_data:
        existing_username = db.query(User).filter(User.username == update_data["username"], User.id != user_id).first()
        if existing_username:
            errors.append("Username already exists")

    # Check if the new email already exists for another user
    if "email" in update_data:
        existing_email = db.query(User).filter(User.email == update_data["email"], User.id != user_id).first()
        if existing_email:
            errors.append("Email already exists")

    if errors:
        raise HTTPException(status_code=400, detail=errors)

    if "password" in update_data:
        update_data["password"] = pwd_context.hash(update_data["password"])

    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


# Delete a user
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted successfully"}