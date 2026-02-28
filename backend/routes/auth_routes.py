from fastapi import APIRouter, HTTPException
from database.db import SessionLocal
from database.models import User
from passlib.hash import bcrypt
from core.security import create_access_token, create_refresh_token
from schemas.request_models import UserLogin, UserRegister
from jose import jwt, JWTError
from core.security import SECRET_KEY, ALGORITHM
import re

router = APIRouter()

# ===============================
# PASSWORD VALIDATION
# ===============================
def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Must contain uppercase letter")

    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Must contain lowercase letter")

    if not re.search(r"[0-9]", password):
        raise HTTPException(status_code=400, detail="Must contain number")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(status_code=400, detail="Must contain special character")


# ===============================
# SIGNUP
# ===============================
@router.post("/signup")
def signup(user: UserRegister):

    db = SessionLocal()

    try:
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        validate_password(user.password)

        hashed_password = bcrypt.hash(user.password)

        new_user = User(
            username=user.username,
            password=hashed_password
        )

        db.add(new_user)
        db.commit()
    finally:
        db.close()

    return {"message": "User registered successfully"}


# ===============================
# LOGIN
# ===============================
@router.post("/login")
def login(user: UserLogin):

    db = SessionLocal()

    try:
        db_user = db.query(User).filter(User.username == user.username).first()

        if not db_user or not bcrypt.verify(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token({"sub": db_user.username})
        refresh_token = create_refresh_token({"sub": db_user.username})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    finally:
        db.close()


# ===============================
# REFRESH TOKEN
# ===============================
@router.post("/refresh")
def refresh_token(refresh_token: str):

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_access_token = create_access_token({"sub": username})

        return {"access_token": new_access_token}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")