# Import necessary modules and dependencies
# FastAPI components for routing and exceptions
# Custom models and schemas for organizations and users
# Authentication dependency
# Typing for type hints

from fastapi import APIRouter, HTTPException
from app.models.org_model import Organization
from app.schemas.org_schema import OrganizationCreate
from typing import List
from app.dependencies.auth import get_current_user
from app.models.user_model import OrgMembership, User, UserRole
from fastapi import Depends


# Create a router for organization-related endpoints with a prefix and tags
router = APIRouter(prefix="/org", tags=["Orgs"])


# Endpoint to create a new organization
# Accepts organization data and the current user as input
# Returns the created organization
@router.post("/create-org", response_model=Organization)
async def create_org(
    org_data: OrganizationCreate, user: User = Depends(get_current_user)
):
    # Check if an organization with the same domain or org_slug already exists
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
    # Create a new organization object from the provided data
    org = Organization(
        name=org_data.name,
        domain=org_data.domain,
        org_slug=org_data.org_slug,
        created_by=user.id,  # type: ignore
        # because if code reaches here, user is not None
        created_by_username=user.full_name,
    )
    org = await org.save()
    # If the organization is successfully saved, create a new organization membership for the user
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


# Endpoint to list all organizations the user is a member of
# Accepts the current user as input
# Returns a list of organizations
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


# Endpoint to get an organization by its domain
# Accepts the domain as input
# Returns the organization if found
@router.get("/get-org-by-domain", response_model=Organization)
async def get_org(domain: str):
    org = await Organization.collection().find_one({"domain": domain})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return Organization(**org)
