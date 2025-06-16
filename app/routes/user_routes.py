from fastapi import APIRouter, HTTPException
from app.models.org_model import Organization
from app.models.user_model import User, OrgMembership, UserRole
from app.schemas.user_schema import UserCreate
from app.dependencies.auth import get_current_user
from fastapi import Depends
from app.core.logger import logger
from typing import List
from bson import ObjectId
from app.models.base import PyObjectId
from firebase_admin import auth

router = APIRouter(prefix="/user", tags=["Users"])


@router.post("/sync-user-to-db", response_model=User)
async def sync_user_to_db(user_data: UserCreate):
    existing_user = await User.find_one({"email": user_data.email})
    if existing_user:
        if user_data.photo_url and not existing_user.photo_url:
            existing_user.photo_url = user_data.photo_url
            await existing_user.update({"photo_url": user_data.photo_url})
        return existing_user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        photo_url=user_data.photo_url,
    )
    await user.save()
    return user


@router.post("/update-current-org", response_model=User)
async def update_current_org(org_id: str, user: User = Depends(get_current_user)):
    org = await Organization.find_by_id(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    user_org_membership = next(
        (
            membership
            for membership in user.org_memberships
            if str(membership.org_id) == org_id
        ),
        None,
    )
    if not user_org_membership:
        raise HTTPException(
            status_code=404, detail="User not a member of this organization"
        )

    # Convert ObjectId to string in user_org_membership
    user_org_membership_dict = user_org_membership.model_dump()
    user_org_membership_dict["org_id"] = str(user_org_membership.org_id)

    await user.update({"current_org": user_org_membership_dict})
    return user


@router.get("/{user_id}", response_model=User)
async def fetch_user(user_id: str):
    user = await User.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/org/{org_id}/users", response_model=List[User])
async def fetch_org_users(org_id: str, current_user: User = Depends(get_current_user)):
    org = await Organization.find_by_id(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    users = await User.find_all(
        {"org_memberships.org_id": PyObjectId(org_id), "_id": {"$ne": current_user.id}}
    )
    return users


@router.post("/create-user-in-org", response_model=User)
async def create_user_in_org(
    user_data: UserCreate, org_id: str, current_user: User = Depends(get_current_user)
):
    # Check if the current user has admin access in the organization
    user_org_membership = next(
        (
            membership
            for membership in current_user.org_memberships
            if str(membership.org_id) == org_id and membership.role == UserRole.ADMIN
        ),
        None,
    )
    if not user_org_membership:
        raise HTTPException(
            status_code=403,
            detail="User does not have admin access in this organization",
        )

    # Find the org_slug from the current user's org_membership
    org_slug = user_org_membership.org_slug

    # Create the new user in Firebase
    try:
        firebase_user = auth.create_user(
            email=user_data.email,
            password=user_data.password if user_data.password else None,
            display_name=user_data.full_name,
            photo_url=user_data.photo_url,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create user in Firebase: {str(e)}"
        )

    # Create the new user in the local database
    existing_user = await User.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        photo_url=user_data.photo_url,
        org_memberships=[
            OrgMembership(
                org_id=PyObjectId(org_id), org_slug=org_slug, role=UserRole.MEMBER
            )
        ],
    )
    await new_user.save()
    return new_user
