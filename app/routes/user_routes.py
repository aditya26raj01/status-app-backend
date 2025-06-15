from fastapi import APIRouter, HTTPException
from app.models.org_model import Organization
from app.models.user_model import User
from app.schemas.user_schema import UserCreate
from app.dependencies.auth import get_current_user
from fastapi import Depends
from app.core.logger import logger

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
