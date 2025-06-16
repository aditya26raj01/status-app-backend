from fastapi import APIRouter, HTTPException
from app.models.base import PyObjectId
from app.models.incident_model import AffectedService, Incident, IncidentUpdate
from app.models.service_model import Service
from app.schemas.incident_schema import IncidentCreate, UpdateIncident
from app.models.user_model import User
from app.dependencies.auth import get_current_user
from fastapi import Depends
from typing import List
from app.models.log_model import LogEntry, EntityType, ChangeType
from app.websocket_manager import broadcast_message


router = APIRouter(prefix="/incident", tags=["Incidents"])


@router.post("/create-incident", response_model=Incident)
async def create_incident(
    incident_data: IncidentCreate, user: User = Depends(get_current_user)
):
    incident = Incident(
        title=incident_data.title,
        description=incident_data.description,
        status=incident_data.status,
        severity=incident_data.severity,
        affected_services=(
            [
                AffectedService(
                    service_id=affected_service.service_id,
                    status=affected_service.status,
                    service_name=affected_service.service_name,
                )
                for affected_service in incident_data.affected_services
            ]
            if incident_data.affected_services
            else []
        ),
        org_id=PyObjectId(incident_data.org_id),
        created_by=user.id,  # type: ignore
        # because if code reaches here, user is not None
        created_by_username=user.full_name,
        started_at=incident_data.started_at,
        resolved_at=incident_data.resolved_at,
        updates=(
            [
                IncidentUpdate(
                    message=update.message,
                    created_by=user.id,
                    created_by_username=user.full_name,
                )
                for update in incident_data.updates
            ]
            if incident_data.updates
            else []
        ),
    )
    incident = await incident.save()

    # update affected services
    for affected_service in incident.affected_services:
        await Service.collection().update_one(
            {"_id": affected_service.service_id},
            {"$set": {"status": affected_service.status}},
        )

    if incident.id is None:
        raise HTTPException(
            status_code=500, detail="Incident ID is not set after saving."
        )

    if user.id is None:
        raise HTTPException(status_code=500, detail="User ID is not available.")

    # Log the creation of the incident
    log_entry = LogEntry(
        entity_id=incident.id,
        entity_type=EntityType.INCIDENT,
        change_type=ChangeType.CREATE,
        changes={
            "name": incident.title,
            "description": incident.description,
            "status": incident.status,
            "severity": incident.severity,
        },
        org_id=incident.org_id,
        created_by=user.id,
    )
    await log_entry.save()

    await broadcast_message(
        {"type": "incident", "data": incident.model_dump_json(), "action": "create"}
    )
    return incident


@router.post("/update-incident", response_model=Incident)
async def update_incident(
    incident_data: UpdateIncident, user: User = Depends(get_current_user)
):
    incident = await Incident.find_by_id(incident_data.incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if not user.current_org:
        raise HTTPException(
            status_code=403, detail="You are not authorized to update this incident"
        )
    if str(incident.org_id) != str(user.current_org.org_id):
        raise HTTPException(
            status_code=403, detail="You are not authorized to update this incident"
        )

    incident.title = incident_data.title
    incident.description = incident_data.description
    incident.status = incident_data.status
    incident.severity = incident_data.severity
    incident.affected_services = (
        [
            AffectedService(
                service_id=PyObjectId(affected_service.service_id),
                status=affected_service.status,
                created_at=affected_service.created_at,
                service_name=affected_service.service_name,
            )
            for affected_service in incident_data.affected_services
        ]
        if incident_data.affected_services
        else []
    )
    incident.resolved_at = incident_data.resolved_at
    incident.updates = (
        [
            IncidentUpdate(
                message=update.message,
                created_by=(
                    PyObjectId(update.created_by) if update.created_by else user.id
                ),
                created_by_username=(
                    update.created_by_username
                    if update.created_by_username
                    else user.full_name
                ),
                created_at=update.created_at,
            )
            for update in incident_data.updates
        ]
        if incident_data.updates
        else []
    )

    await incident.update(
        {
            "title": incident.title,
            "description": incident.description,
            "status": incident.status,
            "severity": incident.severity,
            "affected_services": [
                service.model_dump() for service in incident.affected_services
            ],
            "resolved_at": incident.resolved_at,
            "updates": [update.model_dump() for update in incident.updates],
        }
    )

    incident = await Incident.find_by_id(incident_data.incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident.id is None:
        raise HTTPException(
            status_code=500, detail="Incident ID is not set after update."
        )

    if user.id is None:
        raise HTTPException(status_code=500, detail="User ID is not available.")

    # Log the update of the incident
    log_entry = LogEntry(
        entity_id=incident.id,
        entity_type=EntityType.INCIDENT,
        change_type=ChangeType.UPDATE,
        changes={
            "name": incident.title,
            "description": incident.description,
            "status": incident.status,
            "severity": incident.severity,
        },
        org_id=incident.org_id,
        created_by=user.id,
    )
    await log_entry.save()

    for affected_service in incident.affected_services:
        await Service.collection().update_one(
            {"_id": affected_service.service_id},
            {"$set": {"status": affected_service.status.value}},
        )

    await broadcast_message(
        {
            "type": "incident",
            "data": incident.model_dump_json(),
            "action": "update",
        }
    )
    return incident


@router.get("/get-all-incidents", response_model=List[Incident])
async def list_incidents(org_id: str, user: User = Depends(get_current_user)):
    incidents = await Incident.find_all(
        {
            "org_id": PyObjectId(org_id),
        }
    )
    return incidents


@router.delete("/delete-incident", response_model=Incident)
async def delete_incident(incident_id: str, user: User = Depends(get_current_user)):
    incident = await Incident.find_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if not user.current_org:
        raise HTTPException(
            status_code=403, detail="You are not authorized to delete this incident"
        )
    if str(incident.org_id) != str(user.current_org.org_id):
        raise HTTPException(
            status_code=403, detail="You are not authorized to delete this incident"
        )
    await incident.delete()

    if incident.id is None:
        raise HTTPException(
            status_code=500, detail="Incident ID is not set after deletion."
        )

    if user.id is None:
        raise HTTPException(status_code=500, detail="User ID is not available.")

    # Log the deletion of the incident
    log_entry = LogEntry(
        entity_id=incident.id,
        entity_type=EntityType.INCIDENT,
        change_type=ChangeType.DELETE,
        changes={},
        org_id=incident.org_id,
        created_by=user.id,
    )
    await log_entry.save()

    await broadcast_message(
        {"type": "incident", "data": incident.model_dump_json(), "action": "delete"}
    )
    return incident


@router.get("/{incident_id}", response_model=Incident)
async def fetch_incident(incident_id: str):
    incident = await Incident.find_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
