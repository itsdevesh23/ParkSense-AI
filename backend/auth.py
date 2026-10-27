"""
backend/auth.py
Role-Based Access Control (RBAC) and Demo Authentication for ParkSense AI.
Supports three distinct roles:
1. customer: Driver looking for vacant parking and forecast trends.
2. operator: Parking facility owner/operator with assigned facility permissions.
3. admin: System administrator managing platform, models, and FL testbed.
"""

from typing import Optional, List, Dict
from pydantic import BaseModel
from fastapi import HTTPException, Header, Depends

DEMO_USERS: Dict[str, dict] = {
    "driver@parksense.ai": {
        "id": "usr_driver_01",
        "email": "driver@parksense.ai",
        "name": "Sarah Jenkins",
        "role": "customer",
        "title": "Urban Commuter & Driver",
        "assigned_facilities": [],
        "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150"
    },
    "owner.retail@parksense.ai": {
        "id": "usr_operator_01",
        "email": "owner.retail@parksense.ai",
        "name": "Marcus Vance",
        "role": "operator",
        "title": "Commercial Retail Operations Lead",
        "assigned_facilities": [
            "Bull Ring",
            "BHMBRCBRG01",
            "BHMBRCBRG02",
            "BHMBRCBRG03",
            "Shopping",
            "BHMMBMMBX01",
            "Others-CCCPS98"
        ],
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150"
    },
    "owner.council@parksense.ai": {
        "id": "usr_operator_02",
        "email": "owner.council@parksense.ai",
        "name": "Elena Rostova",
        "role": "operator",
        "title": "Municipal Parking Operations Manager",
        "assigned_facilities": [
            "BHMBCCMKT01",
            "BHMBCCPST01",
            "BHMBCCSNH01",
            "BHMBCCTHL01"
        ],
        "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150"
    },
    "admin@parksense.ai": {
        "id": "usr_admin_01",
        "email": "admin@parksense.ai",
        "name": "Dr. Devesh Munagala",
        "role": "admin",
        "title": "Smart Cities & FL Systems Architect",
        "assigned_facilities": ["*"],  # Access to all 30 facilities
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"
    }
}


class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    role: str
    title: str
    assigned_facilities: List[str]
    avatar: str


def get_current_user(x_demo_user: Optional[str] = Header(None)) -> UserProfile:
    """
    Resolves the authenticated user from the X-Demo-User header or default driver.
    Provides real backend RBAC verification for routes.
    """
    user_email = x_demo_user or "driver@parksense.ai"
    if user_email not in DEMO_USERS:
        # Fallback to driver if unrecognized
        user_email = "driver@parksense.ai"
    user_data = DEMO_USERS[user_email]
    return UserProfile(**user_data)


def require_role(allowed_roles: List[str]):
    """
    Dependency factory enforcing strict role permission in FastAPI backend.
    """
    def role_checker(user: UserProfile = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Forbidden: Access requires one of roles {allowed_roles}, but current user has role '{user.role}'."
            )
        return user
    return role_checker
