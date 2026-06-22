import os
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models.models import UserProfile, PlanTier

router = APIRouter(prefix="/auth", tags=["auth"])

class SignUpSchema(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: UUID

@router.post("/signup", response_model=TokenResponse)
async def signup(data: SignUpSchema, db: AsyncSession = Depends(get_db)):
    # 1. Supabase integration would typically create the user in Supabase auth.users
    # Here, we mock the creation and save the profile in our PostgreSQL `user_profiles` table.
    # To be fully robust, we verify if user profile already exists.
    # In a real environment, we'd invoke: supabase.auth.admin.create_user(...)
    
    # Simple email check
    from sqlalchemy import select
    stmt = select(UserProfile).where(UserProfile.email == data.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Mocking Supabase user ID creation
    new_user_id = uuid4()
    
    profile = UserProfile(
        id=new_user_id,
        email=data.email,
        full_name=data.full_name,
        plan_tier=PlanTier.free
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    # Return mock Supabase JWT tokens
    return TokenResponse(
        access_token="mock-jwt-access-token-string",
        refresh_token="mock-jwt-refresh-token-string",
        user_id=new_user_id
    )

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginSchema, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    stmt = select(UserProfile).where(UserProfile.email == data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
        
    return TokenResponse(
        access_token="mock-jwt-access-token-string",
        refresh_token="mock-jwt-refresh-token-string",
        user_id=user.id
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str):
    return TokenResponse(
        access_token="mock-jwt-new-access-token-string",
        refresh_token=refresh_token,
        user_id=uuid4()
    )

@router.post("/logout")
async def logout():
    return {"detail": "Successfully logged out"}

@router.get("/me")
async def get_me(db: AsyncSession = Depends(get_db)):
    # Authenticated user is injected into the request state by the AuthMiddleware
    # Here, we can retrieve user from request or mock it if auth is bypassed
    return {
        "id": "authenticated-user-uuid",
        "email": "user@protoforge.ai",
        "plan_tier": PlanTier.free
    }
