from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models.user import User
from schemas.login import LoginRequest, LoginResponse
from database import get_db

router = APIRouter(prefix="/login", tags=["Login"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/", response_model=LoginResponse)
def login(user_credentials: LoginRequest, db: Session = Depends(get_db)):

    # Search for the user in the database by username
    db_user = db.query(User).filter(User.username == user_credentials.username).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify the provided password against the stored hashed password
    if not pwd_context.verify(user_credentials.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Return the user information (excluding the password) if authentication is successful
    return db_user