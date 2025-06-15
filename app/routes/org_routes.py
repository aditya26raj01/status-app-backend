from fastapi import APIRouter, HTTPException
from app.models.org_model import Organization
from app.schemas.org_schema import OrganizationCreate
from typing import List
from app.dependencies.auth import get_current_user
from app.models.user_model import OrgMembership, User, UserRole
from fastapi import Depends


router = APIRouter(prefix="/org", tags=["Orgs"])


@router.post("/create-org", response_model=Organization)
async def create_org(
    org_data: OrganizationCreate, user: User = Depends(get_current_user)
):
    existing_org = await Organization.collection().find_one(
        {
            "$or": [
                {"domain": org_data.domain},
                {"org_slug": org_data.org_slug},
            ]
        }
    )
    if existing_org:
        raise HTTPException(
            status_code=400,
            detail="Organization with the same domain and org_slug already exists, please use a different domain or org_slug",
        )
    org = Organization(
        name=org_data.name,
        domain=org_data.domain,
        org_slug=org_data.org_slug,
        created_by=user.id,  # type: ignore
        # because if code reaches here, user is not None
    )
    org = await org.save()
    if org.id:
        new_org_membership = OrgMembership(
            org_id=org.id,
            org_slug=org.org_slug,
            role=UserRole.ADMIN,
        )
        user.org_memberships.append(new_org_membership)
        user.current_org = new_org_membership
        org_memberships_dicts = [
            membership.model_dump() for membership in user.org_memberships
        ]
        current_org_dict = user.current_org.model_dump()

        await user.update(
            {
                "org_memberships": org_memberships_dicts,
                "current_org": current_org_dict,
            }
        )

    return org


@router.get("/get-all-orgs", response_model=List[Organization])
async def list_orgs(user: User = Depends(get_current_user)):
    user_org_memberships = user.org_memberships
    org_ids = [membership.org_id for membership in user_org_memberships]
    orgs = await Organization.find_all(
        {
            "_id": {"$in": org_ids},
        }
    )
    return orgs


@router.get("/get-org-by-domain", response_model=Organization)
async def get_org(domain: str):
    org = await Organization.collection().find_one({"domain": domain})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return Organization(**org)
