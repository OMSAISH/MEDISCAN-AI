import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.config import settings
from backend.app.database.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.schemas.auth import UserRegister, UserLogin, UserResponse, Token
from backend.app.auth.password import get_password_hash, verify_password
from backend.app.auth.jwt import create_access_token
from backend.app.security.rbac import get_current_active_user, record_audit_log

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister, request: Request, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    stmt = select(User).where(User.email == user_in.email.lower())
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        email=user_in.email.lower(),
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        organization=user_in.organization,
        is_active=True,
        is_verified=False
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    client_ip = request.client.host if request.client else None
    await record_audit_log(
        db=db,
        user_id=new_user.id,
        action="USER_REGISTER",
        resource_type="USER",
        resource_id=new_user.id,
        ip_address=client_ip,
        details={"email": new_user.email, "role": new_user.role.value}
    )

    return new_user

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user_in.email.lower())
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )

    client_ip = request.client.host if request.client else None
    await record_audit_log(
        db=db,
        user_id=user.id,
        action="USER_LOGIN",
        resource_type="USER",
        resource_id=user.id,
        ip_address=client_ip
    )

    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    client_ip = request.client.host if request.client else None
    await record_audit_log(
        db=db,
        user_id=current_user.id,
        action="USER_LOGOUT",
        resource_type="USER",
        resource_id=current_user.id,
        ip_address=client_ip
    )
    return {"status": "success", "message": "Successfully logged out."}
