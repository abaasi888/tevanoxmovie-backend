from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from bson import ObjectId
from app.core.config import settings
from app.core.database import get_database
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse, TokenResponse

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    db = get_database()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
    
    return user

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    db = get_database()
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = await db.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.model_dump()
    user_dict["password_hash"] = hashed_password
    user_dict["created_at"] = datetime.utcnow()
    user_dict["is_active"] = True
    user_dict["is_admin"] = False
    user_dict["is_verified"] = False
    
    # Generate referral code
    import random
    import string
    user_dict["referral_code"] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Remove password from dict before inserting
    del user_dict["password"]
    
    result = await db.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    user_dict["_id"] = str(result.inserted_id)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(result.inserted_id)})
    
    return TokenResponse(
        token=access_token,
        user=UserResponse(**{
            "id": str(result.inserted_id),
            "username": user_dict["username"],
            "email": user_dict["email"],
            "referral_code": user_dict["referral_code"],
            "is_active": user_dict["is_active"],
            "is_admin": user_dict["is_admin"]
        })
    )

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user"""
    db = get_database()
    
    # Find user by username or email
    user = await db.users.find_one({
        "$or": [
            {"username": form_data.username},
            {"email": form_data.username}
        ]
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user["_id"])})
    
    return TokenResponse(
        token=access_token,
        user=UserResponse(**{
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "referral_code": user.get("referral_code", ""),
            "is_active": user.get("is_active", True),
            "is_admin": user.get("is_admin", False)
        })
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse(**{
        "id": str(current_user["_id"]),
        "username": current_user["username"],
        "email": current_user["email"],
        "referral_code": current_user.get("referral_code", ""),
        "is_active": current_user.get("is_active", True),
        "is_admin": current_user.get("is_admin", False)
    })
