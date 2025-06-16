# Import necessary modules and dependencies
# FastAPI components for routing and exceptions
# Custom models for organizations, services, and incidents

from fastapi import APIRouter, HTTPException
from app.models.org_model import Organization
from app.models.service_model import Service
from app.models.incident_model import Incident

router = APIRouter(prefix="/status", tags=["Status"])


# Endpoint to get the status of an organization
# Accepts organization slug as input
# Returns the organization, its services, and incidents


@router.get("/get-org-status")
async def get_all_statuses(org_slug: str):
    # Find the organization by its slug
    # Raise an HTTPException if not found
    org = await Organization.collection().find_one({"org_slug": org_slug})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    org = Organization(**org)

    # Find all services for the organization
    org_services = await Service.find_all({"org_id": org.id})

    # Find all incidents for the organization
    incidents = await Incident.find_all({"org_id": org.id})

    # Return the organization, services, and incidents
    return {
        "org": org,
        "org_services": org_services,
        "incidents": incidents,
    }
