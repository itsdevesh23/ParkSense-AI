"""
backend/routes/auth_routes.py
Authentication, demo profiles, and instant role switching routes.
"""

from fastapi import APIRouter, Depends, Header
from typing import Dict, Any, List
from backend.auth import get_current_user, UserProfile, DEMO_USERS

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.get("/me", response_model=UserProfile)
def get_user_profile(user: UserProfile = Depends(get_current_user)):
    return user


@router.get("/demo-users")
def list_demo_users():
    return list(DEMO_USERS.values())


@router.post("/switch-role")
def switch_role(email: str):
    if email in DEMO_USERS:
        return {"status": "success", "user": DEMO_USERS[email]}
    return {"status": "error", "message": "Demo user not found"}
