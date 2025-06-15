from fastapi import APIRouter, HTTPException
from app.models.org_model import Organization
from app.models.service_model import Service
from app.models.incident_model import Incident

router = APIRouter(prefix="/status", tags=["Status"])


@router.get("/get-org-status")
async def get_all_statuses(org_slug: str):
    org = await Organization.collection().find_one({"org_slug": org_slug})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    org = Organization(**org)

    org_services = await Service.find_all({"org_id": org.id})
    incidents = await Incident.find_all({"org_id": org.id})

    return {
        "org": org,
        "org_services": org_services,
        "incidents": incidents,
    }
