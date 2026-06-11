from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address
import uuid 
from datetime import datetime, timedelta, timezone

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate,
    UserResponse,
    TokenResponse,
    TokenRefresh,
    ApprovalAction,
)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

login_attempts = {}


def get_current_user(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    if payload.get("type") == "refresh":
        raise HTTPException(status_code=401, detail="Refresh token cannot be used for API access")
    
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # safely convert string ID back to native Python UUID object
    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Malformed user identifier in token")
    
    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def signup(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        role=UserRole(user_data.role) if user_data.role in ["production_team", "quality_team"] else UserRole.production_team,
        is_approved=False,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    ip = request.client.host if request.client else "unknown"
    now = datetime.now(timezone.utc)
    
    # Check rate limit based on failed attempts
    if ip in login_attempts:
        # Cleanup old attempts outside the lockout window
        login_attempts[ip] = [t for t in login_attempts[ip] if now - t < timedelta(minutes=settings.RATE_LIMIT_LOCKOUT_MINUTES)]
        if len(login_attempts[ip]) >= settings.RATE_LIMIT_MAX_FAILURES:
            raise HTTPException(
                status_code=429, 
                detail=f"Too many failed attempts. Locked out for {settings.RATE_LIMIT_LOCKOUT_MINUTES} minutes."
            )

    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        if ip not in login_attempts:
            login_attempts[ip] = []
        login_attempts[ip].append(now)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Reset attempts on successful login
    if ip in login_attempts:
        del login_attempts[ip]
    
    if not user.is_approved:
        raise HTTPException(status_code=403, detail="Account not approved. Please wait for admin approval.")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Force explicit token_type assignment here:
    return TokenResponse(
        access_token=access_token, 
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post("/refresh", response_model=TokenResponse)
def refresh(refresh_data: TokenRefresh, db: Session = Depends(get_db)):
    payload = decode_token(refresh_data.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Malformed user identifier in token")
    
    user = db.query(User).filter(User.id == user_uuid).first()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.get("/users", response_model=List[UserResponse])
def list_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    users = db.query(User).filter(User.is_active == True).order_by(User.created_at.desc()).all()
    return users


@router.get("/users/pending", response_model=List[UserResponse])
def list_pending_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    users = db.query(User).filter(User.is_approved == False, User.is_active == True).all()
    return users


@router.post("/approve/{user_id}", response_model=UserResponse)
def approve_user(
    user_id: str,
    approval: ApprovalAction,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        target_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    user = db.query(User).filter(User.id == target_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if approval.approved:
        user.is_approved = True
    else:
        user.is_active = False

    
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Successfully logged out"}
