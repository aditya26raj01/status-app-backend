# Import necessary modules and dependencies
# FastAPI components for routing and exceptions
# Custom models and schemas for incidents, services, and users
# Authentication dependency
# Typing for type hints
# Websocket manager for broadcasting messages
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


# Create a router for incident-related endpoints with a prefix and tags
router = APIRouter(prefix="/incident", tags=["Incidents"])


# Endpoint to create a new incident
# Accepts incident data and the current user as input
# Returns the created incident
@router.post("/create-incident", response_model=Incident)
async def create_incident(
    incident_data: IncidentCreate, user: User = Depends(get_current_user)
):
    # Create a new incident object from the provided data
    # Set the title, description, status, severity, and affected services
    # Convert affected services from input data to AffectedService objects
    # Set the organization ID and creator information
    # Set the start and resolution times
    # Convert updates from input data to IncidentUpdate objects
    # Save the incident to the database
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

    # Update the status of affected services in the database
    for affected_service in incident.affected_services:
        await Service.collection().update_one(
            {"_id": affected_service.service_id},
            {"$set": {"status": affected_service.status}},
        )

    # Check if the incident ID is set after saving
    # Raise an HTTPException if not
    if incident.id is None:
        raise HTTPException(
            status_code=500, detail="Incident ID is not set after saving."
        )

    # Check if the user ID is available
    # Raise an HTTPException if not
    if user.id is None:
        raise HTTPException(status_code=500, detail="User ID is not available.")

    # Log the creation of the incident
    # Save the log entry to the database
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

    # Broadcast the creation of the incident to connected clients
    await broadcast_message(
        {"type": "incident", "data": incident.model_dump_json(), "action": "create"}
    )
    return incident


# Endpoint to update an existing incident
# Accepts updated incident data and the current user as input
# Returns the updated incident
@router.post("/update-incident", response_model=Incident)
async def update_incident(
    incident_data: UpdateIncident, user: User = Depends(get_current_user)
):
    # Find the incident by its ID
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

    # Update the incident's title, description, status, severity, and affected services
    # Convert affected services from input data to AffectedService objects
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

    # Update the incident in the database
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

    # Re-fetch the incident to ensure it was updated
    incident = await Incident.find_by_id(incident_data.incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident.id is None:
        raise HTTPException(
            status_code=500, detail="Incident ID is not set after update."
        )

    # Check if the user ID is available
    # Raise an HTTPException if not
    if user.id is None:
        raise HTTPException(status_code=500, detail="User ID is not available.")

    # Log the update of the incident
    # Save the log entry to the database
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

    # Update the status of affected services in the database
    for affected_service in incident.affected_services:
        await Service.collection().update_one(
            {"_id": affected_service.service_id},
            {"$set": {"status": affected_service.status.value}},
        )

    # Broadcast the update of the incident to connected clients
    await broadcast_message(
        {
            "type": "incident",
            "data": incident.model_dump_json(),
            "action": "update",
        }
    )
    return incident


# Endpoint to list all incidents for a given organization
# Accepts organization ID and the current user as input
# Returns a list of incidents
@router.get("/get-all-incidents", response_model=List[Incident])
async def list_incidents(org_id: str, user: User = Depends(get_current_user)):
    # Find all incidents for the given organization ID
    incidents = await Incident.find_all(
        {
            "org_id": PyObjectId(org_id),
        }
    )
    return incidents


# Endpoint to delete an incident
# Accepts incident ID and the current user as input
# Returns the deleted incident
@router.delete("/delete-incident", response_model=Incident)
async def delete_incident(incident_id: str, user: User = Depends(get_current_user)):
    # Find the incident by its ID
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

    # Check if the incident ID is set after deletion
    # Raise an HTTPException if not
    if incident.id is None:
        raise HTTPException(
            status_code=500, detail="Incident ID is not set after deletion."
        )

    # Check if the user ID is available
    # Raise an HTTPException if not
    if user.id is None:
        raise HTTPException(status_code=500, detail="User ID is not available.")

    # Log the deletion of the incident
    # Save the log entry to the database
    log_entry = LogEntry(
        entity_id=incident.id,
        entity_type=EntityType.INCIDENT,
        change_type=ChangeType.DELETE,
        changes={},
        org_id=incident.org_id,
        created_by=user.id,
    )
    await log_entry.save()

    # Broadcast the deletion of the incident to connected clients
    await broadcast_message(
        {"type": "incident", "data": incident.model_dump_json(), "action": "delete"}
    )
    return incident


# Endpoint to fetch a specific incident by its ID
# Accepts incident ID as input
# Returns the incident if found
@router.get("/{incident_id}", response_model=Incident)
async def fetch_incident(incident_id: str):
    # Find the incident by its ID
    incident = await Incident.find_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
